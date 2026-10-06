"""Task 1.6 de mvp-copiloto-verificacao: a busca entrega `apto_citacao`.

Decisão 17 do design.md: o FACTCK.BR está no índice com `apto_citacao=false`,
e a ancoragem MUST descartar como âncora todo fragmento nessa condição. Para
isso a marca precisa sair da busca junto com o trecho — até aqui ela ficava no
índice e `_reduzir` a deixava para trás.

A busca só entrega a marca; quem decide o que fazer com ela é a ancoragem.
"""
import pathlib

import numpy as np
import pytest

from prototipo.rag.hibrida import Recuperador

INDICE = pathlib.Path(__file__).resolve().parents[2] / "indice"


class _Braco:
    def __init__(self, scores):
        self.scores = np.asarray(scores, dtype="float32")

    def pontuar(self, consulta):
        return self.scores


def _recuperador(aptos):
    fragmentos, unidades = [], []
    for i, apto in enumerate(aptos):
        uid = f"u{i:02d}"
        fragmento = {"fragmento_id": f"{uid}-00", "unidade_id": uid, "idioma": "pt-BR",
                     "trecho": f"trecho {i}"}
        if apto is not None:
            fragmento["apto_citacao"] = apto
        fragmentos.append(fragmento)
        unidades.append({"unidade_id": uid, "agencia": "AGENCIA", "data_publicacao": "2020-01-01",
                         "url": f"https://exemplo.org/{i}", "alegacao": f"alegação {i}",
                         "veredito_original": "Falso", "veredito_chave": "falso",
                         "cobre_multiplas_alegacoes": False})
    denso = [1.0 - i / 10 for i in range(len(aptos))]
    return Recuperador(fragmentos, unidades, _Braco([0.0] * len(aptos)), _Braco(denso))


def test_buscar_entrega_a_marca_de_cada_fragmento():
    achados = _recuperador([True, False, True]).buscar("q", k=3, modo="densa")
    assert [r["apto_citacao"] for r in achados] == [True, False, True]


def test_recuperar_entrega_a_marca_de_cada_fragmento():
    achados = _recuperador([False, True]).recuperar("q", k=2, modo="densa").resultados
    assert [r["apto_citacao"] for r in achados] == [False, True]


def test_indice_sem_a_marca_entrega_none_e_nao_inventa_valor():
    # Índice anterior ao esquema 1.0.0. A busca não supõe que o trecho é citável;
    # deixa a ausência visível para a ancoragem recusar.
    achados = _recuperador([None]).buscar("q", k=1, modo="densa")
    assert achados[0]["apto_citacao"] is None


@pytest.mark.skipif(not (INDICE / "fragmentos.jsonl").exists(), reason="índice não construído")
def test_no_indice_real_so_o_factckbr_e_inapto():
    import json

    inaptos = set()
    with (INDICE / "fragmentos.jsonl").open(encoding="utf-8") as f:
        for linha in f:
            frag = json.loads(linha)
            assert isinstance(frag["apto_citacao"], bool)
            if not frag["apto_citacao"]:
                inaptos.add(frag["corpus"])
    assert inaptos == {"factckbr"}
