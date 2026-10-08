"""Tasks 2.5 e 2.6 de add-interface-chat-web: rota de verificação.

Decisões 3, 5 e 10 do design: `POST /verificar` responde em streaming, uma
verificação por vez, com tempo máximo; mensagem que é só link não chama o fluxo.
"""
import json
import threading
import time

import pytest
from fastapi.testclient import TestClient

from interface import fluxo
from interface.app import criar_app
from interface.config import Config


def ler_eventos(resposta):
    return [json.loads(linha[len("data: "):]) for linha in resposta.text.splitlines()
            if linha.startswith("data: ")]


def _cliente(verificar, tempo_max=180, carregar_recuperador=object):
    app = criar_app(Config(modo="uso", tempo_max=tempo_max),
                    carregar_recuperador=carregar_recuperador, verificar=verificar)
    cliente = TestClient(app)
    cliente.__enter__()
    for _ in range(100):
        if carregar_recuperador is not object or cliente.get("/saude").status_code == 200:
            break
        time.sleep(0.01)
    return cliente


def _fixo(*eventos):
    def verificar(texto, emitir, *, recuperador, chat):
        for e in eventos:
            emitir(e)
    return verificar


def test_eventos_saem_em_streaming_na_ordem():
    eventos = [{"tipo": "fronteira", "desfecho": "segue", "texto": None},
               {"tipo": "andamento", "etapa": "extracao", "frase": "…"},
               {"tipo": "resposta", "forma": "com evidência", "texto": "t", "detalhe": [],
                "redirecionamentos": []}]
    c = _cliente(_fixo(*eventos))
    r = c.post("/verificar", json={"texto": "A casca do jatobá cura o câncer!"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    assert ler_eventos(r) == eventos


@pytest.mark.parametrize("corpo", [{}, {"texto": ""}, {"texto": "   "}])
def test_mensagem_vazia_e_recusada(corpo):
    assert _cliente(_fixo()).post("/verificar", json=corpo).status_code == 422


def test_texto_nao_vai_na_url():
    assert _cliente(_fixo()).get("/verificar", params={"texto": "x"}).status_code == 405


def test_passado_o_tempo_maximo_sai_erro():
    def lento(texto, emitir, *, recuperador, chat):
        time.sleep(3)
    inicio = time.perf_counter()
    r = _cliente(lento, tempo_max=1).post("/verificar", json={"texto": "x"})
    assert time.perf_counter() - inicio < 2.5
    assert ler_eventos(r)[-1] == {"tipo": "erro", "texto": fluxo.textos()["erro"]}


def test_uma_verificacao_por_vez():
    ativas, picos = [0], []
    trava = threading.Lock()

    def contando(texto, emitir, *, recuperador, chat):
        with trava:
            ativas[0] += 1
            picos.append(ativas[0])
        time.sleep(0.2)
        with trava:
            ativas[0] -= 1
        emitir({"tipo": "aviso", "chave": "x", "texto": "x"})

    c = _cliente(contando)
    fios = [threading.Thread(target=c.post, args=("/verificar",), kwargs={"json": {"texto": "x"}})
            for _ in range(3)]
    for f in fios:
        f.start()
    for f in fios:
        f.join()
    assert picos and max(picos) == 1


def test_recuperador_ainda_carregando_vira_erro():
    trava = threading.Event()

    def preso():
        trava.wait(5)
        return object()
    c = _cliente(_fixo(), carregar_recuperador=preso)
    r = c.post("/verificar", json={"texto": "x"})
    trava.set()
    assert ler_eventos(r) == [{"tipo": "erro", "texto": fluxo.textos()["erro"]}]


# ---- só link (task 2.6) --------------------------------------------------------------

@pytest.mark.parametrize("texto", ["https://exemplo.com.br/noticia",
                                   "  http://bit.ly/abc123 \n"])
def test_mensagem_so_com_link_pede_o_texto_sem_chamar_o_fluxo(texto):
    def explode(*a, **k):
        raise AssertionError("o fluxo não pode ser chamado")
    r = _cliente(explode).post("/verificar", json={"texto": texto})
    assert ler_eventos(r) == [{"tipo": "aviso", "chave": "so_link",
                               "texto": fluxo.textos()["so_link"]}]


def test_texto_com_link_junto_vai_ao_fluxo():
    chamado = []

    def registra(texto, emitir, *, recuperador, chat):
        chamado.append(texto)
    _cliente(registra).post("/verificar", json={"texto": "Vejam isso https://x.com cura tudo"})
    assert chamado == ["Vejam isso https://x.com cura tudo"]
