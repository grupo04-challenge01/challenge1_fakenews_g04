"""Testes de frescor do corpus — change add-tratamento-datasets-ptbr, bloco 4.

Capability `frescor-corpus`: a cobertura SHALL ser declarada e versionada, e
MUST ser verificável por reexecução da busca. Lacuna de acervo MUST NOT ser
apresentada como `evidência insuficiente`.
"""
from __future__ import annotations

from tratamento import frescor, leitura


def test_declaracao_traz_a_janela_medida():
    d = frescor.declaracao_de_cobertura(leitura.ler_corpus())

    assert d["janela"]["inicio"][:4] == "2013"
    assert d["janela"]["fim"][:4] == "2021"


def test_declaracao_traz_a_concentracao_por_ano():
    d = frescor.declaracao_de_cobertura(leitura.ler_corpus())

    assert d["por_ano"]["2020"] == 2188
    assert d["concentracao_maxima"]["ano"] == "2020"
    assert round(d["concentracao_maxima"]["proporcao"], 2) == 0.54


def test_termos_de_pauta_ausentes_sao_verificados_por_busca():
    d = frescor.declaracao_de_cobertura(leitura.ler_corpus())

    for termo in ("qdenga", "mpox", "oropouche", "semaglutida"):
        assert d["termos_de_pauta"][termo] == 0
    assert d["termos_de_pauta"]["covid"] > 2000


def test_busca_de_termo_ignora_acento_e_caixa():
    assert frescor.contar_termo(["Vacina contra a DENGUE"], "dengue") == 1
    assert frescor.contar_termo(["oropouche e Oropouché"], "oropouche") == 1


def test_pauta_posterior_a_janela_recebe_lacuna_de_acervo():
    resposta = frescor.classificar_pauta("Qdenga causa a própria dengue",
                                         leitura.ler_corpus())

    assert resposta.tipo == "lacuna_de_acervo"
    assert resposta.tipo != "evidencia_insuficiente"
    assert "2021" in resposta.mensagem
    assert resposta.onde_procurar, "a resposta indica onde procurar checagem recente"


def test_pauta_coberta_pelo_acervo_nao_vira_lacuna():
    resposta = frescor.classificar_pauta("cloroquina cura covid",
                                         leitura.ler_corpus())

    assert resposta.tipo == "coberta"


def test_caminho_de_atualizacao_nomeia_alcancadas_e_nao_alcancadas():
    caminho = frescor.caminho_de_atualizacao()

    assert len(caminho["agencias_alcancadas"]) == 3
    assert len(caminho["agencias_nao_alcancadas"]) == 3
    assert set(caminho["agencias_alcancadas"]) & set(caminho["agencias_nao_alcancadas"]) == set()
    assert caminho["pre_requisito_de_reparo"]
