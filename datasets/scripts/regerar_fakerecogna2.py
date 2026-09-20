"""Regeração dos derivados da FakeRecogna a partir da 2.0 — bloco 4 do change.

Substitui a v1, que sai do repositório. Gera:

- `fakerecogna2_subset_saude_ciencia.csv` — o subset temático, por filtro
  declarado (task 4.2);
- `fakerecogna2_amostra_estimulos_300.csv` — amostra estratificada com semente
  versionada (task 4.3);
- `fakerecogna2_transformacao.json` — a declaração de transformação de texto por
  classe, com os itens transformados identificáveis por consulta (task 4.4).

**A transformação é assimétrica por classe, e isso é o achado que mais importa
nesta base.** A notícia real passou por sumarização extrativa na origem; a
falsa veio crua. Consequência medida: um classificador que olha **apenas o
número de caracteres** acerta 80,6% nesta base balanceada, contra 50% de linha
de base. Nenhuma acurácia medida sobre ela significa detecção de desinformação.

Uso:
    python datasets/scripts/regerar_fakerecogna2.py
"""
from __future__ import annotations

import json
import pathlib
import sys
import unicodedata

import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
FONTE = RAIZ / "datasets" / "03_banco_estimulos" / "fakerecogna2" / "fakerecogna_extrativo.csv"
SAIDA = RAIZ / "datasets" / "derivados"

# O critério de categoria da v1 NÃO é válido na 2.0. Medido em 19/09/2026:
# a classe real tem exatamente cinco categorias (`saude`, `politica`,
# `entretenimento`, `ciencia`, `brasil`), um vocabulário controlado; a classe
# falsa tem 69, das quais 64 não existem na classe real — entre elas 6.870
# itens com categoria **vazia**, nomes de editoria de agência (`nas redes`,
# `uol confere`, `falso`) e temas que a classe real nunca recebe (`pandemia`,
# `conspiracoes`, `tecnologia`). Filtrar por categoria selecionaria
# sistematicamente notícia real: o subset sai 14.434 reais contra 1.603 falsas,
# e perde todo item falso de saúde arquivado sob `pandemia` ou sob vazio.
#
# O critério adotado é **temático por termo sobre o texto**, aplicado igual às
# duas classes — o mesmo método que produziu `factcenter_subset_saude.csv`.
CATEGORIAS_ALVO = ("saude", "ciencia")

TERMOS_DE_SAUDE = (
    "vacina", "vacinacao", "imuniza", "covid", "coronavirus", "pandemia",
    "virus", "bacteria", "doenca", "sintoma", "contagio", "epidemia", "surto",
    "remedio", "medicamento", "farmaco", "dose", "bula", "anvisa", "sus",
    "ministerio da saude", "oms", "medico", "medica", "hospital", "enfermeir",
    "cancer", "diabetes", "hipertens", "alzheimer", "autismo", "hiv", "aids",
    "dengue", "zika", "chikungunya", "sarampo", "gripe", "h1n1", "influenza",
    "febre amarela", "meningite", "tuberculose", "hepatite", "hpv", "mpox",
    "qdenga", "oropouche", "semaglutida", "cloroquina", "ivermectina",
    "tratamento", "cura", "estudo clinico", "pesquisa medica", "saude",
    "cientista", "cientific",
)

SEMENTE = 42
ITENS_POR_CLASSE = 150       # 300 no total, como a amostra da v1

# Teto de caracteres observado na classe real, consequência da sumarização.
TETO_CLASSE_REAL = 1493


def chave(valor: str) -> str:
    sem = "".join(c for c in unicodedata.normalize("NFD", str(valor))
                  if unicodedata.category(c) != "Mn")
    return sem.strip().lower()


def carregar() -> pd.DataFrame:
    df = pd.read_csv(FONTE, dtype=str, keep_default_na=False)
    if len(df) != 52_800:
        raise SystemExit(f"{FONTE.name}: {len(df)} linhas contra 52.800 declaradas "
                         "pela fonte. Leitura rejeitada.")
    return df


def subset_tematico(df: pd.DataFrame) -> pd.DataFrame:
    """Filtro temático por termo sobre o texto, igual para as duas classes."""
    import re

    texto = (df["Titulo"] + " " + df["Subtitulo"] + " " + df["Noticia"]).map(chave)
    padrao = re.compile("|".join(re.escape(t) for t in TERMOS_DE_SAUDE))
    return df[texto.str.contains(padrao, regex=True)].copy()


def subset_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """Só para registro: o critério da v1, que não é válido aqui."""
    return df[df["Categoria"].map(chave).isin(CATEGORIAS_ALVO)].copy()


def amostra_estratificada(subset: pd.DataFrame) -> pd.DataFrame:
    partes = []
    for rotulo, grupo in subset.groupby("Label"):
        n = min(ITENS_POR_CLASSE, len(grupo))
        partes.append(grupo.sample(n=n, random_state=SEMENTE))
    return pd.concat(partes).sort_values(["Label", "URL"]).reset_index(drop=True)


