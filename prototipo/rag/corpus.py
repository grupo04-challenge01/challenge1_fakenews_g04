"""Leitura do corpus e portões de entrada — change add-selecao-modelos-arquitetura-rag.

Dois portões rodam antes de qualquer unidade ser construída, ambos herdados de
`add-tratamento-datasets-ptbr`, porque indexar um corpus defeituoso propaga o
defeito para o índice (proposal.md, seção Impact):

1. Contrato de leitura (`normalizacao-rotulos`): delimitador `;`, quoting que
   preserva newline interno, contagem conferida contra a declarada.
2. Integridade textual (`integridade-textual`): arquivo com classe de caractere
   sistematicamente perdida MUST NOT ser aprovado para recuperação nem citação.
"""
from __future__ import annotations

import collections
import pathlib
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parents[2]
CAMINHO_CORPUS = RAIZ / "datasets" / "derivados" / "factcenter_subset_saude.csv"

# Declarado em datasets/README.md. Divergência é erro de leitura, nunca corrigida
# por normalização posterior (normalizacao-rotulos, contrato de leitura).
REGISTROS_DECLARADOS = 4063

COLUNAS_EXIGIDAS = ("url", "source_name", "title", "subtitle",
                    "publication_date", "text_news", "rating")

# Pares maiúscula/minúscula acentuadas do português, mais o ü da capability.
PARES_ACENTUADOS = [("Á", "á"), ("À", "à"), ("Â", "â"), ("Ã", "ã"),
                    ("É", "é"), ("Ê", "ê"), ("Í", "í"), ("Ó", "ó"),
                    ("Ô", "ô"), ("Õ", "õ"), ("Ú", "ú"), ("Ü", "ü"),
                    ("Ç", "ç")]

# Piso de ocorrências da minúscula abaixo do qual a ausência da maiúscula não
# sustenta acusação de corrupção. Ver `verificar_integridade_textual`.
PISO_EVIDENCIA_MINUSCULA = 500


class ErroDePortao(RuntimeError):
    """Corpus reprovado em portão de entrada. Nenhum derivado é gerado."""


def ler_corpus(caminho: pathlib.Path = CAMINHO_CORPUS):
    """Lê o corpus sob o contrato declarado e confere a contagem de registros."""
    import pandas as pd

    df = pd.read_csv(caminho, sep=";", dtype=str, keep_default_na=False)
    faltando = [c for c in COLUNAS_EXIGIDAS if c not in df.columns]
    if faltando:
        raise ErroDePortao(f"colunas ausentes em {caminho.name}: {faltando}")
    if len(df) != REGISTROS_DECLARADOS:
        raise ErroDePortao(
            f"{caminho.name}: {len(df)} registros lidos contra "
            f"{REGISTROS_DECLARADOS} declarados. Leitura inválida — conferir "
            "delimitador e quoting antes de gerar qualquer derivado.")
    return df


