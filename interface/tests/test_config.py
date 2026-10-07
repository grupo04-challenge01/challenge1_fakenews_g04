"""Task 1.2 de add-interface-chat-web: configuração só por ambiente.

Requirement Modo de execução obrigatório, de `interface-chat-web`, e decisão 2
do design: `DONA_CHECA_MODO` sem padrão, as demais com padrão seguro.
"""
import pytest

from interface.config import Config, ErroConfig, carregar


def test_modo_ausente_e_erro_que_nomeia_a_variavel_e_os_valores():
    with pytest.raises(ErroConfig, match=r"DONA_CHECA_MODO.*uso.*piloto"):
        carregar({})


@pytest.mark.parametrize("valor", ["", "Piloto", "teste", "uso "])
def test_modo_fora_dos_valores_aceitos_e_erro(valor):
    with pytest.raises(ErroConfig, match="DONA_CHECA_MODO"):
        carregar({"DONA_CHECA_MODO": valor})


def test_padroes_seguros():
    assert carregar({"DONA_CHECA_MODO": "uso"}) == Config(
        modo="uso", host="127.0.0.1", porta=8000, tempo_max=180)


def test_piloto_e_valores_explicitos():
    c = carregar({"DONA_CHECA_MODO": "piloto", "DONA_CHECA_HOST": "0.0.0.0",
                  "DONA_CHECA_PORTA": "8080", "DONA_CHECA_TEMPO_MAX": "60"})
    assert (c.modo, c.host, c.porta, c.tempo_max) == ("piloto", "0.0.0.0", 8080, 60)
    assert c.piloto


@pytest.mark.parametrize("variavel, valor", [
    ("DONA_CHECA_PORTA", "oito mil"), ("DONA_CHECA_PORTA", "0"),
    ("DONA_CHECA_TEMPO_MAX", "-1"), ("DONA_CHECA_TEMPO_MAX", "x")])
def test_numero_invalido_e_erro_que_nomeia_a_variavel(variavel, valor):
    with pytest.raises(ErroConfig, match=variavel):
        carregar({"DONA_CHECA_MODO": "uso", variavel: valor})
