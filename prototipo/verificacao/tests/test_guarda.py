"""Task 2.3 de mvp-copiloto-verificacao: guarda contra veredito por conhecimento paramétrico.

A guarda é código em volta da classificação. Ela não confia no prompt para a regra
da spec: sem trecho, o modelo nem é chamado; com trecho, veredito que não cita
trecho recuperado cai para `evidência insuficiente`.
"""
import json

import pytest

from prototipo.rag.hibrida import LIMIAR_EVIDENCIA
from prototipo.verificacao.guarda import INSUFICIENTE, VEREDITOS_AMPLA, sujeito_ausente, verificar


def _trecho(score=0.9, apto=True):
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
    assert v.original == {"rotulo": "falso", "trechos": [], "criterio": "Vacinas não causam autismo.",
                          "cobertura": "mesma", "ponte": "", "sujeito": ""}


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


# add-cobertura-alegacao-ampla, task 2.1 (D2) ---------------------------------

def test_veredito_de_cobertura_mesma_declara_a_cobertura():
    v = verificar("X.", [_trecho()], chat=_chat())
    assert (v.cobertura, v.ponte, v.sujeito) == ("mesma", "", "")


def test_insuficiente_nao_declara_cobertura():
    v = verificar("X.", [], chat=_explode)
    assert v.cobertura is None
    v = verificar("X.", [_trecho()], chat=_chat(INSUFICIENTE, [], "Nada."))
    assert v.cobertura is None


# add-cobertura-alegacao-ampla, task 2.2 (D2, travas 1 a 4) --------------------

JACARE = "Vacina de Covid-19 transformam pessoas em jacarés"


def _geral(agencia="boatos", chave="boato", score=0.6):
    return {"agencia": agencia, "data_publicacao": "2020-08-04", "url": f"https://{agencia}/dna",
            "veredito_original": chave, "veredito_chave": chave, "score": score,
            "apto_citacao": True,
            "alegacao": "Vacina contra a Covid-19 vai modificar o DNA das pessoas",
            "trecho": "É boato que a vacina contra a Covid-19 vá modificar o DNA."}


def _chat_ampla(rotulo="falso", trechos=("T1", "T2"), sujeito="vacina de Covid-19"):
    def chat(sistema, usuario):
        return json.dumps({"rotulo": rotulo, "trechos": list(trechos),
                           "criterio": "A geral é falsa.", "cobertura": "ampla",
                           "ponte": "Virar jacaré exigiria alterar o DNA.",
                           "sujeito": sujeito}, ensure_ascii=False)
    return chat


DUAS = [_geral(), _geral("aos fatos", "falso")]


def test_vereditos_aceitos_sao_as_chaves_que_o_mapa_leva_a_falso():
    import json as _json
    import pathlib
    mapa = _json.loads(pathlib.Path("tratamento/mapa_vereditos.json").read_text(encoding="utf-8"))
    assert set(VEREDITOS_AMPLA) == {k for k, e in mapa["entradas"].items() if e["rotulo"] == "falso"}


def test_trava_1_cobertura_ampla_desligada():
    v = verificar(JACARE, DUAS, chat=_chat_ampla(), ampla=False)
    assert v.rotulo == INSUFICIENTE
    assert v.rebaixado_por == "cobertura ampla desligada"
    assert v.original["cobertura"] == "ampla"


def test_trava_2_so_vale_para_falso():
    v = verificar(JACARE, DUAS, chat=_chat_ampla(rotulo="verdadeiro"))
    assert v.rotulo == INSUFICIENTE
    assert v.rebaixado_por == "cobertura ampla só vale para falso"


def test_trava_3_veredito_da_agencia_fora_de_falso():
    v = verificar(JACARE, [_geral(), _geral("lupa", "enganoso")], chat=_chat_ampla())
    assert v.rotulo == INSUFICIENTE
    assert v.rebaixado_por == "cobertura ampla com veredito da agência enganoso"


def test_trava_4_uma_agencia_so():
    v = verificar(JACARE, [_geral(), _geral()], chat=_chat_ampla())
    assert v.rotulo == INSUFICIENTE
    assert v.rebaixado_por == "cobertura ampla com uma agência só"


def test_trava_4_conta_so_os_trechos_citados():
    v = verificar(JACARE, DUAS, chat=_chat_ampla(trechos=("T1",)))
    assert v.rebaixado_por == "cobertura ampla com uma agência só"


# add-cobertura-alegacao-ampla, task 2.3 (D3, trava 5) --------------------------

CHIP = "Vacinas da COVID-19 tem chips chineses para nos monitorar"
LUPA_CHIP = {"agencia": "lupa", "veredito_chave": "falso",
             "alegacao": "É falso que vacinas contra a Covid-19 contêm microchip",
             "trecho": "As vacinas não operam com tecnologia 5G."}
