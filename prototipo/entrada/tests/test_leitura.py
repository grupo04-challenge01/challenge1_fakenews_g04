"""Tasks 4.2 a 4.4 de add-entrada-por-link: ler a página (decisão D6).

`buscar` é trocado por uma função que devolve as páginas gravadas em
`paginas/`; nenhum teste acessa a rede.
"""
import json
import pathlib

import pytest

from prototipo.entrada.leitura import Falha, Leitura, ler
from prototipo.entrada.rede import Pagina, Recusa

PAGINAS = pathlib.Path(__file__).parent / "paginas"
INDICE = json.loads((PAGINAS / "indice.json").read_text(encoding="utf-8"))


def _gravada(nome, url_final=None, tipo="text/html; charset=utf-8"):
    corpo = (PAGINAS / f"{nome}.html").read_bytes()
    info = INDICE.get(nome, {})
    return Pagina(corpo, url_final or info.get("url_final", f"https://exemplo.com.br/{nome}"),
                  info.get("tipo", tipo))


def _buscar(pagina):
    pedidos = []

    def buscar(url):
        pedidos.append(url)
        if isinstance(pagina, Exception):
            raise pagina
        return pagina
    buscar.pedidos = pedidos
    return buscar


def _ler(nome, url="https://exemplo.com.br/x", **kw):
    return ler(url, buscar=_buscar(_gravada(nome, **kw)))


# 4.2 leitura completa

def test_blog_completo_traz_titulo_veiculo_e_data():
    leitura = _ler("blog_oglobo_completo")
    assert isinstance(leitura, Leitura)
    assert not leitura.parcial
    assert leitura.titulo == "A gravidez e o futuro"
    assert leitura.veiculo
    assert leitura.data == "2026-10-04"
    assert leitura.url == INDICE["blog_oglobo_completo"]["url_final"]
    assert leitura.texto.startswith("A gravidez e o futuro")


def test_paywall_mole_e_leitura_completa():
    leitura = _ler("folha_paywall_mole")
    assert isinstance(leitura, Leitura)
    assert not leitura.parcial
    assert len(leitura.texto.split()) > 400


def test_texto_cortado_em_800_palavras():
    # Parágrafos distintos: o extrator descarta parágrafo repetido.
    paragrafos = "".join(f"<p>{' '.join(f'p{i}x{j}' for j in range(50))}.</p>" for i in range(30))
    corpo = f"<html><head><title>T</title></head><body><article>{paragrafos}</article></body></html>"
    leitura = ler("https://exemplo.com.br/longo",
                  buscar=_buscar(Pagina(corpo.encode(), "https://exemplo.com.br/longo", "text/html")))
    assert len(leitura.texto.split()) == 800
    assert leitura.cortado


def test_texto_curto_nao_e_cortado():
    assert not _ler("blog_oglobo_completo").cortado


def test_url_buscada_e_a_limpa():
    buscar = _buscar(_gravada("blog_oglobo_completo"))
    ler("https://oglobo.globo.com/x?utm_source=whatsapp&id=1#topo", buscar=buscar)
    assert buscar.pedidos == ["https://oglobo.globo.com/x?id=1"]


# 4.3 leitura parcial e metadados

def test_titulo_e_lead_e_leitura_parcial():
    leitura = _ler("valor_titulo_lead")
    assert isinstance(leitura, Leitura)
    assert leitura.parcial
    assert leitura.texto.startswith(leitura.titulo)


def _html(corpo_artigo="", cabeca="", titulo="Título da matéria de saúde"):
    return (f"<html><head><title>{titulo}</title>{cabeca}</head>"
            f"<body><article>{corpo_artigo}</article></body></html>").encode()


def test_article_body_do_json_ld_completa_a_leitura():
    corpo = " ".join(["palavra"] * 200)
    cabeca = ('<script type="application/ld+json">{"@type": "NewsArticle", '
              f'"headline": "Título", "articleBody": "{corpo}"}}</script>')
    leitura = ler("https://exemplo.com.br/a",
                  buscar=_buscar(Pagina(_html(cabeca=cabeca), "https://exemplo.com.br/a", "text/html")))
    assert isinstance(leitura, Leitura)
    assert not leitura.parcial
    assert corpo in leitura.texto


