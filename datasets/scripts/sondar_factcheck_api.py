"""Portão de medição do índice de checagens recentes — bloco 1 de add-ampliacao-corpus-ptbr.

Tasks 1.1 e 1.2. Mede o que a Fact Check Tools API devolve para saúde em
português, por ano e por agência, sobre um conjunto de termos de pauta — e grava
o resultado em arquivo, porque a task exige contagem registrada e não saída de
terminal.

A capability `indice-checagens-recentes` só sobrevive se a medição mostrar
retorno útil: é o que a task 1.3 decide.

**A chave nunca é impressa, nem gravada no resultado.** Ela é lida de `.env`
(fora do git) para a variável de ambiente `GOOGLE_FACTCHECK_API_KEY` e usada só
no parâmetro de consulta.

Uso:
    python datasets/scripts/sondar_factcheck_api.py
"""
from __future__ import annotations

import collections
import datetime
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[2]
ENV = RAIZ / "docs" / "engage" / ".env"
SAIDA = RAIZ / "datasets" / "derivados" / "sonda_factcheck_api.json"

ENDPOINT = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
NOME_DA_CHAVE = "GOOGLE_FACTCHECK_API_KEY"

# Termo de controle: precisa devolver resultado, senão o zero dos demais não
# significa ausência de pauta — significa consulta quebrada.
TERMO_DE_CONTROLE = "vacina"

# Pautas de saúde posteriores à janela do acervo (2021), mais os controles.
TERMOS_DE_PAUTA = (
    "vacina", "covid", "dengue",
    "qdenga", "mpox", "oropouche", "semaglutida",
    "sarampo", "gripe", "hpv", "febre amarela",
)

PAGINAS_MAXIMAS = 10          # teto por termo, para a sonda não virar coleta
POR_PAGINA = 50               # máximo aceito pela API
PAUSA_S = 0.4                 # gentileza com o serviço


def carregar_chave() -> str:
    """Lê a chave do ambiente ou do `.env`, sem nunca ecoá-la."""
    chave = os.environ.get(NOME_DA_CHAVE, "").strip()
    if chave:
        return chave
    if not ENV.exists():
        sys.exit(f"{NOME_DA_CHAVE} ausente do ambiente e {ENV} não existe.")
    for linha in ENV.read_text(encoding="utf-8-sig").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        nome, valor = linha.split("=", 1)
        if nome.strip() == NOME_DA_CHAVE:
            return valor.strip().strip('"').strip("'")
    sys.exit(f"{NOME_DA_CHAVE} não encontrada em {ENV}.")


def consultar(chave: str, termo: str, pagina: str | None = None) -> dict:
    parametros = {
        "key": chave,
        "query": termo,
        "languageCode": "pt",
        "pageSize": str(POR_PAGINA),
    }
    if pagina:
        parametros["pageToken"] = pagina
    url = f"{ENDPOINT}?{urllib.parse.urlencode(parametros)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resposta:
            return json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        # O corpo do erro pode repetir a URL com a chave. Nunca é propagado.
        raise RuntimeError(
            f"HTTP {erro.code} ao consultar {termo!r} — corpo omitido para não "
            "vazar a chave na mensagem de erro") from None


def coletar_termo(chave: str, termo: str) -> list[dict]:
    """Todas as páginas de um termo, até o teto."""
    achados: list[dict] = []
    pagina = None
    for _ in range(PAGINAS_MAXIMAS):
        dados = consultar(chave, termo, pagina)
        achados.extend(dados.get("claims", []))
        pagina = dados.get("nextPageToken")
        if not pagina:
            break
        time.sleep(PAUSA_S)
    return achados


def resumir(claims: list[dict]) -> dict:
    """Contagem por ano e por agência, sem guardar texto de artigo de terceiro."""
    por_ano = collections.Counter()
    por_agencia = collections.Counter()
    sem_data = 0
    for claim in claims:
        for review in claim.get("claimReview", []):
            editor = review.get("publisher", {}).get("name") or "(sem editor)"
            por_agencia[editor] += 1
            data = review.get("reviewDate") or claim.get("claimDate") or ""
            if len(data) >= 4:
                por_ano[data[:4]] += 1
            else:
                sem_data += 1
    return {
        "checagens": sum(por_agencia.values()),
        "por_ano": dict(sorted(por_ano.items())),
        "por_agencia": dict(por_agencia.most_common()),
        "sem_data": sem_data,
        "posteriores_a_2021": sum(n for a, n in por_ano.items() if a > "2021"),
    }


def main() -> int:
    chave = carregar_chave()

    controle = coletar_termo(chave, TERMO_DE_CONTROLE)
    if not controle:
        print(f"CONTROLE VAZIO para {TERMO_DE_CONTROLE!r} em pt — a sonda não "
              "distingue ausência de pauta de consulta quebrada. Parando.",
              file=sys.stderr)
        return 1

    resultado = {
        "gerado_em": datetime.datetime.now().isoformat(timespec="seconds"),
        "endpoint": ENDPOINT,
        "parametros": {"languageCode": "pt", "pageSize": POR_PAGINA,
                       "paginas_maximas": PAGINAS_MAXIMAS},
        "controle": {"termo": TERMO_DE_CONTROLE, "checagens": len(controle)},
        "por_termo": {},
    }

    for termo in TERMOS_DE_PAUTA:
        claims = controle if termo == TERMO_DE_CONTROLE else coletar_termo(chave, termo)
        resultado["por_termo"][termo] = resumir(claims)
        r = resultado["por_termo"][termo]
        print(f"{termo:16s} {r['checagens']:5d} checagens | "
              f"{r['posteriores_a_2021']:5d} posteriores a 2021 | "
              f"{len(r['por_agencia'])} agências", flush=True)
        time.sleep(PAUSA_S)

    agencias = collections.Counter()
    for r in resultado["por_termo"].values():
        agencias.update(r["por_agencia"])
    resultado["agencias_alcancadas"] = dict(agencias.most_common())
    resultado["total_checagens"] = sum(r["checagens"]
                                       for r in resultado["por_termo"].values())
    resultado["total_posteriores_a_2021"] = sum(
        r["posteriores_a_2021"] for r in resultado["por_termo"].values())

    SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    print(f"\ngravado em {SAIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
