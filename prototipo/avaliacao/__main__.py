"""CLI do instrumento de avaliação — task 6.5 de mvp-copiloto-verificacao.

    python -m prototipo.avaliacao modelo --participante P-01 --tipo piloto \\
        --com 3562ed9e,496ecb51,c39a780a --transf 5a13e6ce,2c8828d5
    python -m prototipo.avaliacao validar prototipo/avaliacao/sessoes/*.json
    python -m prototipo.avaliacao metricas [prototipo/avaliacao/sessoes]

`modelo` grava o esqueleto do registro com os casos da sessão na ordem de
apresentação e o hash do conjunto de casos; o pesquisador preenche o resto
durante a sessão. Os ids aceitam prefixo (8 caracteres bastam).

Os registros ficam em `prototipo/avaliacao/sessoes/`, fora do git: são dados
de participante, ainda que anônimos. Só o relatório agregado é versionado.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

from .metricas import COM, TRANSF, agregar, metricas_sessao
from .sessao import CASOS, carregar_casos, validar

PASTA = pathlib.Path(__file__).with_name("sessoes")
RELATORIO = pathlib.Path(__file__).with_name("relatorio_metricas.json")


def _resolver(prefixos: str, casos: dict) -> list[str]:
    ids = []
    for prefixo in filter(None, (p.strip() for p in prefixos.split(","))):
        achados = [cid for cid in casos if cid.startswith(prefixo)]
        if len(achados) != 1:
            raise SystemExit(f"prefixo '{prefixo}' casa com {len(achados)} casos; precisa casar com 1")
        ids.append(achados[0])
    return ids


def _item_vazio(caso_id: str, bloco: str) -> dict:
    com = bloco == COM
    return {"caso_id": caso_id, "bloco": bloco, "inicio": "", "decisao": "",
            "rotulo_exibido": "" if com else None, "expressou_duvida": False if com else None,
            "julgamento": "", "criterios_citados": [], "abriu_detalhe": False,
            "consultou_fonte_externa": False, "abandono": None, "observacao": ""}


def cmd_modelo(args) -> int:
    casos, sha = carregar_casos(args.casos)
    itens = ([_item_vazio(c, COM) for c in _resolver(args.com, casos)]
             + [_item_vazio(c, TRANSF) for c in _resolver(args.transf, casos)])
    registro = {
        "versao_instrumento": "1.0.0", "participante": args.participante, "tipo": args.tipo,
        "data": args.data or dt.date.today().isoformat(), "faixa_etaria": "", "casos_sha256": sha,
        "tcle_assinado": False,
        "confianca_fontes": {"inicio": {"ministerio_saude": 0, "fiocruz": 0, "anvisa": 0},
                             "fim": {"ministerio_saude": 0, "fiocruz": 0, "anvisa": 0}},
        "itens": itens, "abandono_sessao": None, "debriefing_realizado": False,
    }
    destino = pathlib.Path(args.saida or PASTA / f"{args.participante}.json")
    if destino.exists():
        raise SystemExit(f"{destino} já existe; não sobrescrevo registro de sessão")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"modelo gravado em {destino}: {len(itens)} itens")
    return 0


def _arquivos(caminhos: list[str]) -> list[pathlib.Path]:
    saida = []
    for c in caminhos or [str(PASTA)]:
        p = pathlib.Path(c)
        if not p.exists():
            raise SystemExit(f"{p} não existe; grave uma sessão com 'modelo' antes")
        saida.extend(sorted(p.glob("*.json")) if p.is_dir() else [p])
    return saida


def _ler_validar(caminhos, casos, sha):
    validos, excluidos, avisos = [], [], []
    for arquivo in _arquivos(caminhos):
        registro = json.loads(arquivo.read_text(encoding="utf-8"))
        laudo = validar(registro, casos, casos_sha256=sha)
        avisos += [f"{arquivo.name}: {a}" for a in laudo.avisos]
        if laudo.valido:
            validos.append((arquivo, registro))
        else:
            excluidos.append({"arquivo": arquivo.name, "erros": laudo.erros})
    return validos, excluidos, avisos


def cmd_validar(args) -> int:
    casos, sha = carregar_casos(args.casos)
    validos, excluidos, avisos = _ler_validar(args.arquivos, casos, sha)
    for arquivo, _ in validos:
        print(f"ok    {arquivo.name}")
    for x in excluidos:
        print(f"ERRO  {x['arquivo']}")
        for e in x["erros"]:
            print(f"      {e}")
    for a in avisos:
        print(f"aviso {a}")
    return 1 if excluidos else 0


def cmd_metricas(args) -> int:
    casos, sha = carregar_casos(args.casos)
    validos, excluidos, avisos = _ler_validar(args.arquivos, casos, sha)
    registros = [r for _, r in validos]
    relatorio = {
        "gerado_em": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "versao_instrumento": "1.0.0",
        "casos": {"arquivo": str(pathlib.Path(args.casos).resolve().relative_to(CASOS.parents[2])),
                  "sha256": sha},
        "agregado": agregar(registros, casos),
        "sessoes": [metricas_sessao(r, casos) for r in registros],
        "excluidos": excluidos,
        "avisos": avisos,
    }
    destino = pathlib.Path(args.saida)
    destino.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(registros)} sessões, {len(excluidos)} excluídas, {len(avisos)} avisos -> {destino}")
    return 1 if excluidos else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m prototipo.avaliacao")
    p.add_argument("--casos", default=str(CASOS))
    sub = p.add_subparsers(dest="comando", required=True)

    m = sub.add_parser("modelo", help="grava o esqueleto do registro de uma sessão")
    m.add_argument("--participante", required=True)
    m.add_argument("--tipo", choices=["piloto", "coleta"], required=True)
    m.add_argument("--com", required=True, help="casos do bloco com ferramenta, na ordem")
    m.add_argument("--transf", required=True, help="casos do bloco de transferência, na ordem")
    m.add_argument("--data")
    m.add_argument("--saida")
    m.set_defaults(func=cmd_modelo)

    v = sub.add_parser("validar", help="confere registros contra o esquema e as invariantes")
    v.add_argument("arquivos", nargs="*")
    v.set_defaults(func=cmd_validar)

    r = sub.add_parser("metricas", help="calcula as métricas e grava o relatório")
    r.add_argument("arquivos", nargs="*")
    r.add_argument("--saida", default=str(RELATORIO))
    r.set_defaults(func=cmd_metricas)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
