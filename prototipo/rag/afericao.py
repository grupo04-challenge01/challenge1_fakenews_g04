"""Aferição da recuperação — tasks 3.1 a 3.6 de add-selecao-modelos-arquitetura-rag.

O índice de 18/09 funciona mas não está medido: a sobreposição de 35% entre os
braços é sanidade, não aferição. Este módulo mede recall das três configurações
— só léxica, só densa, híbrida — sobre o conjunto de 20 consultas da task 2.6,
onde o documento correto é conhecido para cada uma.

**O resultado é registrado mesmo se contrariar a decisão 4 do `design.md`**,
que adotou o híbrido como linha de base. É a task 3.2 em texto expresso, e é a
única forma de a medição significar alguma coisa.

Um acerto é a recuperação trazer, dentro do corte `k`, qualquer unidade cujo
`registro_id` seja o do documento correto — porque um registro pode gerar mais
de uma unidade quando cobre mais de uma alegação.
"""
from __future__ import annotations

import json
import pathlib
import statistics
import time

CONSULTAS = pathlib.Path(__file__).resolve().parent / "consultas_afericao.json"
CORTES = (1, 3, 5, 10)
MODOS = ("lexica", "densa", "hibrida")


def carregar_consultas(caminho: pathlib.Path = CONSULTAS) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def _registro_de(unidade: dict) -> str:
    """O registro de origem da unidade, que é o que a consulta aponta."""
    return unidade.get("registro_id") or unidade["unidade_id"].split("-")[0]


def posicao_do_alvo(resultados: list[dict], registro_id: str) -> int | None:
    """Posição (1-based) da primeira unidade do documento correto, ou None."""
    for posicao, unidade in enumerate(resultados, start=1):
        if _registro_de(unidade) == registro_id:
            return posicao
    return None


def aferir_modo(recuperador, consultas: list[dict], modo: str,
                k: int = max(CORTES), fusao: str = "score") -> dict:
    """Recall@k e latência de um modo, sobre todas as consultas."""
    posicoes: list[int | None] = []
    latencias: list[float] = []

    for consulta in consultas:
        marca = time.perf_counter()
        resultados = recuperador.buscar(consulta["consulta"], k=k, modo=modo,
                                        fusao=fusao)
        latencias.append(time.perf_counter() - marca)
        posicoes.append(posicao_do_alvo(resultados, consulta["registro_id"]))

    def recall(corte: int) -> float:
        acertos = sum(1 for p in posicoes if p is not None and p <= corte)
        return acertos / len(posicoes)

    encontrados = [p for p in posicoes if p is not None]
    mrr = sum(1 / p for p in encontrados) / len(posicoes) if posicoes else 0.0

    return {
        "modo": modo,
        "fusao": fusao if modo == "hibrida" else "",
        "consultas": len(consultas),
        "recall": {f"@{c}": round(recall(c), 3) for c in CORTES},
        "mrr": round(mrr, 3),
        "nao_encontrados": [c["id"] for c, p in zip(consultas, posicoes)
                            if p is None],
        "latencia_s": {
            "mediana": round(statistics.median(latencias), 3),
            "media": round(statistics.fmean(latencias), 3),
            "maxima": round(max(latencias), 3),
        },
        "posicoes": {c["id"]: p for c, p in zip(consultas, posicoes)},
    }


def aferir_por_familia(recuperador, consultas: list[dict], modo: str,
                       k: int = max(CORTES)) -> dict:
    """Recall separado por família de consulta.

    Medir só com `verbatim` favorece a léxica por construção, e só com
    `reformulada` favorece a densa. A média das duas esconde isso; a separação
    é o que torna a comparação honesta.
    """
    familias = sorted({c["familia"] for c in consultas})
    return {
        familia: aferir_modo(
            recuperador, [c for c in consultas if c["familia"] == familia],
            modo, k)
        for familia in familias
    }


def aferir_tudo(recuperador, consultas_json: dict | None = None,
                k: int = max(CORTES)) -> dict:
    """As três configurações sobre o mesmo conjunto, no mesmo índice."""
    dados = consultas_json or carregar_consultas()
    consultas = dados["consultas"]

    por_modo = {modo: aferir_modo(recuperador, consultas, modo)
                for modo in MODOS}
    por_modo["hibrida_rrf"] = aferir_modo(recuperador, consultas, "hibrida",
                                          fusao="rrf")

    melhor = max(por_modo, key=lambda m: (por_modo[m]["recall"]["@5"],
                                          por_modo[m]["mrr"]))

    return {
        "conjunto": {"versao": dados["versao"], "n": dados["n"]},
        "modelo_embedding": recuperador.denso.modelo_nome,
        "alfa": recuperador.alfa,
        "k": k,
        "por_modo": por_modo,
        "por_familia": {modo: aferir_por_familia(recuperador, consultas, modo)
                        for modo in MODOS},
        "melhor_por_recall_em_5": melhor,
        "contraria_a_decisao_4": melhor != "hibrida",
    }
