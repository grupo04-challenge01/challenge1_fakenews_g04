"""Contrato de leitura em streaming — task 9.5 de add-ampliacao-corpus-ptbr.

Estende `normalizacao-rotulos` para arquivo `.jsonl` que não cabe em memória:
o corpus de circulação tem 3,6 GB e 3.998.633 linhas. A leitura precisa ser por
linha, e a contagem obtida continua sendo conferida contra a declarada.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from tratamento import leitura


def test_le_jsonl_linha_a_linha_sem_carregar_o_arquivo(tmp_path: pathlib.Path):
    arquivo = tmp_path / "amostra.jsonl"
    arquivo.write_text(
        "\n".join(json.dumps({"i": i}) for i in range(1000)) + "\n",
        encoding="utf-8")

    total = sum(1 for _ in leitura.ler_jsonl(arquivo))

    assert total == 1000


def test_linha_ilegivel_interrompe_com_o_numero_da_linha(tmp_path: pathlib.Path):
    arquivo = tmp_path / "quebrado.jsonl"
    arquivo.write_text('{"i": 1}\nnao e json\n{"i": 3}\n', encoding="utf-8")

    with pytest.raises(leitura.ErroDeLeitura) as erro:
        list(leitura.ler_jsonl(arquivo))

    assert "linha 2" in str(erro.value)


def test_linha_em_branco_e_ignorada_sem_erro(tmp_path: pathlib.Path):
    arquivo = tmp_path / "com_branco.jsonl"
    arquivo.write_text('{"i": 1}\n\n{"i": 2}\n', encoding="utf-8")

    assert len(list(leitura.ler_jsonl(arquivo))) == 2


def test_contagem_divergente_da_declarada_interrompe(tmp_path: pathlib.Path):
    arquivo = tmp_path / "curto.jsonl"
    arquivo.write_text('{"i": 1}\n{"i": 2}\n', encoding="utf-8")

    with pytest.raises(leitura.ErroDeLeitura) as erro:
        list(leitura.ler_jsonl(arquivo, registros_declarados=3))

    assert "2" in str(erro.value) and "3" in str(erro.value)


def test_leitura_nao_acumula_registros_em_memoria(tmp_path: pathlib.Path):
    """O leitor é gerador: consumi-lo não deixa os registros vivos."""
    import types

    arquivo = tmp_path / "amostra.jsonl"
    arquivo.write_text('{"i": 1}\n{"i": 2}\n', encoding="utf-8")

    fluxo = leitura.ler_jsonl(arquivo)

    assert isinstance(fluxo, types.GeneratorType)
