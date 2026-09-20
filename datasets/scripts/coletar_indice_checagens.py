"""Coletor do índice de checagens recentes — bloco 7 de add-ampliacao-corpus-ptbr.

`indice-checagens-recentes` é **índice de localização, nunca de citação**: o
sistema pode dizer «a Lupa checou isso em 03/2025, aqui está», e MUST NOT
reproduzir o texto jornalístico de terceiro.

Por isso o coletor grava **nove campos do ClaimReview** e nenhum texto de
artigo. O que ele guarda é o suficiente para atribuir e apontar, e insuficiente
para substituir a leitura da fonte primária — que é exatamente a intenção.

O veredito da agência é preservado **com a grafia original** (task 7.3). A chave
canônica é derivação nossa, marcada como tal, e o mapeamento para os quatro
rótulos de `verificacao-alegacao` **não** acontece aqui: é o mapa versionado de
`normalizacao-rotulos`, e atribuir rótulo por semelhança de string é vedado.

Uso:
    python datasets/scripts/coletar_indice_checagens.py [--termos a,b,c]
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import pathlib
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[2]

# Importa o módulo irmão por caminho. `datasets/` NÃO é pacote Python de
# propósito: o nome colide com a biblioteca `datasets` do HuggingFace, que o
# `sentence-transformers` carrega.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sondar_factcheck_api as sonda  # noqa: E402

SAIDA = RAIZ / "datasets" / "derivados" / "indice_checagens_recentes.json"

# Os nove campos do ClaimReview que o índice guarda. Nenhum deles é texto de
# artigo: `title` é o título da checagem, que é atribuição, não conteúdo.
CAMPOS = (
    "alegacao",              # claim.text
    "alegacao_autor",        # claim.claimant
    "alegacao_data",         # claim.claimDate
    "agencia",               # claimReview.publisher.name
    "agencia_site",          # claimReview.publisher.site
    "data_da_checagem",      # claimReview.reviewDate
    "veredito_original",     # claimReview.textualRating — grafia preservada
    "titulo_da_checagem",    # claimReview.title
    "url",                   # claimReview.url
)

PAUSA_S = 0.4


def chave_canonica(valor: str) -> str:
    """Derivação nossa, marcada como tal. Dobra caixa e acento, nada mais."""
    sem = "".join(c for c in unicodedata.normalize("NFD", valor)
                  if unicodedata.category(c) != "Mn")
    return sem.strip().lower()


def extrair(claim: dict) -> list[dict]:
    """Um registro por review, com os nove campos e nada além deles."""
    linhas = []
    for review in claim.get("claimReview", []):
        editor = review.get("publisher", {}) or {}
        veredito = review.get("textualRating", "") or ""
        linhas.append({
            "alegacao": claim.get("text", ""),
            "alegacao_autor": claim.get("claimant", ""),
            "alegacao_data": claim.get("claimDate", ""),
            "agencia": editor.get("name", ""),
            "agencia_site": editor.get("site", ""),
            "data_da_checagem": review.get("reviewDate", ""),
            "veredito_original": veredito,
            "titulo_da_checagem": review.get("title", ""),
            "url": review.get("url", ""),
            # Derivação declarada. NÃO é rótulo de `verificacao-alegacao`.
            "veredito_chave_derivada": chave_canonica(veredito),
        })
    return linhas


def coletar(termos: tuple[str, ...]) -> dict:
    chave = sonda.carregar_chave()
    por_url: dict[str, dict] = {}
    por_termo: dict[str, int] = {}

    for termo in termos:
        claims = sonda.coletar_termo(chave, termo)
        novos = 0
        for claim in claims:
            for linha in extrair(claim):
                if linha["url"] and linha["url"] not in por_url:
                    por_url[linha["url"]] = linha
                    novos += 1
        por_termo[termo] = novos
        print(f"  {termo:16s} {novos:5d} checagens novas", flush=True)
        time.sleep(PAUSA_S)

    itens = list(por_url.values())
    anos = collections.Counter(
        (i["data_da_checagem"] or i["alegacao_data"] or "")[:4] for i in itens)
    anos.pop("", None)
    agencias = collections.Counter(i["agencia"] for i in itens)
    vereditos = collections.Counter(i["veredito_original"] for i in itens)

    return {
        "_licenca": ("metadado de ClaimReview, publicado pelas próprias agências "
                     "para indexação. Nenhum texto de artigo é reproduzido."),
        "data_de_corte": datetime.date.today().isoformat(),
        "gerado_em": datetime.datetime.now().isoformat(timespec="seconds"),
        "parametros_de_consulta": {
            "endpoint": sonda.ENDPOINT,
            "languageCode": "pt",
            "pageSize": sonda.POR_PAGINA,
            "paginas_maximas": sonda.PAGINAS_MAXIMAS,
            "termos": list(termos),
        },
        "campos_guardados": list(CAMPOS),
        "campo_nao_guardado": "texto do artigo de checagem — vedado por "
                              "`indice-checagens-recentes`",
        "checagens": len(itens),
        "por_termo": por_termo,
        "por_ano": dict(sorted(anos.items())),
        "agencias_alcancadas": dict(agencias.most_common()),
        "vereditos_originais": dict(vereditos.most_common(40)),
        "nota_sobre_veredito": (
            "`veredito_original` preserva a grafia publicada pela agência. "
            "`veredito_chave_derivada` é derivação nossa por dobra de caixa e "
            "acento, e MUST NOT ser confundida com os quatro rótulos de "
            "`verificacao-alegacao` — esse mapeamento é do mapa versionado de "
            "`normalizacao-rotulos` e não acontece aqui."),
        "itens": itens,
    }


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--termos", default=",".join(sonda.TERMOS_DE_PAUTA))
    args = analisador.parse_args()

    termos = tuple(t.strip() for t in args.termos.split(",") if t.strip())
    resultado = coletar(termos)
    SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")

    print(f"\nchecagens: {resultado['checagens']}")
    print(f"agências:  {len(resultado['agencias_alcancadas'])}")
    print(f"por ano:   {resultado['por_ano']}")
    print(f"gravado em {SAIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
