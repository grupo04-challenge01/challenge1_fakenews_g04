"""Tasks 3.1 a 3.5 de add-entrada-por-link: busca com bloqueios (decisão D4).

Nenhum teste abre socket: o resolvedor e a conexão são falsos, e as respostas
HTTP vêm de `httpx.MockTransport`.
"""
import gzip

import httpx
import pytest

from prototipo.entrada import rede
from prototipo.entrada.rede import BackendSeguro, Recusa, buscar

HTML = "text/html; charset=utf-8"


def _transporte(rotas, pedidos=None):
    """MockTransport que responde por URL; `rotas[url]` é Response ou função."""
    def responder(request):
        if pedidos is not None:
            pedidos.append(request)
        r = rotas[str(request.url)]
        return r(request) if callable(r) else r
    return httpx.MockTransport(responder)


def _resposta(status=200, corpo=b"", **cabecalhos):
    """Fábrica de resposta com corpo em stream, como a de um servidor real."""
    def fazer(request):
        return httpx.Response(status, headers=cabecalhos, content=iter([corpo]))
    return fazer


def _pagina(corpo="<html><body>ok</body></html>", tipo=HTML):
    return _resposta(corpo=corpo.encode(), **{"content-type": tipo})


def _redireciona(para, status=302):
    return httpx.Response(status, headers={"location": para})


# 3.1 regras de URL

@pytest.mark.parametrize("url", [
    "ftp://exemplo.com.br/x", "file:///etc/passwd", "https://exemplo.com.br:8080/x",
    "http://exemplo.com.br:22/", "https://user:senha@exemplo.com.br/", "https://@exemplo.com.br/",
    "javascript:alert(1)", "https:///sem-host",
])
def test_url_fora_das_regras_recusada_sem_requisicao(url):
    pedidos = []
    with pytest.raises(Recusa):
        buscar(url, transporte=_transporte({}, pedidos))
    assert pedidos == []


@pytest.mark.parametrize("url", [
    "http://192.168.0.1/admin", "http://127.0.0.1/", "http://169.254.169.254/latest/meta-data",
    "http://[::1]/", "http://[::ffff:127.0.0.1]/", "http://10.0.0.1/", "http://0.0.0.0/",
])
def test_ip_literal_nao_publico_recusado_sem_requisicao(url):
    pedidos = []
    with pytest.raises(Recusa):
        buscar(url, transporte=_transporte({}, pedidos))
    assert pedidos == []


def test_portas_padrao_aceitas():
    rotas = {"https://exemplo.com.br/a": _pagina(), "http://exemplo.com.br/b": _pagina()}
    assert buscar("https://exemplo.com.br:443/a", transporte=_transporte(rotas)).corpo
    assert buscar("http://exemplo.com.br:80/b", transporte=_transporte(rotas)).corpo


# 3.2 conexão só a endereço público

class _Conexoes:
    """Backend interno falso: registra para onde se tentou conectar."""
    def __init__(self):
        self.destinos = []

    def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        self.destinos.append((host, port))
        return object()


def _resolvedor(*respostas):
    chamadas = []

    def resolver(host, port):
        chamadas.append(host)
        return respostas[min(len(chamadas), len(respostas)) - 1]
    resolver.chamadas = chamadas
    return resolver


@pytest.mark.parametrize("enderecos", [
    ["127.0.0.1"], ["10.0.0.1"], ["192.168.0.1"], ["169.254.169.254"], ["::1"],
    ["::ffff:127.0.0.1"], ["fc00::1"], ["2002:7f00:1::1"], ["224.0.0.1"], ["0.0.0.0"],
    ["8.8.8.8", "192.168.0.1"],
])
def test_backend_recusa_endereco_nao_publico(enderecos):
    conexoes = _Conexoes()
    backend = BackendSeguro(resolver=_resolvedor(enderecos), interno=conexoes)
    with pytest.raises(Recusa):
        backend.connect_tcp("golpe.exemplo", 443)
    assert conexoes.destinos == []


def test_backend_conecta_no_endereco_validado():
    conexoes = _Conexoes()
    backend = BackendSeguro(resolver=_resolvedor(["93.184.216.34"]), interno=conexoes)
    backend.connect_tcp("exemplo.com", 443)
    assert conexoes.destinos == [("93.184.216.34", 443)]


def test_transporte_padrao_usa_o_backend_seguro():
    transporte = rede.transporte_seguro()
    assert isinstance(transporte._pool._network_backend, BackendSeguro)


# 3.3 DNS rebinding

def test_rebinding_conecta_no_endereco_da_checagem():
    resolver = _resolvedor(["93.184.216.34"], ["127.0.0.1"])
    conexoes = _Conexoes()
    BackendSeguro(resolver=resolver, interno=conexoes).connect_tcp("rebind.exemplo", 80)
    assert resolver.chamadas == ["rebind.exemplo"]
    assert conexoes.destinos == [("93.184.216.34", 80)]


# 3.4 redirecionamentos

