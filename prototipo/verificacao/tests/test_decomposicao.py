"""Task 2.5 de mvp-copiloto-verificacao: decomposição fato / evidência / opinião.

Como em test_extracao, o modelo é substituído por JSON fixo. O comportamento do
modelo nos dois casos da spec (mensagem mista e fato verdadeiro com conclusão que
não decorre) é medido pela sonda `prototipo/sonda_extracao_decomposicao.py`.
"""
import json

import pytest

from prototipo.verificacao.decomposicao import FORCAS, SISTEMA, decompor, defeitos, interpretar


def _bruto(**campos):
    base = {"fatos": [], "evidencias": [], "opinioes": [], "conclusao": None}
    base.update(campos)
    return json.dumps(base, ensure_ascii=False)


CASO_MISTO = _bruto(
    fatos=["O jejum de três dias limpa o fígado."],
    evidencias=[{"texto": "Um médico no YouTube disse.", "forca": "fraca"}],
    opinioes=["Remédio de farmácia só faz mal."],
)

CASO_SALTO = _bruto(
    fatos=["A bula da Tripedia cita relatos de autismo depois da vacina."],
    evidencias=[{"texto": "Trecho da bula da Tripedia.", "forca": "fraca"}],
    conclusao={"texto": "Vacina causa autismo.", "decorre": False,
               "salto": "Relato registrado na bula não mostra que a vacina causou o autismo."},
)


def test_prompt_define_as_forcas_da_evidencia():
    for forca in FORCAS:
        assert f'"{forca}"' in SISTEMA


def test_prompt_proibe_veredito():
    assert "NÃO diga se" in SISTEMA


def test_caso_misto_separa_as_tres_partes():
    d = interpretar(CASO_MISTO)
    assert d.fatos == ["O jejum de três dias limpa o fígado."]
    assert d.evidencias == [{"texto": "Um médico no YouTube disse.", "forca": "fraca"}]
    assert d.opinioes == ["Remédio de farmácia só faz mal."]
    assert d.conclusao is None


def test_salto_entre_fato_e_conclusao_e_lido():
    d = interpretar(CASO_SALTO)
    assert d.conclusao["decorre"] is False
    assert d.conclusao["salto"].startswith("Relato registrado")


def test_conclusao_toda_nula_e_ausencia_de_conclusao():
    # Bancada de 06/10, caso X2: sem conclusão na mensagem, o modelo devolveu o
    # objeto com os três campos nulos em vez de `null` (decisão 24).
    bruto = _bruto(fatos=["X."], conclusao={"texto": None, "decorre": None, "salto": None})
    assert defeitos(bruto) == []
    assert interpretar(bruto).conclusao is None


def test_conclusao_parcial_continua_defeito():
    bruto = _bruto(fatos=["X."], conclusao={"texto": None, "decorre": False, "salto": "Z."})
    assert "conclusão sem texto" in defeitos(bruto)


def test_conclusao_que_nao_decorre_sem_salto_explicado_e_defeito():
    bruto = _bruto(fatos=["X."], conclusao={"texto": "Y.", "decorre": False, "salto": ""})
    assert "conclusão que não decorre sem o salto explicado" in defeitos(bruto)


def test_conclusao_que_decorre_nao_precisa_de_salto():
    bruto = _bruto(fatos=["X."], conclusao={"texto": "Y.", "decorre": True, "salto": None})
    assert defeitos(bruto) == []


@pytest.mark.parametrize("campo, texto", [
    ("fatos", "É falso que o jejum limpa o fígado."),
    ("opinioes", "Isso é mentira, remédio de farmácia só faz mal."),
    ("salto", "A conclusão é falsa."),
])
def test_decomposicao_com_veredito_e_defeito(campo, texto):
    # A decomposição é independente do veredito; veredito aqui é vazamento.
    if campo == "salto":
        bruto = _bruto(fatos=["X."], conclusao={"texto": "Y.", "decorre": False, "salto": texto})
    else:
        bruto = _bruto(**{campo: [texto]})
    assert any(d.startswith("veredito dentro da decomposição") for d in defeitos(bruto))


def test_palavra_verdadeiro_dentro_de_fato_citado_nao_e_veredito():
    # "verdadeiro" pode ser parte da alegação ("o verdadeiro remédio é..."), e só
    # conta como veredito na forma de julgamento: "é falso", "é verdadeiro", "mentira".
    bruto = _bruto(fatos=["O verdadeiro remédio para a gripe é o limão."])
    assert defeitos(bruto) == []


def test_mesma_frase_como_fato_e_opiniao_e_defeito():
    # Sonda de 29/09, D1 tentativa 2: a opinião voltou também como fato.
    bruto = _bruto(fatos=["Jejum de três dias limpa o fígado", "Remédio de farmácia só faz mal"],
                   opinioes=["Eu acho que remédio de farmácia só faz mal."])
    assert "opinião repetida como fato: Remédio de farmácia só faz mal" in defeitos(bruto)


@pytest.mark.parametrize("bruto, defeito", [
    ("{", "saída não é JSON"),
    (json.dumps({"fatos": []}), "falta `evidencias`"),
    (_bruto(evidencias=[{"texto": "X", "forca": "média"}]), "evidência 1 com força fora de forte/fraca/ausente"),
    (_bruto(fatos=[""]), "fatos: item 1 vazio"),
    (_bruto(conclusao={"texto": "Y.", "salto": None}), "conclusão sem `decorre` booleano"),
])
def test_saida_malformada_e_defeito(bruto, defeito):
    assert defeito in defeitos(bruto)
    with pytest.raises(ValueError):
        interpretar(bruto)


def test_decompor_passa_pelo_modelo_injetado():
    assert decompor("qualquer", chat=lambda s, u: CASO_MISTO).opinioes == ["Remédio de farmácia só faz mal."]
