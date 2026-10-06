"""CLI da prova de conceito de recuperação — tasks 2.2 a 2.5.

    python -m prototipo.rag construir [--modelo NOME] [--estender]
    python -m prototipo.rag buscar "consulta" [--modo lexica|densa|hibrida]   (com prioridade de idioma, task 1.4)
                                              [--fusao score|rrf] [--k 10]
    python -m prototipo.rag aferir [--modelo NOME] [--alfa 0.9]
    python -m prototipo.rag varrer-alfa [--modelo NOME]
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


def _etapa(mensagem: str) -> None:
    """Aviso de etapa em stderr. O stdout fica só com o manifesto, no final."""
    print(f"[{time.strftime('%H:%M:%S')}] {mensagem}", file=sys.stderr, flush=True)


def _prefixo_reaproveitavel(fragmentos: list[dict]) -> int:
    """Quantas linhas da matriz densa gravada continuam válidas.

    Só o prefixo idêntico, por id e por texto, na mesma ordem. Qualquer
    divergência devolve 0 e força a reconstrução inteira: vetor desalinhado de
    fragmento é erro silencioso de recuperação (decisão 16).
    """
    import numpy as np

    antigos_caminho = SAIDA / "fragmentos.jsonl"
    if not (MATRIZ.exists() and antigos_caminho.exists()):
        return 0
    antigos = _ler_jsonl(antigos_caminho)
    linhas = np.load(MATRIZ, mmap_mode="r").shape[0]
    if linhas != len(antigos) or len(antigos) > len(fragmentos):
        return 0
    for velho, novo in zip(antigos, fragmentos):
        if velho["fragmento_id"] != novo["fragmento_id"] or velho["texto"] != novo["texto"]:
            return 0
    return len(antigos)


def construir(args) -> None:
    import numpy as np

    inicio = time.perf_counter()
    _etapa("1/4 portões de entrada: integridade textual e leitura dos corpora")
    laudo = corpus_mod.verificar_integridade_textual()
    laudo_fb = corpus_mod.verificar_integridade_auxiliar("factckbr")
    df = corpus_mod.ler_corpus()
    df_fb = corpus_mod.ler_factckbr()
    _etapa(f"2/4 unidades e fragmentos de {len(df)} registros do FactCenter e "
           f"{len(df_fb)} linhas do FACTCK.BR, com validação do esquema")
    unidades, fragmentos, quarentena, manifesto = unidades_mod.construir_indice(df, df_fb)
    _etapa(f"    {len(unidades)} unidades, {len(fragmentos)} fragmentos, "
           f"{len(quarentena)} em quarentena — esquema {manifesto['esquema']['versao']} aprovado")

    # Antes de sobrescrever os .jsonl: o prefixo reaproveitável é medido contra
    # os fragmentos que estão em disco junto com a matriz.
    reaproveitar = _prefixo_reaproveitavel(fragmentos) if args.estender else 0
    if args.estender and not reaproveitar:
        sys.exit("--estender recusado: a matriz gravada não corresponde a um prefixo "
                 "idêntico dos fragmentos novos. Rode `construir` sem --estender.")

    SAIDA.mkdir(parents=True, exist_ok=True)
    unidades_mod._gravar(SAIDA / "unidades.jsonl", unidades)
    unidades_mod._gravar(SAIDA / "fragmentos.jsonl", fragmentos)
    unidades_mod._gravar(SAIDA / "quarentena.jsonl", quarentena)

    _etapa("3/4 índice léxico (BM25)")
    marca = time.perf_counter()
    IndiceLexico(fragmentos)
    custo_lexico = time.perf_counter() - marca

    marca = time.perf_counter()
    if reaproveitar:
        _etapa(f"4/4 índice denso com {args.modelo}: {reaproveitar} linhas "
               f"reaproveitadas, {len(fragmentos) - reaproveitar} fragmentos novos")
        prefixo = np.load(MATRIZ)
        partes = [prefixo]
        if reaproveitar < len(fragmentos):
            partes.append(IndiceDenso.construir(fragmentos[reaproveitar:], args.modelo).matriz)
        denso = IndiceDenso(np.ascontiguousarray(
            np.concatenate(partes).astype("float32")), args.modelo)
    else:
        _etapa(f"4/4 índice denso com {args.modelo}: a etapa longa (883 s no M4 em "
               "18/09). Na primeira vez nesta máquina o modelo (~1 GB) é baixado antes "
               "da barra de progresso aparecer")
        denso = IndiceDenso.construir(fragmentos, args.modelo)
    if denso.matriz.shape[0] != len(fragmentos):
        sys.exit(f"matriz com {denso.matriz.shape[0]} linhas para {len(fragmentos)} "
                 "fragmentos — nada gravado")
    custo_denso = time.perf_counter() - marca
    denso.gravar(MATRIZ)
    _etapa(f"índice denso gravado em {MATRIZ.name} "
           f"({time.perf_counter() - marca:.0f} s); manifesto a seguir")

    if reaproveitar:
        manifesto["matriz_densa"] = (
            f"estendida por `python -m prototipo.rag construir --estender` em "
            f"{time.strftime('%d/%m/%Y')}: {reaproveitar} linhas do FactCenter "
            "reaproveitadas após conferência de id e texto na mesma ordem, e "
            f"{len(fragmentos) - reaproveitar} linhas novas do FACTCK.BR — decisão 17 "
            "de mvp-copiloto-verificacao")
    manifesto.update({
        "integridade_textual": laudo,
        "integridade_textual_factckbr": laudo_fb,
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


def conferir_indice(fragmentos: list[dict], denso: IndiceDenso,
                    matriz: pathlib.Path) -> IndiceDenso:
    """Portão de carga: a matriz densa tem uma linha por fragmento, na mesma ordem.

    `fragmentos.jsonl` e as `.npy` não são versionados, então cada máquina tem os
    seus. Rodar só `python -m prototipo.rag.unidades` sobre uma matriz antiga
    desalinha fragmento e vetor, e a busca densa devolve o fragmento vizinho sem
    erro nenhum (decisão 16 de mvp-copiloto-verificacao). Linhas a mais ou a
    menos param a carga; índice anterior ao esquema só gera aviso.
    """
    linhas = denso.matriz.shape[0]
    if linhas != len(fragmentos):
        sys.exit(f"índice desalinhado: {matriz.name} tem {linhas} linhas e "
                 f"fragmentos.jsonl tem {len(fragmentos)} fragmentos — rode "
                 "`python -m prototipo.rag construir` para reconstruir os dois juntos.")
    if fragmentos and "corpus" not in fragmentos[0]:
        print("aviso: índice anterior ao esquema de indexação 1.0.0 (fragmentos "
              "sem `corpus`) — rode `python -m prototipo.rag construir` para "
              "atualizar.", file=sys.stderr, flush=True)
    return denso


def carregar(modelo: str = MODELO_PADRAO, alfa: float = ALFA_PADRAO) -> Recuperador:
    if not MATRIZ.exists():
        sys.exit("índice ausente — rode `python -m prototipo.rag construir` antes.")
    fragmentos = _ler_jsonl(SAIDA / "fragmentos.jsonl")
    unidades = _ler_jsonl(SAIDA / "unidades.jsonl")
    denso = conferir_indice(fragmentos, IndiceDenso.carregar(MATRIZ, modelo), MATRIZ)
    return Recuperador(fragmentos, unidades, IndiceLexico(fragmentos), denso, alfa=alfa)


def buscar(args) -> None:
    recuperador = carregar(args.modelo, args.alfa)
    inicio = time.perf_counter()
    # A CLI consulta como o sistema consulta: com a prioridade de idioma da
    # task 1.4. A aferição continua sobre o ranking cru de `buscar`.
    recuperacao = recuperador.recuperar(args.consulta, k=args.k, modo=args.modo,
                                        fusao=args.fusao)
    achados = recuperacao.resultados
    custo = (time.perf_counter() - inicio) * 1000

    print(f'consulta: {args.consulta!r}  modo={args.modo}  {custo:.0f} ms')
    print(f'camada: {recuperacao.idioma}  consultadas: {", ".join(recuperacao.consultados)}  '
          f'coberto: {"sim" if recuperacao.coberto else "não"}\n')
    for posicao, achado in enumerate(achados, 1):
        marca = "  [unidade cobre mais de uma alegação]" if achado["cobre_multiplas_alegacoes"] else ""
        print(f'{posicao:2d}. {achado["score"]:.4f}  '
              f'(lex {achado["score_lexico"]:6.2f} | den {achado["score_denso"]:.3f})  '
              f'[{achado["veredito_original"]}] {achado["agencia"]}, '
              f'{achado["data_publicacao"]}, {achado["idioma"]}{marca}')
        print(f'    {achado["alegacao"][:110]}')
        print(f'    {achado["url"]}')


def _recuperador_de(modelo: str, alfa: float = ALFA_PADRAO) -> Recuperador:
    """Monta o recuperador, construindo a matriz densa só se ela faltar.

    A matriz é o custo caro (883 s para o `e5-base`) e não depende do conjunto
    de aferição. Reconstruí-la a cada medição desperdiçaria a única parte que
    já está paga.
    """
    matriz = _matriz_de(modelo)
    fragmentos = _ler_jsonl(SAIDA / "fragmentos.jsonl")
    if not matriz.exists():
        print(f"matriz de {modelo} ausente — construindo", flush=True)
        marca = time.perf_counter()
        IndiceDenso.construir(fragmentos, modelo).gravar(matriz)
        print(f"indexação: {time.perf_counter() - marca:.1f} s", flush=True)

    unidades = _ler_jsonl(SAIDA / "unidades.jsonl")
    denso = conferir_indice(fragmentos, IndiceDenso.carregar(matriz, modelo), matriz)
    return Recuperador(fragmentos, unidades, IndiceLexico(fragmentos), denso, alfa=alfa)


def varrer_alfa(args) -> None:
    """Task 3.1 — varre o peso do braço denso e valida o ótimo.

    Separado de `aferir` porque responde outra pergunta. `aferir` compara três
    arquiteturas num alfa; esta compara alfas numa arquitetura, e é ela que diz
    se o alfa fixado em `hibrida.py` se sustenta neste modelo.
    """
    from . import afericao

    recuperador = _recuperador_de(args.modelo)
    resultado = afericao.varrer_alfa(recuperador)

    destino = SAIDA / f"varredura_alfa_{args.modelo.split('/')[-1]}.json"
    destino.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    for alfa in resultado["alfas"]:
        medida = resultado["por_alfa"][str(alfa)]
        print(f"alfa={alfa:<5} recall@5={medida['recall']['@5']:<5} "
              f"mrr={medida['mrr']:<6} perdidos={medida['nao_encontrados']}")
    loo = resultado["leave_one_out"]
    print(f"\nmelhor alfa: {resultado['melhor_alfa']} | "
          f"platô dentro de 0,01: {resultado['dentro_de_0_01_do_topo']}")
    print(f"leave-one-out: híbrida {loo['mrr_validado']} vs "
          f"densa pura {loo['mrr_densa_pura']}")
    print(resultado["leitura"])
    print(f"gravado em {destino}")


def aferir(args) -> None:
    """Mede recall das três configurações sobre o conjunto da task 2.6."""
    from . import afericao

    recuperador = _recuperador_de(args.modelo, args.alfa)

    resultado = afericao.aferir_tudo(recuperador)
    resultado["calibracao_do_limiar"] = afericao.calibrar_limiar(recuperador)
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
    c.add_argument("--estender", action="store_true",
                   help="reaproveita a matriz densa gravada quando ela é prefixo "
                        "idêntico dos fragmentos novos; só calcula os vetores que faltam")
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

    v = sub.add_parser("varrer-alfa",
                       help="varre o peso do braço denso e valida o ótimo (task 3.1)")
    v.add_argument("--modelo", default=MODELO_PADRAO)
    v.set_defaults(func=varrer_alfa)

    args = analisador.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
