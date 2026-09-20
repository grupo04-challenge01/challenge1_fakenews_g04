"""Cobertura do corpus e resposta de lacuna — capability `frescor-corpus`.

Decisão 4 do `design.md`: frescor é requisito de produto, não manutenção. O
corpus termina em 2021, e responder `evidência insuficiente` sobre a Qdenga é
enganoso — existe checagem publicada; o acervo é que não a contém. As duas
respostas são diferentes e o sistema precisa distingui-las:

| Situação | Resposta | O que a pessoa faz com isso |
| --- | --- | --- |
| Pauta dentro da janela, sem correspondência | `evidência insuficiente` | não há o que procurar |
| Pauta posterior à janela do acervo | `lacuna de acervo` | procurar na agência, o link vai junto |

A declaração produzida aqui é reexecutável: roda sobre o arquivo, não sobre
memória de quem escreveu o relatório.
"""
from __future__ import annotations

import collections
import dataclasses
import datetime
import json
import re
import unicodedata

from tratamento import leitura

# Pautas brasileiras de saúde posteriores ao fim do corpus, mais os controles
# que devem aparecer. A lista é o instrumento da task 4.1: o zero de `qdenga`
# só vale como evidência se for medido junto de um termo que dá diferente de zero.
TERMOS_DE_PAUTA: tuple[str, ...] = (
    "qdenga", "mpox", "oropouche", "semaglutida",
    "covid", "dengue", "vacina", "cloroquina",
)

# Agências cujos feeds o `update_factckbr.py` alcança, e as do corpus que ele
# não alcança. `frescor-corpus` exige nomear as duas listas.
AGENCIAS_ALCANCADAS: tuple[str, ...] = ("aos fatos", "lupa", "agência pública (truco)")
AGENCIAS_NAO_ALCANCADAS: tuple[str, ...] = ("boatos", "fato-ou-fake", "COMPROVA")

# Fonte apontada ao usuário quando a pauta é posterior ao acervo. Agregador
# público de checagens, não conteúdo de terceiro copiado para o nosso lado.
ONDE_PROCURAR = (
    "https://toolbox.google.com/factcheck/explorer — busca nas agências "
    "signatárias do IFCN, inclusive as brasileiras, sem limite de data"
)


@dataclasses.dataclass(frozen=True)
class RespostaDePauta:
    """O que o sistema pode dizer sobre a pauta antes mesmo de recuperar."""

    tipo: str
    mensagem: str
    onde_procurar: str = ""
    termos_reconhecidos: tuple[str, ...] = ()


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


def _padrao(termo: str) -> re.Pattern:
    """Palavra inteira: `mpox` não pode casar dentro de outra palavra, senão o
    zero medido deixa de significar ausência de pauta."""
    return re.compile(rf"\b{re.escape(sem_acento(termo).lower())}\b")


def contar_termo(textos, termo: str) -> int:
    """Conta em quantos textos o termo aparece, ignorando caixa e acento."""
    padrao = _padrao(termo)
    return sum(1 for t in textos if padrao.search(sem_acento(str(t)).lower()))


def contar_termos(textos_normalizados, termos) -> dict[str, int]:
    """Conta vários termos numa única passada de normalização.

    Normalizar 21,5 milhões de caracteres custa cerca de 5 s; fazer isso uma vez
    por termo levava a declaração a 40 s. A normalização acontece antes, uma vez
    só, e aqui só correm as buscas.
    """
    padroes = {t: _padrao(t) for t in termos}
    contagem = dict.fromkeys(termos, 0)
    for texto in textos_normalizados:
        for termo, padrao in padroes.items():
            if padrao.search(texto):
                contagem[termo] += 1
    return contagem


def _textos_do_corpus(df) -> list[str]:
    return (df["title"].fillna("") + " " + df["subtitle"].fillna("") + " " +
            df["text_news"].fillna("")).tolist()


def _textos_normalizados(df) -> list[str]:
    """Textos do corpus dobrados por caixa e acento, memoizados por conteúdo."""
    chave = (id(df), len(df))
    memo = _MEMO_TEXTOS.get(chave)
    if memo is None:
        memo = [sem_acento(t).lower() for t in _textos_do_corpus(df)]
        _MEMO_TEXTOS.clear()
        _MEMO_TEXTOS[chave] = memo
    return memo


_MEMO_TEXTOS: dict[tuple[int, int], list[str]] = {}


