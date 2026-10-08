"""Task 6.1 de add-entrada-por-link: casos com link na bancada.

A página de cada caso vem de `prototipo/entrada/tests/paginas/`; a bancada
nunca acessa a rede, nem com modelo real.
"""
import pytest

from bancada.__main__ import buscar_do_caso, carregar_casos, rodar_caso
from bancada.avaliacao import avaliar
from bancada.tests.test_bancada import Recuperador, chat_fixo
from prototipo.entrada.rede import Recusa


def test_caso_com_pagina_le_o_arquivo_gravado():
    buscar = buscar_do_caso({"pagina": "blog_oglobo_completo"})
    pagina = buscar("https://oglobo.globo.com/qualquer")
    assert pagina.url_final.startswith("https://oglobo.globo.com/blogs/daniel-becker/")
    assert b"gravidez" in pagina.corpo


def test_pagina_sintetica_usa_a_url_pedida():
    pagina = buscar_do_caso({"pagina": "injecao_sintetica"})("https://saude.exemplo/jatoba")
    assert pagina.url_final == "https://saude.exemplo/jatoba"


@pytest.mark.parametrize("url", ["http://192.168.0.1/admin", "https://exemplo.com.br/x"])
def test_caso_sem_pagina_nunca_vai_a_rede(url):
    with pytest.raises(Recusa):
        buscar_do_caso({})(url)


def test_todo_caso_com_pagina_aponta_para_arquivo_existente():
    for caso in carregar_casos():
        if "pagina" in caso:
            assert buscar_do_caso(caso)("https://exemplo.com.br/x").corpo


def test_rodar_caso_usa_a_pagina_do_caso():
    caso = {"id": "L", "mensagem": "https://youtu.be/abc", "esperado": {"leitura": "video"}}
    r = rodar_caso(caso, chat_fixo(), Recuperador())
    assert r["passou"]
    assert r["rastro"]["resposta"] == {"forma": "leitura", "causa": "video"}


def _rastro_leitura(causa="nao_abriu"):
    return {"etapas": [{"etapa": "fronteira", "saida": {"categorias": []}},
                       {"etapa": "leitura", "saida": {"causa": causa}}],
            "origem": {"tipo": "pagina", "parcial": False},
            "resposta": {"forma": "leitura", "causa": causa}}


def test_resposta_de_leitura_nao_exige_defeitos():
    assert all(c["ok"] for c in avaliar({"esperado": {}}, _rastro_leitura()))


def test_esperado_leitura_compara_a_causa():
    checks = avaliar({"esperado": {"leitura": "video"}}, _rastro_leitura("nao_abriu"))
    assert [c for c in checks if c["check"] == "leitura"] == [
        {"etapa": "leitura", "check": "leitura", "esperado": "video", "obtido": "nao_abriu",
         "ok": False}]


@pytest.mark.parametrize("parcial, esperado", [(False, "completa"), (True, "parcial")])
def test_esperado_leitura_completa_ou_parcial(parcial, esperado):
    rastro = {"etapas": [], "origem": {"tipo": "pagina", "parcial": parcial},
              "resposta": None}
    checks = avaliar({"esperado": {"leitura": esperado}}, rastro)
    assert [c["ok"] for c in checks if c["check"] == "leitura"] == [True]
