"""Task 1.3 de add-interface-chat-web: aplicação, página e saúde.

Decisões 1 e 6 do design: a página é arquivo estático; o recuperador carrega
uma vez, em segundo plano, e `/saude` diz quando a carga terminou.
"""
import threading

from fastapi.testclient import TestClient

from interface.app import criar_app
from interface.config import Config

USO = Config(modo="uso")


def _carga_presa():
    liberar, carregou = threading.Event(), threading.Event()

    def carregar():
        liberar.wait(5)
        carregou.set()
        return object()
    return carregar, liberar, carregou


def test_pagina_e_html():
    with TestClient(criar_app(USO, carregar_recuperador=object)) as c:
        r = c.get("/")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert "Dona Checa" in r.text


def test_saude_e_503_ate_o_recuperador_carregar_e_200_depois():
    carregar, liberar, carregou = _carga_presa()
    with TestClient(criar_app(USO, carregar_recuperador=carregar)) as c:
        assert c.get("/saude").status_code == 503
        liberar.set()
        carregou.wait(5)
        for _ in range(50):
            if c.get("/saude").status_code == 200:
                break
            threading.Event().wait(0.02)
        assert c.get("/saude").status_code == 200


# ---- textos e modo injetados na página (tasks 4.1 e 4.2) -----------------------------

import json  # noqa: E402
import re  # noqa: E402

from prototipo.identidade import textos as textos_persona  # noqa: E402


def _config_da_pagina(modo):
    with TestClient(criar_app(Config(modo=modo), carregar_recuperador=object)) as c:
        html = c.get("/").text
    bruto = re.search(r'<script type="application/json" id="config">(.*?)</script>', html, re.S)
    return json.loads(bruto[1]), html


def test_pagina_traz_textos_da_persona_e_da_interface():
    config, _ = _config_da_pagina("uso")
    persona = textos_persona()
    assert config["modo"] == "uso"
    assert config["textos"]["abertura"] == persona["abertura"]
    assert config["textos"]["chamada"] == persona["chamada"]
    assert config["textos"]["lendo"] == "Dona Checa está lendo…"
    assert config["pergunta"] == {"pergunta": persona["pergunta_confianca"],
                                  "opcoes": ["1 a 3", "4 a 6", "7 a 10"]}


def test_modo_piloto_injeta_pergunta_nula_e_marca_o_rodape():
    config, html = _config_da_pagina("piloto")
    assert config["modo"] == "piloto"
    assert config["pergunta"] is None
    assert "modo piloto" in html


def test_modo_uso_nao_marca_o_rodape():
    assert "modo piloto" not in _config_da_pagina("uso")[1]


def test_url_nao_muda_o_modo():
    with TestClient(criar_app(Config(modo="piloto"), carregar_recuperador=object)) as c:
        html = c.get("/", params={"modo": "uso", "DONA_CHECA_MODO": "uso"}).text
    assert '"pergunta": null' in html


# ---- aviso de serviço externo (add-gerador-api-deepseek, task 3.2) -------------------

from interface.fluxo import textos as textos_interface  # noqa: E402


def _html(config):
    with TestClient(criar_app(config, carregar_recuperador=object)) as c:
        return c.get("/").text


def _aviso():
    return " ".join(textos_interface()["servico-externo"].split())


def test_gerador_remoto_mostra_o_aviso_no_rodape():
    html = _html(Config(modo="uso", gerador="deepseek", chave="sk-teste"))
    rodape = re.search(r"<footer[^>]*>(.*?)</footer>", html, re.S)[1]
    assert _aviso() in " ".join(rodape.split())
    assert "modo piloto" not in rodape


def test_gerador_local_nao_mostra_o_aviso():
    assert "fora do Brasil" not in _html(Config(modo="uso", gerador="ollama"))


def test_piloto_com_gerador_remoto_tem_um_rodape_so_com_os_dois_textos():
    html = _html(Config(modo="piloto", gerador="deepseek", chave="sk-teste"))
    assert html.count("<footer") == 1
    assert "modo piloto" in html and _aviso() in " ".join(html.split())


def test_chave_nunca_vai_para_a_pagina():
    assert "sk-teste-0123" not in _html(Config(modo="uso", gerador="deepseek",
                                               chave="sk-teste-0123"))
