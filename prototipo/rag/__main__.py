"""CLI da prova de conceito de recuperação — tasks 2.2 a 2.5.

    python -m prototipo.rag construir [--modelo NOME]
    python -m prototipo.rag buscar "consulta" [--modo lexica|densa|hibrida]
                                              [--fusao score|rrf] [--k 10]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

from . import corpus as corpus_mod
from . import unidades as unidades_mod
from .densa import MODELO_PADRAO, IndiceDenso
from .hibrida import ALFA_PADRAO, PERCENTIL_FUNDO, PERCENTIL_TOPO, Recuperador
from .lexica import IndiceLexico

SAIDA = unidades_mod.SAIDA
MATRIZ = SAIDA / "densa.npy"


def _ler_jsonl(caminho: pathlib.Path) -> list[dict]:
    with caminho.open(encoding="utf-8") as arquivo:
        return [json.loads(linha) for linha in arquivo]


def construir(args) -> None:
    inicio = time.perf_counter()
    laudo = corpus_mod.verificar_integridade_textual()
    df = corpus_mod.ler_corpus()
    unidades, fragmentos, quarentena, manifesto = unidades_mod.construir(df)

    SAIDA.mkdir(parents=True, exist_ok=True)
    unidades_mod._gravar(SAIDA / "unidades.jsonl", unidades)
    unidades_mod._gravar(SAIDA / "fragmentos.jsonl", fragmentos)
    unidades_mod._gravar(SAIDA / "quarentena.jsonl", quarentena)

    marca = time.perf_counter()
    IndiceLexico(fragmentos)
    custo_lexico = time.perf_counter() - marca

    marca = time.perf_counter()
    denso = IndiceDenso.construir(fragmentos, args.modelo)
    custo_denso = time.perf_counter() - marca
    denso.gravar(MATRIZ)

    manifesto.update({
        "integridade_textual": laudo,
        "modelo_embedding": args.modelo,
        "dimensao": int(denso.matriz.shape[1]),
        "custo_indexacao_s": {"lexico": round(custo_lexico, 2),
                              "denso": round(custo_denso, 2),
                              "total": round(time.perf_counter() - inicio, 2)},
        "fusao_padrao": {"forma": "combinação convexa de scores realçados contra "
                                  "o fundo da própria consulta",
                         "alfa": ALFA_PADRAO, "percentil_fundo": PERCENTIL_FUNDO,
                         "percentil_topo": PERCENTIL_TOPO,
                         "provisorio": "alfa é fixado por medição na task 3.1; o "
                                       "limiar de evidência insuficiente, na 3.5"},
    })
    (SAIDA / "manifesto.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifesto, ensure_ascii=False, indent=2))


def carregar(modelo: str = MODELO_PADRAO, alfa: float = ALFA_PADRAO) -> Recuperador:
    if not MATRIZ.exists():
        sys.exit("índice ausente — rode `python -m prototipo.rag construir` antes.")
    fragmentos = _ler_jsonl(SAIDA / "fragmentos.jsonl")
    unidades = _ler_jsonl(SAIDA / "unidades.jsonl")
    return Recuperador(fragmentos, unidades, IndiceLexico(fragmentos),
                       IndiceDenso.carregar(MATRIZ, modelo), alfa=alfa)


def buscar(args) -> None:
    recuperador = carregar(args.modelo, args.alfa)
    inicio = time.perf_counter()
    achados = recuperador.buscar(args.consulta, k=args.k, modo=args.modo,
                                 fusao=args.fusao)
    custo = (time.perf_counter() - inicio) * 1000

    print(f'consulta: {args.consulta!r}  modo={args.modo}  {custo:.0f} ms\n')
    for posicao, achado in enumerate(achados, 1):
        marca = "  [unidade cobre mais de uma alegação]" if achado["cobre_multiplas_alegacoes"] else ""
        print(f'{posicao:2d}. {achado["score"]:.4f}  '
              f'(lex {achado["score_lexico"]:6.2f} | den {achado["score_denso"]:.3f})  '
              f'[{achado["veredito_original"]}] {achado["agencia"]}, '
              f'{achado["data_publicacao"]}{marca}')
        print(f'    {achado["alegacao"][:110]}')
        print(f'    {achado["url"]}')


def aferir(args) -> None:
    """Mede recall das três configurações sobre o conjunto da task 2.6."""
    from . import afericao

    matriz = _matriz_de(args.modelo)
    if not matriz.exists():
        fragmentos = _ler_jsonl(SAIDA / "fragmentos.jsonl")
        print(f"matriz de {args.modelo} ausente — construindo", flush=True)
        marca = time.perf_counter()
        IndiceDenso.construir(fragmentos, args.modelo).gravar(matriz)
        print(f"indexação: {time.perf_counter() - marca:.1f} s", flush=True)

    fragmentos = _ler_jsonl(SAIDA / "fragmentos.jsonl")
    unidades = _ler_jsonl(SAIDA / "unidades.jsonl")
    recuperador = Recuperador(fragmentos, unidades, IndiceLexico(fragmentos),
                              IndiceDenso.carregar(matriz, args.modelo),
                              alfa=args.alfa)

    resultado = afericao.aferir_tudo(recuperador)
    destino = SAIDA / f"afericao_{args.modelo.split('/')[-1]}.json"
    destino.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps(resultado["por_modo"], ensure_ascii=False, indent=2))
    print(f"gravado em {destino}")


def _matriz_de(modelo: str) -> pathlib.Path:
    """Uma matriz por modelo: comparar dois modelos exige guardar os dois."""
    if modelo == MODELO_PADRAO:
        return MATRIZ
    return SAIDA / f"densa_{modelo.split('/')[-1]}.npy"


def main() -> None:
    analisador = argparse.ArgumentParser(prog="prototipo.rag")
    sub = analisador.add_subparsers(dest="comando", required=True)

    c = sub.add_parser("construir", help="constrói unidades, índice léxico e denso")
    c.add_argument("--modelo", default=MODELO_PADRAO)
    c.set_defaults(func=construir)

    b = sub.add_parser("buscar", help="consulta o índice")
    b.add_argument("consulta")
    b.add_argument("--modo", default="hibrida", choices=Recuperador.MODOS)
    b.add_argument("--fusao", default="score", choices=("score", "rrf"))
    b.add_argument("--k", type=int, default=10)
    b.add_argument("--alfa", type=float, default=ALFA_PADRAO)
    b.add_argument("--modelo", default=MODELO_PADRAO)
    b.set_defaults(func=buscar)

    a = sub.add_parser("aferir", help="mede recall das três configurações (task 3.1)")
    a.add_argument("--modelo", default=MODELO_PADRAO)
    a.add_argument("--alfa", type=float, default=ALFA_PADRAO)
    a.set_defaults(func=aferir)

    args = analisador.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
