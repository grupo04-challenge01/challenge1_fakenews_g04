"""Portão de carga do índice: matriz densa e fragmentos têm de andar juntos."""
import pathlib

import numpy as np
import pytest

from prototipo.rag.__main__ import conferir_indice
from prototipo.rag.densa import IndiceDenso

MATRIZ = pathlib.Path("densa.npy")


def _denso(linhas: int) -> IndiceDenso:
    return IndiceDenso(np.zeros((linhas, 4), dtype="float32"), "modelo-falso")


def _fragmentos(n: int, corpus: bool = True) -> list[dict]:
    extra = {"corpus": "factcenter_saude"} if corpus else {}
    return [{"fragmento_id": f"f{i}", **extra} for i in range(n)]


def test_indice_alinhado_passa(capsys):
    denso = _denso(3)
    assert conferir_indice(_fragmentos(3), denso, MATRIZ) is denso
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("linhas", [2, 4])
def test_matriz_desalinhada_para_a_carga(linhas):
    with pytest.raises(SystemExit, match="índice desalinhado"):
        conferir_indice(_fragmentos(3), _denso(linhas), MATRIZ)


def test_indice_anterior_ao_esquema_so_avisa(capsys):
    conferir_indice(_fragmentos(3, corpus=False), _denso(3), MATRIZ)
    assert "anterior ao esquema" in capsys.readouterr().err
