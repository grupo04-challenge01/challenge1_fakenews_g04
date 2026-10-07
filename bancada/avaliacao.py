"""Compara o rastro com o esperado do caso, etapa por etapa.

Chaves aceitas em `esperado`, todas opcionais:

- `fronteira`: categoria esperada em primeiro lugar;
- `verificavel`: se a extração acha alegação de saúde;
- `alegacao_contem`: palavras que a alegação selecionada tem de ter;
- `unidade_no_topo`: `unidade_id` (ou lista de equivalentes) que a recuperação tem de trazer no top-k;
- `rotulo`: rótulo da guarda, ou lista de rótulos aceitos;
- `forma`: forma da resposta (`com evidência`, `sem evidência`, `fronteira`, `leitura`);
- `leitura`: causa da falha de leitura (`nao_abriu`, `fechada`, `video`, `vazia`) ou,
  quando a página foi lida, `completa` ou `parcial` (add-entrada-por-link).

Resposta com defeito e etapa com erro reprovam sempre, sem precisar de chave.
"""
import unicodedata

from bancada.pipeline import etapa_de


def _normal(texto):
    return "".join(c for c in unicodedata.normalize("NFD", (texto or "").lower())
                   if unicodedata.category(c) != "Mn")


def _check(etapa, nome, esperado, obtido, ok):
    return {"etapa": etapa, "check": nome, "esperado": esperado, "obtido": obtido, "ok": bool(ok)}


def avaliar(caso, rastro):
    esp = caso.get("esperado", {})
    checks = []
    saida = {e["etapa"]: e.get("saida") for e in rastro["etapas"]}

    for e in rastro["etapas"]:
        if "erro" in e:
            checks.append(_check(e["etapa"], "sem erro", None, e["erro"], False))

    if "fronteira" in esp:
        cats = (saida.get("fronteira") or {}).get("categorias") or []
        checks.append(_check("fronteira", "primeira categoria", esp["fronteira"],
                             cats[0] if cats else None, cats[:1] == [esp["fronteira"]]))

    ext = saida.get("extracao")
    if "verificavel" in esp:
        obtido = None if etapa_de(rastro, "extracao") is None else bool(ext and ext["selecionada"])
        checks.append(_check("extracao", "verificável", esp["verificavel"], obtido,
                             obtido == esp["verificavel"]))
    if "alegacao_contem" in esp:
        alegacao = ((ext or {}).get("selecionada") or {}).get("texto")
        faltam = [p for p in esp["alegacao_contem"] if _normal(p) not in _normal(alegacao)]
        checks.append(_check("extracao", "alegação contém", esp["alegacao_contem"], alegacao,
                             alegacao and not faltam))

    if "unidade_no_topo" in esp:
        ids = [t["unidade_id"] for t in (saida.get("recuperacao") or {}).get("resultados", [])]
        aceitas = esp["unidade_no_topo"] if isinstance(esp["unidade_no_topo"], list) else [esp["unidade_no_topo"]]
        posicao = next((n for n, u in enumerate(ids, 1) if u in aceitas), None)
        checks.append(_check("recuperacao", "unidade no top-k", aceitas, posicao, posicao is not None))

    if "rotulo" in esp:
        aceitos = esp["rotulo"] if isinstance(esp["rotulo"], list) else [esp["rotulo"]]
        rotulo = (saida.get("guarda") or {}).get("rotulo")
        checks.append(_check("guarda", "rótulo", aceitos, rotulo, rotulo in aceitos))

    resposta = rastro.get("resposta")
    if "leitura" in esp:
        origem = rastro.get("origem") or {}
        if (resposta or {}).get("forma") == "leitura":
            obtido = resposta["causa"]
        elif origem.get("tipo") == "pagina":
            obtido = "parcial" if origem.get("parcial") else "completa"
        else:
            obtido = origem.get("tipo")
        checks.append(_check("leitura", "leitura", esp["leitura"], obtido,
                             obtido == esp["leitura"]))
    if "forma" in esp:
        forma = (resposta or {}).get("forma")
        checks.append(_check("resposta", "forma", esp["forma"], forma, forma == esp["forma"]))
    if resposta and resposta.get("forma") not in ("fronteira", "leitura"):
        checks.append(_check("resposta", "sem defeitos", [], resposta["defeitos"],
                             not resposta["defeitos"]))
    return checks
