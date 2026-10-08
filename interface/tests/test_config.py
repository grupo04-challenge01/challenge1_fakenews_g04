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


CHAVE = "sk-teste-0123456789"


def test_padroes_seguros():
    assert carregar({"DONA_CHECA_MODO": "uso", "DEEPSEEK_API_KEY": CHAVE}) == Config(
        modo="uso", host="127.0.0.1", porta=8000, tempo_max=300, gerador="deepseek",
        chave=CHAVE, modelo_remoto="deepseek-v4-pro")


# add-gerador-api-deepseek, requirements Escolha do gerador e Chave da API.

def test_gerador_padrao_no_piloto_e_ollama_sem_chave():
    c = carregar({"DONA_CHECA_MODO": "piloto"})
    assert (c.gerador, c.chave) == ("ollama", None)


def test_gerador_explicito_vale_nos_dois_modos():
    assert carregar({"DONA_CHECA_MODO": "uso", "DONA_CHECA_GERADOR": "ollama"}).gerador == "ollama"
    c = carregar({"DONA_CHECA_MODO": "piloto", "DONA_CHECA_GERADOR": "deepseek",
                  "DEEPSEEK_API_KEY": CHAVE, "DEEPSEEK_MODELO": "deepseek-v4-pro"})
    assert (c.gerador, c.modelo_remoto) == ("deepseek", "deepseek-v4-pro")


@pytest.mark.parametrize("valor", ["gpt", "", "DeepSeek"])
def test_gerador_invalido_e_erro_que_nomeia_a_variavel_e_os_valores(valor):
    with pytest.raises(ErroConfig, match=r"DONA_CHECA_GERADOR.*deepseek.*ollama"):
        carregar({"DONA_CHECA_MODO": "uso", "DONA_CHECA_GERADOR": valor,
                  "DEEPSEEK_API_KEY": CHAVE})


@pytest.mark.parametrize("ambiente", [{}, {"DEEPSEEK_API_KEY": ""}, {"DEEPSEEK_API_KEY": "  "}])
def test_deepseek_sem_chave_e_erro_que_nomeia_a_variavel(ambiente):
    with pytest.raises(ErroConfig, match="DEEPSEEK_API_KEY"):
        carregar({"DONA_CHECA_MODO": "uso", **ambiente})


def test_chave_nunca_aparece_em_erro_nem_em_repr():
    with pytest.raises(ErroConfig) as erro:
        carregar({"DONA_CHECA_MODO": "uso", "DONA_CHECA_GERADOR": "gpt",
                  "DEEPSEEK_API_KEY": CHAVE})
    assert CHAVE not in str(erro.value)
    c = carregar({"DONA_CHECA_MODO": "uso", "DEEPSEEK_API_KEY": CHAVE})
    assert CHAVE not in repr(c) and CHAVE not in str(c)


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
        carregar({"DONA_CHECA_MODO": "uso", "DEEPSEEK_API_KEY": CHAVE, variavel: valor})


# Task 5.4: alternativa local para quem recusa o termo (D8).

def test_alternativa_local_desligada_por_padrao_e_ligada_com_sim():
    base = {"DONA_CHECA_MODO": "uso", "DEEPSEEK_API_KEY": CHAVE}
    assert carregar(base).alternativa_local is False
    assert carregar({**base, "DONA_CHECA_ALTERNATIVA_LOCAL": "sim"}).alternativa_local is True
    assert carregar({**base, "DONA_CHECA_ALTERNATIVA_LOCAL": "nao"}).alternativa_local is False


def test_alternativa_local_invalida_e_erro_que_nomeia_a_variavel():
    with pytest.raises(ErroConfig, match=r"DONA_CHECA_ALTERNATIVA_LOCAL.*sim.*nao"):
        carregar({"DONA_CHECA_MODO": "uso", "DEEPSEEK_API_KEY": CHAVE,
                  "DONA_CHECA_ALTERNATIVA_LOCAL": "talvez"})
