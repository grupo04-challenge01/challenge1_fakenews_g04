"""Tasks 3.x e 5.2 a 5.5 de add-interface-chat-web: a página no navegador.

Requirements de `interface-chat-web`: fronteira antes de tudo, pergunta de
confiança só no navegador, resposta e detalhe na bolha, nada guardado, e
acessibilidade verificada por teste.
"""
import json
import pathlib
import re

import pytest
from playwright.sync_api import expect

from prototipo.identidade import textos as persona
from prototipo.resposta.estrutura import BORDAO

AXE = (pathlib.Path(__file__).parents[1] / "vendor" / "axe.min.js").read_text(encoding="utf-8")
MENSAGEM = "A casca do jatobá cura o câncer, um médico confirmou!"


def enviar(page, texto):
    page.get_by_label("Cole aqui o que você recebeu").fill(texto)
    page.get_by_role("button", name="Enviar").click()


def resposta(page):
    return page.locator(".bolha.dona").last


# ---- estado inicial ------------------------------------------------------------------

def test_inicial_mostra_cabecalho_chamada_e_abertura(page, servidor_uso):
    page.goto(servidor_uso)
    expect(page.get_by_role("banner")).to_contain_text("Dona Checa")
    expect(page.get_by_text(persona()["chamada"])).to_be_visible()
    expect(page.locator(".bolha.dona").first).to_have_text(persona()["abertura"])
    expect(page.get_by_role("button", name="Enviar")).to_be_visible()


def test_mensagem_vazia_nao_e_enviada(page, servidor_uso):
    page.goto(servidor_uso)
    page.get_by_role("button", name="Enviar").click()
    expect(page.locator(".bolha.pessoa")).to_have_count(0)


# ---- verificação comum ---------------------------------------------------------------

def test_verificacao_comum_mostra_bordao_pergunta_andamento_e_resposta(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, MENSAGEM)
    expect(page.locator(".bolha.pessoa")).to_have_text(MENSAGEM)
    bolha = resposta(page)
    expect(bolha).to_contain_text(BORDAO)
    expect(bolha.get_by_role("button", name="4 a 6")).to_be_visible()
    expect(bolha.locator(".andamento")).not_to_be_empty()
    expect(bolha).to_contain_text("Veredito: Falso.")
    expect(bolha).to_contain_text("O que observar da próxima vez:")
    expect(bolha.locator(".andamento")).to_have_count(0)
    assert bolha.inner_text().count(BORDAO) == 1


def test_campo_fica_livre_e_cada_envio_e_uma_verificacao_nova(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, MENSAGEM)
    expect(resposta(page)).to_contain_text("Veredito:")
    enviar(page, "Outra mensagem sobre chá que cura gripe")
    expect(page.locator(".bolha.pessoa")).to_have_count(2)
    expect(resposta(page)).to_contain_text("Veredito:")


def test_foco_vai_para_a_resposta(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, MENSAGEM)
    expect(resposta(page)).to_contain_text("Veredito:")
    assert page.evaluate("document.activeElement.closest('.bolha.dona') !== null")


# ---- fronteira (task 5.2) ------------------------------------------------------------

def test_urgencia_aparece_sem_bordao_nem_pergunta_e_com_tel(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, "Minha mãe está com dor no peito agora")
    alerta = page.get_by_role("alert")
    expect(alerta).to_contain_text("SAMU")
    expect(alerta.locator('a[href="tel:192"]')).to_be_visible()
    expect(page.get_by_text(BORDAO)).to_have_count(0)
    expect(page.get_by_role("button", name="4 a 6")).to_have_count(0)


def test_sofrimento_aparece_com_tel_188(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, "Vou tomar tudo pra acabar com tudo")
    expect(page.get_by_role("alert").locator('a[href="tel:188"]')).to_be_visible()
    expect(page.get_by_text(BORDAO)).to_have_count(0)


