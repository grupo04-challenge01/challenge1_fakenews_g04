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


def resumir(resultados):
    por_etapa = {}
    for r in resultados:
        for c in r["checks"]:
            ok, total = por_etapa.get(c["etapa"], (0, 0))
            por_etapa[c["etapa"]] = (ok + c["ok"], total + 1)
    return {"casos": len(resultados),
            "passaram": sum(r["passou"] for r in resultados),
            "por_etapa": {e: f"{ok}/{total}" for e, (ok, total) in por_etapa.items()}}


def rodar(args):
    from prototipo.rag.hibrida import ALFA_PADRAO

    casos = carregar_casos()
    if args.caso:
        casos = [c for c in casos if c["id"] in args.caso]
    real_chat = real_rec = None
    if not args.offline:
        from prototipo.rag.__main__ import carregar
        from prototipo.verificacao.modelo import chat_ollama
        print("carregando índice...", flush=True)
        real_chat, real_rec = chat_ollama, carregar()

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
    RELATORIOS.mkdir(exist_ok=True)
    destino = RELATORIOS / f"{time.strftime('%Y%m%d-%H%M%S')}.json"
    destino.write_text(json.dumps({"modo": "offline" if args.offline else "real",
                                   "parametros": parametros, "resumo": resumo,
                                   "resultados": resultados},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{resumo['passaram']}/{resumo['casos']} casos  {resumo['por_etapa']}\n{destino}")
    return 0 if resumo["passaram"] == resumo["casos"] else 1


def main():
    p = argparse.ArgumentParser(prog="python -m bancada")
    sub = p.add_subparsers(dest="comando", required=True)
    r = sub.add_parser("rodar")
    r.add_argument("--offline", action="store_true")
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
