"""Configuração do chat web, só por variável de ambiente (decisão 2 do design).

`DONA_CHECA_MODO` é obrigatória e não tem padrão: em `piloto`, a pergunta de
confiança some (requirement Modo de execução obrigatório). As demais têm padrão
seguro; `127.0.0.1` evita expor o servidor na rede sem querer.
"""
import os
from dataclasses import dataclass

MODOS = ("uso", "piloto")


class ErroConfig(ValueError):
    pass


@dataclass(frozen=True)
class Config:
    modo: str
    host: str = "127.0.0.1"
    porta: int = 8000
    tempo_max: int = 300

    @property
    def piloto(self):
        return self.modo == "piloto"


def _inteiro_positivo(ambiente, nome, padrao):
    bruto = ambiente.get(nome)
    if bruto is None:
        return padrao
    try:
        valor = int(bruto)
    except ValueError:
        valor = 0
    if valor <= 0:
        raise ErroConfig(f"{nome} precisa ser inteiro positivo; veio {bruto!r}")
    return valor


def carregar(ambiente=os.environ):
    modo = ambiente.get("DONA_CHECA_MODO")
    if modo not in MODOS:
        raise ErroConfig(f"DONA_CHECA_MODO precisa ser um de {' ou '.join(MODOS)}; "
                         f"veio {modo!r}")
    return Config(modo=modo,
                  host=ambiente.get("DONA_CHECA_HOST", "127.0.0.1"),
                  porta=_inteiro_positivo(ambiente, "DONA_CHECA_PORTA", 8000),
                  tempo_max=_inteiro_positivo(ambiente, "DONA_CHECA_TEMPO_MAX", 300))
