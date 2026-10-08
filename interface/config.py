"""Configuração do chat web, só por variável de ambiente (decisão 2 do design).

`DONA_CHECA_MODO` é obrigatória e não tem padrão: em `piloto`, a pergunta de
confiança some (requirement Modo de execução obrigatório). As demais têm padrão
seguro; `127.0.0.1` evita expor o servidor na rede sem querer.

`DONA_CHECA_GERADOR` escolhe o modelo (add-gerador-api-deepseek, D3): padrão
`deepseek` em `uso` e `ollama` em `piloto`. Com `deepseek`, `DEEPSEEK_API_KEY`
é obrigatória e fica fora do `repr`, para não vazar em log nem em erro (D4).
"""
import os
from dataclasses import dataclass, field

MODOS = ("uso", "piloto")
GERADORES = ("deepseek", "ollama")
GERADOR_PADRAO = {"uso": "deepseek", "piloto": "ollama"}
MODELO_REMOTO = "deepseek-v4-pro"


class ErroConfig(ValueError):
    pass


@dataclass(frozen=True)
class Config:
    modo: str
    host: str = "127.0.0.1"
    porta: int = 8000
    tempo_max: int = 300
    gerador: str = "ollama"
    chave: str | None = field(default=None, repr=False)
    modelo_remoto: str = MODELO_REMOTO
    alternativa_local: bool = False

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
    gerador = ambiente.get("DONA_CHECA_GERADOR", GERADOR_PADRAO[modo])
    if gerador not in GERADORES:
        raise ErroConfig(f"DONA_CHECA_GERADOR precisa ser um de {' ou '.join(GERADORES)}; "
                         f"veio {gerador!r}")
    chave = (ambiente.get("DEEPSEEK_API_KEY") or "").strip() or None
    if gerador == "deepseek" and chave is None:
        raise ErroConfig("DEEPSEEK_API_KEY é obrigatória com o gerador deepseek")
    alternativa = ambiente.get("DONA_CHECA_ALTERNATIVA_LOCAL", "nao")
    if alternativa not in ("sim", "nao"):
        raise ErroConfig(f"DONA_CHECA_ALTERNATIVA_LOCAL precisa ser sim ou nao; veio {alternativa!r}")
    return Config(modo=modo,
                  host=ambiente.get("DONA_CHECA_HOST", "127.0.0.1"),
                  porta=_inteiro_positivo(ambiente, "DONA_CHECA_PORTA", 8000),
                  tempo_max=_inteiro_positivo(ambiente, "DONA_CHECA_TEMPO_MAX", 300),
                  gerador=gerador, chave=chave if gerador == "deepseek" else None,
                  modelo_remoto=ambiente.get("DEEPSEEK_MODELO") or MODELO_REMOTO,
                  alternativa_local=alternativa == "sim")
