"""Reexecução dos artefatos do tratamento — `python -m tratamento <comando>`.

Todo número que aparece na documentação do change sai daqui. A declaração de
cobertura, o laudo de integridade e o relatório de veredito são artefatos
gerados, não texto escrito à mão: `frescor-corpus` exige que a cobertura seja
verificável por reexecução da busca.
"""
from __future__ import annotations

import json
import sys

from tratamento import criterios, frescor, integridade, relatorios

COMANDOS = {
    "frescor": lambda: frescor.gravar(),
    "integridade": lambda: integridade.gravar_laudo(),
    "vereditos": lambda: relatorios.gravar(),
    "criterios": lambda: criterios.gravar(),
}


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0] not in COMANDOS:
        print(f"uso: python -m tratamento [{'|'.join(COMANDOS)}|tudo]",
              file=sys.stderr)
        return 2

    resultado = COMANDOS[argv[0]]()
    print(json.dumps(resultado, ensure_ascii=False, indent=2)[:2000])
    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    if argv == ["tudo"]:
        for nome, acao in COMANDOS.items():
            acao()
            print(f"gerado: {nome}")
        raise SystemExit(0)
    raise SystemExit(main(argv))
