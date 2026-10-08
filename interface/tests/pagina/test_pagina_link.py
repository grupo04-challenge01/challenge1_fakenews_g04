"""Tasks 7.2 a 7.5 de add-entrada-por-link: mensagem com link na página.

Requirement Mensagem com link, de `interface-chat-web` no delta de
add-entrada-por-link. Usa o servidor e o fluxo falso de `conftest.py`.
"""
import pathlib

import pytest
from playwright.sync_api import expect

from interface import fluxo
from interface.tests.pagina.conftest import ORIGEM
from interface.tests.pagina.test_pagina import AXE, enviar, resposta
from prototipo.entrada.leitura import AVISO_PARCIAL
from prototipo.resposta.estrutura import BORDAO

LINK = "Olha isso: https://blog.exemplo/cura"


def _origem_aberta(page, url, mensagem=LINK):
    page.goto(url)
    enviar(page, mensagem)
    resposta(page).get_by_role("button", name="Ver fontes e detalhes").click()
    expect(resposta(page).locator(".origem")).to_be_visible()


# 7.2

def test_link_mostra_abrindo_o_link(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, LINK)
    expect(resposta(page).locator(".andamento")).to_have_text("Abrindo o link…")


# 7.3

def test_video_mostra_o_texto_sem_bordao_pergunta_nem_tentar_de_novo(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, "https://youtu.be/abc123")
    expect(resposta(page)).to_have_text(fluxo.textos()["video"])
    expect(page.get_by_text(BORDAO)).to_have_count(0)
    expect(page.get_by_role("button", name="4 a 6")).to_have_count(0)
    expect(page.get_by_role("button", name="Tentar de novo")).to_have_count(0)


# 7.4

def test_cartao_de_origem_abre_o_detalhe_antes_das_fontes(page, servidor_uso):
    _origem_aberta(page, servidor_uso)
    cartoes = resposta(page).locator(".detalhe > article")
    expect(cartoes).to_have_count(3)
    origem = cartoes.first
    expect(origem).to_have_class("origem")
    expect(origem).to_contain_text("Li esta página:")
    expect(origem).to_contain_text(ORIGEM["titulo"])
    expect(origem).to_contain_text("Blog Exemplo")
    expect(origem).to_contain_text("20/09/2026")
    expect(origem.get_by_role("link")).to_have_attribute("href", ORIGEM["url"])


def test_resposta_de_texto_nao_tem_cartao_de_origem(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, "A casca do jatobá cura o câncer!")
    resposta(page).get_by_role("button", name="Ver fontes e detalhes").click()
    expect(resposta(page).locator(".fonte").first).to_be_visible()
    expect(resposta(page).locator(".origem")).to_have_count(0)


# 7.5

def test_aviso_parcial_entre_bordao_e_primeiro_bloco(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, "https://blog.exemplo/parcial")
    paragrafos = resposta(page).locator(":scope > p")
    expect(paragrafos.nth(0)).to_have_text(BORDAO)
    expect(paragrafos.nth(1)).to_have_text(AVISO_PARCIAL)
    expect(paragrafos.nth(2)).to_contain_text("Veredito:")


def test_axe_sem_violacoes_com_origem_aberta(page, servidor_uso):
    _origem_aberta(page, servidor_uso)
    page.add_script_tag(content=AXE)
    violacoes = page.evaluate("axe.run().then(r => r.violations.map(v => v.id + ': ' + "
                              "v.nodes.map(n => n.target.join(' ')).join(', ')))")
    assert violacoes == []


def test_320px_com_origem_aberta_sem_rolagem_horizontal(page, servidor_uso):
    page.set_viewport_size({"width": 320, "height": 640})
    page.goto(servidor_uso)
    page.add_style_tag(content="html { font-size: 225% !important; }")
    enviar(page, LINK)
    resposta(page).get_by_role("button", name="Ver fontes e detalhes").click()
    expect(resposta(page).locator(".origem")).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth") <= 320
    expect(page.get_by_role("button", name="Enviar")).to_be_in_viewport()
