"""Esquema de indexação — task 1.1 de mvp-copiloto-verificacao.

O contrato está em `prototipo/indice/esquema_indexacao.json`. Este módulo faz
duas coisas com ele:

1. `atributos_de_corpus` carimba em cada unidade e fragmento os atributos que o
   MVP exige do índice e que a prova de conceito não gravava: corpus de origem,
   tipo de fonte, idioma (prioridade PT-BR antes de EN, task 1.4), aptidão a
   citação (integridade-textual) e nome exibível da agência (atribuição).
2. `validar` confere o índice inteiro: a forma de cada registro pelo JSON Schema
   e as invariantes I1 a I12 de `x-invariantes`, que JSON Schema não expressa
   porque dependem de mais de um registro.

Uso: `python -m prototipo.rag.esquema` constrói as unidades em memória a partir
do corpus (sem o braço denso, que exige torch), valida e grava o laudo em
`prototipo/indice/validacao_esquema.json`.
"""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parents[2]
ESQUEMA = RAIZ / "prototipo" / "indice" / "esquema_indexacao.json"
LAUDO = RAIZ / "prototipo" / "indice" / "validacao_esquema.json"

# Campos que o fragmento repete da unidade sem divergência (I3).
HERDADOS = ("corpus", "tipo_fonte", "idioma", "apto_citacao", "agencia",
            "agencia_nome", "url", "data_publicacao", "alegacao",
            "veredito_original")


class ErroDeEsquema(RuntimeError):
    """Índice fora do contrato. Nada é gravado."""


def carregar_esquema(caminho: pathlib.Path = ESQUEMA) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def versao(esquema: dict | None = None) -> str:
    return (esquema or carregar_esquema())["x-versao"]


def atributos_de_corpus(corpus: str, agencia: str, esquema: dict | None = None) -> dict:
    """Atributos que todo registro do corpus carrega. Agência fora do registro
    interrompe, como valor de veredito fora do mapa em normalizacao-rotulos."""
    esquema = esquema or carregar_esquema()
    try:
        declarado = esquema["x-corpora"][corpus]
    except KeyError:
        raise ErroDeEsquema(f"corpus {corpus!r} não registrado em x-corpora") from None
    try:
        nome = esquema["x-agencias"][agencia]
    except KeyError:
        raise ErroDeEsquema(
            f"agência {agencia!r} ausente de x-agencias — registrar o nome exibível "
            "no esquema antes de indexar") from None
    return {"corpus": corpus, "tipo_fonte": declarado["tipo_fonte"],
            "idioma": declarado["idioma"], "apto_citacao": declarado["apto_citacao"],
            "agencia_nome": nome}


def registro_id(corpus: str, url: str, esquema: dict | None = None) -> str:
    """I1. Prefixo vazio no FactCenter mantém as chaves da aferição."""
    esquema = esquema or carregar_esquema()
    prefixo = esquema["x-corpora"][corpus]["prefixo_id"]
    return prefixo + hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]


def normalizar_url(url: str) -> str:
    """Chave de deduplicação entre corpora (I10)."""
    return re.sub(r"^https?://(www\.)?", "", url.strip().rstrip("/").lower())


def _validador(esquema: dict, colecao: str):
    from jsonschema import Draft7Validator

    alvo = dict(esquema)
    alvo.pop("oneOf", None)
    alvo["$ref"] = f"#/definitions/{colecao}"
    return Draft7Validator(alvo)


