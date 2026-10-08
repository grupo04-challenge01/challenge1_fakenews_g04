"""Fluxo do copiloto em eventos para a página (decisões 3 e 4 do design).

`verificar` roda `bancada.pipeline.executar` e chama `emitir` com um evento por
vez: `fronteira` primeiro, depois `andamento` da etapa em curso, e por fim
`resposta`, `aviso` ou `erro`. Quando a fronteira encerra o fluxo (urgência,
sofrimento psíquico), o único evento é o da fronteira, com a resposta padrão.

Os textos da interface vêm dos blocos `##### Texto` da spec `interface-chat-web`,
com os do delta de add-entrada-por-link por cima (link, falhas de leitura e
origem). Arquivados os dois changes, a spec principal já traz todos.

"Abrindo o link…" só aparece quando a página vai mesmo ser buscada, pela mesma
regra de `executar`; falha de leitura vira `aviso` com a causa, e a resposta
leva a origem quando o texto verificado veio de página (add-entrada-por-link).
"""
import logging
import pathlib

from bancada.pipeline import ETAPAS, PALAVRAS_TEXTO_CURTO, executar
from prototipo.entrada import link
from prototipo.entrada.rede import buscar as buscar_rede
from prototipo.identidade import ler_textos
from prototipo.verificacao.modelo import chat_ollama

RAIZ = pathlib.Path(__file__).parents[1]
SPEC = [RAIZ / "openspec/changes/add-interface-chat-web/specs/interface-chat-web/spec.md",
        RAIZ / "openspec/specs/interface-chat-web/spec.md"]
SOBREPOSICAO = [RAIZ / "openspec/changes/add-entrada-por-link/specs/interface-chat-web/spec.md",
               RAIZ / "openspec/changes/add-gerador-api-deepseek/specs/interface-chat-web/spec.md"]

log = logging.getLogger("dona_checa")


def textos():
    """Textos próprios da interface, com `andamento` como {etapa: frase}."""
    spec = next((p for p in SPEC if p.exists()), None)
    if spec is None:
        raise FileNotFoundError("spec interface-chat-web não encontrada")
    t = ler_textos(spec)
    for delta in SOBREPOSICAO:
        if delta.exists():
            t.update(ler_textos(delta))
    t["andamento"] = dict(linha.split(": ", 1) for linha in t["andamento"].splitlines())
    if "leitura" in t:
        t["andamento"]["leitura"] = t["leitura"]
    return t


def _desfecho(saida):
    categorias = saida["categorias"]
    if saida["bypass"]:
        return "urgencia" if "risco_imediato" in categorias else "sofrimento"
    return "conduta" if "conduta_individual" in categorias else "segue"


def _origem(rastro):
    origem = rastro.get("origem") or {}
    if origem.get("tipo") != "pagina":
        return None
    return {chave: origem[chave] for chave in ("titulo", "veiculo", "data", "url")}


def verificar(texto, emitir, *, recuperador, chat=chat_ollama, canal="web",
              buscar=buscar_rede):
    t = textos()
    desfecho = {}
    texto_pessoa, urls = link.separar(texto)
    le_primeiro = bool(urls) and len(texto_pessoa.split()) < PALAVRAS_TEXTO_CURTO
    lida = {"pagina": False}

    def proxima(nome, saida):
        """Etapa que vem a seguir, ou None quando ela já foi anunciada."""
        if nome == "fronteira":
            return "leitura" if le_primeiro else "extracao"
        if nome == "leitura":
            if saida.get("tipo") == "texto":
                return None  # leitura sem busca: a extração já foi anunciada
            lida["pagina"] = True
            return "extracao"
        if nome == "extracao" and urls and not lida["pagina"] and not saida.get("selecionada"):
            return "leitura"  # texto longo sem alegação: a página vai ser buscada
        seguinte = ETAPAS.index(nome) + 1
        return ETAPAS[seguinte] if seguinte < len(ETAPAS) else None

    def ao_etapa(registro):
        nome = registro["etapa"]
        if "erro" in registro:
            return
        if nome == "fronteira":
            desfecho["valor"] = _desfecho(registro["saida"])
            if desfecho["valor"] in ("urgencia", "sofrimento"):
                return  # o texto só existe no rastro depois que o fluxo para
            emitir({"tipo": "fronteira", "desfecho": desfecho["valor"], "texto": None})
        etapa = proxima(nome, registro["saida"] or {})
        if etapa:
            emitir({"tipo": "andamento", "etapa": etapa, "frase": t["andamento"][etapa]})

    try:
        rastro = executar(texto, recuperador, chat=chat, canal=canal, ao_etapa=ao_etapa,
                          buscar=buscar)
    except Exception as e:  # erro fora de etapa: nada do texto vai ao log
        log.error("fluxo falhou fora de etapa: %s", type(e).__name__)
        emitir({"tipo": "erro", "texto": t["erro"]})
        return

    if rastro["motivo"] == "erro":
        registro = rastro["etapas"][-1]
        log.error("etapa %s falhou: %s (%.3f s)", registro["etapa"],
                  registro["erro"].split(":", 1)[0], registro["segundos"])
        emitir({"tipo": "erro", "texto": t["erro"]})
    elif rastro["motivo"] == "bypass":
        emitir({"tipo": "fronteira", "desfecho": desfecho["valor"],
                "texto": rastro["resposta"]["texto"]})
    elif rastro["parou_em"] == "leitura":
        causa = rastro["motivo"]
        emitir({"tipo": "aviso", "chave": causa, "texto": t[causa]})
    elif rastro["parou_em"] == "extracao":
        emitir({"tipo": "aviso", "chave": "sem_alegacao", "texto": t["sem_alegacao"]})
    else:
        resposta = next(e for e in rastro["etapas"] if e["etapa"] == "resposta")["saida"]
        emitir({"tipo": "resposta", "forma": rastro["resposta"]["forma"],
                "texto": rastro["resposta"]["texto"], "detalhe": resposta["detalhe"],
                "redirecionamentos": list(rastro["redirecionamentos"]),
                "origem": _origem(rastro)})
