#!/usr/bin/env python3
"""Converte o FakeHealth (JSON) para CSV.

O FakeHealth vem como JSON aninhado: cada review traz uma lista `criteria` com
as avaliacoes de especialista. Este script achata isso em tres tabelas:

  fakehealth_reviews_indice.csv     uma linha por noticia (2.296)
  fakehealth_criterios_long.csv     uma linha por criterio avaliado (22.959)
  fakehealth_matriz_10_criterios.csv  uma linha por pergunta (20)

Uso:
    python fakehealth_para_csv.py --raiz <dir do fakehealth> --saida <dir>
    python fakehealth_para_csv.py --raiz ... --saida ... --com-texto

`--com-texto` acrescenta o texto da noticia original (de content/) ao indice.
Sem essa opcao o script le apenas reviews/, que sao dois arquivos.

Atencao: sao 20 perguntas unicas, nao 10. HealthStory e HealthRelease usam
conjuntos de 10 criterios diferentes -- o de release e adaptado para comunicado
institucional. Ao calibrar a Matriz de Confianca, escolha um dos conjuntos ou
faca o mapeamento entre eles a mao.

Fonte e licenca: ver datasets/FONTES.md.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

# Os dois subconjuntos do FakeHealth e o prefixo dos arquivos em content/.
SUBSETS = {
    "HealthStory": "story_reviews",
    "HealthRelease": "release_reviews",
}

COLUNAS_INDICE = [
    "dataset",
    "news_id",
    "rating",
    "title",
    "original_title",
    "news_source",
    "source_link",
    "review_link",
]

COLUNAS_LONG = COLUNAS_INDICE + [
    "criterio_idx",
    "pergunta",
    "resposta",
    "explicacao",
]

COLUNAS_TEXTO = ["texto", "autores", "data_publicacao", "url_canonica"]


def carregar_reviews(raiz: Path) -> list[dict]:
    """Le reviews/HealthStory.json e reviews/HealthRelease.json."""
    registros = []
    for subset in SUBSETS:
        caminho = raiz / "reviews" / f"{subset}.json"
        if not caminho.exists():
            sys.exit(
                f"erro: {caminho} nao encontrado.\n"
                "Os brutos do FakeHealth nao sao versionados neste repositorio; "
                "veja datasets/FONTES.md para baixar da fonte primaria."
            )
        with caminho.open(encoding="utf-8") as fh:
            for review in json.load(fh):
                review["_dataset"] = subset
                registros.append(review)
    return registros


def linha_indice(review: dict) -> dict:
    """Achata os campos de cabecalho de uma review."""
    return {
        "dataset": review["_dataset"],
        "news_id": review.get("news_id", ""),
        "rating": review.get("rating", ""),
        "title": review.get("title", ""),
        "original_title": review.get("original_title", ""),
        "news_source": review.get("news_source", ""),
        "source_link": review.get("source_link", ""),
        "review_link": review.get("link", ""),
    }


def carregar_texto(raiz: Path, review: dict) -> dict:
    """Busca o texto da noticia em content/. Nem toda review tem conteudo."""
    news_id = review.get("news_id", "")
    caminho = raiz / "content" / review["_dataset"] / f"{news_id}.json"
    if not caminho.exists():
        return dict.fromkeys(COLUNAS_TEXTO, "")
    with caminho.open(encoding="utf-8") as fh:
        conteudo = json.load(fh)
    return {
        "texto": conteudo.get("text", ""),
        "autores": "; ".join(conteudo.get("authors") or []),
        "data_publicacao": conteudo.get("publish_date", "") or "",
        "url_canonica": conteudo.get("canonical_link", ""),
    }


def escrever(caminho: Path, colunas: list[str], linhas: list[dict]) -> None:
    """Grava CSV em UTF-8 com quebra de linha LF, para casar com SHA256SUMS."""
    with caminho.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=colunas, lineterminator="\n")
        writer.writeheader()
        writer.writerows(linhas)
    print(f"  {caminho.name}: {len(linhas)} linhas")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raiz", required=True, type=Path, help="diretorio do fakehealth (com reviews/ e content/)")
    parser.add_argument("--saida", required=True, type=Path, help="diretorio onde gravar os CSVs")
    parser.add_argument("--com-texto", action="store_true", help="junta o texto da noticia de content/ ao indice")
    args = parser.parse_args()

    args.saida.mkdir(parents=True, exist_ok=True)
    reviews = carregar_reviews(args.raiz)
    print(f"{len(reviews)} reviews lidas de {args.raiz}")

    indice, longo = [], []
    sem_conteudo = 0

    for review in reviews:
        base = linha_indice(review)

        if args.com_texto:
            texto = carregar_texto(args.raiz, review)
            if not texto["texto"]:
                sem_conteudo += 1
            indice.append(base | texto)
        else:
            indice.append(base)

        # Uma linha por criterio avaliado pelo especialista.
        # criterio_idx e 1-based, para casar com o derivado ja versionado.
        for idx, criterio in enumerate(review.get("criteria") or [], start=1):
            longo.append(
                base
                | {
                    "criterio_idx": idx,
                    "pergunta": criterio.get("question", ""),
                    "resposta": criterio.get("answer", ""),
                    "explicacao": criterio.get("explanation", ""),
                }
            )

    # Agregado por pergunta: base para calibrar a Matriz de Confianca.
    matriz: dict[str, dict[str, int]] = {}
    for linha in longo:
        alvo = matriz.setdefault(linha["pergunta"], {"ocorrencias": 0, "nao_satisfatorio": 0})
        alvo["ocorrencias"] += 1
        if linha["resposta"] == "Not Satisfactory":
            alvo["nao_satisfatorio"] += 1

    colunas_indice = COLUNAS_INDICE + (COLUNAS_TEXTO if args.com_texto else [])
    escrever(args.saida / "fakehealth_reviews_indice.csv", colunas_indice, indice)
    escrever(args.saida / "fakehealth_criterios_long.csv", COLUNAS_LONG, longo)
    escrever(
        args.saida / "fakehealth_matriz_10_criterios.csv",
        ["pergunta", "ocorrencias", "nao_satisfatorio"],
        [{"pergunta": p, **matriz[p]} for p in sorted(matriz)],
    )

    print(f"\n{len(matriz)} perguntas unicas (sao 20, nao 10: os dois subconjuntos usam criterios diferentes)")
    if args.com_texto and sem_conteudo:
        print(f"{sem_conteudo} reviews sem arquivo em content/ -- colunas de texto vazias nessas linhas")


if __name__ == "__main__":
    main()
