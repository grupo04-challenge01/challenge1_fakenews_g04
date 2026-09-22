"""Leitura e normalização do veredito das agências — capability `normalizacao-rotulos`.

Decisão 2 do `design.md`: normalizar rótulo não é achatar rótulo. Cada veredito
recebe uma chave canônica normalizada só por caixa e acento, e a grafia original
fica ao lado, rastreável até a agência. O mapa mora em `mapa_vereditos.json`,
versionado, e valor fora dele interrompe o processamento.
"""
from __future__ import annotations

import ast
import dataclasses
import json
import pathlib
import unicodedata

CAMINHO_MAPA = pathlib.Path(__file__).resolve().parent / "mapa_vereditos.json"

# Medido em 19/09/2026 sobre o corpus: 22 registros de veredito único
# `verdadeiro` ou `verdadeiro, mas` em 4.063.
REGISTROS_VERDADEIROS_MEDIDOS = 22
REGISTROS_TOTAIS = 4063

# `normalizacao-rotulos`: registro com mais de vinte vereditos é compilado
# periódico de agência, não mensagem que alguém receberia.
LIMITE_DE_COMPILADO = 20


class VeredictoDesconhecido(RuntimeError):
    """Valor fora do mapa. Nenhum registro afetado entra no índice."""


class CaveatDeCarencia(RuntimeError):
    """Uso vedado do corpus por carência declarada de itens da classe pedida."""


def _carregar_mapa() -> dict:
    return json.loads(CAMINHO_MAPA.read_text(encoding="utf-8"))


MAPA = _carregar_mapa()


@dataclasses.dataclass(frozen=True)
class Veredito:
    """Um veredito de agência: a grafia publicada e a chave para comparação."""

    original: str
    chave: str


@dataclasses.dataclass(frozen=True)
class RegistroClassificado:
    """O que se pode afirmar sobre um registro do corpus a partir do seu `rating`."""

    vereditos: tuple[Veredito, ...]
    rotulos: tuple[str, ...]
    misto: bool
    rotulo_consolidado: str | None
    caso_de_teste_de_decomposicao: bool
    excluido_do_banco_de_estimulos: bool
    motivo_da_exclusao: str


def chave_canonica(valor: str) -> str:
    """Dobra caixa e acento. Nenhuma outra aproximação é aplicada."""
    sem_acento = "".join(c for c in unicodedata.normalize("NFD", valor)
                         if unicodedata.category(c) != "Mn")
    return sem_acento.strip().lower()


def ler_campo(bruto: str) -> list[Veredito]:
    """Interpreta o campo `rating` como lista de vereditos, não como string."""
    try:
        valores = ast.literal_eval(bruto)
    except (ValueError, SyntaxError) as erro:
        raise VeredictoDesconhecido(
            f"campo `rating` ilegível: {bruto!r} — {erro}") from erro
    if not isinstance(valores, list):
        valores = [valores]
    return [Veredito(original=str(v), chave=chave_canonica(str(v)))
            for v in valores]


def rotular(valor: str) -> str:
    """Rótulo de destino de um veredito. Valor fora do mapa interrompe."""
    chave = chave_canonica(valor)
    entrada = MAPA["entradas"].get(chave)
    if entrada is None:
        raise VeredictoDesconhecido(
            f"veredito {valor!r} (chave {chave!r}) não consta do mapa versão "
            f"{MAPA['versao']}. O processamento para aqui: o valor precisa de "
            "decisão registrada no mapa, e MUST NOT receber rótulo por "
            "semelhança de string. Nenhum registro afetado entra no índice "
            "até a decisão ser registrada.")
    return entrada["rotulo"]


def classificar_registro(bruto: str) -> RegistroClassificado:
    """Classifica um registro do corpus sem forçá-lo a caber num rótulo único."""
    vereditos = tuple(ler_campo(bruto))
    rotulos = tuple(rotular(v.original) for v in vereditos)
    distintos = set(rotulos)

    misto = len(distintos) > 1
    consolidado = None if misto else (rotulos[0] if rotulos else None)

    excluido = len(vereditos) > LIMITE_DE_COMPILADO
    motivo = ""
    if excluido:
        motivo = (f"compilado periódico de agência: {len(vereditos)} vereditos "
                  f"num registro, acima do limite de {LIMITE_DE_COMPILADO}. "
                  "Não é mensagem que alguém receberia, logo não serve de "
                  "estímulo de teste com usuário.")

    return RegistroClassificado(
        vereditos=vereditos,
        rotulos=rotulos,
        misto=misto,
        rotulo_consolidado=consolidado,
        caso_de_teste_de_decomposicao=misto,
        excluido_do_banco_de_estimulos=excluido,
        motivo_da_exclusao=motivo,
    )


def amostrar_verdadeiros(df) -> None:
    """Recusa amostrar itens verdadeiros deste corpus e apresenta o caveat."""
    total = f"{REGISTROS_TOTAIS:,}".replace(",", ".")
    raise CaveatDeCarencia(
        f"o corpus tem {REGISTROS_VERDADEIROS_MEDIDOS} registros de veredito "
        f"único `verdadeiro` ou `verdadeiro, mas` em {total} "
        "— carência declarada em `normalizacao-rotulos`. A amostragem não é "
        "executada sobre este corpus; a coleta de itens verdadeiros é trabalho "
        "manual à parte, registrado como questão em aberto no design.")
