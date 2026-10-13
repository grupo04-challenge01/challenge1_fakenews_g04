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


# add-cobertura-alegacao-ampla, task 1.1 (D1) ---------------------------------

def _ampla(**campos):
    dados = {"rotulo": "falso", "trechos": ["T1"], "criterio": "O trecho desmente a geral.",
             "cobertura": "ampla", "ponte": "Virar jacaré exigiria alterar o DNA.",
             "sujeito": "vacina de Covid-19"}
    dados.update(campos)
    return json.dumps(dados, ensure_ascii=False)


def test_cobertura_ampla_e_lida_com_ponte_e_sujeito():
    c = interpretar(_ampla())
    assert (c.cobertura, c.ponte, c.sujeito) == (
        "ampla", "Virar jacaré exigiria alterar o DNA.", "vacina de Covid-19")


def test_cobertura_ausente_conta_como_mesma():
    c = interpretar(_bruto())
    assert (c.cobertura, c.ponte, c.sujeito) == ("mesma", "", "")


def test_cobertura_mesma_dispensa_ponte_e_sujeito():
    assert interpretar(_ampla(cobertura="Mesma", ponte="", sujeito="")).cobertura == "mesma"


@pytest.mark.parametrize("campos, defeito", [
    ({"cobertura": "parecida"}, "cobertura fora de mesma e ampla: parecida"),
    ({"ponte": ""}, "cobertura ampla sem ponte"),
    ({"sujeito": "  "}, "cobertura ampla sem sujeito"),
])
def test_cobertura_malformada_e_defeito(campos, defeito):
    assert defeito in defeitos(_ampla(**campos))
    with pytest.raises(ValueError):
        interpretar(_ampla(**campos))


def test_insuficiente_nao_exige_cobertura():
    bruto = json.dumps({"rotulo": "evidência insuficiente", "trechos": [],
                        "criterio": "Nada sobre isso.", "cobertura": "ampla"},
                       ensure_ascii=False)
    assert defeitos(bruto) == []


def test_classificar_passa_pelo_modelo_injetado():
    visto = {}

    def chat(sistema, usuario):
        visto["usuario"] = usuario
        return _bruto()

    assert classificar("Casca do jatobá cura câncer.", TRECHOS, chat=chat).rotulo == "falso"
    assert "[T1]" in visto["usuario"]


# add-cobertura-alegacao-ampla, task 1.2 (D1) ---------------------------------

def test_prompt_define_cobertura_ampla_por_implicacao():
    assert '"ampla"' in SISTEMA
    assert "caso particular" in SISTEMA
    assert "se esta alegação fosse verdade, a mais geral também seria" in SISTEMA


def test_prompt_define_cobertura_mesma():
    assert '"mesma": o trecho checa esta alegação, mesmo com outras palavras' in SISTEMA


def test_prompt_traz_goiabeira_diante_de_jatoba_como_exemplo_negativo():
    assert "goiabeira" in SISTEMA and "jatobá" in SISTEMA


def test_prompt_limita_cobertura_ampla_ao_falso():
    assert 'Cobertura "ampla" só vale para o rótulo "falso"' in SISTEMA


def test_prompt_pede_os_campos_novos_no_formato():
    for campo in ('"cobertura"', '"ponte"', '"sujeito"'):
        assert campo in SISTEMA
