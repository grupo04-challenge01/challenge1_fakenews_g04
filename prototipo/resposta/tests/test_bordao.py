"""Tasks 2.1 e 2.2 de add-identidade-dona-checa: bordão na abertura da resposta.

Requirement Estrutura de quatro blocos, de `resposta-formativa`, na redação de
add-identidade-dona-checa: toda resposta abre com o bordão fixo, posto pelo
código, e o bordão conta no teto de palavras da camada visível.
"""
import pytest

from prototipo.resposta import estrutura
from prototipo.resposta.estrutura import Resposta, responder
from prototipo.resposta.tests.test_estrutura import (
    ALEGACAO, BLOCOS_FALSO, BLOCOS_SEM, FALSO, MENSAGEM, SEM_TRECHO, VERDADEIRO, _chat, _com,
    _sem)

BORDAO = "Peraí, de onde veio isso? Vamos olhar juntos, meu bem."


@pytest.mark.parametrize("veredito, blocos, lacuna", [
    (FALSO, BLOCOS_FALSO, None),
    (VERDADEIRO, _com(bloco3="Parecia exagero."), None),
    (SEM_TRECHO, BLOCOS_SEM, None),
    (SEM_TRECHO, _sem(bloco4=""), {"corte": "2021"}),
], ids=["falso", "verdadeiro", "sem evidência", "lacuna"])
def test_toda_resposta_abre_com_o_bordao(veredito, blocos, lacuna):
    r = responder(MENSAGEM, ALEGACAO, veredito, lacuna=lacuna, chat=_chat(blocos))
    assert r.texto.startswith(f"{BORDAO}\n\n")


def test_bordao_sai_da_spec_e_nao_do_modelo():
    assert estrutura.BORDAO == BORDAO
    chat = _chat(BLOCOS_FALSO)
    responder(MENSAGEM, ALEGACAO, FALSO, chat=chat)
    assert "Peraí" not in chat.chamadas[0][0] + chat.chamadas[0][1]


def _blocos_com(palavras):
    """Quatro blocos que somam `palavras`, em frases de 10 palavras."""
    frases = ["um dois três quatro cinco seis sete oito nove dez."] * (palavras // 10)
    resto = palavras % 10
    if resto:
        frases.append(" ".join(["palavra"] * resto) + ".")
    return [" ".join(frases[i::4]) for i in range(4)]


def test_bordao_conta_no_teto_de_palavras():
    r = Resposta("sem evidência", [""] * 4, _blocos_com(111))
    assert any(d.startswith("camada visível com 121 palavras")
               for d in estrutura._defeitos_legibilidade(r))


def test_bordao_no_limite_do_teto_nao_e_defeito():
    r = Resposta("sem evidência", [""] * 4, _blocos_com(110))
    assert not [d for d in estrutura._defeitos_legibilidade(r) if d.startswith("camada visível")]
