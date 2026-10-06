"""Task 1.4 de mvp-copiloto-verificacao: recuperação com prioridade de idioma.

`recuperacao-evidencia` manda esgotar as fontes em português antes de recorrer
às fontes em inglês. Decisão 23 do design.md: a consulta é pontuada uma vez
sobre o índice inteiro, e as camadas de idioma são cortes desse mesmo score. O
critério de que uma camada «cobre» a alegação é parâmetro; o valor é da task 1.5.
"""
import json
import pathlib

import numpy as np
import pytest

from prototipo.rag.hibrida import (PRIORIDADE_IDIOMA, Recuperacao, Recuperador,
                                   cobertura_padrao)

RAIZ = pathlib.Path(__file__).resolve().parents[3]
ESQUEMA = RAIZ / "prototipo" / "indice" / "esquema_indexacao.json"
INDICE = RAIZ / "prototipo" / "indice"
CONSULTAS = RAIZ / "prototipo" / "rag" / "consultas_afericao.json"


class _Braco:
    """Braço falso: devolve scores fixos e conta quantas vezes foi consultado."""

    def __init__(self, scores):
        self.scores = np.asarray(scores, dtype="float32")
        self.chamadas = 0

    def pontuar(self, consulta):
        self.chamadas += 1
        return self.scores


def _recuperador(idiomas, denso, lexico=None):
    fragmentos, unidades = [], []
    for i, idioma in enumerate(idiomas):
        uid = f"u{i:02d}"
        fragmento = {"fragmento_id": f"{uid}-00", "unidade_id": uid, "trecho": f"trecho {i}"}
        if idioma is not None:
            fragmento["idioma"] = idioma
        fragmentos.append(fragmento)
        unidades.append({"unidade_id": uid, "agencia": "AGENCIA", "data_publicacao": "2020-01-01",
                         "url": f"https://exemplo.org/{i}", "alegacao": f"alegação {i}",
                         "veredito_original": "Falso", "veredito_chave": "falso",
                         "cobre_multiplas_alegacoes": False})
    lexico = lexico if lexico is not None else [0.0] * len(idiomas)
    return Recuperador(fragmentos, unidades, _Braco(lexico), _Braco(denso))


# Dez fragmentos; o de maior score denso é o único em inglês.
IDIOMAS = ["pt-BR", "pt-BR", "en", "pt-BR", "pt-BR", "en", "pt-BR", "pt-BR", "pt-BR", "pt-BR"]
DENSO = [0.80, 0.70, 0.95, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10, 0.05]


def _idiomas_de(resultados):
    return [r["idioma"] for r in resultados]


# Contrato -----------------------------------------------------------------

def test_prioridade_e_os_idiomas_do_esquema_na_ordem_da_spec():
    esquema = json.loads(ESQUEMA.read_text(encoding="utf-8"))
    assert PRIORIDADE_IDIOMA == ("pt-BR", "en")
    assert set(PRIORIDADE_IDIOMA) == set(esquema["definitions"]["idioma"]["enum"])


def test_resultado_traz_o_idioma_do_fragmento():
    achados = _recuperador(IDIOMAS, DENSO).buscar("q", k=10, modo="densa")
    assert {r["idioma"] for r in achados} == {"pt-BR", "en"}


def test_cobertura_padrao_e_ter_ao_menos_uma_unidade():
    assert cobertura_padrao([{"unidade_id": "u"}]) is True
    assert cobertura_padrao([]) is False


# Cenário «Alegação já checada em português» -------------------------------

def test_pt_cobre_e_nenhuma_fonte_em_ingles_entra():
    recuperador = _recuperador(IDIOMAS, DENSO)
    # Sem a prioridade, o inglês abriria a lista.
    assert recuperador.buscar("q", k=3, modo="densa")[0]["idioma"] == "en"

    recuperacao = recuperador.recuperar("q", k=3, modo="densa")
    assert isinstance(recuperacao, Recuperacao)
    assert recuperacao.idioma == "pt-BR"
    assert recuperacao.coberto is True
    assert recuperacao.consultados == ("pt-BR",)
    assert _idiomas_de(recuperacao.resultados) == ["pt-BR"] * 3
    assert [r["unidade_id"] for r in recuperacao.resultados] == ["u00", "u01", "u03"]


# Recurso ao inglês --------------------------------------------------------

def test_pt_nao_cobre_e_a_recuperacao_recorre_ao_ingles():
    recuperador = _recuperador(IDIOMAS, DENSO)
    todos = {r["unidade_id"]: r["score"] for r in recuperador.buscar("q", k=10, modo="densa")}
    corte = (todos["u02"] + todos["u00"]) / 2   # entre o melhor EN e o melhor PT
    vistos = []

    def limiar(resultados):
        vistos.append(_idiomas_de(resultados))
        return bool(resultados) and resultados[0]["score"] >= corte

    recuperacao = recuperador.recuperar("q", k=3, modo="densa", cobre=limiar)
    assert vistos[0] == ["pt-BR"] * 3          # o PT é julgado primeiro
    assert recuperacao.idioma == "en"
    assert recuperacao.coberto is True
    assert recuperacao.consultados == ("pt-BR", "en")
    assert [r["unidade_id"] for r in recuperacao.resultados] == ["u02", "u05"]


