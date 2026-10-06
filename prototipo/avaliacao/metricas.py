"""Métricas de resultado e de guarda — task 6.5 de mvp-copiloto-verificacao.

Requirement Métricas de resultado e de guarda, de `avaliacao-instrumento`:

- resultado: discernimento (acerto com a ferramenta), transferência (acerto sem
  ela, reportado à parte), tempo até decisão fundamentada e consulta a fonte
  externa;
- guarda: aceitação cega quando a IA erra, falso positivo em conteúdo legítimo,
  queda de confiança em fonte confiável e abandono por atrito.

Entra o registro de sessão (`registro_sessao.json`, já validado por
`sessao.validar`) e o conjunto de casos indexado por id. Sai um dicionário de
números; nenhuma taxa leva limiar de aprovação, porque a spec não define um e
a decisão sobre o que é aceitável é do grupo, depois do piloto. Toda taxa é
`{"n", "de", "taxa"}`: com 2 a 30 participantes a fração diz mais que o
percentual, e denominador zero dá `taxa` nula em vez de 0.

Definições operacionais: decisão 27 do design.md.
"""
from __future__ import annotations

import collections
import datetime as dt
import statistics

CONFIAVEL = "confiavel"
NAO_CONFIAVEL = "nao_confiavel"
COM = "com_ferramenta"
TRANSF = "transferencia"

# Veredito do gabarito ou rótulo exibido -> julgamento que concorda com ele.
# "evidência insuficiente" não tem polaridade: a ferramenta se absteve, não errou.
POLARIDADE = {
    "falso": NAO_CONFIAVEL,
    "verdadeiro fora de contexto ou exagerado": NAO_CONFIAVEL,
    "verdadeiro": CONFIAVEL,
    "evidência insuficiente": None,
}


def polaridade(rotulo: str | None) -> str | None:
    return POLARIDADE.get(rotulo) if rotulo else None


def fracao(n: int, de: int) -> dict:
    return {"n": n, "de": de, "taxa": round(n / de, 3) if de else None}


def _soma(fracoes: list[dict]) -> dict:
    return fracao(sum(f["n"] for f in fracoes), sum(f["de"] for f in fracoes))


def _instante(texto: str) -> dt.datetime:
    # Python 3.10 não lê o sufixo Z.
    return dt.datetime.fromisoformat(texto.replace("Z", "+00:00"))


def segundos(item: dict) -> float | None:
    if not item.get("decisao"):
        return None
    return (_instante(item["decisao"]) - _instante(item["inicio"])).total_seconds()


def concluido(item: dict) -> bool:
    return item.get("abandono") is None


def gabarito(item: dict, casos: dict) -> str:
    return polaridade(casos[item["caso_id"]]["veredito"])


def acertou(item: dict, casos: dict) -> bool:
    return item["julgamento"] == gabarito(item, casos)


def erro_ia(item: dict, casos: dict) -> bool:
    """A ferramenta exibiu um veredito de polaridade oposta à do gabarito."""
    exibido = polaridade(item.get("rotulo_exibido"))
    return exibido is not None and exibido != gabarito(item, casos)


def reacao(item: dict) -> str:
    """Classificação do cenário Item-armadilha: aceitou, questionou ou consultou fonte.

    Vale o comportamento mais forte observado: consultar (camada de detalhe ou
    fora da ferramenta) vence questionar, que vence aceitar.
    """
    if item.get("abriu_detalhe") or item.get("consultou_fonte_externa"):
        return "consultou_fonte"
    if item.get("expressou_duvida"):
        return "questionou"
    return "aceitou"


def aceitou_cegamente(item: dict, casos: dict) -> bool:
    """IA errou, participante não questionou nem consultou e julgou como a IA."""
    return (erro_ia(item, casos) and reacao(item) == "aceitou"
            and item["julgamento"] == polaridade(item["rotulo_exibido"]))


def _mediana(valores: list[float]) -> dict:
    return {"mediana": statistics.median(valores) if valores else None, "n": len(valores)}


def _confianca(registro: dict) -> dict:
    inicio = registro["confianca_fontes"]["inicio"]
    fim = registro["confianca_fontes"]["fim"]
    if fim is None:
        return {"inicio": statistics.mean(inicio.values()), "fim": None, "delta_medio": None, "queda": None}
    a, b = statistics.mean(inicio.values()), statistics.mean(fim.values())
    delta = round(b - a, 3)
    return {"inicio": round(a, 3), "fim": round(b, 3), "delta_medio": delta, "queda": delta < 0}


