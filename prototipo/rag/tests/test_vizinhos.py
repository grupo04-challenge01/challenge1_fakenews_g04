"""Decisão 29 de mvp-copiloto-verificacao: fragmentos vizinhos da checagem citada.

A busca reduz a unidade e entrega o melhor fragmento de cada checagem. O fato
que decide a resposta pode estar em outro fragmento da mesma checagem: no R4 da
bancada, a data do vídeo estava no quarto fragmento, e o modelo só viu o
primeiro. `expandir` devolve os trechos citados e, depois deles, os outros
fragmentos de cada checagem citada, pelos mais próximos da consulta.
"""
import numpy as np

from prototipo.rag.hibrida import TETO_VIZINHOS, Recuperador


class _Braco:
    def __init__(self, scores):
        self.scores = np.asarray(scores, dtype="float32")

    def pontuar(self, consulta):
        return self.scores


# Unidade u0 com cinco fragmentos, u1 com dois.
FRAGMENTOS = [("u0", 0), ("u0", 1), ("u0", 2), ("u0", 3), ("u0", 4), ("u1", 0), ("u1", 1)]
DENSO = [0.90, 0.10, 0.20, 0.80, 0.70, 0.15, 0.05]


def _recuperador():
    fragmentos = [{"fragmento_id": f"{u}-00-{n:02d}", "unidade_id": u, "trecho": f"{u} parte {n}",
                   "idioma": "pt-BR", "apto_citacao": True} for u, n in FRAGMENTOS]
    unidades = [{"unidade_id": u, "agencia": "boatos", "data_publicacao": "2021-01-31",
                 "url": f"https://x/{u}", "alegacao": f"alegação {u}",
                 "veredito_original": "boato", "veredito_chave": "falso",
                 "cobre_multiplas_alegacoes": False} for u in ("u0", "u1")]
    return Recuperador(fragmentos, unidades, _Braco([0.0] * len(FRAGMENTOS)), _Braco(DENSO))


def test_citados_vem_primeiro_e_na_mesma_ordem():
    r = _recuperador()
    citados = r.buscar("q", k=2, modo="densa")
    expandidos = r.expandir("q", citados, modo="densa")
    assert expandidos[:2] == citados


def test_vizinhos_sao_da_mesma_checagem_pelos_mais_proximos_da_consulta():
    r = _recuperador()
    citado = [t for t in r.buscar("q", k=2, modo="densa") if t["unidade_id"] == "u0"]
    assert citado[0]["fragmento_id"] == "u0-00-00"
    vizinhos = r.expandir("q", citado, teto=2, modo="densa")[1:]
    assert [t["fragmento_id"] for t in vizinhos] == ["u0-00-03", "u0-00-04"]
    assert all(t["unidade_id"] == "u0" for t in vizinhos)


def test_teto_por_checagem():
    r = _recuperador()
    citado = r.buscar("q", k=1, modo="densa")
    assert len(r.expandir("q", citado, modo="densa")) == 1 + TETO_VIZINHOS
    assert len(r.expandir("q", citado, teto=10, modo="densa")) == 5


def test_vizinho_tem_o_formato_do_resultado_da_busca():
    r = _recuperador()
    citado = r.buscar("q", k=1, modo="densa")
    vizinho = r.expandir("q", citado, modo="densa")[1]
    assert set(vizinho) == set(citado[0])
    assert vizinho["url"] == citado[0]["url"] and vizinho["apto_citacao"] is True


def test_cada_checagem_citada_ganha_os_seus_e_nada_se_repete():
    r = _recuperador()
    citados = r.buscar("q", k=2, modo="densa")
    ids = [t["fragmento_id"] for t in r.expandir("q", citados, teto=10, modo="densa")]
    assert len(ids) == len(set(ids)) == len(FRAGMENTOS)


def test_sem_citado_nao_expande():
    assert _recuperador().expandir("q", [], modo="densa") == []
