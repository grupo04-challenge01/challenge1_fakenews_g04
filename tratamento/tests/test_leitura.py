"""Testes do contrato de leitura — change add-tratamento-datasets-ptbr, bloco 1.

Capability `normalizacao-rotulos`, requirement "Contrato de leitura do corpus":
a contagem obtida SHALL ser conferida contra a declarada, e divergência MUST ser
tratada como erro de leitura, nunca corrigida por normalização posterior.
"""
from __future__ import annotations

import pathlib

import pytest

from tratamento import leitura


def test_le_o_corpus_com_a_contagem_declarada():
    df = leitura.ler_derivado("factcenter_subset_saude.csv")
    assert len(df) == 4063


def test_preserva_newline_interno_em_text_news():
    df = leitura.ler_derivado("factcenter_subset_saude.csv")
    assert (df["text_news"].str.contains("\n")).sum() > 0


def test_todo_derivado_do_catalogo_bate_com_a_contagem_declarada():
    divergentes = {}
    for nome, formato in leitura.CATALOGO.items():
        df = leitura.ler_derivado(nome)
        if len(df) != formato.registros_declarados:
            divergentes[nome] = (len(df), formato.registros_declarados)
    assert divergentes == {}


def test_contagem_divergente_interrompe_a_leitura(tmp_path: pathlib.Path):
    origem = leitura.caminho("factckbr_normalizado.csv")
    linhas = origem.read_text(encoding="utf-8").splitlines(keepends=True)
    mutilado = tmp_path / "factckbr_normalizado.csv"
    mutilado.write_text("".join(linhas[:-1]), encoding="utf-8")

    with pytest.raises(leitura.ErroDeLeitura) as erro:
        leitura.ler_derivado("factckbr_normalizado.csv", caminho=mutilado)

    assert "1312" in str(erro.value) and "1313" in str(erro.value)


def test_corpus_lido_com_delimitador_default_e_rejeitado():
    with pytest.raises(leitura.ErroDeLeitura):
        leitura.ler_derivado("factcenter_subset_saude.csv", sep=",")
