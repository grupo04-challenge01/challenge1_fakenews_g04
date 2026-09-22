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


ALFAS_VARREDURA = tuple(round(0.70 + 0.02 * i, 2) for i in range(16))


def _reciproco(posicao: int | None) -> float:
    return 1.0 / posicao if posicao else 0.0


def _mrr_de(posicoes: dict, ids: list[str]) -> float:
    return sum(_reciproco(posicoes[i]) for i in ids) / len(ids)


def _recall_de(posicoes: dict, ids: list[str], corte: int) -> float:
    acertos = sum(1 for i in ids
                  if posicoes[i] is not None and posicoes[i] <= corte)
    return acertos / len(ids)


def varrer_alfa(recuperador, dados: dict | None = None,
                alfas=ALFAS_VARREDURA, k: int = max(CORTES)) -> dict:
    """Task 3.1 — o peso do braço denso na fusão por score.

    `hibrida.py` declara `alfa` provisório e parâmetro explícito «para que a
    task 3.1 possa varrê-lo». `aferir_tudo` mede um alfa só, e medir um alfa só
    não compara arquiteturas: compara uma calibração. A primeira medição com
    alfa em 0,5 concluiu que a híbrida perde da densa pura, e a varredura
    mostrou que o que perdia era o 0,5.

    Duas guardas contra ler ruído de 20 consultas como achado:

    - **forma da curva.** Um ótimo isolado entre vizinhos piores é indistinguível
      de sorte. `dentro_de_0_01_do_topo` diz a largura do platô, e um platô
      largo é o que autoriza fixar o padrão.
    - **leave-one-out.** Escolher alfa e avaliar no mesmo conjunto superestima.
      O campo `leave_one_out` escolhe alfa em n-1 consultas, avalia na que
      ficou de fora, e compara com a densa pura. Se a híbrida não ganhar aqui,
      **ela não ganha** — foi o que aconteceu com o `e5-small`.
    """
    dados = dados or carregar_consultas()
    consultas = dados["consultas"]
    ids = [c["id"] for c in consultas]
    alfa_original = recuperador.alfa

    por_alfa = {}
    try:
        for alfa in alfas:
            recuperador.alfa = alfa
            por_alfa[alfa] = aferir_modo(recuperador, consultas, "hibrida", k)
    finally:
        recuperador.alfa = alfa_original

    posicoes = {a: por_alfa[a]["posicoes"] for a in alfas}
    chave = lambda a, sub: (_recall_de(posicoes[a], sub, 5),  # noqa: E731
                            _mrr_de(posicoes[a], sub))

    melhor = max(alfas, key=lambda a: chave(a, ids))
    teto = chave(melhor, ids)
    proximos = [a for a in alfas
                if _recall_de(posicoes[a], ids, 5) == teto[0]
                and _mrr_de(posicoes[a], ids) >= teto[1] - 0.01]

    # Leave-one-out: o alfa é escolhido sem ver a consulta em que é avaliado.
    validacao = []
    for fora in ids:
        dentro = [i for i in ids if i != fora]
        escolhido = max(alfas, key=lambda a: chave(a, dentro))
        validacao.append({
            "consulta": fora,
            "alfa_escolhido": escolhido,
            "reciproco_hibrida": round(_reciproco(posicoes[escolhido][fora]), 4),
            "reciproco_densa_pura": round(_reciproco(posicoes[1.0][fora]), 4)
            if 1.0 in posicoes else None,
        })

    mrr_validado = sum(v["reciproco_hibrida"] for v in validacao) / len(validacao)
    densos = [v["reciproco_densa_pura"] for v in validacao
              if v["reciproco_densa_pura"] is not None]
    mrr_densa = sum(densos) / len(densos) if densos else None
    ganha = mrr_densa is not None and mrr_validado > mrr_densa

    return {
        "conjunto": {"versao": dados["versao"], "n": dados["n"]},
        "modelo_embedding": recuperador.denso.modelo_nome,
        "fusao": "score",
        "alfas": list(alfas),
        "por_alfa": {str(a): {"recall": por_alfa[a]["recall"],
                              "mrr": por_alfa[a]["mrr"],
                              "nao_encontrados": por_alfa[a]["nao_encontrados"],
                              "posicoes": por_alfa[a]["posicoes"]}
                     for a in alfas},
        "melhor_alfa": melhor,
        "dentro_de_0_01_do_topo": proximos,
        "leave_one_out": {
            "por_consulta": validacao,
            "mrr_validado": round(mrr_validado, 4),
            "mrr_densa_pura": round(mrr_densa, 4) if mrr_densa is not None else None,
            "alfas_escolhidos": sorted({v["alfa_escolhido"] for v in validacao}),
            "hibrida_ganha_fora_da_amostra": ganha,
        },
        "leitura": (
            f"o platô de recall@5 máximo cobre {len(proximos)} "
            f"{'valor' if len(proximos) == 1 else 'valores'} de alfa "
            f"({min(proximos)} a {max(proximos)}), e a híbrida "
            f"{'supera' if ganha else 'NÃO supera'} a densa pura sob "
            f"leave-one-out. Fixar o padrão "
            f"{'é' if ganha else 'NÃO é'} justificado para este modelo."),
    }