def test_dois_saltos_registram_a_url_final():
    rotas = {
        "https://bit.ly/abc": _redireciona("https://encurtador.com.br/x?utm_source=zap"),
        "https://encurtador.com.br/x": _redireciona("/noticia#topo", status=301),
        "https://encurtador.com.br/noticia": _pagina(),
    }
    pagina = buscar("https://bit.ly/abc", transporte=_transporte(rotas))
    assert pagina.url_final == "https://encurtador.com.br/noticia"


def test_salto_para_endereco_interno_nao_e_seguido():
    pedidos = []
    rotas = {"https://bit.ly/x": _redireciona("http://169.254.169.254/")}
    with pytest.raises(Recusa):
        buscar("https://bit.ly/x", transporte=_transporte(rotas, pedidos))
    assert [str(p.url) for p in pedidos] == ["https://bit.ly/x"]


def test_cinco_saltos_aceitos_seis_recusados():
    rotas = {f"https://r.com/{i}": _redireciona(f"https://r.com/{i + 1}") for i in range(6)}
    rotas["https://r.com/5"] = _pagina()
    assert buscar("https://r.com/0", transporte=_transporte(rotas)).url_final == "https://r.com/5"
    rotas["https://r.com/5"] = _redireciona("https://r.com/6")
    rotas["https://r.com/6"] = _pagina()
    with pytest.raises(Recusa):
        buscar("https://r.com/0", transporte=_transporte(rotas))


def test_redirecionamento_sem_location_recusado():
    with pytest.raises(Recusa):
        buscar("https://r.com/0", transporte=_transporte({"https://r.com/0": httpx.Response(302)}))


# 3.5 limites, identificação e ausência de cookie

def test_corpo_acima_de_2mb_recusado():
    grande = "<p>" + "a" * (2 * 1024 * 1024) + "</p>"
    with pytest.raises(Recusa):
        buscar("https://g.com/", transporte=_transporte({"https://g.com/": _pagina(grande)}))


def test_corpo_ate_2mb_aceito():
    corpo = "a" * (2 * 1024 * 1024)
    pagina = buscar("https://g.com/", transporte=_transporte({"https://g.com/": _pagina(corpo)}))
    assert len(pagina.corpo) == 2 * 1024 * 1024


def test_bomba_gzip_para_em_2mb_descomprimidos():
    bomba = gzip.compress(b"a" * (50 * 1024 * 1024))
    assert len(bomba) < 100 * 1024
    resposta = _resposta(corpo=bomba, **{"content-type": HTML, "content-encoding": "gzip"})
    with pytest.raises(Recusa):
        buscar("https://b.com/", transporte=_transporte({"https://b.com/": resposta}))


@pytest.mark.parametrize("tipo", ["application/pdf", "image/png", "application/json", ""])
def test_tipo_nao_html_recusado(tipo):
    with pytest.raises(Recusa):
        buscar("https://p.com/", transporte=_transporte({"https://p.com/": _pagina(tipo=tipo)}))


def test_xhtml_aceito():
    rotas = {"https://p.com/": _pagina(tipo="application/xhtml+xml")}
    assert buscar("https://p.com/", transporte=_transporte(rotas)).corpo


@pytest.mark.parametrize("status", [404, 500, 503])
def test_erro_do_site_recusado(status):
    rotas = {"https://p.com/": _resposta(status, **{"content-type": HTML})}
    with pytest.raises(Recusa):
        buscar("https://p.com/", transporte=_transporte(rotas))


def test_tempo_esgotado_vira_recusa():
    def lento(request):
        raise httpx.ReadTimeout("lento", request=request)
    with pytest.raises(Recusa):
        buscar("https://p.com/", transporte=_transporte({"https://p.com/": lento}))


def test_prazo_total_conta_entre_saltos():
    instantes = iter([0, 4, 8, 12, 16])
    rotas = {f"https://r.com/{i}": _redireciona(f"https://r.com/{i + 1}") for i in range(4)}
    rotas["https://r.com/4"] = _pagina()
    with pytest.raises(Recusa):
        buscar("https://r.com/0", transporte=_transporte(rotas), relogio=lambda: next(instantes))


def test_agente_honesto_e_nenhum_cookie_enviado():
    pedidos = []
    rotas = {
        "https://c.com/1": httpx.Response(302, headers={"location": "https://c.com/2",
                                                        "set-cookie": "sessao=abc; Path=/"}),
        "https://c.com/2": _pagina(),
    }
    buscar("https://c.com/1", transporte=_transporte(rotas, pedidos))
    for p in pedidos:
        assert p.headers["user-agent"].startswith("DonaChecaBot/")
        assert "cookie" not in p.headers
        assert "authorization" not in p.headers


def test_busca_nao_deixa_a_url_no_log(caplog):
    caplog.set_level("DEBUG")
    rotas = {"https://segredo.exemplo/noticia": _pagina()}
    buscar("https://segredo.exemplo/noticia", transporte=_transporte(rotas))
    assert "segredo.exemplo" not in caplog.text
