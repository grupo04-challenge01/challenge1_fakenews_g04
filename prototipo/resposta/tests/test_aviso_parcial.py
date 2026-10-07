"""Task 5.6 de add-entrada-por-link: aviso de leitura parcial na resposta (D7).

Requirement Leitura completa e parcial, de `entrada-por-link`: na leitura
parcial, o aviso entra entre o bordão e o bloco 1, posto pelo código, e conta
no teto de palavras da camada visível.
"""
from prototipo.entrada.leitura import AVISO_PARCIAL
from prototipo.resposta import estrutura
from prototipo.resposta.estrutura import Resposta, responder
from prototipo.resposta.tests.test_bordao import _blocos_com
from prototipo.resposta.tests.test_estrutura import (
    ALEGACAO, BLOCOS_FALSO, FALSO, MENSAGEM, _chat)


def test_aviso_vem_da_spec():
    assert AVISO_PARCIAL == "Li só o título e o começo dessa notícia."


def test_aviso_entre_bordao_e_bloco_1():
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(BLOCOS_FALSO), aviso=AVISO_PARCIAL)
    assert r.texto.startswith(f"{estrutura.BORDAO}\n\n{AVISO_PARCIAL}\n\nVEREDITO:")


def test_sem_aviso_a_resposta_nao_muda():
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(BLOCOS_FALSO))
    assert r.texto.startswith(f"{estrutura.BORDAO}\n\nVEREDITO:")


def test_aviso_nao_vai_ao_modelo():
    chat = _chat(BLOCOS_FALSO)
    responder(MENSAGEM, ALEGACAO, FALSO, chat=chat, aviso=AVISO_PARCIAL)
    assert all(AVISO_PARCIAL not in s + u for s, u in chat.chamadas)


def test_aviso_conta_no_teto_de_palavras():
    # Bordão (10) + 102 dos blocos = 112; com o aviso de 9 palavras, 121.
    r = Resposta("sem evidência", [""] * 4, _blocos_com(102), aviso=AVISO_PARCIAL)
    assert any(d.startswith("camada visível com 121 palavras")
               for d in estrutura._defeitos_legibilidade(r))
