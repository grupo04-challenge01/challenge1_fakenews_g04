"""Task 3.1 de add-cobertura-alegacao-ampla: verificação de implicação (D4).

O modelo é substituído por função que devolve texto fixo. O comportamento real
é medido pela sonda `prototipo/sonda_cobertura_ampla.py`.
"""
import json

from prototipo.verificacao.implicacao import SISTEMA, confirmar

P = "Vacina de Covid-19 transformam pessoas em jacarés"
G = "Vacina contra a Covid-19 vai modificar o DNA das pessoas"


def _chat(resposta):
    vistos = []

    def chat(sistema, usuario):
        vistos.append((sistema, usuario))
        return resposta if isinstance(resposta, str) else json.dumps(resposta, ensure_ascii=False)
    chat.vistos = vistos
    return chat


def test_sim_confirma():
    assert confirmar(P, G, _chat({"resposta": "sim"})) == (True, "sim")


def test_caixa_e_espaco_sao_normalizados():
    assert confirmar(P, G, _chat({"resposta": " Sim "})) == (True, "sim")


def test_nao_e_incerto_nao_confirmam():
    assert confirmar(P, G, _chat({"resposta": "não"})) == (False, "não")
    assert confirmar(P, G, _chat({"resposta": "incerto"})) == (False, "incerto")


def test_saida_que_nao_e_json_nao_confirma():
    assert confirmar(P, G, _chat("acho que sim")) == (False, "saída inválida")


def test_resposta_fora_das_tres_nao_confirma():
    assert confirmar(P, G, _chat({"resposta": "talvez"})) == (False, "saída inválida")


def test_erro_do_gerador_nao_confirma():
    def chat(sistema, usuario):
        raise RuntimeError("caiu")
    assert confirmar(P, G, chat) == (False, "erro: RuntimeError")


def test_pedido_e_cego_so_as_duas_frases():
    chat = _chat({"resposta": "sim"})
    confirmar(P, G, chat)
    sistema, usuario = chat.vistos[0]
    assert usuario == f"FRASE A:\n{P}\n\nFRASE B:\n{G}"
    assert sistema == SISTEMA


def test_prompt_pergunta_implicacao_necessaria():
    assert "necessariamente" in SISTEMA
    assert '{"resposta": "sim"}' in SISTEMA
