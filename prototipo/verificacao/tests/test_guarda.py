"""Task 2.3 de mvp-copiloto-verificacao: guarda contra veredito por conhecimento paramétrico.

A guarda é código em volta da classificação. Ela não confia no prompt para a regra
da spec: sem trecho, o modelo nem é chamado; com trecho, veredito que não cita
trecho recuperado cai para `evidência insuficiente`.
"""
import json

import pytest

from prototipo.verificacao.guarda import INSUFICIENTE, verificar


def _trecho(score=0.5, apto=True):
    return {"agencia": "aos fatos", "data_publicacao": "2021-01-08", "url": "https://a/1",
            "veredito_original": "falso", "trecho": "Não é verdade que...", "score": score,
            "apto_citacao": apto}


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


def test_sem_limiar_todos_os_trechos_vao_ao_modelo():
    chat = _chat()
    verificar("X.", [_trecho(0.01), _trecho(0.02)], chat=chat)
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


# Task 1.6: fragmento inapto é só metadado (decisão 17) -----------------------

def _inapto(texto="TEXTO REPROVADO NO PORTÃO", url="https://factckbr/1", score=0.9):
    t = _trecho(score=score, apto=False)
    t.update({"agencia": "lupa", "url": url, "veredito_original": "falso", "trecho": texto})
    return t


def test_texto_do_inapto_nao_vai_ao_modelo_e_nao_ganha_numero():
    chat = _chat(trechos=("T1",))
    verificar("alegação", [_inapto(), _trecho()], chat=chat)
    assert "TEXTO REPROVADO" not in chat.chamadas[0]
    assert "[T1]" in chat.chamadas[0] and "[T2]" not in chat.chamadas[0]


def test_so_inaptos_da_insuficiente_sem_chamar_o_modelo():
    v = verificar("alegação", [_inapto(), _inapto(url="https://factckbr/2")], chat=_explode)
    assert v.rotulo == INSUFICIENTE
    assert "apto" in v.rebaixado_por
    assert [r["url"] for r in v.referencias] == ["https://factckbr/1", "https://factckbr/2"]


def test_referencia_leva_agencia_link_e_veredito_e_nunca_o_trecho():
    v = verificar("alegação", [_inapto(), _trecho()], chat=_chat(trechos=("T1",)))
    assert v.rotulo == "falso"
    assert v.referencias == [{"agencia": "lupa", "data_publicacao": "2021-01-08",
                              "url": "https://factckbr/1", "veredito_original": "falso"}]
    assert all("trecho" not in r for r in v.referencias)
    assert all(t["apto_citacao"] is True for t in v.trechos)


def test_sem_a_marca_conta_como_inapto():
    sem_marca = _trecho()
    del sem_marca["apto_citacao"]
    v = verificar("alegação", [sem_marca], chat=_explode)
    assert v.rotulo == INSUFICIENTE
    assert len(v.referencias) == 1


def test_limiar_vale_tambem_para_o_inapto():
    v = verificar("alegação", [_inapto(score=0.1), _trecho(score=0.8)],
                  chat=_chat(trechos=("T1",)), limiar=0.5)
    assert v.referencias == []
