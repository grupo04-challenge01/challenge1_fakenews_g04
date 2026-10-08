"""Bateria da bancada em lote.

    python -m bancada rodar [--offline] [--caso ID ...] [--canal web|whatsapp]
                            [--k 5] [--modo hibrida] [--alfa A] [--limiar L]
                            [--sem-idioma]

Sem `--offline`, usa Ollama e o índice local e grava as saídas em
`bancada/gravacoes/`. Com `--offline`, reproduz essas gravações; caso sem
gravação, ou com prompt alterado, sai com erro no rastro.
O relatório vai para `bancada/relatorios/AAAAMMDD-HHMMSS.json`.

Caso com link traz `pagina`, o nome de um arquivo de
`prototipo/entrada/tests/paginas/`: a busca devolve esse arquivo. A bancada
nunca acessa a rede, nem no modo real (add-entrada-por-link, task 6.1).
"""
import argparse
import json
import pathlib
import sys
import time

from bancada import gravacao
from bancada.avaliacao import avaliar
from bancada.pipeline import executar
from prototipo.entrada import rede
from prototipo.rag.hibrida import LIMIAR_EVIDENCIA

AQUI = pathlib.Path(__file__).parent
CASOS = AQUI / "casos.json"
RELATORIOS = AQUI / "relatorios"
PAGINAS = AQUI.parent / "prototipo/entrada/tests/paginas"


def carregar_casos(arquivo=CASOS):
    return json.loads(pathlib.Path(arquivo).read_text(encoding="utf-8"))


def buscar_do_caso(caso):
    """Busca que devolve a página gravada do caso, depois das regras de URL de `rede`.

    Sem `pagina`, toda busca é recusada: link de caso sem página gravada nunca
    sai para a rede.
    """
    indice = json.loads((PAGINAS / "indice.json").read_text(encoding="utf-8"))

    def buscar(url):
        rede.validar_url(url)
        if "pagina" not in caso:
            raise rede.Recusa("sem página gravada")
        info = indice.get(caso["pagina"], {})
        corpo = (PAGINAS / f"{caso['pagina']}.html").read_bytes()
        return rede.Pagina(corpo, info.get("url_final", url),
                           info.get("tipo", "text/html; charset=utf-8"))
    return buscar


def rodar_caso(caso, chat, recuperador, **parametros):
    rastro = executar(caso["mensagem"], recuperador, chat=chat,
                      lacuna=caso.get("lacuna"), buscar=buscar_do_caso(caso), **parametros)
    checks = avaliar(caso, rastro)
    return {"id": caso["id"], "origem": caso.get("origem"), "nota": caso.get("nota"),
            "passou": all(c["ok"] for c in checks), "checks": checks, "rastro": rastro}


# Critério de aceite revisto (add-gerador-api-deepseek, D10): falha que chega à
# pessoa como veredito sem base, mito repetido, urgência não desviada ou erro é
# eliminatória; as demais têm limite por rodada.
ELIMINATORIAS = ("erro", "rotulo", "fronteira", "mito", "veredito_implicito")
LIMITE_DEMAIS = 3


def _tipo_do_defeito(defeito):
    if defeito.startswith("mito:"):
        return "mito"
    if defeito.startswith(("técnica nomeada", "bloco 3 da forma sem evidência afirma")):
        return "veredito_implicito"
    if defeito.startswith(("camada visível com", "frase com mais de")):
        return "tamanho"
    return "outro_defeito"


def tipos_de_falha(resultado):
    """Tipos das falhas de um caso, para o critério e para acompanhar a taxa."""
    tipos = set()
    for c in resultado["checks"]:
        if c["ok"]:
            continue
        if c["check"] == "sem erro":
            tipos.add("erro")
        elif c["etapa"] == "guarda" and c["check"] == "rótulo":
            tipos.add("rotulo")
        elif c["etapa"] == "fronteira":
            tipos.add("fronteira")
        elif c["check"] == "sem defeitos":
            tipos |= {_tipo_do_defeito(d) for d in c["obtido"] or []}
        else:
            tipos.add("acerto")
    return tipos


def _cortou(resultado):
    """Caso em que o teto da resposta foi garantido por corte (fix-teto-resposta)."""
    etapas = (resultado.get("rastro") or {}).get("etapas") or []
    return any(e["etapa"] == "resposta" and (e.get("saida") or {}).get("cortadas")
               for e in etapas)


def resumir(resultados):
    por_tipo, eliminatorias, demais = {}, [], []
    for r in resultados:
        tipos = tipos_de_falha(r)
        for t in tipos:
            por_tipo.setdefault(t, []).append(r["id"])
        if tipos & set(ELIMINATORIAS):
            eliminatorias.append(r["id"])
        elif tipos:
            demais.append(r["id"])
    por_etapa = {}
    for r in resultados:
        for c in r["checks"]:
            ok, total = por_etapa.get(c["etapa"], (0, 0))
            por_etapa[c["etapa"]] = (ok + c["ok"], total + 1)
    return {"casos": len(resultados),
            "passaram": sum(r["passou"] for r in resultados),
            "por_etapa": {e: f"{ok}/{total}" for e, (ok, total) in por_etapa.items()},
            "por_tipo": {t: sorted(ids) for t, ids in sorted(por_tipo.items())},
            "cortes": sorted(r["id"] for r in resultados if _cortou(r)),
            "criterio": {"eliminatorias": sorted(eliminatorias), "demais": sorted(demais),
                         "cumpre": not eliminatorias and len(demais) <= LIMITE_DEMAIS}}