def validar(unidades: list[dict], fragmentos: list[dict],
            quarentena: list[dict] | None = None,
            esquema: dict | None = None, limite_exemplos: int = 20) -> dict:
    """Devolve o laudo. Não levanta: quem decide o que fazer com ele é o chamador."""
    from . import unidades as unidades_mod  # import tardio: unidades importa este módulo

    esquema = esquema or carregar_esquema()
    corpora, agencias = esquema["x-corpora"], esquema["x-agencias"]
    quarentena = quarentena or []
    violacoes: collections.Counter = collections.Counter()
    exemplos: list[dict] = []

    def falha(regra: str, ident: str, detalhe: str) -> None:
        violacoes[regra] += 1
        if len(exemplos) < limite_exemplos:
            exemplos.append({"regra": regra, "id": ident, "detalhe": detalhe[:300]})

    # Forma, registro a registro.
    for colecao, registros, chave in (("unidade", unidades, "unidade_id"),
                                      ("fragmento", fragmentos, "fragmento_id")):
        validador = _validador(esquema, colecao)
        for registro in registros:
            for erro in validador.iter_errors(registro):
                caminho = "/".join(str(p) for p in erro.path) or "(registro)"
                falha(f"forma:{colecao}", str(registro.get(chave)),
                      f"{caminho}: {erro.message}")

    # I1, I2, I7, I8, I9 — unidade isolada.
    por_id: dict[str, dict] = {}
    for u in unidades:
        uid = u.get("unidade_id")
        if uid in por_id:
            falha("I2", uid, "unidade_id repetido")
        por_id[uid] = u
        corpus = u.get("corpus")
        if corpus not in corpora:
            continue  # já contado como forma
        if u.get("registro_id") != registro_id(corpus, u.get("url", ""), esquema):
            falha("I1", uid, "registro_id difere de prefixo + sha1(url)[:10]")
        if uid != f'{u.get("registro_id")}-{u.get("indice_alegacao", -1):02d}':
            falha("I1", uid, "unidade_id difere de registro_id + indice_alegacao")
        if u.get("veredito_original") is not None and \
                u.get("veredito_chave") != unidades_mod.chave_canonica(u["veredito_original"]):
            falha("I7", uid, f'chave {u.get("veredito_chave")!r} não é a de '
                             f'{u["veredito_original"]!r}')
        disp = u.get("disposicao")
        if disp == "unica" and u.get("alegacoes_no_registro") != 1:
            falha("I8", uid, "unica com mais de uma alegação no registro")
        if (disp == "nao_segmentada") != bool(u.get("cobre_multiplas_alegacoes")):
            falha("I8", uid, "cobre_multiplas_alegacoes incoerente com a disposição")
        if disp == "segmentada" and u.get("origem_alegacao") not in ("citacao_segmentada",
                                                                     "claim_review"):
            falha("I8", uid, "segmentada sem origem de segmentação")
        declarado = corpora[corpus]
        for campo in ("idioma", "tipo_fonte", "apto_citacao"):
            if u.get(campo) != declarado[campo]:
                falha("I9", uid, f"{campo}={u.get(campo)!r} contra {declarado[campo]!r}")
        if agencias.get(u.get("agencia")) != u.get("agencia_nome"):
            falha("I9", uid, f'agencia_nome não bate com x-agencias para {u.get("agencia")!r}')

    # I2 a I6 — fragmento contra unidade.
    vistos_frag: set[str] = set()
    posicoes: dict[str, set[int]] = collections.defaultdict(set)
    for f in fragmentos:
        fid = f.get("fragmento_id")
        if fid in vistos_frag:
            falha("I2", fid, "fragmento_id repetido")
        vistos_frag.add(fid)
        u = por_id.get(f.get("unidade_id"))
        if u is None:
            falha("I3", fid, "fragmento sem unidade")
            continue
        if fid != f'{u["unidade_id"]}-{f.get("posicao", -1):02d}':
            falha("I1", fid, "fragmento_id difere de unidade_id + posicao")
        for campo in HERDADOS:
            if f.get(campo) != u.get(campo):
                falha("I3", fid, f"{campo} diverge da unidade")
        trecho, texto = f.get("trecho") or "", f.get("texto") or ""
        if u.get("tipo_fonte") == "checagem":
            linhas = texto.split("\n", 2)
            if len(linhas) < 3 or linhas[0] != f'Alegação: {u.get("alegacao")}' \
                    or str(u.get("veredito_original")) not in linhas[1]:
                falha("I4", fid, "cabeçalho alegação + veredito ausente ou divergente")
        if not texto.endswith("\n" + trecho):
            falha("I4", fid, "texto não termina pelo trecho")
        if trecho not in (u.get("justificativa") or ""):
            falha("I5", fid, "trecho não é substring literal da justificativa")
        if f.get("total") != u.get("fragmentos"):
            falha("I6", fid, "total difere de unidade.fragmentos")
        posicoes[u["unidade_id"]].add(f.get("posicao"))
    for uid, u in por_id.items():
        if posicoes.get(uid, set()) != set(range(u.get("fragmentos") or 0)):
            falha("I6", uid, "posições dos fragmentos incompletas")

    # I10 — mesma URL em dois corpora.
    corpora_por_url: dict[str, set[str]] = collections.defaultdict(set)
    for u in unidades:
        corpora_por_url[normalizar_url(u.get("url", ""))].add(u.get("corpus"))
    for url, conjunto in corpora_por_url.items():
        if len(conjunto) > 1:
            falha("I10", url, f"URL em {sorted(conjunto)}")

    # I11, I12 — quarentena disjunta e contagem fechada.
    q_unidades = {q["unidade_id"] for q in quarentena if q.get("unidade_id")}
    q_registros = [q for q in quarentena if not q.get("unidade_id")]
    for uid in q_unidades & set(por_id):
        falha("I11", uid, "unidade indexada e em quarentena")
    indexados = collections.defaultdict(set)
    for u in unidades:
        indexados[u.get("corpus")].add(u.get("url"))
    q_por_corpus = collections.Counter()
    for q in q_registros:
        if q.get("url") in indexados.get(q.get("corpus"), set()):
            falha("I11", q.get("url"), "registro em quarentena inteira tem unidade indexada")
        q_por_corpus[q.get("corpus")] += 1
    contagem = {}
    for corpus in sorted(set(indexados) | set(q_por_corpus)):
        if corpus not in corpora:
            falha("I12", str(corpus), "corpus sem registro em x-corpora")
            continue
        declarados = corpora[corpus]["registros_declarados"]
        com_unidade = len(indexados.get(corpus, ()))
        contagem[corpus] = {"registros_declarados": declarados,
                            "registros_com_unidade": com_unidade,
                            "registros_em_quarentena": q_por_corpus[corpus],
                            "unidades": sum(1 for u in unidades if u.get("corpus") == corpus),
                            "unidades_em_quarentena": sum(
                                1 for q in quarentena
                                if q.get("unidade_id") and q.get("corpus") == corpus)}
        if com_unidade + q_por_corpus[corpus] != declarados:
            falha("I12", corpus, f"{com_unidade} com unidade + {q_por_corpus[corpus]} em "
                                 f"quarentena ≠ {declarados} declarados")

    return {"esquema_versao": esquema["x-versao"],
            "unidades": len(unidades), "fragmentos": len(fragmentos),
            "quarentena": len(quarentena), "por_corpus": contagem,
            "aprovado": not violacoes,
            "violacoes": dict(sorted(violacoes.items())),
            "exemplos": exemplos}