def test_conduta_mostra_a_recusa_sem_pergunta(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, "Posso parar meu remédio de pressão? Li que chuchu resolve")
    expect(page.get_by_text("não posso indicar nem mudar tratamento").first).to_be_visible()
    expect(page.get_by_role("button", name="4 a 6")).to_have_count(0)


# ---- avisos e erro -------------------------------------------------------------------

def test_mensagem_sem_saude_mostra_aviso_sem_bordao(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, "Quem ganhou o futebol ontem?")
    expect(resposta(page)).to_contain_text("não achei nessa mensagem nada de saúde")
    expect(page.get_by_text(BORDAO)).to_have_count(0)


def test_so_link_pede_o_texto(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, "https://exemplo.com.br/noticia")
    expect(resposta(page)).to_contain_text("ainda não consigo abrir link")


def test_erro_tem_tentar_de_novo_que_reenvia_a_mesma_mensagem(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, "isso quebra tudo")
    expect(resposta(page)).to_contain_text("deu um problema aqui do meu lado")
    pedidos = []
    page.on("request", lambda r: pedidos.append(r.post_data) if r.method == "POST" else None)
    page.get_by_role("button", name="Tentar de novo").click()
    expect(page.locator(".bolha.pessoa")).to_have_count(2)
    assert json.loads(pedidos[0]) == {"texto": "isso quebra tudo"}


# ---- pergunta de confiança (task 5.3) ------------------------------------------------

def test_piloto_nao_tem_pergunta_e_marca_o_rodape(page, servidor_piloto):
    page.goto(servidor_piloto)
    expect(page.get_by_role("contentinfo")).to_have_text("modo piloto")
    enviar(page, MENSAGEM)
    expect(resposta(page)).to_contain_text("Veredito:")
    expect(page.get_by_role("button", name="4 a 6")).to_have_count(0)


def test_escolha_da_pergunta_nao_sai_do_navegador(page, servidor_uso):
    corpos = []
    page.on("request", lambda r: corpos.append(r.post_data or "") if r.method == "POST" else None)
    page.goto(servidor_uso)
    enviar(page, MENSAGEM)
    escolha = resposta(page).get_by_role("button", name="4 a 6")
    escolha.click()
    expect(escolha).to_have_attribute("aria-pressed", "true")
    expect(resposta(page)).to_contain_text("Veredito:")
    assert all("4 a 6" not in c for c in corpos)
    guardado = page.evaluate("JSON.stringify(localStorage) + JSON.stringify(sessionStorage)"
                             " + document.cookie")
    assert "4 a 6" not in guardado and "confia" not in guardado


def test_resposta_chega_mesmo_sem_responder_a_pergunta(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, MENSAGEM)
    expect(resposta(page)).to_contain_text("Veredito:")
    expect(resposta(page).get_by_role("button", name="4 a 6")).to_have_attribute(
        "aria-pressed", "false")


# ---- detalhe e nada guardado (task 5.4) ----------------------------------------------

def test_detalhe_abre_e_fecha_dentro_da_bolha(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, MENSAGEM)
    botao = resposta(page).get_by_role("button", name="Ver fontes e detalhes")
    expect(botao).to_have_attribute("aria-expanded", "false")
    botao.click()
    expect(botao).to_have_attribute("aria-expanded", "true")
    cartoes = resposta(page).locator(".fonte")
    expect(cartoes).to_have_count(2)
    expect(cartoes.first).to_contain_text("Aos Fatos")
    expect(cartoes.first).to_contain_text("08/01/2021")
    expect(cartoes.first.get_by_role("link")).to_have_attribute("href", "https://www.aosfatos.org/x")
    expect(cartoes.nth(1)).to_contain_text("Trecho não exibido")
    botao.click()
    expect(botao).to_have_attribute("aria-expanded", "false")
    expect(cartoes.first).to_be_hidden()


