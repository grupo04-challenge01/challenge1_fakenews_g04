"""Task 5.5 de add-gerador-api-deepseek: termo de consentimento na página.

Requirement Consentimento antes do envio ao serviço externo, de
`interface-chat-web`, e decisão D8: o campo só libera depois de uma escolha, o
pedido leva a escolha, e recarregar pede de novo.
"""
import json
import pathlib

from playwright.sync_api import expect

from interface.app import RECUSADO, TERMO_VERSAO
from interface.fluxo import textos
from interface.tests.pagina.test_pagina import MENSAGEM, enviar, resposta

AXE = (pathlib.Path(__file__).parents[1] / "vendor" / "axe.min.js").read_text(encoding="utf-8")


def _junto(t):
    return " ".join(t.split())


def _corpos(page):
    corpos = []
    page.on("request", lambda r: corpos.append(json.loads(r.post_data))
            if r.method == "POST" else None)
    return corpos


def _termo(page):
    return page.get_by_role("group", name=_junto(textos()["termo-servico-externo"]))


def test_termo_aparece_e_o_campo_fica_bloqueado_ate_a_escolha(page, servidor_deepseek):
    page.goto(servidor_deepseek)
    termo = _termo(page)
    expect(termo).to_be_visible()
    expect(termo.get_by_role("button", name="Aceito", exact=True)).to_be_visible()
    expect(termo.get_by_role("button", name="Não aceito")).to_be_visible()
    expect(page.get_by_label("Cole aqui o que você recebeu")).to_be_disabled()
    expect(page.get_by_role("button", name="Enviar")).to_be_disabled()


def test_aceite_libera_o_campo_e_o_pedido_leva_a_versao(page, servidor_deepseek):
    corpos = _corpos(page)
    page.goto(servidor_deepseek)
    page.get_by_role("button", name="Aceito", exact=True).click()
    expect(page.get_by_role("button", name="Aceito", exact=True)).to_have_count(0)
    enviar(page, MENSAGEM)
    expect(resposta(page)).to_contain_text("Veredito:")
    assert corpos == [{"texto": MENSAGEM, "consentimento": TERMO_VERSAO}]


def test_recusa_sem_alternativa_mostra_o_texto_e_mantem_o_campo_bloqueado(page, servidor_deepseek):
    corpos = _corpos(page)
    page.goto(servidor_deepseek)
    page.get_by_role("button", name="Não aceito").click()
    expect(resposta(page)).to_have_text(_junto(textos()["recusa"]))
    expect(page.get_by_label("Cole aqui o que você recebeu")).to_be_disabled()
    assert corpos == []


def test_recusa_com_alternativa_libera_o_campo_e_pede_o_gerador_local(page, servidor_deepseek_local):
    corpos = _corpos(page)
    page.goto(servidor_deepseek_local)
    page.get_by_role("button", name="Não aceito").click()
    expect(resposta(page)).to_have_text(_junto(textos()["recusa-local"]))
    enviar(page, MENSAGEM)
    expect(resposta(page)).to_contain_text("Veredito:")
    assert corpos == [{"texto": MENSAGEM, "consentimento": RECUSADO}]


def test_recarregar_pede_o_termo_de_novo(page, servidor_deepseek):
    page.goto(servidor_deepseek)
    page.get_by_role("button", name="Aceito", exact=True).click()
    page.reload()
    expect(_termo(page)).to_be_visible()
    expect(page.get_by_label("Cole aqui o que você recebeu")).to_be_disabled()


def test_gerador_local_nao_mostra_termo(page, servidor_uso):
    page.goto(servidor_uso)
    expect(page.get_by_role("button", name="Não aceito")).to_have_count(0)
    expect(page.get_by_label("Cole aqui o que você recebeu")).to_be_enabled()


def test_axe_sem_violacoes_com_o_termo_aberto(page, servidor_deepseek):
    page.goto(servidor_deepseek)
    expect(_termo(page)).to_be_visible()
    page.add_script_tag(content=AXE)
    violacoes = page.evaluate("axe.run().then(r => r.violations.map(v => v.id + ': ' + "
                              "v.nodes.map(n => n.target.join(' ')).join(', ')))")
    assert violacoes == []