def declaracao_de_transformacao(df: pd.DataFrame, subset: pd.DataFrame) -> dict:
    comp = df.assign(n=df["Noticia"].str.len())
    por_classe = {}
    for rotulo, nome in (("0", "real"), ("1", "falsa")):
        g = comp[comp["Label"] == rotulo]["n"]
        por_classe[nome] = {
            "label": rotulo,
            "itens": int(len(g)),
            "caracteres_mediana": int(g.median()),
            "caracteres_media": round(float(g.mean()), 1),
            "caracteres_maximo": int(g.max()),
        }

    # Acurácia de um classificador que olha só o comprimento.
    y = (comp["Label"] == "1").astype(int)
    melhor = max(((((comp["n"] < corte).astype(int) == y).mean()), corte)
                 for corte in range(100, 1400, 25))

    return {
        "base": "FakeRecogna 2.0, variante extrativa",
        "metodo_declarado_pelos_autores": (
            "sumarização de texto aplicada à notícia real, porque o texto "
            "genuíno é muito maior que o conteúdo falso produzido"),
        "variante": "extrativa — o resumo reusa sentenças do original, sem "
                    "reescrita generativa",
        "classe_transformada": "real (Label 0)",
        "classe_nao_transformada": "falsa (Label 1)",
        "consulta_que_identifica_os_itens_transformados": "Label == '0'",
        "por_classe": por_classe,
        "teto_da_classe_real": TETO_CLASSE_REAL,
        "itens_da_classe_falsa_acima_do_teto": int(
            (comp[(comp["Label"] == "1") & (comp["n"] > TETO_CLASSE_REAL)]).shape[0]),
        "vazamento_medido": {
            "acuracia_so_pelo_comprimento": round(float(melhor[0]), 4),
            "corte_em_caracteres": melhor[1],
            "linha_de_base": 0.5,
            "leitura": (
                "um classificador que não lê nenhuma palavra, só conta "
                "caracteres, acerta 80,6% nesta base balanceada. A separação "
                "entre as classes é em boa parte artefato da sumarização "
                "assimétrica, não sinal de desinformação. Nenhuma acurácia "
                "medida sobre esta base sustenta afirmação sobre detecção."),
        },
        "consequencia": (
            "a base entra como banco de estímulos com a transformação "
            "declarada, e MUST NOT aparecer em nenhuma lista de fonte de "
            "trecho citado — o texto da classe real não é o que a fonte "
            "publicou."),
        "subset_tematico": {
            "criterio": ("termo de saúde ou ciência no texto (título, subtítulo "
                         "e notícia), normalizado por caixa e acento, aplicado "
                         "igual às duas classes"),
            "termos": list(TERMOS_DE_SAUDE),
            "itens": int(len(subset)),
            "por_classe": {k: int(v) for k, v in
                           subset["Label"].value_counts().items()},
        },
        "criterio_de_categoria_descartado": {
            "motivo": ("`Categoria` não é vocabulário compartilhado entre as "
                       "classes: a real tem cinco valores, a falsa tem 69, das "
                       "quais 64 não existem na real, incluindo 6.870 itens de "
                       "categoria vazia e nomes de editoria de agência. O "
                       "filtro por categoria seleciona notícia real por "
                       "construção."),
            "resultado_se_aplicado": None,
        },
        "amostra": {"semente": SEMENTE, "itens_por_classe": ITENS_POR_CLASSE},
    }


def main() -> int:
    if not FONTE.exists():
        sys.exit(f"{FONTE} ausente — ver datasets/FONTES.md para reconstituir.")

    df = carregar()
    subset = subset_tematico(df)
    por_categoria = subset_por_categoria(df)
    amostra = amostra_estratificada(subset)
    declaracao = declaracao_de_transformacao(df, subset)
    declaracao["criterio_de_categoria_descartado"]["resultado_se_aplicado"] = {
        "itens": int(len(por_categoria)),
        "por_classe": {k: int(v) for k, v in
                       por_categoria["Label"].value_counts().items()},
    }

    subset.to_csv(SAIDA / "fakerecogna2_subset_saude_ciencia.csv",
                  index=False, encoding="utf-8")
    amostra.to_csv(SAIDA / "fakerecogna2_amostra_estimulos_300.csv",
                   index=False, encoding="utf-8")
    (SAIDA / "fakerecogna2_transformacao.json").write_text(
        json.dumps(declaracao, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    print(f"subset: {len(subset)} itens {declaracao['subset_tematico']['por_classe']}")
    print(f"amostra: {len(amostra)} itens, semente {SEMENTE}")
    print(f"vazamento por comprimento: "
          f"{declaracao['vazamento_medido']['acuracia_so_pelo_comprimento']:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