def test_og_description_vira_leitura_parcial():
    cabeca = ('<meta property="og:description" content="Estudo diz que chá de jatobá '
              'controla a glicose em pessoas com diabetes tipo 2 segundo pesquisadores">')
    leitura = ler("https://exemplo.com.br/a",
                  buscar=_buscar(Pagina(_html(cabeca=cabeca), "https://exemplo.com.br/a", "text/html")))
    assert isinstance(leitura, Leitura)
    assert leitura.parcial
    assert "chá de jatobá" in leitura.texto


def test_fica_com_o_corpo_mais_longo():
    cabeca = ('<meta property="og:description" content="Resumo curto da matéria.">')
    artigo = "<p>" + " ".join(["conteúdo"] * 60) + "</p>"
    leitura = ler("https://exemplo.com.br/a", buscar=_buscar(
        Pagina(_html(artigo, cabeca), "https://exemplo.com.br/a", "text/html")))
    assert leitura.texto.count("conteúdo") == 60


# 4.4 falhas

def test_paywall_sinalizado_sem_texto_e_fechada():
    assert _ler("fechada_sintetica") == Falha("fechada")


def test_rede_social_com_login_e_fechada():
    assert _ler("instagram_login") == Falha("fechada")


def test_pagina_so_js_com_resumo_e_parcial():
    # Excalidraw publica um resumo em og:description: a leitura é parcial, e o
    # pipeline a transforma em `vazia` se não houver alegação de saúde (task 5.4).
    leitura = _ler("excalidraw_so_js")
    assert isinstance(leitura, Leitura) and leitura.parcial


def test_pagina_so_com_titulo_e_vazia():
    html = b"<html><head><title>Carregando</title></head><body><div id='app'></div></body></html>"
    assert ler("https://exemplo.com.br/spa",
               buscar=_buscar(Pagina(html, "https://exemplo.com.br/spa", "text/html"))) == Falha("vazia")


def test_titulo_nao_se_repete_quando_o_corpo_ja_comeca_com_ele():
    artigo = "<h1>Chá de jatobá cura diabetes</h1><p>" + " ".join(["texto"] * 30) + "</p>"
    html = _html(artigo, titulo="Chá de jatobá cura diabetes")
    leitura = ler("https://exemplo.com.br/a",
                  buscar=_buscar(Pagina(html, "https://exemplo.com.br/a", "text/html")))
    assert leitura.texto.count("Chá de jatobá cura diabetes") == 1


@pytest.mark.parametrize("motivo", ["endereco", "status", "tempo", "tamanho", "tipo"])
def test_recusa_da_rede_e_nao_abriu(motivo):
    assert ler("https://exemplo.com.br/x", buscar=_buscar(Recusa(motivo))) == Falha("nao_abriu")


def test_html_ilegivel_e_vazia():
    leitura = ler("https://exemplo.com.br/x",
                  buscar=_buscar(Pagina(b"\x00\x01\x02", "https://exemplo.com.br/x", "text/html")))
    assert leitura == Falha("vazia")


@pytest.mark.parametrize("url, causa", [
    ("https://youtu.be/abc123", "video"),
    ("https://chat.whatsapp.com/AbC", "nao_abriu"),
])
def test_reconhecido_pela_url_nao_chama_buscar(url, causa):
    def buscar(_):
        raise AssertionError("buscar não deveria ser chamado")
    assert ler(url, buscar=buscar) == Falha(causa)


def test_falha_registra_a_url_limpa():
    falha = ler("https://youtu.be/abc?si=xyz", buscar=_buscar(Recusa("x")))
    assert falha.url == "https://youtu.be/abc"


def test_leitura_nao_deixa_url_nem_texto_no_log(caplog):
    caplog.set_level("DEBUG")
    _ler("valor_titulo_lead", url_final="https://segredo.exemplo/noticia")
    _ler("blog_oglobo_completo", url_final="https://segredo.exemplo/blog")
    assert "segredo.exemplo" not in caplog.text
    assert "gravidez" not in caplog.text.lower()
