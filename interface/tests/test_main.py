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
