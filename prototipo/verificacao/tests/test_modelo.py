"""Tasks 2.1 a 2.3 de add-gerador-api-deepseek: gerador remoto sem rede.

A API entra simulada com `httpx.MockTransport`. Requirements "Chamada à API com
saída JSON e sem raciocínio" e "Uma nova tentativa em falha passageira", de
`gerador-modelo`; decisões D1, D4 e D5 do design.
"""
import json
import logging

import httpx
import pytest

from prototipo.verificacao import modelo
from prototipo.verificacao.modelo import ChatDeepSeek, ErroGerador

CHAVE = "sk-teste-0123456789"
SISTEMA = "Responda em JSON."
USUARIO = "A vacina tem chip?"


def _resposta(content, model="deepseek-v4.1-flash", usage=None):
    corpo = {"model": model, "choices": [{"message": {"role": "assistant", "content": content}}]}
    if usage is not None:
        corpo["usage"] = usage
    return httpx.Response(200, json=corpo)


def _gerador(respostas, pedidos=None, **kwargs):
    fila = list(respostas)

    def responder(pedido):
        if pedidos is not None:
            pedidos.append(pedido)
        return fila.pop(0)

    cliente = httpx.Client(transport=httpx.MockTransport(responder))
    return ChatDeepSeek(chave=CHAVE, cliente=cliente, **kwargs)


@pytest.fixture(autouse=True)
def sem_espera(monkeypatch):
    monkeypatch.setattr(modelo, "ESPERA", 0)


def test_pedido_montado_conforme_d1():
    pedidos = []
    _gerador([_resposta('{"ok": true}')], pedidos)(SISTEMA, USUARIO)
    (pedido,) = pedidos
    corpo = json.loads(pedido.content)
    assert pedido.method == "POST"
    assert str(pedido.url) == "https://api.deepseek.com/chat/completions"
    assert pedido.headers["Authorization"] == f"Bearer {CHAVE}"
    assert corpo["model"] == "deepseek-v4-pro"
    assert corpo["response_format"] == {"type": "json_object"}
    assert corpo["thinking"] == {"type": "disabled"}
    assert (corpo["temperature"], corpo["max_tokens"]) == (0.2, 1200)
    assert corpo["messages"] == [{"role": "system", "content": SISTEMA},
                                 {"role": "user", "content": USUARIO}]


def test_devolve_content_e_guarda_modelo_servido():
    chat = _gerador([_resposta('{"ok": true}', model="deepseek-v4.1-flash")])
    assert chat(SISTEMA, USUARIO) == '{"ok": true}'
    assert chat.modelo_servido == "deepseek-v4.1-flash"


def test_modelo_configuravel():
    pedidos = []
    _gerador([_resposta("{}")], pedidos, modelo="deepseek-v4-pro")(SISTEMA, USUARIO)
    assert json.loads(pedidos[0].content)["model"] == "deepseek-v4-pro"


def test_chave_do_ambiente_quando_nao_passada(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", CHAVE)
    assert ChatDeepSeek().chave == CHAVE


def test_sem_chave_e_erro(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(ErroGerador, match="DEEPSEEK_API_KEY"):
        ChatDeepSeek()


@pytest.mark.parametrize("primeira", [
    _resposta(""), _resposta(None), httpx.Response(503), httpx.Response(429),
    httpx.Response(500), httpx.Response(502)])
def test_falha_passageira_tem_uma_nova_tentativa(primeira):
    pedidos = []
    chat = _gerador([primeira, _resposta('{"ok": true}')], pedidos)
    assert chat(SISTEMA, USUARIO) == '{"ok": true}'
    assert len(pedidos) == 2


@pytest.mark.parametrize("respostas", [
    [httpx.Response(503), httpx.Response(503)],
    [_resposta(""), _resposta("")]])
def test_falha_repetida_levanta_depois_de_duas_tentativas(respostas):
    pedidos = []
    with pytest.raises(ErroGerador):
        _gerador(respostas, pedidos)(SISTEMA, USUARIO)
    assert len(pedidos) == 2


@pytest.mark.parametrize("status", [400, 401, 402])
def test_erro_definitivo_nao_tenta_de_novo(status):
    pedidos = []
    with pytest.raises(ErroGerador, match=str(status)):
        _gerador([httpx.Response(status)], pedidos)(SISTEMA, USUARIO)
    assert len(pedidos) == 1


def test_tempo_limite_levanta_sem_nova_tentativa():
    chamadas = []

    def estourar(pedido):
        chamadas.append(pedido)
        raise httpx.ReadTimeout("tempo", request=pedido)

    chat = ChatDeepSeek(chave=CHAVE, cliente=httpx.Client(transport=httpx.MockTransport(estourar)))
    with pytest.raises(ErroGerador, match="ReadTimeout"):
        chat(SISTEMA, USUARIO)
    assert len(chamadas) == 1


def test_falha_loga_status_sem_chave_nem_texto(caplog):
    caplog.set_level(logging.DEBUG)
    with pytest.raises(ErroGerador) as erro:
        _gerador([httpx.Response(401, json={"error": {"message": "Authentication Fails"}})])(
            SISTEMA, USUARIO)
    tudo = caplog.text + str(erro.value) + repr(erro.value)
    assert "401" in caplog.text
    for segredo in (CHAVE, USUARIO, SISTEMA):
        assert segredo not in tudo


def test_repr_nao_mostra_chave():
    chat = _gerador([])
    assert CHAVE not in repr(chat) and CHAVE not in str(chat)


def _usage(entrada, saida, cache):
    return {"prompt_tokens": entrada, "completion_tokens": saida,
            "total_tokens": entrada + saida, "prompt_cache_hit_tokens": cache,
            "prompt_cache_miss_tokens": entrada - cache}


def test_soma_tokens_informados_pela_api_inclusive_da_tentativa_falha():
    chat = _gerador([_resposta("", usage=_usage(100, 0, 0)),
                     _resposta("{}", usage=_usage(100, 20, 64)),
                     _resposta("{}", usage=_usage(50, 10, 0))])
    chat(SISTEMA, USUARIO)
    chat(SISTEMA, USUARIO)
    assert chat.uso == {"chamadas": 3, "entrada": 250, "entrada_cache": 64, "saida": 30}


def test_resposta_sem_usage_conta_a_chamada_sem_tokens():
    chat = _gerador([_resposta("{}")])
    chat(SISTEMA, USUARIO)
    assert chat.uso == {"chamadas": 1, "entrada": 0, "entrada_cache": 0, "saida": 0}


def test_saida_cortada_por_limite_vai_ao_log_sem_texto(caplog):
    caplog.set_level(logging.WARNING)
    resposta = httpx.Response(200, json={"model": "m", "choices": [
        {"finish_reason": "length", "message": {"content": '{"alegacoes": [{"tex'}}]})
    assert _gerador([resposta])(SISTEMA, USUARIO) == '{"alegacoes": [{"tex'
    assert "limite de tokens" in caplog.text
    assert "alegacoes" not in caplog.text and USUARIO not in caplog.text
