"""Tasks 5.3 e 5.4 de add-gerador-api-deepseek: consentimento e minimização na rota.

Requirement Consentimento antes do envio ao serviço externo, de
`interface-chat-web`, e Minimização antes do envio, de `gerador-modelo`.
Decisões D8 e D9: o servidor confere a versão do termo antes de chamar o
gerador; a página não é a única barreira.
"""
import json
import logging
import re
import time

from fastapi.testclient import TestClient

from interface.app import RECUSADO, TERMO_VERSAO, criar_app
from interface.config import Config
from interface.fluxo import textos

REMOTO = Config(modo="uso", gerador="deepseek", chave="sk-teste")
FIM = {"tipo": "resposta", "forma": "com evidência", "texto": "t", "detalhe": [],
       "redirecionamentos": []}
MENSAGEM = "Me liga no (11) 98765-4321, chá de boldo cura hepatite"


def _remoto(sistema, usuario):
    raise AssertionError("não chamado nos testes da rota")


def _local(sistema, usuario):
    raise AssertionError("não chamado nos testes da rota")


def _cliente(config=REMOTO):
    chamadas = []

    def verificar(texto, emitir, *, recuperador, chat):
        chamadas.append((texto, chat))
        emitir(FIM)

    c = TestClient(criar_app(config, carregar_recuperador=object, chat=_remoto,
                             chat_local=_local, verificar=verificar))
    c.__enter__()
    for _ in range(100):
        if c.get("/saude").status_code == 200:
            break
        time.sleep(0.01)
    return c, chamadas


def test_sem_consentimento_e_403_e_nada_e_chamado():
    c, chamadas = _cliente()
    for corpo in ({"texto": MENSAGEM}, {"texto": MENSAGEM, "consentimento": "0"},
                  {"texto": MENSAGEM, "consentimento": RECUSADO}):
        assert c.post("/verificar", json=corpo).status_code == 403
    assert chamadas == []


def test_aceite_usa_o_gerador_remoto_com_o_texto_minimizado(caplog):
    caplog.set_level(logging.INFO, logger="dona_checa")
    c, chamadas = _cliente()
    r = c.post("/verificar", json={"texto": MENSAGEM, "consentimento": TERMO_VERSAO})
    assert r.status_code == 200
    assert chamadas == [("Me liga no [telefone], chá de boldo cura hepatite", _remoto)]
    assert f"consentimento versão {TERMO_VERSAO}" in caplog.text
    assert "boldo" not in caplog.text and "98765" not in caplog.text


def test_recusa_com_alternativa_usa_o_gerador_local_sem_minimizar():
    c, chamadas = _cliente(Config(modo="uso", gerador="deepseek", chave="sk-teste",
                                  alternativa_local=True))
    r = c.post("/verificar", json={"texto": MENSAGEM, "consentimento": RECUSADO})
    assert r.status_code == 200
    assert chamadas == [(MENSAGEM, _local)]


def test_gerador_local_ignora_o_consentimento():
    c, chamadas = _cliente(Config(modo="uso", gerador="ollama"))
    assert c.post("/verificar", json={"texto": MENSAGEM}).status_code == 200
    assert chamadas == [(MENSAGEM, _remoto)]


def _termo_da_pagina(config):
    with TestClient(criar_app(config, carregar_recuperador=object)) as c:
        html = c.get("/").text
    bruto = re.search(r'<script type="application/json" id="config">(.*?)</script>', html, re.S)
    return json.loads(bruto[1])["termo"]


def _junto(t):
    return " ".join(t.split())


def test_pagina_recebe_o_termo_so_com_gerador_remoto():
    t = textos()
    assert _termo_da_pagina(REMOTO) == {
        "versao": TERMO_VERSAO, "texto": _junto(t["termo-servico-externo"]),
        "recusa": _junto(t["recusa"]), "alternativa": False}
    assert _termo_da_pagina(Config(modo="uso", gerador="ollama")) is None


def test_com_alternativa_a_recusa_e_o_texto_local():
    termo = _termo_da_pagina(Config(modo="uso", gerador="deepseek", chave="sk-teste",
                                    alternativa_local=True))
    assert termo["alternativa"] is True
    assert termo["recusa"] == _junto(textos()["recusa-local"])