def metricas_sessao(registro: dict, casos: dict) -> dict:
    itens = registro["itens"]
    com = [i for i in itens if i["bloco"] == COM]
    transf = [i for i in itens if i["bloco"] == TRANSF]
    com_ok = [i for i in com if concluido(i)]
    transf_ok = [i for i in transf if concluido(i)]
    nao_armadilha = [i for i in com_ok if not casos[i["caso_id"]].get("armadilha")]
    armadilhas_com_erro = [i for i in com_ok if casos[i["caso_id"]].get("armadilha") and erro_ia(i, casos)]
    erros = [i for i in com_ok if erro_ia(i, casos)]
    legitimos_com = [i for i in com_ok if gabarito(i, casos) == CONFIAVEL]
    legitimos_transf = [i for i in transf_ok if gabarito(i, casos) == CONFIAVEL]
    fundamentadas = lambda bloco: [segundos(i) for i in bloco if concluido(i) and i["criterios_citados"]]
    abandono_sessao = registro.get("abandono_sessao")

    return {
        "participante": registro["participante"],
        "tipo": registro["tipo"],
        "resultado": {
            "discernimento": fracao(sum(acertou(i, casos) for i in nao_armadilha), len(nao_armadilha)),
            "transferencia": fracao(sum(acertou(i, casos) for i in transf_ok), len(transf_ok)),
            "transferencia_com_criterio": fracao(sum(bool(i["criterios_citados"]) for i in transf_ok),
                                                 len(transf_ok)),
            "criterios_transferencia": dict(collections.Counter(
                c for i in transf_ok for c in i["criterios_citados"])),
            "tempo_decisao_fundamentada_s": {COM: _mediana(fundamentadas(com)),
                                             TRANSF: _mediana(fundamentadas(transf))},
            "consulta_fonte_externa": {
                COM: fracao(sum(i["consultou_fonte_externa"] for i in com_ok), len(com_ok)),
                TRANSF: fracao(sum(i["consultou_fonte_externa"] for i in transf_ok), len(transf_ok)),
            },
            "abriu_camada_detalhe": fracao(sum(i["abriu_detalhe"] for i in com_ok), len(com_ok)),
        },
        "guarda": {
            "aceitacao_cega": {
                "armadilhas": fracao(sum(aceitou_cegamente(i, casos) for i in armadilhas_com_erro),
                                     len(armadilhas_com_erro)),
                "todos_erros": fracao(sum(aceitou_cegamente(i, casos) for i in erros), len(erros)),
            },
            "falso_positivo_legitimo": {
                "participante_com_ferramenta": fracao(
                    sum(i["julgamento"] == NAO_CONFIAVEL for i in legitimos_com), len(legitimos_com)),
                "participante_transferencia": fracao(
                    sum(i["julgamento"] == NAO_CONFIAVEL for i in legitimos_transf), len(legitimos_transf)),
                "sistema": fracao(
                    sum(polaridade(i["rotulo_exibido"]) == NAO_CONFIAVEL for i in legitimos_com),
                    len(legitimos_com)),
            },
            "confianca_fontes": _confianca(registro),
            "abandono_atrito": {
                "itens": fracao(sum((i.get("abandono") or {}).get("motivo") == "atrito" for i in itens),
                                len(itens)),
                "sessao": bool(abandono_sessao and abandono_sessao["motivo"] == "atrito"),
            },
        },
    }


def _tempos(registros: list[dict], bloco: str) -> list[float]:
    return [segundos(i) for reg in registros for i in reg["itens"]
            if i["bloco"] == bloco and concluido(i) and i["criterios_citados"]]


def _agregar_grupo(registros: list[dict], sessoes: list[dict]) -> dict:
    r = [s["resultado"] for s in sessoes]
    g = [s["guarda"] for s in sessoes]
    criterios = collections.Counter()
    for x in r:
        criterios.update(x["criterios_transferencia"])
    deltas = [x["confianca_fontes"]["delta_medio"] for x in g if x["confianca_fontes"]["delta_medio"] is not None]
    return {
        "sessoes": len(sessoes),
        "resultado": {
            "discernimento": _soma([x["discernimento"] for x in r]),
            "transferencia": _soma([x["transferencia"] for x in r]),
            "transferencia_com_criterio": _soma([x["transferencia_com_criterio"] for x in r]),
            "criterios_transferencia": dict(criterios.most_common()),
            "tempo_decisao_fundamentada_s": {b: _mediana(_tempos(registros, b)) for b in (COM, TRANSF)},
            "consulta_fonte_externa": {b: _soma([x["consulta_fonte_externa"][b] for x in r]) for b in (COM, TRANSF)},
            "abriu_camada_detalhe": _soma([x["abriu_camada_detalhe"] for x in r]),
        },
        "guarda": {
            "aceitacao_cega": {k: _soma([x["aceitacao_cega"][k] for x in g]) for k in ("armadilhas", "todos_erros")},
            "falso_positivo_legitimo": {
                k: _soma([x["falso_positivo_legitimo"][k] for x in g])
                for k in ("participante_com_ferramenta", "participante_transferencia", "sistema")},
            "confianca_fontes": {
                "sessoes_com_queda": fracao(sum(d < 0 for d in deltas), len(deltas)),
                "delta_medio": round(statistics.mean(deltas), 3) if deltas else None,
            },
            "abandono_atrito": {
                "sessoes": fracao(sum(x["abandono_atrito"]["sessao"] for x in g), len(g)),
                "itens": _soma([x["abandono_atrito"]["itens"] for x in g]),
            },
        },
    }


def agregar(registros: list[dict], casos: dict) -> dict:
    """Agrega por tipo de sessão. Piloto e coleta nunca se misturam."""
    por_tipo: dict[str, list[dict]] = collections.defaultdict(list)
    for registro in registros:
        por_tipo[registro["tipo"]].append(registro)
    return {tipo: _agregar_grupo(grupo, [metricas_sessao(r, casos) for r in grupo])
            for tipo, grupo in por_tipo.items()}
