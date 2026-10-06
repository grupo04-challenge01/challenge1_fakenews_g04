"""Task 2.3 de mvp-copiloto-verificacao: guarda contra veredito por conhecimento paramétrico.

A guarda é código em volta da classificação. Ela não confia no prompt para a regra
da spec: sem trecho, o modelo nem é chamado; com trecho, veredito que não cita
trecho recuperado cai para `evidência insuficiente`.
"""
import json

import pytest

from prototipo.rag.hibrida import LIMIAR_EVIDENCIA
from prototipo.verificacao.guarda import INSUFICIENTE, verificar


def _trecho(score=0.9):
    return {"agencia": "aos fatos", "data_publicacao": "2021-01-08", "url": "https://a/1",
            "veredito_original": "falso", "trecho": "Não é verdade que...", "score": score}


def _chat(rotulo="falso", trechos=("T1",), criterio="O trecho T1 desmente."):
    chamadas = []

    def chat(sistema, usuario):
        chamadas.append(usuario)
        return json.dumps({"rotulo": rotulo, "trechos": list(trechos), "criterio": criterio},
                          ensure_ascii=False)
    chat.chamadas = chamadas
    return chat


def _explode(sistema, usuario):
    raise AssertionError("o modelo não pode ser chamado sem trecho")


def test_sem_trecho_da_insuficiente_sem_chamar_o_modelo():
    v = verificar("Vacina causa autismo.", [], chat=_explode)
    assert v.rotulo == INSUFICIENTE
    assert v.rebaixado_por == "nenhum trecho recuperado"


def test_trechos_abaixo_do_limiar_contam_como_nenhum():
    v = verificar("X.", [_trecho(0.1), _trecho(0.2)], chat=_explode, limiar=0.3)
    assert v.rotulo == INSUFICIENTE
    assert v.rebaixado_por == "nenhum trecho acima do limiar 0.3"


def test_limiar_filtra_so_os_trechos_fracos():
    chat = _chat(trechos=("T1",))
    v = verificar("X.", [_trecho(0.1), _trecho(0.6)], chat=chat, limiar=0.3)
    # Só o trecho acima do limiar vai ao modelo, e passa a ser o T1.
    assert "[T2]" not in chat.chamadas[0]
    assert v.rotulo == "falso"
    assert v.trechos[0]["score"] == 0.6


def test_limiar_padrao_e_o_calibrado_na_1_5():
    v = verificar("X.", [_trecho(LIMIAR_EVIDENCIA - 0.01)], chat=_explode)
    assert v.rebaixado_por == f"nenhum trecho acima do limiar {LIMIAR_EVIDENCIA}"
    chat = _chat()
    verificar("X.", [_trecho(LIMIAR_EVIDENCIA)], chat=chat)
    assert "[T1]" in chat.chamadas[0]


def test_sem_limiar_todos_os_trechos_vao_ao_modelo():
    chat = _chat()
    verificar("X.", [_trecho(0.01), _trecho(0.02)], chat=chat, limiar=None)
    assert "[T2]" in chat.chamadas[0]


def test_veredito_que_cita_trecho_recuperado_passa():
    v = verificar("X.", [_trecho()], chat=_chat("verdadeiro", ["T1"]))
    assert v.rotulo == "verdadeiro"
    assert v.rebaixado_por is None
    assert v.trechos[0]["url"] == "https://a/1"


def test_veredito_sem_trecho_citado_cai_para_insuficiente():
    v = verificar("X.", [_trecho()], chat=_chat("falso", []))
    assert v.rotulo == INSUFICIENTE
    assert v.rebaixado_por == "veredito falso sem trecho citado"


def test_veredito_citando_trecho_que_nao_foi_recuperado_cai():
    # T3 não existe: o modelo inventou a fonte.
    v = verificar("X.", [_trecho()], chat=_chat("falso", ["T3"]))
    assert v.rotulo == INSUFICIENTE
    assert v.rebaixado_por == "veredito falso cita trecho não recuperado: T3"


def test_trecho_inventado_ao_lado_de_um_real_tambem_cai():
    v = verificar("X.", [_trecho()], chat=_chat("falso", ["T1", "T9"]))
    assert v.rotulo == INSUFICIENTE


def test_insuficiente_do_modelo_passa_sem_trecho():
    v = verificar("X.", [_trecho()], chat=_chat(INSUFICIENTE, [], "O trecho não fala da alegação."))
    assert v.rotulo == INSUFICIENTE
    assert v.rebaixado_por is None


def test_rebaixado_guarda_o_que_o_modelo_disse():
    # Para a sonda e para auditoria: o que foi rebaixado não some.
    v = verificar("X.", [_trecho()], chat=_chat("falso", [], "Vacinas não causam autismo."))
    assert v.original == {"rotulo": "falso", "trechos": [], "criterio": "Vacinas não causam autismo."}


def test_saida_malformada_do_modelo_propaga_erro():
    with pytest.raises(ValueError):
        verificar("X.", [_trecho()], chat=lambda s, u: "sem json")
