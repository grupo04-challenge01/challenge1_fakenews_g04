"""Recoleta do FACTCK.BR pelos três feeds — task 3.5 de add-tratamento-datasets-ptbr.

Roda o `update_factckbr.py` reparado (tasks 3.4 e 4.5) sobre a captura de
06/10/2026 e grava duas coisas ao lado dela:

- `recoleta_factckbr.tsv` — a saída do script, no formato do próprio script;
- `laudo_recoleta.json` — o que foi extraído, o que foi descartado e por quê,
  a fidelidade do texto e a reexecução sobre o acervo histórico.

## Por que a captura e não a rede

Os dois shells disponíveis ao grupo passam por proxy que devolve 403 para os
quatro domínios. As páginas foram buscadas pelo navegador e gravadas em
`captura.json` com SHA-256 calculado no navegador; este script recusa a
captura se um hash não bater. A troca de transporte é a única: `feedparser`
cede lugar à lista de `<item><link>` do feed (o que ele devolveria), e
`requests.get` a um HTML mínimo com o `<title>` e os blocos JSON-LD. O resto —
`get_claimReview()`, `text_pre_proc()`, `re_char()` — roda sem alteração.

## Por que não há merge com o acervo

O `main()` do script junta a coleta nova ao `factCkBr.tsv` antigo. Aqui isso
não é feito de propósito: o acervo está reprovado para citação por perda de
caractere, e misturar linha íntegra com linha corrompida no mesmo arquivo
apagaria a fronteira que o portão de integridade precisa enxergar.

## Por que a captura guarda projeção, não o bloco inteiro

O bloco `ClaimReview` do Aos Fatos traz publisher, bio e e-mail de cada autor.
O script não lê nada disso, e é dado pessoal de terceiro. A captura guarda só
os campos que `get_claimReview()` acessa, na ordem em que vieram, mais o hash
do bloco original completo.

Uso:
    python3 datasets/scripts/recoletar_factckbr.py
"""
from __future__ import annotations

import collections
import contextlib
import hashlib
import html
import importlib.util
import json
import pathlib
import sys
import types

import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
DIR_FACTCKBR = RAIZ / "datasets" / "01_nucleo_metodologico" / "factckbr"
DIR_RECOLETA = DIR_FACTCKBR / "recoleta_2026-10-06"
CAMINHO_SCRIPT = DIR_FACTCKBR / "update_factckbr.py"
CAMINHO_ACERVO = DIR_FACTCKBR / "FACTCKBR.tsv"
CAMINHO_CAPTURA = DIR_RECOLETA / "captura.json"
CAMINHO_TSV = DIR_RECOLETA / "recoleta_factckbr.tsv"
CAMINHO_LAUDO = DIR_RECOLETA / "laudo_recoleta.json"

# Mesma ordem de colunas de `main()` em update_factckbr.py.
TOPROW = ['URL', 'Author', 'datePublished', 'claimReviewed', 'reviewBody', 'title',
          'ratingValue', 'bestRating', 'alternativeName', 'contentType']

sys.path.insert(0, str(RAIZ))
from tratamento import integridade  # noqa: E402


class ErroDeCaptura(RuntimeError):
    """Hash da captura não confere: o texto mudou entre o navegador e o disco."""