def calibrar_limiar(recuperador, dados: dict | None = None,
                    modo: str = "hibrida") -> dict:
    """Task 3.5 — o limiar de `evidência insuficiente` sobre o score fundido.

    Compara duas distribuições sobre o mesmo índice:

    - **positivas**: o score do documento correto, nas 20 consultas de aferição
      cujo alvo é conhecido;
    - **sem alvo**: o score do topo, nas consultas de pauta ausente do corpus.

    Se as duas se sobrepõem, não existe limiar sobre score bruto que separe — e
    o registro precisa dizer isso, porque é o caso que a sonda de 18/09 já
    sugeria e a decisão 4 do `design.md` depende de saber.
    """
    dados = dados or carregar_consultas()

    positivas = []
    for consulta in dados["consultas"]:
        resultados = recuperador.buscar(consulta["consulta"], k=max(CORTES),
                                        modo=modo)
        alvo = next((r for r in resultados
                     if _registro_de(r) == consulta["registro_id"]), None)
        positivas.append({
            "id": consulta["id"],
            "familia": consulta["familia"],
            "score_do_alvo": round(alvo["score"], 4) if alvo else None,
            "score_do_topo": round(resultados[0]["score"], 4) if resultados else None,
        })

    sem_alvo = []
    for consulta in dados["consultas_sem_alvo"]["consultas"]:
        resultados = recuperador.buscar(consulta["consulta"], k=max(CORTES),
                                        modo=modo)
        sem_alvo.append({
            "id": consulta["id"],
            "consulta": consulta["consulta"],
            "score_do_topo": round(resultados[0]["score"], 4) if resultados else None,
            "topo_recuperado": resultados[0]["alegacao"][:90] if resultados else "",
        })

    alvos = [p["score_do_alvo"] for p in positivas if p["score_do_alvo"] is not None]
    ruidos = [n["score_do_topo"] for n in sem_alvo if n["score_do_topo"] is not None]

    separa = bool(alvos) and bool(ruidos) and min(alvos) > max(ruidos)

    return {
        "modo": modo,
        "positivas": positivas,
        "sem_alvo": sem_alvo,
        "faixa_do_alvo": {"minimo": min(alvos), "mediana": statistics.median(alvos),
                          "maximo": max(alvos)} if alvos else {},
        "faixa_do_ruido": {"minimo": min(ruidos), "mediana": statistics.median(ruidos),
                           "maximo": max(ruidos)} if ruidos else {},
        "score_bruto_separa": separa,
        "limiar_sugerido": (round((min(alvos) + max(ruidos)) / 2, 4)
                            if separa else None),
        "leitura": (
            "as duas distribuições não se cruzam; um limiar sobre o score "
            "fundido separa recuperação útil de ruído"
            if separa else
            "as distribuições se sobrepõem: NÃO existe limiar sobre score "
            "bruto que separe. `evidência insuficiente` precisa de outro sinal "
            "— confirma o achado de 18/09 e obriga a decisão 4 a registrar o "
            "limite. A resposta de lacuna de acervo de `frescor-corpus`, que "
            "decide pela janela do acervo e não pelo score, continua valendo e "
            "fica sendo o único mecanismo medido que funciona hoje."),
    }