CLOROQUINA = {"agencia": "aos fatos", "veredito_chave": "falso",
              "alegacao": "Cloroquina não previne a covid",
              "trecho": "Estudos mostram que a hidroxicloroquina não tem efeito."}


def test_sujeito_com_plural_e_caixa_diferentes_passa():
    assert sujeito_ausente("vacinas da COVID-19", CHIP, [LUPA_CHIP]) is None


def test_sujeito_ausente_do_trecho_falha_e_diz_onde():
    assert sujeito_ausente("vacinas da COVID-19", CHIP, [LUPA_CHIP, CLOROQUINA]) == \
        "sujeito vacinas da COVID-19 ausente de aos fatos"


def test_sujeito_ausente_da_alegacao_da_pessoa_falha():
    assert sujeito_ausente("imunizante", CHIP, [LUPA_CHIP]) == \
        "sujeito imunizante ausente da alegação"


def test_sujeito_so_de_palavras_vazias_falha():
    assert sujeito_ausente("da de a", CHIP, [LUPA_CHIP]) == "sujeito da de a vazio"


def test_trava_5_rebaixa_na_guarda():
    trechos = [{**_geral(), "trecho": "A cloroquina não altera nada."},
               {**_geral("aos fatos", "falso"), "alegacao": "Cloroquina", "trecho": "Cloroquina."}]
    v = verificar(JACARE, trechos, chat=_chat_ampla())
    assert v.rotulo == INSUFICIENTE
    assert v.rebaixado_por == "sujeito vacina de Covid-19 ausente de aos fatos"


# add-cobertura-alegacao-ampla, task 3.2 (D4, trava 6) --------------------------

from prototipo.verificacao import implicacao  # noqa: E402


def _chat_duplo(resposta="sim", **ampla):
    classificar = _chat_ampla(**ampla)
    pedidos = []

    def chat(sistema, usuario):
        if sistema == implicacao.SISTEMA:
            pedidos.append(usuario)
            return json.dumps({"resposta": resposta}, ensure_ascii=False)
        return classificar(sistema, usuario)
    chat.pedidos = pedidos
    return chat


def test_cobertura_ampla_confirmada_vira_falso():
    v = verificar(JACARE, DUAS, chat=_chat_duplo("sim"))
    assert v.rotulo == "falso"
    assert v.rebaixado_por is None
    assert (v.cobertura, v.implicacao) == ("ampla", "sim")
    assert v.ponte == "Virar jacaré exigiria alterar o DNA."
    assert v.sujeito == "vacina de Covid-19"
    assert {t["agencia"] for t in v.trechos} == {"boatos", "aos fatos"}


def test_implicacao_recusada_rebaixa_e_fica_registrada():
    v = verificar(JACARE, DUAS, chat=_chat_duplo("não"))
    assert v.rotulo == INSUFICIENTE
    assert v.rebaixado_por == "implicação não confirmada: não"
    assert v.implicacao == "não"
    assert v.original["cobertura"] == "ampla"


def test_rebaixada_guarda_as_alegacoes_checadas_para_a_revisao_das_pontes():
    """D7: a revisão humana precisa ver G mesmo quando a trava rebaixa."""
    v = verificar(JACARE, DUAS, chat=_chat_duplo("não"))
    assert v.trechos == []
    assert v.original["alegacoes_checadas"] == [t["alegacao"] for t in DUAS]


def test_cobertura_mesma_nao_ganha_alegacoes_checadas():
    def chat(sistema, usuario):
        return json.dumps({"rotulo": "falso", "trechos": ["T1", "T2"],
                           "criterio": "A geral é falsa.", "cobertura": "mesma"})
    v = verificar(JACARE, DUAS, chat=chat)
    assert "alegacoes_checadas" not in v.original


def test_implicacao_usa_a_alegacao_checada_de_maior_score():
    alta = {**_geral("aos fatos", "falso", score=0.9), "alegacao": "Vacinas de RNA não alteram o DNA"}
    chat = _chat_duplo("sim")
    verificar(JACARE, [_geral(score=0.6), alta], chat=chat)
    assert chat.pedidos == [f"FRASE A:\n{JACARE}\n\nFRASE B:\nVacinas de RNA não alteram o DNA"]


def test_implicacao_nao_e_pedida_quando_trava_de_codigo_falha():
    chat = _chat_duplo("sim")
    v = verificar(JACARE, [_geral(), _geral()], chat=chat)
    assert v.rebaixado_por == "cobertura ampla com uma agência só"
    assert chat.pedidos == []
    assert v.implicacao is None


def test_cobertura_mesma_nao_pede_implicacao():
    chat = _chat_duplo("não")
    real = chat
    v = verificar("X.", [_trecho()], chat=lambda s, u: _chat()(s, u) if s != implicacao.SISTEMA else real(s, u))
    assert v.rotulo == "falso" and v.implicacao is None
    assert real.pedidos == []
