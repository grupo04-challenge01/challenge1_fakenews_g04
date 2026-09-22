"""Medição do acervo de circulação — bloco 3 e task 6.4 de add-ampliacao-corpus-ptbr.

Lê o `.jsonl` de 3,6 GB **em streaming**, uma linha por vez, e grava apenas
agregados. Nenhuma coluna do derivado contém texto de post nem identificador de
autor: `acervo-circulacao` veda versionar os dois, e a vedação é o que permite
o acervo existir no repositório.

O que mede:

- task 3.4 — janela real, distribuição por mês, canais distintos, proporção de
  `is_vaccine_related`;
- task 3.5 — frequência dos termos de pauta, inclusive os zeros, comparados
  contra o zero do acervo antigo;
- task 3.6 — as lacunas declaradas pelos autores, **medidas** e não copiadas:
  reações ausentes antes de 30/12/2021 e meses com queda abrupta por canal
  apagado;
- task 6.4 — derivados agregados por mês, por canal e por termo.

Uso:
    python datasets/scripts/medir_telegram.py [--limite N]
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from tratamento import leitura  # noqa: E402

BASE = RAIZ / "datasets" / "04_acervo_circulacao" / "telegram_antivacina_br"
ARQUIVO = BASE / "telegram-vaccine-info-disorder-dataset-2020-2025.jsonl"
SAIDA = RAIZ / "datasets" / "derivados"

# Declarado pelos autores no registro do REDU.
POSTS_DECLARADOS = 3_998_633
CANAIS_DECLARADOS = 119

# Data a partir da qual os autores declaram ter coletado reações (task 3.6).
CORTE_REACOES = datetime.date(2021, 12, 30)

TERMOS_DE_PAUTA = (
    "qdenga", "mpox", "oropouche", "semaglutida",
    "covid", "vacina", "dengue", "sarampo", "hpv", "autismo",
)


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


PADROES = {t: re.compile(rf"\b{re.escape(t)}\b") for t in TERMOS_DE_PAUTA}


def _mes(milissegundos) -> str | None:
    """A data vem como epoch em milissegundos."""
    if milissegundos in (None, ""):
        return None
    try:
        d = datetime.datetime.fromtimestamp(int(milissegundos) / 1000,
                                            tz=datetime.timezone.utc)
    except (ValueError, OSError, OverflowError):
        return None
    return d.strftime("%Y-%m")


def medir(limite: int | None = None) -> dict:
    por_mes = collections.Counter()
    por_canal = collections.Counter()
    por_termo = collections.Counter()
    vacina_related = collections.Counter()
    idiomas = collections.Counter()
    com_reacao_por_mes = collections.Counter()
    sem_data = 0
    minimo = maximo = None
    lidos = 0

    for registro in leitura.ler_jsonl(ARQUIVO):
        lidos += 1
        if limite and lidos > limite:
            lidos -= 1
            break

        mes = _mes(registro.get("date"))
        if mes is None:
            sem_data += 1
        else:
            por_mes[mes] += 1
            minimo = mes if minimo is None or mes < minimo else minimo
            maximo = mes if maximo is None or mes > maximo else maximo
            reacoes = registro.get("reactions")
            if reacoes not in (None, "", 0):
                com_reacao_por_mes[mes] += 1

        canal = registro.get("channel_id")
        if canal:
            por_canal[canal] += 1

        vacina_related[str(registro.get("is_vaccine_related"))] += 1
        idiomas[str(registro.get("language"))] += 1

        texto = registro.get("text_content") or ""
        if texto:
            normalizado = sem_acento(texto).lower()
            for termo, padrao in PADROES.items():
                if padrao.search(normalizado):
                    por_termo[termo] += 1

        if lidos % 500_000 == 0:
            print(f"  {lidos:,} linhas...", flush=True)

    # Task 3.6 — queda abrupta por canal apagado, medida e não copiada.
    meses = sorted(por_mes)
    quedas = []
    for anterior, atual in zip(meses, meses[1:]):
        if por_mes[anterior] >= 1000 and por_mes[atual] < por_mes[anterior] * 0.5:
            quedas.append({"mes": atual, "posts": por_mes[atual],
                           "mes_anterior": anterior,
                           "posts_anteriores": por_mes[anterior],
                           "queda": round(1 - por_mes[atual] / por_mes[anterior], 3)})

    corte = CORTE_REACOES.strftime("%Y-%m")
    reacoes_antes = sum(n for m, n in com_reacao_por_mes.items() if m < corte)
    posts_antes = sum(n for m, n in por_mes.items() if m < corte)

    return {
        "gerado_em": datetime.date.today().isoformat(),
        "arquivo": ARQUIVO.name,
        "bytes": ARQUIVO.stat().st_size,
        "leitura": "streaming por linha; o arquivo nunca é carregado inteiro",
        "posts_lidos": lidos,
        "posts_declarados": POSTS_DECLARADOS,
        "divergencia_de_contagem": lidos - POSTS_DECLARADOS if not limite else None,
        "canais_distintos": len(por_canal),
        "canais_declarados": CANAIS_DECLARADOS,
        "janela": {"inicio": minimo, "fim": maximo},
        "sem_data": sem_data,
        "por_mes": dict(sorted(por_mes.items())),
        "por_canal_top20": dict(por_canal.most_common(20)),
        "is_vaccine_related": dict(vacina_related.most_common()),
        "idiomas_top10": dict(idiomas.most_common(10)),
        "termos_de_pauta": {t: por_termo[t] for t in TERMOS_DE_PAUTA},
        "lacunas_medidas": {
            "reacoes_antes_de_2021_12_30": {
                "posts_no_periodo": posts_antes,
                "posts_com_reacao": reacoes_antes,
                "proporcao": round(reacoes_antes / posts_antes, 5) if posts_antes else None,
                "declarado_pelos_autores": "reações ausentes antes de 30/12/2021",
            },
            "meses_com_queda_abrupta": quedas,
        },
    }


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--limite", type=int, default=None,
                            help="lê apenas as N primeiras linhas (sonda)")
    args = analisador.parse_args()

    if not ARQUIVO.exists():
        sys.exit(f"{ARQUIVO} ausente — ver datasets/FONTES.md para reconstituir.")

    resultado = medir(args.limite)
    destino = SAIDA / ("telegram_agregados.json" if not args.limite
                       else "telegram_agregados_amostra.json")
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")

    print(f"posts: {resultado['posts_lidos']:,} | canais: {resultado['canais_distintos']}")
    print(f"janela: {resultado['janela']}")
    print(f"is_vaccine_related: {resultado['is_vaccine_related']}")
    print(f"termos: {resultado['termos_de_pauta']}")
    print(f"gravado em {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