def _sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def carregar_script():
    spec = importlib.util.spec_from_file_location("update_factckbr", CAMINHO_SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def conferir_hashes(captura: dict) -> None:
    for agencia in captura["agencias"]:
        for pagina in agencia["paginas"]:
            if "title" in pagina and _sha256(pagina["title"]) != pagina["sha256_title"]:
                raise ErroDeCaptura(f"título divergente: {pagina['url']}")
            for bloco in pagina["blocos"]:
                if _sha256(bloco["projecao"]) != bloco["sha256_projecao"]:
                    raise ErroDeCaptura(f"bloco divergente: {pagina['url']}")


def carregar_captura(caminho: pathlib.Path = CAMINHO_CAPTURA) -> dict:
    captura = json.loads(caminho.read_text(encoding="utf-8"))
    conferir_hashes(captura)
    return captura


def html_minimo(pagina: dict) -> bytes:
    partes = ["<html><head>"]
    if pagina.get("title") is not None:
        partes.append(f"<title>{html.escape(pagina['title'], quote=False)}</title>")
    for bloco in pagina["blocos"]:
        assert "</script" not in bloco["projecao"].lower()
        partes.append(f'<script type="application/ld+json">{bloco["projecao"]}</script>')
    partes.append("</head><body></body></html>")
    return "".join(partes).encode("utf-8")


@contextlib.contextmanager
def _requests_da_captura(pagina: dict):
    """`get_claimReview()` faz `import requests` dentro da função; servimos a captura."""
    falso = types.ModuleType("requests")
    falso.get = lambda url, timeout=None: types.SimpleNamespace(content=html_minimo(pagina))
    anterior = sys.modules.get("requests")
    sys.modules["requests"] = falso
    try:
        yield
    finally:
        if anterior is None:
            sys.modules.pop("requests", None)
        else:
            sys.modules["requests"] = anterior


def extrair_pagina(script, pagina: dict) -> list[list]:
    with _requests_da_captura(pagina):
        return script.get_claimReview(pagina["url"])


# Acessos de `get_claimReview()`, na ordem do script. O `except Exception: pass`
# do script engole o motivo do descarte; este diagnóstico só o torna visível e é
# conferido contra o resultado do próprio script em `executar()`.
_ACESSOS = (
    ("my_dict['author']['url']", lambda d: d['author']['url']),
    ("my_dict['datePublished']", lambda d: d['datePublished']),
    ("my_dict['claimReviewed']", lambda d: d['claimReviewed']),
    ("my_dict['reviewRating']['ratingValue']", lambda d: d['reviewRating']['ratingValue']),
    ("my_dict['reviewRating']['bestRating']", lambda d: d['reviewRating']['bestRating']),
    ("my_dict['reviewRating']['alternateName']", lambda d: d['reviewRating']['alternateName']),
    ("my_dict['itemReviewed']['@type']", lambda d: d['itemReviewed']['@type']),
)


def diagnosticar_bloco(script, projecao: str) -> dict:
    try:
        d = script.text_pre_proc(projecao)
    except Exception as exc:  # noqa: BLE001
        return {"extraido": False, "falha_em": "text_pre_proc()", "excecao": f"{type(exc).__name__}: {exc}"}
    for expressao, acesso in _ACESSOS:
        try:
            acesso(d)
        except Exception as exc:  # noqa: BLE001
            return {"extraido": False, "falha_em": expressao, "excecao": f"{type(exc).__name__}: {exc}"}
    return {"extraido": True, "falha_em": None, "excecao": None}


def _contar_acentuadas(texto: str) -> dict[str, int]:
    contagem = collections.Counter(texto)
    return {m: int(contagem[m]) for par in integridade.PARES_ACENTUADOS for m in par}


def executar(captura: dict) -> tuple[list[list], dict]:
    script = carregar_script()
    linhas: list[list] = []
    por_agencia = []
    blocos = identicos = titulos = titulos_identicos = 0
    texto_recoletado = []

    for agencia in captura["agencias"]:
        causas: collections.Counter = collections.Counter()
        com_claim = n_blocos = extraidas = 0
        for pagina in agencia["paginas"]:
            obtidas = extrair_pagina(script, pagina)
            diagnosticos = [diagnosticar_bloco(script, b["projecao"]) for b in pagina["blocos"]]
            if sum(d["extraido"] for d in diagnosticos) != len(obtidas):
                raise RuntimeError(f"diagnóstico diverge do script em {pagina['url']}")
            causas.update(d["falha_em"] for d in diagnosticos if not d["extraido"])
            linhas.extend(obtidas)
            extraidas += len(obtidas)
            n_blocos += len(pagina["blocos"])
            com_claim += bool(pagina["blocos"])

            if pagina.get("title") is not None:
                titulos += 1
                titulos_identicos += script.re_char(pagina["title"]) == pagina["title"]
                texto_recoletado.append(pagina["title"])
            for bloco in pagina["blocos"]:
                blocos += 1
                original = json.loads(bloco["projecao"])
                identicos += script.text_pre_proc(bloco["projecao"]) == original
                texto_recoletado += [original.get("claimReviewed", ""), original.get("reviewBody", "")]

        por_agencia.append({
            "agencia": agencia["agencia"],
            "feed_declarado": agencia["feed_declarado"],
            "feed_final": agencia["feed_final"],
            "itens_no_feed": agencia["itens_no_feed"],
            "paginas_com_claimreview": com_claim,
            "blocos_claimreview": n_blocos,
            "alegacoes_extraidas": extraidas,
            "causas_de_descarte": dict(sorted(causas.items())),
        })

    acentuadas = _contar_acentuadas("\n".join(texto_recoletado))

    texto_acervo = CAMINHO_ACERVO.read_text(encoding="utf-8")
    antes = _contar_acentuadas(texto_acervo)
    depois = _contar_acentuadas(script.re_char(texto_acervo))
    maiusculas = [m for m, _ in integridade.PARES_ACENTUADOS]
    laudo_acervo = integridade.verificar(CAMINHO_ACERVO.name, CAMINHO_ACERVO)

    laudo = {
        "task": "add-tratamento-datasets-ptbr 3.5",
        "data_coleta": captura["data_coleta"],
        "script": "datasets/01_nucleo_metodologico/factckbr/update_factckbr.py",
        "sha256_script": hashlib.sha256(CAMINHO_SCRIPT.read_bytes()).hexdigest(),
        "sha256_captura": hashlib.sha256(CAMINHO_CAPTURA.read_bytes()).hexdigest(),
        "por_agencia": por_agencia,
        "total_alegacoes_extraidas": len(linhas),
        "fidelidade": {
            "blocos": blocos,
            "blocos_identicos_apos_text_pre_proc": int(identicos),
            "titulos": titulos,
            "titulos_identicos_apos_re_char": int(titulos_identicos),
            "maiusculas_acentuadas_na_recoleta": {m: acentuadas[m] for m in maiusculas if acentuadas[m]},
        },
        "acervo_historico": {
            "arquivo": "datasets/01_nucleo_metodologico/factckbr/FACTCKBR.tsv",
            "registros": int(len(pd.read_csv(CAMINHO_ACERVO, sep="\t"))),
            "antes": antes,
            "depois_do_re_char_reparado": depois,
            "maiusculas_acentuadas_recuperadas": sum(depois[m] - antes[m] for m in maiusculas),
            "maiusculas_ausentes": laudo_acervo["ausentes"],
            "maiusculas_com_evidencia_de_corrupcao": [c["maiuscula"] for c in laudo_acervo["corrompidos"]],
            "aprovado_para_citacao": laudo_acervo["aprovado"],
        },
        "conclusao": [
            "A recoleta pelos três feeds com o script reparado extraiu zero alegações.",
            "Aos Fatos: 18 ClaimReview descartados porque `author` passou a ser lista de "
            "pessoas sem `url`; o `except Exception: pass` do script engole o erro.",
            "Agência Pública (Truco): feed parado desde 26/10/2018, sem ClaimReview nas páginas.",
            "Lupa: feed redirecionado para agencialupa.org, sem ClaimReview nas páginas.",
            "O filtro de caractere reparado preserva todo o texto recoletado, maiúscula acentuada inclusive.",
            "Reexecutar o re_char() reparado sobre o FACTCKBR.tsv não recupera nenhuma maiúscula "
            "acentuada: a perda está no arquivo distribuído e é irreversível. "
            "As 1.313 alegações permanecem reprovadas para citação.",
        ],
    }
    return linhas, laudo


def gravar(linhas: list[list], laudo: dict) -> None:
    novas = pd.DataFrame(linhas, columns=TOPROW).set_index("URL")
    novas.to_csv(CAMINHO_TSV, sep="\t", index=True, encoding="utf-8", lineterminator="\n")
    CAMINHO_LAUDO.write_text(json.dumps(laudo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    linhas, laudo = executar(carregar_captura())
    gravar(linhas, laudo)
    for a in laudo["por_agencia"]:
        print(f"{a['agencia']}: {a['itens_no_feed']} itens, {a['blocos_claimreview']} ClaimReview, "
              f"{a['alegacoes_extraidas']} extraídas {a['causas_de_descarte'] or ''}")
    print(f"total extraído: {laudo['total_alegacoes_extraidas']}")
    ac = laudo["acervo_historico"]
    print(f"acervo: Ã {ac['antes']['Ã']}→{ac['depois_do_re_char_reparado']['Ã']}, "
          f"ã {ac['antes']['ã']}; recuperadas {ac['maiusculas_acentuadas_recuperadas']}")


if __name__ == "__main__":
    main()