def declaracao_de_cobertura(df) -> dict:
    """Janela, concentração por ano e contagem por termo de pauta — tudo medido."""
    datas = sorted(d for d in df["publication_date"] if d)
    por_ano = collections.Counter(d[:4] for d in datas)
    ano_maximo, contagem_maxima = por_ano.most_common(1)[0]

    termos = contar_termos(_textos_normalizados(df), TERMOS_DE_PAUTA)

    return {
        "gerado_em": datetime.date.today().isoformat(),
        "arquivo": "datasets/derivados/factcenter_subset_saude.csv",
        "registros": int(len(df)),
        "janela": {"inicio": datas[0], "fim": datas[-1]},
        "por_ano": dict(sorted(por_ano.items())),
        "concentracao_maxima": {
            "ano": ano_maximo,
            "registros": int(contagem_maxima),
            "proporcao": contagem_maxima / len(df),
        },
        "termos_de_pauta": termos,
        "termos_com_zero_ocorrencia": sorted(t for t, n in termos.items() if n == 0),
        "agencias": dict(collections.Counter(df["source_name"]).most_common()),
        "reexecutar": "python -m tratamento frescor",
    }


def _declaracao_memoizada(df) -> dict:
    """Evita remedir o corpus a cada alegação classificada."""
    chave = (id(df), len(df))
    memo = _MEMO_DECLARACAO.get(chave)
    if memo is None:
        memo = declaracao_de_cobertura(df)
        _MEMO_DECLARACAO.clear()
        _MEMO_DECLARACAO[chave] = memo
    return memo


_MEMO_DECLARACAO: dict[tuple[int, int], dict] = {}


def classificar_pauta(alegacao: str, df) -> RespostaDePauta:
    """Diz se a pauta cai fora do acervo antes de qualquer recuperação.

    O teste é o termo de pauta com zero ocorrência medido: se a alegação cita
    um deles, a ausência de resultado é do acervo, não do mundo.
    """
    declaracao = _declaracao_memoizada(df)
    ausentes = declaracao["termos_com_zero_ocorrencia"]
    fim = declaracao["janela"]["fim"]

    reconhecidos = tuple(t for t in ausentes if contar_termo([alegacao], t))
    if reconhecidos:
        return RespostaDePauta(
            tipo="lacuna_de_acervo",
            mensagem=(
                f"O acervo de checagens vai até {fim} e não cobre "
                f"{', '.join(reconhecidos)}. Isso não quer dizer que não exista "
                "checagem publicada sobre o assunto — quer dizer que ela está "
                "fora do que este sistema consultou."),
            onde_procurar=ONDE_PROCURAR,
            termos_reconhecidos=reconhecidos,
        )

    return RespostaDePauta(
        tipo="coberta",
        mensagem=(f"A pauta está dentro da janela do acervo, que vai até {fim}. "
                  "Ausência de fonte aqui é `evidência insuficiente`, e não "
                  "lacuna de cobertura."),
    )


def caminho_de_atualizacao() -> dict:
    """Cobertura declarada do caminho de atualização (task 4.4)."""
    return {
        "script": "datasets/01_nucleo_metodologico/factckbr/update_factckbr.py",
        "agencias_alcancadas": list(AGENCIAS_ALCANCADAS),
        "agencias_nao_alcancadas": list(AGENCIAS_NAO_ALCANCADAS),
        "cobertura": ("três feeds contra as seis agências do corpus principal. "
                      "Não é atualização do corpus completo."),
        "pre_requisito_de_reparo": (
            "reparado em 19/09/2026 pelas tasks 3.4 e 4.5: allowlist de "
            "caractere substituída por normalização Unicode, `DataFrame.append` "
            "substituído por `pd.concat`, JSON-LD lido por `json.loads`."),
        "limite_conhecido": (
            "o feed devolve apenas os artigos recentes de cada agência; o "
            "caminho serve a incremento, não a recomposição do acervo."),
    }


def gravar(caminho=None) -> dict:
    """Versiona a declaração de cobertura como artefato reexecutável (task 4.2)."""
    destino = caminho or (leitura.DIRETORIO_DERIVADOS / "declaracao_cobertura.json")
    declaracao = declaracao_de_cobertura(leitura.ler_corpus())
    declaracao["caminho_de_atualizacao"] = caminho_de_atualizacao()
    destino.write_text(json.dumps(declaracao, ensure_ascii=False, indent=2),
                       encoding="utf-8")
    return declaracao
