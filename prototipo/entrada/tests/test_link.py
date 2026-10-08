"""Tasks 2.1 a 2.3 de add-entrada-por-link: separar, limpar e reconhecer link.

Só parsing de texto e URL; nenhum teste acessa a rede.
"""
import pytest

from prototipo.entrada.link import classificar_antes, limpar, separar


# 2.1 separar

def test_texto_sem_url_fica_inteiro():
    assert separar("chá de jatobá cura diabetes") == ("chá de jatobá cura diabetes", [])


def test_mensagem_so_com_link():
    assert separar("  https://exemplo.com.br/noticia  ") == ("", ["https://exemplo.com.br/noticia"])


def test_duas_urls_preservam_a_ordem():
    texto, urls = separar("https://a.com/1 e http://b.com/2")
    assert urls == ["https://a.com/1", "http://b.com/2"]
    assert texto == "e"


def test_pontuacao_colada_nao_entra_na_url():
    texto, urls = separar("Veja (https://exemplo.com.br/noticia). Ou https://b.com/x, https://c.com/y!")
    assert urls == ["https://exemplo.com.br/noticia", "https://b.com/x", "https://c.com/y"]


def test_parenteses_da_propria_url_ficam():
    _, urls = separar("ver https://pt.wikipedia.org/wiki/Dengue_(doença) agora")
    assert urls == ["https://pt.wikipedia.org/wiki/Dengue_(doença)"]


def test_url_no_meio_do_texto_sai_e_o_resto_fica():
    texto, urls = separar("Olha isso, minha tia mandou: https://blog.exemplo/cura e disse que funciona")
    assert urls == ["https://blog.exemplo/cura"]
    assert texto == "Olha isso, minha tia mandou: e disse que funciona"


def test_so_http_e_https_contam_como_link():
    assert separar("ftp://a.com/x www.b.com") == ("ftp://a.com/x www.b.com", [])


# 2.2 limpar

@pytest.mark.parametrize("param", [
    "utm_source", "utm_medium", "utm_campaign", "utm_whatever", "fbclid", "gclid", "dclid",
    "gbraid", "wbraid", "msclkid", "igshid", "mc_cid", "mc_eid", "_hsenc", "_hsmi",
    "ref_src", "si",
])
def test_remove_parametro_de_rastreio(param):
    assert limpar(f"https://exemplo.com.br/n?id=7&{param}=abc") == "https://exemplo.com.br/n?id=7"


def test_mantem_parametros_legitimos_na_ordem():
    url = "https://exemplo.com.br/n?b=2&utm_source=whatsapp&a=1&fbclid=x"
    assert limpar(url) == "https://exemplo.com.br/n?b=2&a=1"


def test_remove_fragmento():
    assert limpar("https://exemplo.com.br/n?id=7#comentarios") == "https://exemplo.com.br/n?id=7"


def test_sem_query_sobra_sem_interrogacao():
    assert limpar("https://exemplo.com.br/n?utm_source=x") == "https://exemplo.com.br/n"


# 2.3 classificar_antes

@pytest.mark.parametrize("url", [
    "https://www.youtube.com/watch?v=abc", "https://youtube.com/shorts/abc",
    "https://m.youtube.com/watch?v=abc", "https://youtu.be/abc123",
    "https://www.tiktok.com/@x/video/1", "https://vm.tiktok.com/ZM123/",
    "https://www.kwai.com/@x/video/1", "https://vimeo.com/123",
    "https://www.instagram.com/reel/abc/", "https://instagram.com/reels/abc/",
    "https://www.facebook.com/reel/123",
])
def test_video_reconhecido_sem_buscar(url):
    assert classificar_antes(url) == "video"


@pytest.mark.parametrize("url", [
    "https://chat.whatsapp.com/AbCdEf", "https://wa.me/5561999999999",
    "https://api.whatsapp.com/send?phone=1",
])
def test_link_de_whatsapp_nao_abre(url):
    assert classificar_antes(url) == "nao_abriu"


@pytest.mark.parametrize("url", [
    "https://g1.globo.com/saude/noticia/x.ghtml", "https://www.instagram.com/p/abc/",
    "https://notyoutube.com/watch", "https://youtube.com.golpe.net/x",
])
def test_outros_links_seguem_para_busca(url):
    assert classificar_antes(url) is None
