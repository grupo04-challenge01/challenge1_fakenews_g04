"""Sobe o chat web: `DONA_CHECA_MODO=uso python -m interface`.

Sem `DONA_CHECA_MODO` válido o processo termina com erro antes de carregar
qualquer coisa (requirement Modo de execução obrigatório). O log da interface
registra etapa, tipo de erro e tempo, nunca o texto da pessoa. O gerador sai
de `DONA_CHECA_GERADOR` (add-gerador-api-deepseek, D3).
"""
import logging
import sys

from interface.config import ErroConfig, carregar


MARCADORES = ("CONTATO_DO_GRUPO",)


def pendencias_do_termo(config, textos):
    """Marcadores ainda no termo; com gerador remoto, impedem o servidor de subir (D8)."""
    if config.gerador != "deepseek":
        return []
    return [m for m in MARCADORES if m in textos["termo-servico-externo"]]


def escolher_chat(config):
    from prototipo.verificacao.modelo import ChatDeepSeek, chat_ollama
    if config.gerador == "deepseek":
        return ChatDeepSeek(chave=config.chave, modelo=config.modelo_remoto)
    return chat_ollama


def main():
    try:
        config = carregar()
    except ErroConfig as e:
        sys.exit(f"Dona Checa não subiu: {e}")
    from interface.fluxo import textos
    pendentes = pendencias_do_termo(config, textos())
    if pendentes:
        sys.exit(f"Dona Checa não subiu: preencha {', '.join(pendentes)} no termo de "
                 "consentimento (spec interface-chat-web de add-gerador-api-deepseek)")
    import uvicorn

    from interface.app import criar_app
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    print(f"Dona Checa em modo {config.modo}, gerador {config.gerador}: "
          f"http://{config.host}:{config.porta}"
          f"{'  (aberto na rede local)' if config.host == '0.0.0.0' else ''}", flush=True)
    uvicorn.run(criar_app(config, chat=escolher_chat(config)), host=config.host, port=config.porta)


if __name__ == "__main__":
    main()