def test_nenhuma_camada_cobre_devolve_o_pt_marcado_como_descoberto():
    recuperacao = _recuperador(IDIOMAS, DENSO).recuperar(
        "q", k=3, modo="densa", cobre=lambda resultados: False)
    assert recuperacao.coberto is False
    assert recuperacao.idioma == "pt-BR"
    assert recuperacao.consultados == ("pt-BR", "en")
    assert _idiomas_de(recuperacao.resultados) == ["pt-BR"] * 3


def test_indice_sem_ingles_nao_consulta_o_ingles():
    recuperacao = _recuperador(["pt-BR"] * 4, [0.4, 0.3, 0.2, 0.1]).recuperar(
        "q", k=2, modo="densa", cobre=lambda resultados: False)
    assert recuperacao.consultados == ("pt-BR",)
    assert recuperacao.coberto is False
    assert recuperacao.idioma == "pt-BR"


def test_camada_cortada_mantem_a_escala_do_score():
    """O inglês não é renormalizado entre si: o limiar da 1.5 vale nas duas camadas."""
    recuperador = _recuperador(IDIOMAS, DENSO)
    todos = {r["unidade_id"]: r["score"] for r in recuperador.buscar("q", k=10, modo="densa")}
    recuperacao = recuperador.recuperar("q", k=3, modo="densa",
                                        cobre=lambda r: bool(r) and r[0]["idioma"] == "en")
    assert {r["unidade_id"]: r["score"] for r in recuperacao.resultados} == \
        {uid: todos[uid] for uid in ("u02", "u05")}


def test_consulta_e_pontuada_uma_vez_mesmo_recorrendo_ao_ingles():
    recuperador = _recuperador(IDIOMAS, DENSO, lexico=DENSO[::-1])
    recuperador.recuperar("q", k=3, cobre=lambda resultados: False)
    assert recuperador.lexico.chamadas == 1
    assert recuperador.denso.chamadas == 1


# Regressão: com o índice de hoje, só em português, nada muda ---------------

@pytest.mark.parametrize("modo,fusao", [("lexica", "score"), ("densa", "score"),
                                        ("hibrida", "score"), ("hibrida", "rrf")])
def test_indice_so_pt_devolve_o_mesmo_que_a_busca(modo, fusao):
    gerador = np.random.default_rng(14)
    # Valores repetidos de propósito: empate é onde uma ordenação diferente apareceria.
    denso = gerador.choice([0.1, 0.2, 0.3, 0.5, 0.8], size=300)
    lexico = gerador.choice([0.0, 1.0, 3.0, 7.0], size=300)
    recuperador = _recuperador(["pt-BR"] * 300, denso, lexico)
    esperado = recuperador.buscar("q", k=10, modo=modo, fusao=fusao)
    recuperacao = recuperador.recuperar("q", k=10, modo=modo, fusao=fusao)
    assert recuperacao.resultados == esperado
    assert recuperacao.consultados == ("pt-BR",)


@pytest.mark.skipif(not (INDICE / "fragmentos.jsonl").exists(),
                    reason="índice não construído nesta máquina (os .jsonl não são versionados)")
def test_indice_real_nas_20_consultas_da_afericao_nao_muda():
    """Braço léxico sobre o índice real: não pede o modelo de embedding."""
    from prototipo.rag.lexica import IndiceLexico

    def ler(nome):
        with (INDICE / nome).open(encoding="utf-8") as arquivo:
            return [json.loads(linha) for linha in arquivo]

    fragmentos, unidades = ler("fragmentos.jsonl"), ler("unidades.jsonl")
    zeros = _Braco(np.zeros(len(fragmentos)))
    recuperador = Recuperador(fragmentos, unidades, IndiceLexico(fragmentos), zeros)
    consultas = json.loads(CONSULTAS.read_text(encoding="utf-8"))["consultas"]
    assert len(consultas) == 20
    for consulta in consultas:
        esperado = recuperador.buscar(consulta["consulta"], k=10, modo="lexica")
        recuperacao = recuperador.recuperar(consulta["consulta"], k=10, modo="lexica")
        assert recuperacao.resultados == esperado, consulta["consulta"]
        assert recuperacao.consultados == ("pt-BR",)
        assert recuperacao.coberto is True


# Índice que não diz o idioma não pode ser priorizado -----------------------

@pytest.mark.parametrize("idioma", [None, "es"])
def test_fragmento_sem_idioma_conhecido_e_recusado(idioma):
    recuperador = _recuperador(["pt-BR", idioma, "en"], [0.3, 0.2, 0.1])
    with pytest.raises(ValueError, match="idioma"):
        recuperador.recuperar("q", k=2, modo="densa")
    assert len(recuperador.buscar("q", k=2, modo="densa")) == 2   # a busca crua segue
