"""Derivados e relatórios reexecutáveis do tratamento — tasks 2.2, 2.6 a 2.8 e 4.1.

Nada aqui decide: tudo mede o corpus sob o mapa versionado e grava o resultado
em arquivo, para que a declaração de cobertura e os caveats do portfólio sejam
verificáveis por reexecução, e não por confiança no texto.
"""
from __future__ import annotations

import collections
import json

from tratamento import leitura, vereditos

COLUNAS_DO_DERIVADO = (
    "url", "source_name", "publication_date", "rating",
    "n_vereditos", "chaves_canonicas", "rotulos", "misto",
    "rotulo_consolidado", "excluido_do_banco_de_estimulos",
    "motivo_da_exclusao",
)


def marcar_registros(df):
    """Anota cada registro do corpus com o que o mapa permite afirmar dele.

    A grafia original do campo `rating` é preservada na coluna `rating`, intacta.
    Registro misto fica sem consolidado — não recebe rótulo por maioria nem por
    primeiro elemento.
    """
    import pandas as pd

    linhas = []
    for registro in df.itertuples(index=False):
        classificado = vereditos.classificar_registro(registro.rating)
        linhas.append({
            "url": registro.url,
            "source_name": registro.source_name,
            "publication_date": registro.publication_date,
            "rating": registro.rating,
            "n_vereditos": len(classificado.vereditos),
            "chaves_canonicas": "|".join(v.chave for v in classificado.vereditos),
            "rotulos": "|".join(classificado.rotulos),
            "misto": classificado.misto,
            "rotulo_consolidado": classificado.rotulo_consolidado or "",
            "excluido_do_banco_de_estimulos":
                classificado.excluido_do_banco_de_estimulos,
            "motivo_da_exclusao": classificado.motivo_da_exclusao,
        })
    return pd.DataFrame(linhas, columns=list(COLUNAS_DO_DERIVADO))


def relatorio_de_vereditos(df) -> dict:
    """Contagens do campo de veredito, por agência e no total."""
    marcado = marcar_registros(df)

    grafias = collections.Counter()
    chaves = collections.Counter()
    por_agencia: dict[str, dict] = {}

    for agencia, bruto in zip(df["source_name"], df["rating"]):
        lidos = vereditos.ler_campo(bruto)
        bucket = por_agencia.setdefault(
            agencia, {"registros": 0, "grafias": collections.Counter()})
        bucket["registros"] += 1
        for v in lidos:
            grafias[v.original] += 1
            chaves[v.chave] += 1
            bucket["grafias"][v.original] += 1

    for bucket in por_agencia.values():
        bucket["grafias"] = dict(bucket["grafias"].most_common())
        bucket["grafias_distintas"] = len(bucket["grafias"])

    verdadeiros_unicos = int(
        ((~marcado["misto"]) & (marcado["n_vereditos"] == 1) &
         (marcado["chaves_canonicas"].isin(["verdadeiro", "verdadeiro, mas"]))).sum())

    return {
        "mapa_versao": vereditos.MAPA["versao"],
        "registros": int(len(df)),
        "strings_brutas_distintas": int(df["rating"].nunique()),
        "grafias_distintas": len(grafias),
        "chaves_canonicas_distintas": len(chaves),
        "registros_multi_alegacao": int((marcado["n_vereditos"] > 1).sum()),
        "registros_mistos": int(marcado["misto"].sum()),
        "registros_compilados_excluidos":
            int(marcado["excluido_do_banco_de_estimulos"].sum()),
        "registros_verdadeiro_unico": verdadeiros_unicos,
        "por_rotulo_consolidado":
            dict(collections.Counter(
                marcado.loc[~marcado["misto"], "rotulo_consolidado"]).most_common()),
        "grafias": dict(grafias.most_common()),
        "chaves_canonicas": dict(chaves.most_common()),
        "por_agencia": por_agencia,
    }


def gravar(caminho_derivado=None, caminho_relatorio=None) -> dict:
    """Regera o derivado marcado e o relatório de veredito a partir do corpus."""
    derivado = caminho_derivado or (
        leitura.DIRETORIO_DERIVADOS / "factcenter_vereditos_normalizados.csv")
    relatorio_json = caminho_relatorio or (
        leitura.DIRETORIO_DERIVADOS / "relatorio_vereditos.json")

    df = leitura.ler_corpus()
    marcar_registros(df).to_csv(derivado, index=False, encoding="utf-8")
    relatorio = relatorio_de_vereditos(df)
    relatorio_json.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    return relatorio