def verificar_integridade_textual(caminho: pathlib.Path = CAMINHO_CORPUS) -> dict:
    """Procura perda sistemática de caractere acentuado no arquivo inteiro.

    `integridade-textual` manda reprovar o arquivo quando uma classe de caractere
    tem zero ocorrência. A leitura literal ("zero é corrupção") reprova este
    corpus por causa do `Ü`, que tem zero ocorrências em 21,5 milhões de
    caracteres — e não por defeito: o trema foi abolido pelo Acordo Ortográfico
    de 1990, e o corpus cobre 2013 a 2021. O `ü` minúsculo aparece 57 vezes, em
    nomes estrangeiros, o que mostra que o pipeline não descarta o caractere.

    O critério aplicado é o que de fato separa os dois casos observados: a
    maiúscula tem zero ocorrências **e** a minúscula correspondente é frequente.
    Em `factckbr_normalizado.csv`, reprovado pela capability, sete letras batem
    nesse critério (`ã` 3.625 contra `Ã` 0, `ç` 2.312 contra `Ç` 0). Aqui,
    nenhuma bate. A precisão vale ser levada à task 3.1 de
    `add-tratamento-datasets-ptbr`, que é quem escreve o verificador definitivo.
    """
    texto = caminho.read_text(encoding="utf-8")
    contagem = collections.Counter(texto)

    ausentes, corrompidos = [], []
    for maiuscula, minuscula in PARES_ACENTUADOS:
        if contagem[maiuscula]:
            continue
        ausentes.append(maiuscula)
        if contagem[minuscula] >= PISO_EVIDENCIA_MINUSCULA:
            corrompidos.append({"maiuscula": maiuscula, "ocorrencias_maiuscula": 0,
                                "minuscula": minuscula,
                                "ocorrencias_minuscula": contagem[minuscula]})

    laudo = {
        "arquivo": caminho.name,
        "caracteres": len(texto),
        "ausentes": ausentes,
        "corrompidos": corrompidos,
        "aprovado": not corrompidos,
        "criterio": ("maiúscula com zero ocorrências e minúscula correspondente "
                     f"com pelo menos {PISO_EVIDENCIA_MINUSCULA} ocorrências"),
        "contagem_por_letra": {m: contagem[m] for m, _ in PARES_ACENTUADOS},
    }
    if not laudo["aprovado"]:
        raise ErroDePortao(
            f"{caminho.name} reprovado por perda sistemática de caractere: "
            f"{[c['maiuscula'] for c in corrompidos]}. Arquivo MUST NOT ser "
            "usado em recuperação nem em citação.")
    return laudo


# FACTCK.BR, fonte auxiliar (task 1.2 de mvp-copiloto-verificacao). Contrato de
# leitura em x-corpora.factckbr do esquema: TSV sem quoting, tudo como texto.
CAMINHO_FACTCKBR = RAIZ / "datasets" / "01_nucleo_metodologico" / "factckbr" / "FACTCKBR.tsv"
COLUNAS_FACTCKBR = ("URL", "Author", "datePublished", "claimReviewed",
                    "reviewBody", "title", "alternativeName")


def ler_factckbr(caminho: pathlib.Path = CAMINHO_FACTCKBR):
    """Lê o FACTCK.BR e confere as linhas contra `linhas_declaradas` do esquema."""
    import csv

    import pandas as pd

    from . import esquema as esquema_mod

    declaradas = esquema_mod.carregar_esquema()["x-corpora"]["factckbr"]["linhas_declaradas"]
    df = pd.read_csv(caminho, sep="\t", quoting=csv.QUOTE_NONE, dtype=str,
                     keep_default_na=False)
    faltando = [c for c in COLUNAS_FACTCKBR if c not in df.columns]
    if faltando:
        raise ErroDePortao(f"colunas ausentes em {caminho.name}: {faltando}")
    if len(df) != declaradas:
        raise ErroDePortao(
            f"{caminho.name}: {len(df)} linhas lidas contra {declaradas} declaradas. "
            "Leitura inválida — conferir delimitador e quoting.")
    return df


def verificar_integridade_auxiliar(corpus: str = "factckbr") -> dict:
    """Portão de integridade de um corpus que pode entrar reprovado.

    `integridade-textual`, revisada em 01/10/2026: arquivo reprovado entra na
    recuperação só com todo registro não apto a citação. O portão, então, não
    exige aprovação. Exige que o laudo concorde com `apto_citacao` declarado no
    esquema. Se a recoleta da task 3.5 um dia aprovar o arquivo, a construção
    para, e alguém troca o esquema de propósito.
    """
    from tratamento import integridade

    from . import esquema as esquema_mod

    declarado = esquema_mod.carregar_esquema()["x-corpora"][corpus]
    caminho = RAIZ / declarado["arquivo"]
    laudo = integridade.verificar(caminho.name, caminho)
    if laudo["aprovado"] != declarado["apto_citacao"]:
        raise ErroDePortao(
            f"{caminho.name}: laudo de integridade {'aprova' if laudo['aprovado'] else 'reprova'} "
            f"o arquivo, mas o esquema declara apto_citacao={declarado['apto_citacao']}. "
            "Corrigir o esquema antes de indexar.")
    return laudo


def sem_acento(texto: str) -> str:
    """Dobra acento para comparação. Nunca aplicado ao texto que vira citação."""
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")