def exigir(laudo: dict) -> None:
    if not laudo["aprovado"]:
        raise ErroDeEsquema(
            f'índice fora do esquema {laudo["esquema_versao"]}: {laudo["violacoes"]} '
            f'— primeiros casos: {laudo["exemplos"][:3]}')


def main() -> None:
    import datetime

    from . import corpus as corpus_mod
    from . import unidades as unidades_mod

    corpus_mod.verificar_integridade_auxiliar("factckbr")
    unidades, fragmentos, quarentena, manifesto = unidades_mod.construir_indice(
        corpus_mod.ler_corpus(), corpus_mod.ler_factckbr(), validar_esquema=False)
    laudo = validar(unidades, fragmentos, quarentena)
    laudo = {"data": datetime.date.today().isoformat(),
             "change": "mvp-copiloto-verificacao", "task": "1.1, 1.2",
             "esquema": str(ESQUEMA.relative_to(RAIZ)),
             "corpus": [str(corpus_mod.CAMINHO_CORPUS.relative_to(RAIZ)),
                        str(corpus_mod.CAMINHO_FACTCKBR.relative_to(RAIZ))],
             "comando": "python -m prototipo.rag.esquema",
             "disposicoes": {c: m["disposicoes"]
                             for c, m in manifesto["por_corpus"].items()}, **laudo}
    LAUDO.write_text(json.dumps(laudo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in laudo.items() if k != "exemplos"},
                     ensure_ascii=False, indent=2))
    print(f"gravado em {LAUDO.relative_to(RAIZ)}")
    exigir(laudo)


if __name__ == "__main__":
    main()
