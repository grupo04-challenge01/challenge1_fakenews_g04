"""Busca de página com bloqueios contra acesso à rede interna (decisão D4).

A checagem do endereço vale para o endereço efetivamente conectado: o backend
de rede resolve o nome, recusa se algum endereço não for público e conecta no
próprio endereço validado. Assim um nome que muda de resposta entre a checagem
e a conexão (DNS rebinding) não alcança a rede interna. TLS continua usando o
nome original para SNI e certificado.

Recusa por qualquer regra levanta `Recusa`; `leitura` a traduz em `nao_abriu`.
Nada é gravado em disco: cliente novo por busca, sem cookie, sem cache.
"""
import ipaddress
import logging
import socket
import time
import zlib
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

import httpcore
import httpx

from prototipo.entrada.link import limpar

# O httpx registra cada URL pedida em INFO. A URL é da pessoa e não vai ao log
# do servidor (requirement Busca sem rastro da pessoa).
for _nome in ("httpx", "httpcore"):
    logging.getLogger(_nome).setLevel(logging.WARNING)

AGENTE = "DonaChecaBot/0.1 (+https://github.com/grupo04-challenge01/challenge1_fakenews_g04)"
PORTAS = (None, 80, 443)
MAX_SALTOS = 5
PRAZO_TOTAL = 10.0
PRAZO_CONEXAO = 5.0
LIMITE_BYTES = 2 * 1024 * 1024
TIPOS_HTML = ("text/html", "application/xhtml+xml")
# Só codificações que sabemos descomprimir com teto de tamanho.
_DESCOMPRESSAO = {"gzip": 31, "x-gzip": 31, "deflate": 15}


class Recusa(Exception):
    """A página não foi buscada ou lida; `motivo` vai para o rastro, nunca para a pessoa."""

    def __init__(self, motivo):
        super().__init__(motivo)
        self.motivo = motivo


@dataclass(frozen=True)
class Pagina:
    corpo: bytes
    url_final: str
    tipo: str


def publico(endereco):
    """True só para endereço roteável na internet; IPv6 que embute IPv4 é julgado pelo IPv4."""
    ip = ipaddress.ip_address(endereco.split("%", 1)[0])
    if ip.version == 6:
        if ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        elif ip.sixtofour:
            ip = ip.sixtofour
        elif ip.teredo:
            return False
    return ip.is_global and not ip.is_multicast


def _resolver(host, port):
    return [info[4][0] for info in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)]


class BackendSeguro(httpcore.NetworkBackend):
    """Backend do httpcore que só conecta em endereço público já validado."""

    def __init__(self, resolver=_resolver, interno=None):
        self._resolver = resolver
        self._interno = interno or httpcore.SyncBackend()

    def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        try:
            enderecos = self._resolver(host, port)
        except OSError as e:
            raise Recusa("dns") from e
        if not enderecos or not all(publico(e) for e in enderecos):
            raise Recusa("endereco")
        return self._interno.connect_tcp(enderecos[0], port, timeout=timeout,
                                         local_address=local_address,
                                         socket_options=socket_options)

    def connect_unix_socket(self, path, timeout=None, socket_options=None):
        raise Recusa("endereco")

    def sleep(self, seconds):
        time.sleep(seconds)


def transporte_seguro():
    """Transporte do httpx com o `BackendSeguro` no lugar da conexão padrão."""
    transporte = httpx.HTTPTransport(retries=0)
    # httpx não expõe o backend de rede; o pool é trocado por um igual com o nosso.
    transporte._pool = httpcore.ConnectionPool(ssl_context=httpx.create_ssl_context(),
                                               network_backend=BackendSeguro())
    return transporte


def validar_url(url):
    """Recusa esquema, porta, credencial ou IP literal fora das regras de D4."""
    partes = urlsplit(url)
    if partes.scheme.lower() not in ("http", "https") or not partes.hostname:
        raise Recusa("url")
    if "@" in partes.netloc:
        raise Recusa("url")
    try:
        porta = partes.port
    except ValueError as e:
        raise Recusa("url") from e
    if porta not in PORTAS:
        raise Recusa("url")
    try:
        literal = ipaddress.ip_address(partes.hostname)
    except ValueError:
        return
    if not publico(str(literal)):
        raise Recusa("endereco")


def _ler_corpo(resposta, inicio, relogio):
    """Corpo descomprimido, parando acima de `LIMITE_BYTES` sem descomprimir o resto."""
    codificacao = resposta.headers.get("content-encoding", "identity").strip().lower()
    if codificacao not in ("identity", "", *_DESCOMPRESSAO):
        raise Recusa("codificacao")
    descomp = (zlib.decompressobj(_DESCOMPRESSAO[codificacao])
               if codificacao in _DESCOMPRESSAO else None)
    corpo, bruto = bytearray(), 0
    for parte in resposta.iter_raw():
        bruto += len(parte)
        if descomp:
            parte = descomp.decompress(parte, LIMITE_BYTES + 1 - len(corpo))
        corpo += parte
        if bruto > LIMITE_BYTES or len(corpo) > LIMITE_BYTES:
            raise Recusa("tamanho")
        if relogio() - inicio > PRAZO_TOTAL:
            raise Recusa("tempo")
    if descomp:
        corpo += descomp.flush()
        if len(corpo) > LIMITE_BYTES:
            raise Recusa("tamanho")
    return bytes(corpo)


def buscar(url, *, transporte=None, relogio=time.monotonic):
    """Página HTML da URL limpa, seguindo até `MAX_SALTOS` redirecionamentos validados."""
    inicio = relogio()
    atual = limpar(url)
    cabecalhos = {"user-agent": AGENTE, "accept": "text/html,application/xhtml+xml",
                  "accept-encoding": "gzip, deflate"}
    with httpx.Client(transport=transporte or transporte_seguro(), follow_redirects=False,
                      trust_env=False, headers=cabecalhos) as cliente:
        for _ in range(MAX_SALTOS + 1):
            validar_url(atual)
            restante = PRAZO_TOTAL - (relogio() - inicio)
            if restante <= 0:
                raise Recusa("tempo")
            cliente.cookies.clear()
            prazo = httpx.Timeout(restante, connect=min(PRAZO_CONEXAO, restante))
            try:
                with cliente.stream("GET", atual, timeout=prazo) as resposta:
                    if resposta.is_redirect:
                        destino = resposta.headers.get("location")
                        if not destino:
                            raise Recusa("redirecionamento")
                        atual = limpar(urljoin(atual, destino))
                        continue
                    if resposta.status_code != 200:
                        raise Recusa("status")
                    tipo = resposta.headers.get("content-type", "")
                    if tipo.split(";", 1)[0].strip().lower() not in TIPOS_HTML:
                        raise Recusa("tipo")
                    return Pagina(_ler_corpo(resposta, inicio, relogio), atual, tipo)
            except (httpx.HTTPError, httpx.InvalidURL) as e:
                raise Recusa("rede") from e
    raise Recusa("saltos")
