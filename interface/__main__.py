"""Sobe o chat web: `DONA_CHECA_MODO=uso python -m interface`.

Sem `DONA_CHECA_MODO` válido o processo termina com erro antes de carregar
qualquer coisa (requirement Modo de execução obrigatório). O log da interface
registra etapa, tipo de erro e tempo, nunca o texto da pessoa.
"""
import logging
import sys

from interface.config import ErroConfig, carregar


def main():
    try:
        config = carregar()
    except ErroConfig as e:
        sys.exit(f"Dona Checa não subiu: {e}")
    import uvicorn

    from interface.app import criar_app
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    print(f"Dona Checa em modo {config.modo}: http://{config.host}:{config.porta}"
          f"{'  (aberto na rede local)' if config.host == '0.0.0.0' else ''}", flush=True)
    uvicorn.run(criar_app(config), host=config.host, port=config.porta)


if __name__ == "__main__":
    main()
