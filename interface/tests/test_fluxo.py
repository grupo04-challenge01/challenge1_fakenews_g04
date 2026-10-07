"""Tasks 2.3 e 2.4 de add-interface-chat-web: eventos do fluxo e desfecho da fronteira.

Decisão 3 do design: `fronteira`, `andamento`, `resposta`, `aviso` e `erro`,
com a fronteira sempre primeiro. Roda o `executar` de verdade, com o modelo e o
recuperador falsos da bancada.
"""
import json

import pytest

from bancada.tests.test_bancada import SAIDAS, Recuperador, chat_fixo
from interface import fluxo
from interface.fluxo import verificar
from prototipo.resposta import estrutura
from prototipo.verificacao import extracao, fronteira

MENSAGEM = "A casca do jatobá cura o câncer!"


def _eventos(texto, chat=None, recuperador=None):
    eventos = []
    verificar(texto, eventos.append, chat=chat or chat_fixo(),
              recuperador=recuperador or Recuperador())
    return eventos


def _com_fronteira(*categorias):
    return chat_fixo({**SAIDAS, fronteira.SISTEMA: {"categorias": list(categorias),
                                                    "motivo": "teste"}})


def test_verificacao_completa_tem_fronteira_primeiro_andamento_em_ordem_e_resposta():
    eventos = _eventos(MENSAGEM)
    assert [e["tipo"] for e in eventos] == ["fronteira"] + ["andamento"] * 5 + ["resposta"]
    assert [e["etapa"] for e in eventos if e["tipo"] == "andamento"] == [
        "extracao", "decomposicao", "recuperacao", "guarda", "resposta"]
    assert eventos[1]["frase"] == "Entendendo o que a mensagem diz…"


def test_resposta_traz_camada_visivel_com_bordao_e_detalhe():
    resposta = _eventos(MENSAGEM)[-1]
    assert resposta["forma"] == "com evidência"
    assert resposta["texto"].startswith(estrutura.BORDAO)
    assert resposta["detalhe"][0]["agencia"] == "Aos Fatos"
    assert resposta["redirecionamentos"] == []


def test_eventos_sao_serializaveis_em_json():
    for e in _eventos(MENSAGEM):
        json.dumps(e, ensure_ascii=False)


def test_mensagem_sem_alegacao_de_saude_vira_aviso():
    chat = chat_fixo({**SAIDAS, extracao.SISTEMA: {"alegacoes": [], "opiniao": None}})
    ultimo = _eventos("Quem ganhou o jogo ontem?", chat=chat)[-1]
    assert ultimo == {"tipo": "aviso", "chave": "sem_alegacao",
                      "texto": fluxo.textos()["sem_alegacao"]}


# ---- desfecho da fronteira (task 2.4) ------------------------------------------------

def test_urgencia_encerra_com_a_resposta_padrao_e_nada_mais():
    eventos = _eventos("Minha mãe está com dor no peito e falta de ar agora")
    assert eventos == [{"tipo": "fronteira", "desfecho": "urgencia",
                        "texto": fronteira.carregar_respostas()["risco_imediato"]["web"]}]


def test_sofrimento_encerra_com_a_resposta_padrao():
    eventos = _eventos("x", chat=_com_fronteira("sofrimento_psiquico"))
    assert [(e["tipo"], e["desfecho"]) for e in eventos] == [("fronteira", "sofrimento")]
    assert "188" in eventos[0]["texto"]


def test_urgencia_tem_prioridade_sobre_sofrimento():
    eventos = _eventos("x", chat=_com_fronteira("sofrimento_psiquico", "risco_imediato"))
    assert eventos[0]["desfecho"] == "urgencia"
    assert "SAMU" in eventos[0]["texto"] and "188" in eventos[0]["texto"]


def test_conduta_segue_o_fluxo_com_a_recusa_nos_redirecionamentos():
    eventos = _eventos("x", chat=_com_fronteira("conduta_individual", "checagem"))
    assert eventos[0] == {"tipo": "fronteira", "desfecho": "conduta", "texto": None}
    assert eventos[-1]["tipo"] == "resposta"
    assert eventos[-1]["redirecionamentos"] == [
        fronteira.carregar_respostas()["conduta_individual"]["web"]]


@pytest.mark.parametrize("categorias", [["checagem"], []])
def test_checagem_segue_sem_texto(categorias):
    assert _eventos(MENSAGEM, chat=_com_fronteira(*categorias))[0] == {
        "tipo": "fronteira", "desfecho": "segue", "texto": None}


# ---- erro sem vazamento (task 2.7) ---------------------------------------------------

SEGREDO = "Minha vizinha Dona Zélia, CPF 123, toma remédio X"


def _quebra_com_o_texto(sistema, usuario):
    raise ConnectionError(f"ollama recusou: {usuario}")


def test_falha_do_modelo_vira_erro_e_o_log_nao_tem_o_texto(caplog):
    caplog.set_level("ERROR", logger="dona_checa")
    eventos = _eventos(SEGREDO, chat=_quebra_com_o_texto)
    assert eventos[-1] == {"tipo": "erro", "texto": fluxo.textos()["erro"]}
    assert "fronteira" in caplog.text
    assert "ConnectionError" in caplog.text
    assert "Zélia" not in caplog.text and "123" not in caplog.text


def test_falha_numa_etapa_do_meio_registra_a_etapa(caplog):
    caplog.set_level("ERROR", logger="dona_checa")
    chat = chat_fixo({**SAIDAS, extracao.SISTEMA: None})

    def quebra_na_extracao(sistema, usuario):
        if sistema == extracao.SISTEMA:
            raise TimeoutError(usuario)
        return chat(sistema, usuario)
    eventos = _eventos(SEGREDO, chat=quebra_na_extracao)
    assert eventos[-1]["tipo"] == "erro"
    assert "extracao" in caplog.text and "TimeoutError" in caplog.text
    assert "Zélia" not in caplog.text
