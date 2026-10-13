"""Task 5.3 de add-cobertura-alegacao-ampla: ponte e alegação checada no detalhe.

Requirement Veredito por alegação mais ampla declarado, de `resposta-formativa`:
o detalhe traz a alegação que cada agência checou, literal, e a ponte. Usa o
servidor e o fluxo falso de `conftest.py`.
"""
from playwright.sync_api import expect

from interface.tests.pagina.conftest import DETALHE_AMPLO, PONTE
from interface.tests.pagina.test_pagina import AXE, enviar, resposta

JACARE = "Vacina de Covid-19 transformam pessoas em jacarés"


def _detalhe_aberto(page, url):
    page.goto(url)
    enviar(page, JACARE)
    resposta(page).get_by_role("button", name="Ver fontes e detalhes").click()
    expect(resposta(page).locator(".ponte")).to_be_visible()


def test_detalhe_mostra_a_ponte_antes_das_fontes(page, servidor_uso):
    _detalhe_aberto(page, servidor_uso)
    ponte = resposta(page).locator(".detalhe > .ponte")
    expect(ponte).to_contain_text("Por que esta checagem vale para a sua mensagem:")
    expect(ponte).to_contain_text(PONTE)
    expect(resposta(page).locator(".detalhe > *").first).to_have_class("ponte")


def test_cada_fonte_mostra_a_alegacao_checada_literal(page, servidor_uso):
    _detalhe_aberto(page, servidor_uso)
    fontes = resposta(page).locator(".fonte")
    expect(fontes).to_have_count(2)
    for n, item in enumerate(DETALHE_AMPLO):
        expect(fontes.nth(n).locator(".checada")).to_have_text(
            f"Alegação checada pela agência: {item['alegacao_checada']}")


def test_resposta_comum_nao_mostra_ponte_nem_alegacao_checada(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, "A casca do jatobá cura o câncer!")
    resposta(page).get_by_role("button", name="Ver fontes e detalhes").click()
    expect(resposta(page).locator(".fonte").first).to_be_visible()
    expect(resposta(page).locator(".ponte")).to_have_count(0)
    expect(resposta(page).locator(".checada")).to_have_count(0)


def test_axe_sem_violacoes_com_detalhe_amplo_aberto(page, servidor_uso):
    _detalhe_aberto(page, servidor_uso)
    page.add_script_tag(content=AXE)
    violacoes = page.evaluate("axe.run().then(r => r.violations.map(v => v.id + ': ' + "
                              "v.nodes.map(n => n.target.join(' ')).join(', ')))")
    assert violacoes == []


def test_320px_com_detalhe_amplo_sem_rolagem_horizontal(page, servidor_uso):
    page.set_viewport_size({"width": 320, "height": 640})
    _detalhe_aberto(page, servidor_uso)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
