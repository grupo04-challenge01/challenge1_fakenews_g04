"""Fluxo inteiro do copiloto sobre uma mensagem, com rastro por etapa.

Ordem: fronteira, leitura, extração, decomposição, recuperação, guarda e
resposta. Bypass da fronteira encerra com as respostas padrão do canal; link
que não pôde ser lido encerra na leitura; alegação não verificável encerra
antes da recuperação. Erro numa etapa fica no rastro e
encerra o fluxo ali, para que o defeito seja visto onde nasceu.

`chat`, `recuperador` e `buscar` são injetáveis: os testes e o modo offline
trocam o modelo, o índice e a rede por versões gravadas.
"""
import time
from dataclasses import asdict, is_dataclass

from prototipo.entrada import leitura, link
from prototipo.entrada.rede import buscar as buscar_rede
from prototipo.rag.hibrida import LIMIAR_EVIDENCIA
from prototipo.resposta import estrutura
from prototipo.verificacao import decomposicao, extracao, fronteira, guarda
from prototipo.verificacao.modelo import chat_ollama

ETAPAS = ("fronteira", "leitura", "extracao", "decomposicao", "recuperacao", "guarda",
          "resposta")
# Abaixo disso, o texto da pessoa é comentário sobre o link e a página é verificada
# (add-entrada-por-link, requirement Escolha entre texto e página).
PALAVRAS_TEXTO_CURTO = 30

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


def _origem(lido=None, url=None, ignorados=()):
    """Origem do texto verificado (add-entrada-por-link, D2)."""
    if isinstance(lido, leitura.Leitura):
        return {"tipo": "pagina", "url": lido.url, "titulo": lido.titulo,
                "veiculo": lido.veiculo, "data": lido.data, "parcial": lido.parcial,
                "cortado": lido.cortado, "ignorados": list(ignorados)}
    return {"tipo": "pagina" if url else "texto", "url": url, "titulo": None,
            "veiculo": None, "data": None, "parcial": False, "cortado": False,
            "ignorados": list(ignorados)}


def executar(texto, recuperador, chat=chat_ollama, canal="web", k=5, modo="hibrida",
             alfa=None, limiar=LIMIAR_EVIDENCIA, lacuna=None, idioma=True, ao_etapa=None,
             buscar=buscar_rede):
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
        "origem": None,
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

    # A fronteira lê só o que a pessoa escreveu; sem link, a mensagem inteira.
    texto_pessoa, urls = link.separar(texto)
    entrada = texto_pessoa if urls else texto

    def classificar():
        if not entrada:
            return fronteira.Intencao((), "sem texto da pessoa")
        return fronteira.classificar(entrada, chat=chat)

    def ler_pagina():
        lido = etapa("leitura", lambda: leitura.ler(urls[0], buscar=buscar))
        if isinstance(lido, leitura.Falha):
            rastro["origem"] = _origem(url=lido.url, ignorados=urls[1:])
            rastro["resposta"] = {"forma": "leitura", "causa": lido.causa}
            parar("leitura", lido.causa)
        rastro["origem"] = _origem(lido, ignorados=urls[1:])
        return lido

    try:
        intencao = etapa("fronteira", classificar,
                         lambda i: {"categorias": list(i.categorias), "via": i.via,
                                    "bypass": i.bypass})
        if intencao.bypass:
            rastro["resposta"] = {"forma": "fronteira",
                                  "texto": "\n\n".join(fronteira.responder(intencao, canal))}
            parar("fronteira", "bypass")
        if "conduta_individual" in intencao.categorias:
            rastro["redirecionamentos"] = fronteira.responder(intencao, canal)

        lido = None
        if urls and len(texto_pessoa.split()) < PALAVRAS_TEXTO_CURTO:
            lido = ler_pagina()
            alvo = leitura.citar(lido.texto)
        else:
            rastro["origem"] = etapa("leitura", lambda: _origem(ignorados=urls[1:]))
            alvo = entrada
        ext = etapa("extracao", lambda: extracao.extrair(alvo, chat=chat))
        if not ext.verificavel and urls and lido is None:
            # Texto longo sem alegação: a alegação deve estar na página.
            lido = ler_pagina()
            alvo = leitura.citar(lido.texto)
            ext = etapa("extracao", lambda: extracao.extrair(alvo, chat=chat))
        if not ext.verificavel:
            if lido is not None and lido.parcial:
                # Pouco texto lido e nada de saúde nele: a falha é de leitura.
                rastro["resposta"] = {"forma": "leitura", "causa": "vazia"}
                parar("leitura", "vazia")
            parar("extracao", "sem alegação verificável de saúde")
        alegacao = ext.selecionada["texto"]
        aviso = leitura.AVISO_PARCIAL if lido is not None and lido.parcial else None

        def decompor():
            # A decomposição só separa a opinião no bloco 2: falhando duas vezes,
            # a resposta segue sem ela, em vez de virar erro (fix-pergunta-e-conduta, D7).
            try:
                return decomposicao.decompor(alvo, chat=chat)
            except ValueError as e:
                return {"omitida": str(e)}

        dec = etapa("decomposicao", decompor)
        trechos, _ = etapa("recuperacao", lambda: _recuperar(recuperador, alegacao, k, modo, idioma),
                           lambda par: par[1])
        veredito = etapa("guarda", lambda: guarda.verificar(alegacao, trechos, chat=chat,
                                                            limiar=limiar))
        # Decisão 29: a resposta vê os fragmentos vizinhos das checagens citadas.
        expandir = lambda ts: recuperador.expandir(alegacao, ts, modo=modo)  # noqa: E731
        resp = etapa("resposta", lambda: estrutura.responder(
            alvo, alegacao, veredito,
            decomposicao=None if isinstance(dec, dict) else asdict(dec), lacuna=lacuna, chat=chat,
            expandir=expandir, aviso=aviso),
            lambda r: {**asdict(r), "texto": r.texto})
        rastro["resposta"] = {"forma": resp.forma, "texto": resp.texto,
                              "defeitos": resp.defeitos}
    except _Parar:
        pass
    return rastro


def etapa_de(rastro, nome):
    """Registro da etapa no rastro, ou None se ela não rodou."""
    return next((e for e in rastro["etapas"] if e["etapa"] == nome), None)