def test_recarregar_mostra_so_a_abertura(page, servidor_uso):
    page.goto(servidor_uso)
    enviar(page, MENSAGEM)
    expect(resposta(page)).to_contain_text("Veredito:")
    page.reload()
    expect(page.locator(".bolha")).to_have_count(1)
    expect(page.locator(".bolha.dona")).to_have_text(persona()["abertura"])


# ---- acessibilidade (task 5.5) -------------------------------------------------------

def _resposta_com_detalhe_aberto(page, url):
    page.goto(url)
    enviar(page, MENSAGEM)
    resposta(page).get_by_role("button", name="Ver fontes e detalhes").click()
    expect(resposta(page).locator(".fonte").first).to_be_visible()


def test_fonte_base_de_18px_em_rem(page, servidor_uso):
    page.goto(servidor_uso)
    assert page.evaluate("getComputedStyle(document.documentElement).fontSize") == "18px"
    assert page.evaluate("getComputedStyle(document.body).fontSize") == "18px"
    css = page.evaluate("[...document.styleSheets].flatMap(s => [...s.cssRules])"
                        ".map(r => r.cssText).join('\\n')")
    assert not re.search(r"font-size:\s*\d+px", css)


def test_alvos_de_toque_de_44px(page, servidor_uso):
    _resposta_com_detalhe_aberto(page, servidor_uso)
    pequenos = page.evaluate("""[...document.querySelectorAll('button, a, textarea')]
        .filter(e => e.offsetParent !== null)
        .map(e => [e.textContent.trim() || e.getAttribute('aria-label'),
                   e.getBoundingClientRect()])
        .filter(([, r]) => r.height < 44 || r.width < 44)
        .map(([nome, r]) => `${nome}: ${Math.round(r.width)}x${Math.round(r.height)}`)""")
    assert pequenos == []


@pytest.mark.parametrize("url", ["servidor_uso", "servidor_piloto"])
def test_axe_sem_violacoes(page, url, request):
    _resposta_com_detalhe_aberto(page, request.getfixturevalue(url))
    page.add_script_tag(content=AXE)
    violacoes = page.evaluate("axe.run().then(r => r.violations.map(v => v.id + ': ' + "
                              "v.nodes.map(n => n.target.join(' ')).join(', ')))")
    assert violacoes == []


def test_320px_com_fonte_em_200_por_cento_sem_rolagem_horizontal(page, servidor_uso):
    page.set_viewport_size({"width": 320, "height": 640})
    page.goto(servidor_uso)
    page.add_style_tag(content="html { font-size: 225% !important; }")
    enviar(page, MENSAGEM)
    resposta(page).get_by_role("button", name="Ver fontes e detalhes").click()
    expect(resposta(page).locator(".fonte").first).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth") <= 320
    expect(page.get_by_role("button", name="Enviar")).to_be_in_viewport()


def test_fluxo_completo_so_pelo_teclado(page, servidor_uso):
    page.goto(servidor_uso)
    page.get_by_label("Cole aqui o que você recebeu").focus()
    page.keyboard.type(MENSAGEM)
    page.keyboard.press("Shift+Enter")
    page.keyboard.type("Repassem!")
    page.keyboard.press("Enter")
    expect(page.locator(".bolha.pessoa")).to_have_text(f"{MENSAGEM}\nRepassem!")
    expect(resposta(page)).to_contain_text("Veredito:")
    for _ in range(30):
        if page.evaluate("document.activeElement.textContent.trim()") == "Ver fontes e detalhes":
            break
        page.keyboard.press("Tab")
    page.keyboard.press("Enter")
    expect(resposta(page).locator(".fonte").first).to_be_visible()


def test_movimento_reduzido_desliga_animacoes(page, servidor_uso):
    page.emulate_media(reduced_motion="reduce")
    page.goto(servidor_uso)
    enviar(page, MENSAGEM)
    animadas = page.evaluate("""[...document.querySelectorAll('*')]
        .filter(e => { const s = getComputedStyle(e);
                       return s.animationName !== 'none' && s.animationDuration !== '0s'; })
        .length""")
    assert animadas == 0
