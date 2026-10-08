"""Servidor de verdade (uvicorn numa thread) com fluxo falso, para o Playwright.

Task 5.1 de add-interface-chat-web. O fluxo falso escolhe o cenário pelo texto
da mensagem, para que cada teste dirija a página só pelo que digita.
"""
import socket
import threading
import time

import pytest
import uvicorn

from interface import fluxo
from interface.app import criar_app
from interface.config import Config
from prototipo.entrada.leitura import AVISO_PARCIAL
from prototipo.resposta.estrutura import BORDAO
from prototipo.verificacao.fronteira import carregar_respostas

PASSO = 0.12  # segundos entre eventos de andamento, para a pergunta ter tempo de aparecer

RESPOSTA = "\n\n".join([
    BORDAO,
    "VEREDITO: Falso. Nenhum estudo mostra que a casca do jatobá cura câncer.",
    "O QUE SE SABE: As checagens não acharam estudo sobre o jatobá e o câncer.",
    "POR QUE ESSA MENSAGEM ENGANA: Técnica: cura milagrosa. Promete curar doença grave "
    "com algo caseiro.",
    "O QUE OBSERVAR DA PRÓXIMA VEZ: Desconfie de promessa de cura simples."])

DETALHE = [
    {"agencia": "Aos Fatos", "data_publicacao": "2021-01-08", "url": "https://www.aosfatos.org/x",
     "veredito_original": "falso",
     "trecho": "Não há estudo que mostre que o jatobá cure câncer."},
    {"agencia": "Lupa", "data_publicacao": "2020-11-03", "url": "https://lupa.uol.com.br/y",
     "veredito_original": "falso", "trecho": None},
]


ORIGEM = {"titulo": "Chá de jatobá cura câncer", "veiculo": "Blog Exemplo",
          "data": "2026-09-20", "url": "https://blog.exemplo/cura"}


def verificar_falso(texto, emitir, *, recuperador, chat):
    t = fluxo.textos()
    padrao = carregar_respostas()
    if "peito" in texto:
        emitir({"tipo": "fronteira", "desfecho": "urgencia",
                "texto": padrao["risco_imediato"]["web"]})
        return
    if "acabar com tudo" in texto:
        emitir({"tipo": "fronteira", "desfecho": "sofrimento",
                "texto": padrao["sofrimento_psiquico"]["web"]})
        return
    if "remédio de pressão amanhã" in texto:  # conduta sem alegação (fix-pergunta-e-conduta)
        emitir({"tipo": "fronteira", "desfecho": "conduta", "texto": None})
        emitir({"tipo": "aviso", "chave": "conduta",
                "texto": padrao["conduta_individual"]["web"]})
        return
    conduta = "parar meu remédio" in texto
    emitir({"tipo": "fronteira", "desfecho": "conduta" if conduta else "segue", "texto": None})
    if "futebol" in texto:
        emitir({"tipo": "aviso", "chave": "sem_alegacao", "texto": t["sem_alegacao"]})
        return
    if "youtu.be" in texto:
        emitir({"tipo": "andamento", "etapa": "leitura", "frase": t["andamento"]["leitura"]})
        emitir({"tipo": "aviso", "chave": "video", "texto": t["video"]})
        return
    if "blog.exemplo" in texto:
        emitir({"tipo": "andamento", "etapa": "leitura", "frase": t["andamento"]["leitura"]})
        time.sleep(PASSO * 5)  # tempo para a página mostrar "Abrindo o link…"
        partes = RESPOSTA.split("\n\n")
        if "parcial" in texto:
            partes.insert(1, AVISO_PARCIAL)
        emitir({"tipo": "resposta", "forma": "com evidência", "texto": "\n\n".join(partes),
                "detalhe": DETALHE, "redirecionamentos": [], "origem": ORIGEM})
        return
    if "quebra" in texto:
        emitir({"tipo": "erro", "texto": t["erro"]})
        return
    for etapa, frase in t["andamento"].items():
        time.sleep(PASSO)
        emitir({"tipo": "andamento", "etapa": etapa, "frase": frase})
    emitir({"tipo": "resposta", "forma": "com evidência", "texto": RESPOSTA, "detalhe": DETALHE,
            "redirecionamentos": [padrao["conduta_individual"]["web"]] if conduta else [],
            "origem": None})


def _porta_livre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _subir(modo, **extra):
    porta = _porta_livre()
    app = criar_app(Config(modo=modo, porta=porta, **extra), carregar_recuperador=object,
                    verificar=verificar_falso)
    servidor = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=porta,
                                             log_level="warning"))
    threading.Thread(target=servidor.run, daemon=True).start()
    for _ in range(200):
        if servidor.started:
            break
        time.sleep(0.02)
    time.sleep(0.1)  # o recuperador falso carrega numa thread própria
    return servidor, f"http://127.0.0.1:{porta}"


@pytest.fixture(scope="session")
def servidor_uso():
    servidor, url = _subir("uso")
    yield url
    servidor.should_exit = True


@pytest.fixture(scope="session")
def servidor_piloto():
    servidor, url = _subir("piloto")
    yield url
    servidor.should_exit = True


@pytest.fixture(scope="session")
def servidor_deepseek():
    """Gerador remoto só muda a página pelo aviso; o fluxo continua falso, sem rede."""
    servidor, url = _subir("uso", gerador="deepseek", chave="sk-teste")
    yield url
    servidor.should_exit = True


@pytest.fixture(scope="session")
def servidor_deepseek_local():
    """Gerador remoto com alternativa local para quem recusa o termo (D8)."""
    servidor, url = _subir("uso", gerador="deepseek", chave="sk-teste", alternativa_local=True)
    yield url
    servidor.should_exit = True
