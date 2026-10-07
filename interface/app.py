"""Servidor do chat web da Dona Checa (change add-interface-chat-web).

Fábrica `criar_app`: modelo e recuperador entram injetados, para que os testes
troquem os dois e a hospedagem troque o modelo sem mudar a página (decisões 1
e 2 do design). O recuperador carrega uma vez, em segundo plano, e `/saude`
responde 503 até a carga terminar (decisão 6).

`POST /verificar` responde em streaming, um evento JSON por linha `data:`. O
texto vai no corpo, nunca na URL (decisão 3). Uma verificação por vez, com
tempo máximo; passado o tempo, a página recebe `erro` e a thread termina
sozinha, segurando a vez até acabar (decisão 5). Mensagem que é só link recebe
o aviso `so_link` sem chamar o fluxo (decisão 10).
"""
import asyncio
import json
import logging
import pathlib
import re
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from interface import fluxo
from prototipo import identidade
from prototipo.verificacao.modelo import chat_ollama

ESTATICO = pathlib.Path(__file__).parent / "estatico"
SO_LINK = re.compile(r"https?://\S+")
FIM = object()

log = logging.getLogger("dona_checa")


class Pedido(BaseModel):
    texto: str

    @field_validator("texto")
    @classmethod
    def nao_vazio(cls, valor):
        if not valor.strip():
            raise ValueError("mensagem vazia")
        return valor


def _sse(evento):
    return f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"


def _pagina(config, textos):
    """index.html com textos e modo injetados (decisão 7). O modo vem só do servidor."""
    persona = identidade.textos()
    dados = {
        "modo": config.modo,
        "textos": {"abertura": persona["abertura"], "chamada": persona["chamada"],
                   "bordao": identidade.textos("resposta-formativa")["bordao"],
                   "lendo": textos["lendo"], "erro": textos["erro"]},
        "pergunta": identidade.pergunta_confianca(piloto=config.piloto),
    }
    bruto = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    rodape = ('<footer class="modo-piloto"><p>modo piloto</p></footer>'
              if config.piloto else "")
    html = (ESTATICO / "index.html").read_text(encoding="utf-8")
    return html.replace("<!--CONFIG-->", bruto).replace("<!--RODAPE-->", rodape)


def _carregar_recuperador_real():
    from prototipo.rag.__main__ import carregar
    return carregar()


def criar_app(config, *, carregar_recuperador=_carregar_recuperador_real, chat=chat_ollama,
              verificar=fluxo.verificar):
    estado = {"recuperador": None}
    vez = threading.Semaphore(1)
    textos = fluxo.textos()
    erro = {"tipo": "erro", "texto": textos["erro"]}
    pagina_html = _pagina(config, textos)

    def carregar():
        estado["recuperador"] = carregar_recuperador()

    @asynccontextmanager
    async def ciclo(app):
        threading.Thread(target=carregar, daemon=True).start()
        yield

    app = FastAPI(title="Dona Checa", lifespan=ciclo, docs_url=None, redoc_url=None,
                  openapi_url=None)
    app.state.config = config
    app.state.estado = estado

    @app.get("/")
    def pagina():
        return HTMLResponse(pagina_html, headers={"Cache-Control": "no-store"})

    @app.get("/saude")
    def saude():
        pronto = estado["recuperador"] is not None
        return JSONResponse({"pronto": pronto}, status_code=200 if pronto else 503)

    async def eventos(texto):
        if SO_LINK.fullmatch(texto.strip()):
            yield _sse({"tipo": "aviso", "chave": "so_link", "texto": textos["so_link"]})
            return
        recuperador = estado["recuperador"]
        if recuperador is None:
            yield _sse(erro)
            return
        loop = asyncio.get_running_loop()
        prazo = loop.time() + config.tempo_max
        if not await asyncio.to_thread(vez.acquire, True, config.tempo_max):
            log.error("verificação esperou a vez além do tempo máximo")
            yield _sse(erro)
            return
        fila = asyncio.Queue()

        def entregar(evento):
            try:
                loop.call_soon_threadsafe(fila.put_nowait, evento)
            except RuntimeError:  # a página já recebeu o erro por tempo e o laço fechou
                pass

        def rodar():
            try:
                verificar(texto, entregar, recuperador=recuperador, chat=chat)
            except Exception as e:  # nada do texto vai ao log
                log.error("verificação falhou: %s", type(e).__name__)
                entregar(erro)
            finally:
                vez.release()
                entregar(FIM)

        threading.Thread(target=rodar, daemon=True).start()
        while True:
            try:
                evento = await asyncio.wait_for(fila.get(), max(prazo - loop.time(), 0))
            except asyncio.TimeoutError:
                log.error("verificação passou do tempo máximo de %s s", config.tempo_max)
                yield _sse(erro)
                return
            if evento is FIM:
                return
            yield _sse(evento)

    @app.post("/verificar")
    async def verificar_rota(pedido: Pedido):
        return StreamingResponse(eventos(pedido.texto), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache"})

    app.mount("/estatico", StaticFiles(directory=ESTATICO), name="estatico")
    return app