def escolher_gerador(nome):
    """Gerador real da bancada (add-gerador-api-deepseek, D7). A chave vem do ambiente."""
    from prototipo.verificacao.modelo import ChatDeepSeek, chat_ollama
    return ChatDeepSeek() if nome == "deepseek" else chat_ollama


def descrever_gerador(nome, chat):
    """Gerador e modelo para o relatório; na DeepSeek, o modelo que a API diz ter servido
    e os tokens que ela informou, teste inicial incluído."""
    from prototipo.verificacao.modelo import MODELO
    if nome != "deepseek":
        return {"gerador": nome, "modelo": MODELO}
    return {"gerador": nome, "modelo": getattr(chat, "modelo_servido", None),
            "uso": dict(getattr(chat, "uso", {}))}


def gerador_responde(chat):
    """Uma chamada curta antes do primeiro caso. Falha aqui para a rodada antes de
    qualquer gravação ser sobrescrita (chave recusada em 08/10/2026)."""
    from prototipo.verificacao.modelo import ErroGerador
    try:
        chat('Responda só com o JSON {"ok": true}.', "ok")
    except (ErroGerador, ConnectionError) as e:
        print(f"gerador não respondeu, nada foi rodado nem gravado: {e}", file=sys.stderr)
        return False
    return True


def rodar(args):
    from prototipo.rag.hibrida import ALFA_PADRAO

    casos = carregar_casos()
    if args.caso:
        casos = [c for c in casos if c["id"] in args.caso]
    real_chat = real_rec = None
    if not args.offline:
        from prototipo.rag.__main__ import carregar
        print("carregando índice...", flush=True)
        real_chat = escolher_gerador(args.gerador)
        if not gerador_responde(real_chat):
            return 2
        real_rec = carregar()

    parametros = {"canal": args.canal, "k": args.k, "modo": args.modo,
                  "alfa": args.alfa, "limiar": args.limiar, "idioma": not args.sem_idioma}
    resultados = []
    for caso in casos:
        inicio = time.perf_counter()
        if args.offline:
            chat, rec = gravacao.reproduzindo(gravacao.ler(caso["id"]), alfa=ALFA_PADRAO)
        else:
            dados = gravacao.vazio()
            chat, rec = gravacao.gravando(dados, real_chat, real_rec)
        r = rodar_caso(caso, chat, rec, **parametros)
        if not args.offline:
            gravacao.gravar(caso["id"], dados)
        r["segundos"] = round(time.perf_counter() - inicio, 1)
        resultados.append(r)
        falhas = [f"{c['etapa']}: {c['check']} (obtido {c['obtido']!r})"
                  for c in r["checks"] if not c["ok"]]
        print(f"{'ok ' if r['passou'] else 'FALHA'} {caso['id']}  {r['segundos']} s", flush=True)
        for f in falhas:
            print(f"      {f}"[:220])

    resumo = resumir(resultados)
    gerador = ({"gerador": "gravacao", "modelo": None} if args.offline
               else descrever_gerador(args.gerador, real_chat))
    RELATORIOS.mkdir(exist_ok=True)
    destino = RELATORIOS / f"{time.strftime('%Y%m%d-%H%M%S')}.json"
    destino.write_text(json.dumps({"modo": "offline" if args.offline else "real",
                                   "parametros": {**parametros, **gerador},
                                   "resumo": resumo,
                                   "resultados": resultados},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{resumo['passaram']}/{resumo['casos']} casos  {resumo['por_etapa']}\n{destino}")
    c = resumo["criterio"]
    print(f"critério: eliminatórias {c['eliminatorias'] or 'nenhuma'}, demais {len(c['demais'])}"
          f"/{LIMITE_DEMAIS} {c['demais']}  →  {'cumpre' if c['cumpre'] else 'NÃO cumpre'}")
    print(f"corte de teto: {len(resumo['cortes'])} casos {resumo['cortes']}")
    if "uso" in gerador:
        u = gerador["uso"]
        print(f"tokens: {u['chamadas']} chamadas, entrada {u['entrada']} "
              f"(cache {u['entrada_cache']}), saída {u['saida']}")
    return 0 if resumo["passaram"] == resumo["casos"] else 1


def main():
    p = argparse.ArgumentParser(prog="python -m bancada")
    sub = p.add_subparsers(dest="comando", required=True)
    r = sub.add_parser("rodar")
    r.add_argument("--offline", action="store_true")
    r.add_argument("--gerador", default="ollama", choices=("ollama", "deepseek"),
                   help="modelo real; deepseek lê DEEPSEEK_API_KEY do ambiente")
    r.add_argument("--caso", nargs="*")
    r.add_argument("--canal", default="web", choices=("web", "whatsapp"))
    r.add_argument("--k", type=int, default=5)
    r.add_argument("--modo", default="hibrida", choices=("lexica", "densa", "hibrida"))
    r.add_argument("--alfa", type=float)
    r.add_argument("--limiar", type=float, default=LIMIAR_EVIDENCIA,
                   help=f"piso do score fundido (task 1.5, padrão {LIMIAR_EVIDENCIA})")
    r.add_argument("--sem-idioma", action="store_true",
                   help="ranking cru (`buscar`), sem a prioridade de idioma da task 1.4")
    args = p.parse_args()
    sys.exit(rodar(args))


if __name__ == "__main__":
    main()
