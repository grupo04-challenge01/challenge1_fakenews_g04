"""Testes da correção a montante — change add-tratamento-datasets-ptbr, tasks 3.4 e 4.5.

`integridade-textual`: a filtragem de caractere do script de atualização do
FACTCK.BR MUST aceitar as maiúsculas acentuadas do português e o `ü`, ou ser
substituída por normalização Unicode que não descarte caractere.

`frescor-corpus`: o script MUST ser reparado antes do uso, por depender de API
de biblioteca removida em versão maior (`DataFrame.append`, fora desde pandas 2.0).
"""
from __future__ import annotations

import importlib.util
import pathlib

import pandas as pd
import pytest

CAMINHO = (pathlib.Path(__file__).resolve().parents[2] / "datasets" /
           "01_nucleo_metodologico" / "factckbr" / "update_factckbr.py")


def carregar():
    spec = importlib.util.spec_from_file_location("update_factckbr", CAMINHO)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module")
def script():
    return carregar()


def test_maiuscula_acentuada_sobrevive_a_filtragem(script):
    assert script.re_char("Sistema Único de Saúde") == "Sistema Único de Saúde"


def test_todas_as_maiusculas_acentuadas_do_portugues_sobrevivem(script):
    letras = "ÁÀÂÃÉÊÍÓÔÕÚÜÇ"
    assert script.re_char(letras) == letras


def test_caractere_de_controle_e_descartado(script):
    assert script.re_char("texto\x00com\x07controle") == "textocomcontrole"


def test_quebra_de_linha_e_preservada(script):
    assert script.re_char("linha um\nlinha dois") == "linha um\nlinha dois"


def test_atualizacao_do_dataset_nao_usa_api_removida_do_pandas(script):
    antigo = pd.DataFrame({"a": [1]}, index=pd.Index(["u1"], name="URL"))
    novo = pd.DataFrame({"a": [2]}, index=pd.Index(["u2"], name="URL"))

    resultado = script.update_dataset(antigo, novo)

    assert list(resultado["a"]) == [1, 2]


def test_duplicata_e_removida_na_atualizacao(script):
    antigo = pd.DataFrame({"a": [1]}, index=pd.Index(["u1"], name="URL"))
    repetido = pd.DataFrame({"a": [1]}, index=pd.Index(["u1"], name="URL"))

    assert len(script.update_dataset(antigo, repetido)) == 1
