"""fix-limitacoes-mvp, D1: conferência de sustentação.

Requirement Conferência de sustentação, de `resposta-formativa`: frase dos
blocos 1 e 2 sem base nos trechos, e frase do bloco 3 sem base na mensagem,
saem da resposta e ficam registradas. O modelo entra por função fixa.
"""
import json

from prototipo.resposta import conferencia
from prototipo.resposta.estrutura import FRASE_OPINIAO, responder
from prototipo.resposta.tests.test_estrutura import (
    ALEGACAO, BLOCOS_FALSO, FALSO, MENSAGEM, SEM_TRECHO, BLOCOS_SEM)

# Sem termo verificável: passa pela ancoragem léxica, que é o caso que a conferência pega.
DISTORCE = "A casca ajuda no tratamento quando tomada junto com outros remédios."
COM_DISTORCAO = {**BLOCOS_FALSO, "bloco2": BLOCOS_FALSO["bloco2"] + [{"frase": DISTORCE, "trecho": "T1"}]}


def _resposta(blocos=BLOCOS_FALSO, veredito=FALSO, decomposicao=None):
    def chat(sistema, usuario):
        return json.dumps(blocos, ensure_ascii=False)
    return responder(MENSAGEM, ALEGACAO, veredito, decomposicao=decomposicao, chat=chat)


def _juiz(sem_base, pedidos=None):
    def chat(sistema, usuario):
        if pedidos is not None:
            pedidos.append((sistema, usuario))
        return json.dumps({"sem_base": sem_base}, ensure_ascii=False)
    return chat


def _numero(pedido, frase):
    linha = next(l for l in pedido.splitlines() if frase in l)
    return int(linha.split("]")[0].strip("[F"))


def _refazer_proibido(veredito):
    raise AssertionError("não devia rebaixar")


def test_pedido_traz_trechos_mensagem_e_frases_sem_abertura_opiniao_nem_rotulo():
    r = _resposta(COM_DISTORCAO, decomposicao={"opinioes": ["Remédio só faz mal."]})
    pedidos = []
    conferencia.aplicar(r, MENSAGEM, chat=_juiz([], pedidos), refazer=_refazer_proibido)
    sistema, usuario = pedidos[0]
    assert sistema == conferencia.SISTEMA
    assert "[T1]" in usuario and MENSAGEM in usuario and DISTORCE in usuario
    frases = [l for l in usuario.splitlines() if l.startswith("[F")]
    assert not any(l.endswith("Falso.") or FRASE_OPINIAO in l or "Técnica:" in l for l in frases)
    assert any("(fato)" in l for l in frases) and any("(mensagem)" in l for l in frases)


def test_frase_apontada_sai_e_fica_registrada():
    r = _resposta(COM_DISTORCAO)
    pedidos = []
    conferencia.aplicar(r, MENSAGEM, chat=_juiz([], pedidos), refazer=_refazer_proibido)
    n = _numero(pedidos[0][1], DISTORCE)
    novo = conferencia.aplicar(r, MENSAGEM, chat=_juiz([{"n": n, "motivo": "inverte o trecho"}]),
                               refazer=_refazer_proibido)
    assert DISTORCE not in novo.texto
    assert novo.sem_base == [{"bloco": 2, "frase": DISTORCE, "motivo": "inverte o trecho"}]
    assert novo.conferencia == "ok"


def test_sem_frase_apontada_a_resposta_fica_igual():
    r = _resposta()
    novo = conferencia.aplicar(r, MENSAGEM, chat=_juiz([]), refazer=_refazer_proibido)
    assert novo.texto == r.texto and novo.sem_base == [] and novo.conferencia == "ok"


def test_bloco_1_sem_frase_do_modelo_rebaixa():
    r = _resposta()
    pedidos = []
    conferencia.aplicar(r, MENSAGEM, chat=_juiz([], pedidos), refazer=_refazer_proibido)
    n = _numero(pedidos[0][1], "Nenhum estudo mostra isso.")
    rebaixados = []

    def refazer(veredito):
        rebaixados.append(veredito)
        return _resposta(BLOCOS_SEM, SEM_TRECHO)
    novo = conferencia.aplicar(r, MENSAGEM, chat=_juiz([{"n": n, "motivo": "sem trecho"}]),
                               refazer=refazer)
    assert rebaixados[0].rotulo == "evidência insuficiente"
    assert "conferência" in rebaixados[0].rebaixado_por
    assert novo.forma == "sem evidência"
    assert novo.sem_base[0]["frase"] == "Nenhum estudo mostra isso."


def test_bloco_3_nao_fica_vazio():
    so_uma = {**BLOCOS_FALSO, "bloco3": "A mensagem promete curar doença grave com algo caseiro."}
    r = _resposta(so_uma)
    pedidos = []
    conferencia.aplicar(r, MENSAGEM, chat=_juiz([], pedidos), refazer=_refazer_proibido)
    n = _numero(pedidos[0][1], "promete curar doença grave")
    novo = conferencia.aplicar(r, MENSAGEM, chat=_juiz([{"n": n, "motivo": "x"}]),
                               refazer=_refazer_proibido)
    assert "promete curar doença grave" in novo.blocos[2]
    assert any(d.startswith("frase sem base: ") for d in novo.defeitos)


def test_falha_da_chamada_deixa_a_resposta_como_estava():
    r = _resposta()

    def quebra(sistema, usuario):
        raise ConnectionError("fora do ar")
    novo = conferencia.aplicar(r, MENSAGEM, chat=quebra, refazer=_refazer_proibido)
    assert novo.texto == r.texto and novo.conferencia == "não rodou: ConnectionError"


def test_saida_invalida_tambem_nao_derruba():
    r = _resposta()
    novo = conferencia.aplicar(r, MENSAGEM, chat=lambda s, u: "não é json",
                               refazer=_refazer_proibido)
    assert novo.texto == r.texto and novo.conferencia.startswith("não rodou")


def test_forma_sem_evidencia_nao_e_conferida():
    r = _resposta(BLOCOS_SEM, SEM_TRECHO)
    novo = conferencia.aplicar(r, MENSAGEM, chat=lambda s, u: 1 / 0, refazer=_refazer_proibido)
    assert novo is r and r.conferencia is None


def test_prompt_proibe_conhecimento_proprio_e_aceita_so_trecho_ou_mensagem():
    assert "O que você sabe de medicina não conta" in conferencia.SISTEMA
    assert "inverte" in conferencia.SISTEMA and '"sem_base"' in conferencia.SISTEMA
