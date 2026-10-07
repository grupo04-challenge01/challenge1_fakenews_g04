"""Fluxo inteiro do copiloto sobre uma mensagem, com rastro por etapa.

Ordem: fronteira, extração, decomposição, recuperação, guarda e resposta.
Bypass da fronteira encerra com as respostas padrão do canal; alegação não
verificável encerra antes da recuperação. Erro numa etapa fica no rastro e
encerra o fluxo ali, para que o defeito seja visto onde nasceu.

`chat` e `recuperador` são injetáveis: os testes e o modo offline trocam o
modelo e o índice por versões gravadas.
"""
import time
from dataclasses import asdict, is_dataclass

from prototipo.rag.hibrida import LIMIAR_EVIDENCIA
from prototipo.resposta import estrutura
from prototipo.verificacao import decomposicao, extracao, fronteira, guarda
from prototipo.verificacao.modelo import chat_ollama

ETAPAS = ("fronteira", "extracao", "decomposicao", "recuperacao", "guarda", "resposta")

# Tasks do MVP que o fluxo ainda não usa. Vai no rastro para que o resultado
# não seja lido como o do produto fechado.
NAO_LIGADO = (
    "1.3 fontes oficiais",
    "1.6 ancoragem trecho a afirmação",
    "detecção automática de lacuna de acervo (aqui vem do caso)",
)


class _Parar(Exception):
    pass


def _plano(valor):
    if is_dataclass(valor):
        return asdict(valor)
    if isinstance(valor, (list, tuple)):
        return [_plano(v) for v in valor]
    return valor


def _recuperar(recuperador, alegacao, k, modo, idioma):
    """Trechos para a guarda e o resumo da etapa.

    Com `idioma`, é a entrada do sistema (`recuperar`, task 1.4): português
    antes de inglês. Sem, é o ranking cru (`buscar`), o que a aferição mede.
    """
    if not idioma:
        trechos = recuperador.buscar(alegacao, k=k, modo=modo)
        return trechos, {"idioma": None, "coberto": None, "consultados": [],
                         "resultados": trechos}
    r = recuperador.recuperar(alegacao, k=k, modo=modo)
    return r.resultados, {"idioma": r.idioma, "coberto": r.coberto,
                          "consultados": list(r.consultados), "resultados": r.resultados}


def executar(texto, recuperador, chat=chat_ollama, canal="web", k=5, modo="hibrida",
             alfa=None, limiar=LIMIAR_EVIDENCIA, lacuna=None, idioma=True, ao_etapa=None):
    """Rastro do fluxo: parâmetros, etapas na ordem, onde parou e a resposta.

    `ao_etapa`, se dado, recebe o registro de cada etapa assim que ele entra no
    rastro, inclusive o da etapa que errou: é por ele que a interface mostra o
    andamento (decisão 4 de add-interface-chat-web).
    """
    if alfa is not None:
        recuperador.alfa = alfa
    rastro = {
        "mensagem": texto,
        "parametros": {"canal": canal, "k": k, "modo": modo,
                       "alfa": getattr(recuperador, "alfa", None),
                       "limiar": limiar, "lacuna": lacuna,
                       "prioridade_idioma": idioma},
        "nao_ligado": list(NAO_LIGADO),
        "etapas": [],
        "parou_em": None,
        "motivo": None,
        "redirecionamentos": [],
        "resposta": None,
    }

    def etapa(nome, fn, resumo=_plano):
        inicio = time.perf_counter()
        registro = {"etapa": nome}
        try:
            valor = fn()
        except Exception as e:  # o rastro mostra o erro; o fluxo para aqui
            registro.update(erro=f"{type(e).__name__}: {e}",
                            segundos=round(time.perf_counter() - inicio, 3))
            rastro["etapas"].append(registro)
            avisar(registro)
            parar(nome, "erro")
        registro.update(saida=resumo(valor), segundos=round(time.perf_counter() - inicio, 3))
        rastro["etapas"].append(registro)
        avisar(registro)
        return valor

    def avisar(registro):
        if ao_etapa is not None:
            ao_etapa(registro)

    def parar(nome, motivo):
        rastro["parou_em"], rastro["motivo"] = nome, motivo
        raise _Parar

    try:
        intencao = etapa("fronteira", lambda: fronteira.classificar(texto, chat=chat),
                         lambda i: {"categorias": list(i.categorias), "via": i.via,
                                    "bypass": i.bypass})
        if intencao.bypass:
            rastro["resposta"] = {"forma": "fronteira",
                                  "texto": "\n\n".join(fronteira.responder(intencao, canal))}
            parar("fronteira", "bypass")
        if "conduta_individual" in intencao.categorias:
            rastro["redirecionamentos"] = fronteira.responder(intencao, canal)

        ext = etapa("extracao", lambda: extracao.extrair(texto, chat=chat))
        if not ext.verificavel:
            parar("extracao", "sem alegação verificável de saúde")
        alegacao = ext.selecionada["texto"]

        dec = etapa("decomposicao", lambda: decomposicao.decompor(texto, chat=chat))
        trechos, _ = etapa("recuperacao", lambda: _recuperar(recuperador, alegacao, k, modo, idioma),
                           lambda par: par[1])
        veredito = etapa("guarda", lambda: guarda.verificar(alegacao, trechos, chat=chat,
                                                            limiar=limiar))
        # Decisão 29: a resposta vê os fragmentos vizinhos das checagens citadas.
        expandir = lambda ts: recuperador.expandir(alegacao, ts, modo=modo)  # noqa: E731
        resp = etapa("resposta", lambda: estrutura.responder(
            texto, alegacao, veredito, decomposicao=asdict(dec), lacuna=lacuna, chat=chat,
            expandir=expandir),
            lambda r: {**asdict(r), "texto": r.texto})
        rastro["resposta"] = {"forma": resp.forma, "texto": resp.texto,
                              "defeitos": resp.defeitos}
    except _Parar:
        pass
    return rastro


def etapa_de(rastro, nome):
    """Registro da etapa no rastro, ou None se ela não rodou."""
    return next((e for e in rastro["etapas"] if e["etapa"] == nome), None)
