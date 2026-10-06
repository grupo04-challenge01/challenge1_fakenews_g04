"""Task 2.2 de mvp-copiloto-verificacao: classificação nos quatro rótulos.

O modelo é substituído por JSON fixo. O comportamento do modelo com trechos reais
do índice é medido pela sonda `prototipo/sonda_classificacao_guarda.py`.
"""
import json

import pytest

from prototipo.verificacao.classificacao import (
    ROTULOS, SISTEMA, classificar, defeitos, interpretar, mensagem)

TRECHOS = [
    {"agencia": "aos fatos", "data_publicacao": "2021-01-08", "url": "https://a/1",
     "veredito_original": "falso", "trecho": "Não é verdade que a casca do jatobá cure o câncer."},
    {"agencia": "lupa", "data_publicacao": "2020-11-13", "url": "https://b/2",
     "veredito_original": "verdadeiro", "trecho": "A fila de espera quase dobrou."},
]


def _bruto(rotulo="falso", trechos=("T1",), criterio="O trecho T1 diz que não há estudo."):
    return json.dumps({"rotulo": rotulo, "trechos": list(trechos), "criterio": criterio},
                      ensure_ascii=False)


def test_sao_exatamente_os_quatro_rotulos_da_spec():
    assert ROTULOS == ("falso", "verdadeiro", "verdadeiro fora de contexto ou exagerado",
                       "evidência insuficiente")


def test_prompt_lista_os_quatro_rotulos_escritos_igual():
    for r in ROTULOS:
        assert f'"{r}"' in SISTEMA


def test_prompt_proibe_conhecimento_proprio():
    assert "NUNCA use o que você sabe" in SISTEMA


def test_prompt_instrui_nao_rebaixar_verdadeiro_contraintuitivo():
    assert "não rebaixe o rótulo porque a alegação soa estranha" in SISTEMA
def test_prompt_nao_deixa_verdadeiro_contra_o_veredito_da_agencia():
    # Execução ponta a ponta de 06/10: "verdadeiro" citando checagem com veredito
    # "boato" para a mesma alegação.
    assert "NÃO pode ser \"verdadeiro\"" in SISTEMA


def test_mensagem_numera_os_trechos_com_fonte_e_data():
    m = mensagem("Casca do jatobá cura câncer.", TRECHOS)
    assert "[T1] aos fatos, 2021-01-08" in m
    assert "[T2] lupa, 2020-11-13" in m
    assert "Casca do jatobá cura câncer." in m


def test_mensagem_sem_trecho_diz_nenhum():
    assert "TRECHOS RECUPERADOS: nenhum." in mensagem("X.", [])


def test_classificacao_valida_e_lida():
    c = interpretar(_bruto())
    assert c.rotulo == "falso"
    assert c.trechos == ["T1"]
    assert c.criterio.startswith("O trecho T1")


def test_caixa_e_espaco_do_rotulo_sao_normalizados():
    assert interpretar(_bruto(rotulo=" Verdadeiro ")).rotulo == "verdadeiro"


@pytest.mark.parametrize("bruto, defeito", [
    ("nada", "saída não é JSON"),
    (_bruto(rotulo="enganoso"), "rótulo fora dos quatro: enganoso"),
    (_bruto(rotulo="falso", criterio=""), "veredito sem critério"),
    (json.dumps({"rotulo": "falso", "criterio": "x"}), "falta a lista `trechos`"),
    (_bruto(trechos=[1]), "trecho citado não é identificador T1, T2..."),
])
def test_saida_malformada_e_defeito(bruto, defeito):
    assert defeito in defeitos(bruto)
    with pytest.raises(ValueError):
        interpretar(bruto)


def test_classificar_passa_pelo_modelo_injetado():
    visto = {}

    def chat(sistema, usuario):
        visto["usuario"] = usuario
        return _bruto()

    assert classificar("Casca do jatobá cura câncer.", TRECHOS, chat=chat).rotulo == "falso"
    assert "[T1]" in visto["usuario"]
