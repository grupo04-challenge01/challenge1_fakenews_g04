"""Separar link de texto, limpar rastreio e reconhecer link que não se busca.

Decisão D5 de add-entrada-por-link. Só stdlib, sem rede.
"""
import re
from urllib.parse import urlsplit, urlunsplit

_URL = re.compile(r"https?://\S+", re.IGNORECASE)
_PONTUACAO_FINAL = ".,;:!?\"'»”’]}"

# Parâmetros de rastreio removidos antes da busca (D5). Além destes, todo `utm_*`.
RASTREIO = frozenset({"fbclid", "gclid", "dclid", "gbraid", "wbraid", "msclkid", "igshid",
                      "mc_cid", "mc_eid", "_hsenc", "_hsmi", "ref_src", "si"})

# Plataformas de vídeo: a falha `video` sai sem buscar a página.
HOSTS_VIDEO = ("youtube.com", "youtu.be", "tiktok.com", "kwai.com", "vimeo.com")
HOSTS_REEL = ("instagram.com", "facebook.com")
# Redes que exigem login: leitura não completa vira `fechada` (D5).
HOSTS_LOGIN = ("instagram.com", "facebook.com", "x.com", "twitter.com", "threads.com",
               "threads.net")
# Grupo ou conversa de WhatsApp: não há o que ler.
HOSTS_WHATSAPP = ("chat.whatsapp.com", "wa.me", "api.whatsapp.com")


def _aparar(url):
    """Tira pontuação de frase colada ao fim da URL, mantendo parênteses da própria URL."""
    while url:
        fim = url[-1]
        if fim in _PONTUACAO_FINAL:
            url = url[:-1]
        elif fim == ")" and url.count(")") > url.count("("):
            url = url[:-1]
        else:
            break
    return url


def separar(mensagem):
    """(texto da pessoa sem as URLs, URLs http/https na ordem em que aparecem)."""
    urls = []

    def tirar(m):
        url = _aparar(m.group(0))
        urls.append(url)
        return m.group(0)[len(url):]

    texto = _URL.sub(tirar, mensagem)
    return " ".join(texto.split()), urls


def _rastreio(par):
    nome = par.split("=", 1)[0].lower()
    return nome.startswith("utm_") or nome in RASTREIO


def limpar(url):
    """URL sem parâmetros de rastreio e sem fragmento; demais parâmetros na ordem original."""
    partes = urlsplit(url)
    query = "&".join(p for p in partes.query.split("&") if p and not _rastreio(p))
    return urlunsplit((partes.scheme, partes.netloc, partes.path, query, ""))


def no_host(url, dominios):
    """True se o host da URL é um dos domínios ou subdomínio deles."""
    return _no_host((urlsplit(url).hostname or "").lower(), dominios)


def _no_host(host, dominios):
    return any(host == d or host.endswith("." + d) for d in dominios)


def classificar_antes(url):
    """Causa de falha reconhecível só pela URL (`video`, `nao_abriu`), ou None para buscar."""
    partes = urlsplit(url)
    host = (partes.hostname or "").lower()
    if _no_host(host, HOSTS_VIDEO):
        return "video"
    if _no_host(host, HOSTS_REEL) and partes.path.split("/")[1:2] in (["reel"], ["reels"]):
        return "video"
    if _no_host(host, HOSTS_WHATSAPP):
        return "nao_abriu"
    return None
