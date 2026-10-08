"""Requirement Modo de execução obrigatório: o processo não sobe sem o modo."""
import os
import subprocess
import sys


def _rodar(ambiente):
    env = {k: v for k, v in os.environ.items() if not k.startswith("DONA_CHECA_")}
    env.update(ambiente, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-m", "interface"], env=env, capture_output=True,
                          text=True, encoding="utf-8", timeout=60)


def test_sem_modo_o_processo_termina_com_erro_que_nomeia_a_variavel():
    r = _rodar({})
    assert r.returncode != 0
    assert "DONA_CHECA_MODO" in r.stderr and "uso" in r.stderr and "piloto" in r.stderr


def test_modo_invalido_tambem_termina():
    r = _rodar({"DONA_CHECA_MODO": "demo"})
    assert r.returncode != 0
    assert "DONA_CHECA_MODO" in r.stderr


# add-gerador-api-deepseek, task 3.1: o gerador sai da configuração.

from interface.__main__ import escolher_chat  # noqa: E402
from interface.config import Config  # noqa: E402
from prototipo.verificacao.modelo import ChatDeepSeek, chat_ollama  # noqa: E402


def test_gerador_ollama_usa_chat_ollama():
    assert escolher_chat(Config(modo="piloto", gerador="ollama")) is chat_ollama


def test_gerador_deepseek_usa_chave_e_modelo_da_configuracao():
    chat = escolher_chat(Config(modo="uso", gerador="deepseek", chave="sk-teste",
                                modelo_remoto="deepseek-v4-pro"))
    assert isinstance(chat, ChatDeepSeek)
    assert (chat.chave, chat.modelo) == ("sk-teste", "deepseek-v4-pro")


def test_deepseek_sem_chave_o_processo_termina_com_erro_que_nomeia_a_variavel():
    r = _rodar({"DONA_CHECA_MODO": "uso", "DEEPSEEK_API_KEY": ""})
    assert r.returncode != 0
    assert "DEEPSEEK_API_KEY" in r.stderr


# Task 5.6: o termo não vai ao ar com o marcador do contato (D8).

from interface.__main__ import pendencias_do_termo  # noqa: E402


def test_marcador_no_termo_e_pendencia_so_com_gerador_remoto():
    com = {"termo-servico-externo": "Fale com CONTATO_DO_GRUPO."}
    sem = {"termo-servico-externo": "Fale com grupo04@exemplo.org."}
    remoto = Config(modo="uso", gerador="deepseek", chave="sk-teste")
    assert pendencias_do_termo(remoto, com) == ["CONTATO_DO_GRUPO"]
    assert pendencias_do_termo(remoto, sem) == []
    assert pendencias_do_termo(Config(modo="uso", gerador="ollama"), com) == []


def test_servidor_nao_sobe_com_deepseek_e_marcador_no_termo():
    from interface.fluxo import textos
    if "CONTATO_DO_GRUPO" not in textos()["termo-servico-externo"]:
        return  # o grupo já preencheu o contato
    r = _rodar({"DONA_CHECA_MODO": "uso", "DEEPSEEK_API_KEY": "sk-teste"})
    assert r.returncode != 0
    assert "CONTATO_DO_GRUPO" in r.stderr
