"""Task 7.1 de add-cobertura-alegacao-ampla: a sonda roda com modelo falso.

O comportamento real (Gemma, DeepSeek) é a task 7.2 e a 7.3. Aqui se confere a
mecânica: casos do design (D8), trechos com o que a guarda precisa, contagem
por tentativa e o critério de aceite.
"""
import json
import pathlib

import pytest

from prototipo import sonda_cobertura_ampla as sonda
from prototipo.verificacao import implicacao
from prototipo.verificacao.guarda import INSUFICIENTE

INDICE = pathlib.Path(sonda.AQUI / "indice" / "fragmentos.jsonl")


def _falso(trecho_id, agencia, chave="falso"):
    return {"fragmento_id": trecho_id, "agencia": agencia, "url": f"https://{agencia}",
            "data_publicacao": "2020-01-01", "veredito_original": chave, "veredito_chave": chave,
            "apto_citacao": True, "alegacao": "Vacina contra a Covid-19 altera o DNA",
            "trecho": "É falso que a vacina contra a Covid-19 altere o DNA."}


def _trechos():
    ids = {i for s in sonda.SONDAS for i in s["fragmentos"]}
    return {i: _falso(i, f"agencia-{n}") for n, i in enumerate(sorted(ids))}


def _chat_insuficiente(sistema, usuario):
    return json.dumps({"rotulo": INSUFICIENTE, "trechos": [], "criterio": "Nada."},
                      ensure_ascii=False)


def test_casos_sao_os_do_design():
    assert [s["id"] for s in sonda.SONDAS] == [
        "A1_jacare", "A2_chip_chines", "N1_goiabeira_2ag", "N2_cloroquina_2ag",
        "N3_autismo_dna", "N4_miocardite", "N5_uma_agencia", "N6_enganoso"]


def test_sinteticos_sao_marcados():
    sinteticos = [s["id"] for s in sonda.SONDAS if s.get("sintetico")]
    assert sinteticos == ["N4_miocardite"]
    assert all(i in sonda.SINTETICOS for i in
               next(s for s in sonda.SONDAS if s["id"] == "N4_miocardite")["fragmentos"])


def test_trechos_ganham_score_decrescente_na_ordem_do_caso():
    caso = sonda.SONDAS[0]
    montados = sonda.montar(caso, _trechos())
    assert [t["score"] for t in montados] == sorted((t["score"] for t in montados), reverse=True)


def test_modelo_que_sempre_diz_insuficiente_passa_so_nos_negativos():
    rel = sonda.rodar(_chat_insuficiente, _trechos(), tentativas=2)
    passou = {r["id"]: r["passou"] for r in rel["sondas"]}
    assert all(passou[i] == 0 for i in ("A1_jacare", "A2_chip_chines"))
    assert all(passou[s["id"]] == 2 for s in sonda.SONDAS if s["id"].startswith("N"))
    assert sonda.aceite(rel) is False


def test_tentativa_registra_cobertura_ponte_e_implicacao():
    def chat(sistema, usuario):
        if sistema == implicacao.SISTEMA:
            return json.dumps({"resposta": "sim"})
        return json.dumps({"rotulo": "falso", "trechos": ["T1", "T2"], "criterio": "Geral falsa.",
                           "cobertura": "ampla", "ponte": "Virar jacaré altera o DNA.",
                           "sujeito": "vacina de Covid-19"}, ensure_ascii=False)
    rel = sonda.rodar(chat, _trechos(), tentativas=1,
                      sondas=[s for s in sonda.SONDAS if s["id"] == "A1_jacare"])
    t = rel["sondas"][0]["tentativas"][0]
    assert (t["rotulo"], t["cobertura"], t["implicacao"]) == ("falso", "ampla", "sim")
    assert t["ponte"] == "Virar jacaré altera o DNA."
    assert rel["sondas"][0]["passou"] == 1


def test_aceite_exige_todas_as_tentativas_de_todos_os_casos():
    rel = {"tentativas": 3, "sondas": [{"id": s["id"], "passou": 3} for s in sonda.SONDAS]}
    assert sonda.aceite(rel) is True
    rel["sondas"][-1]["passou"] = 2
    assert sonda.aceite(rel) is False


@pytest.mark.skipif(not INDICE.exists(), reason="índice local não construído")
def test_fragmentos_reais_existem_no_indice_com_veredito_e_alegacao():
    trechos = sonda.carregar_trechos()
    for t in trechos.values():
        assert t["veredito_chave"] and t["alegacao"] and t["trecho"]
