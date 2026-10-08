"""Task 2.1 de mvp-copiloto-verificacao: extração de alegação, com seleção quando há várias.

O modelo é substituído por uma função que devolve JSON fixo. O que se testa aqui é
o contrato em volta do prompt: leitura, recusa de saída malformada e a seleção,
que é feita em código, não pelo modelo.
"""
import json

import pytest

from prototipo.verificacao.extracao import (
    RISCOS, SISTEMA, defeitos, extrair, interpretar, mensagem, selecionar)


def _bruto(alegacoes, opiniao=None):
    return json.dumps({"alegacoes": alegacoes, "opiniao": opiniao}, ensure_ascii=False)


def _falso_chat(bruto):
    def chat(sistema, usuario):
        return bruto
    return chat


def test_prompt_define_os_tres_niveis_de_risco():
    for nivel in RISCOS:
        assert f'"{nivel}"' in SISTEMA


def test_prompt_pede_alegacao_que_se_entende_sozinha():
    # Execução ponta a ponta de 06/10: "a vacina da dengue protege contra ela",
    # com o pronome sem referente, e "presidente da Anvisa" separado do que disse.
    assert "pronome" in SISTEMA
    assert "quem afirmou" in SISTEMA


def test_mensagem_leva_o_texto_recebido():
    assert "Chá de boldo" in mensagem("Chá de boldo cura hepatite.")


def test_uma_alegacao_de_saude_e_selecionada():
    r = interpretar(_bruto([{"texto": "Chá de boldo cura hepatite.", "saude": True, "risco": "alto"}]))
    assert r.verificavel
    assert r.selecionada["texto"] == "Chá de boldo cura hepatite."
    assert r.demais == []


def test_varias_alegacoes_seleciona_a_de_maior_risco():
    r = interpretar(_bruto([
        {"texto": "O hospital de Sorocaba ficou lotado ontem.", "saude": True, "risco": "baixo"},
        {"texto": "Chá de boldo cura hepatite, pode parar o remédio.", "saude": True, "risco": "alto"},
        {"texto": "A dengue voltou a subir.", "saude": True, "risco": "medio"},
    ]))
    assert r.selecionada["texto"].startswith("Chá de boldo")
    # As demais ficam na ordem da mensagem, para oferecer verificar depois.
    assert [a["texto"] for a in r.demais] == [
        "O hospital de Sorocaba ficou lotado ontem.", "A dengue voltou a subir."]


def test_empate_de_risco_fica_com_a_primeira_da_mensagem():
    alegacoes = [{"texto": "A", "saude": True, "risco": "alto"},
                 {"texto": "B", "saude": True, "risco": "alto"}]
    assert selecionar(alegacoes)["texto"] == "A"


def test_alegacao_fora_de_saude_nao_e_selecionada_mas_e_oferecida():
    r = interpretar(_bruto([
        {"texto": "O prefeito gastou 2 milhões na obra.", "saude": False, "risco": "alto"},
        {"texto": "A vacina da gripe dá gripe.", "saude": True, "risco": "medio"},
    ]))
    assert r.selecionada["texto"] == "A vacina da gripe dá gripe."
    assert [a["texto"] for a in r.demais] == ["O prefeito gastou 2 milhões na obra."]


def test_so_opiniao_nao_e_verificavel():
    r = interpretar(_bruto([], opiniao="Esse governo não liga para a saúde de ninguém."))
    assert not r.verificavel
    assert r.selecionada is None
    assert r.opiniao == "Esse governo não liga para a saúde de ninguém."


def test_so_alegacao_fora_de_saude_nao_e_verificavel():
    r = interpretar(_bruto([{"texto": "O prefeito gastou 2 milhões.", "saude": False, "risco": "baixo"}]))
    assert not r.verificavel


def test_json_em_bloco_de_codigo_e_aceito():
    bruto = "```json\n" + _bruto([{"texto": "X cura Y.", "saude": True, "risco": "alto"}]) + "\n```"
    assert interpretar(bruto).selecionada["texto"] == "X cura Y."


@pytest.mark.parametrize("bruto, defeito", [
    ("não é json", "saída não é JSON"),
    (json.dumps({"opiniao": None}), "falta a lista `alegacoes`"),
    (_bruto([{"texto": "", "saude": True, "risco": "alto"}]), "alegação 1 sem texto"),
    (_bruto([{"texto": "X", "saude": True, "risco": "altíssimo"}]), "alegação 1 com risco fora de alto/medio/baixo"),
    (_bruto([{"texto": "X", "saude": "sim", "risco": "alto"}]), "alegação 1 sem `saude` booleano"),
])
def test_saida_malformada_e_defeito(bruto, defeito):
    assert defeito in defeitos(bruto)
    with pytest.raises(ValueError):
        interpretar(bruto)


def test_extrair_passa_pelo_modelo_injetado():
    chat = _falso_chat(_bruto([{"texto": "X cura Y.", "saude": True, "risco": "alto"}]))
    assert extrair("qualquer texto", chat=chat).selecionada["texto"] == "X cura Y."


# ---- teto e nova tentativa (fix-qualidade-gerador-remoto, D6) ------------------------

from prototipo.verificacao.extracao import SISTEMA as SISTEMA_EXTRACAO, extrair  # noqa: E402

BOA = json.dumps({"alegacoes": [{"texto": "Chá de boldo cura hepatite.", "saude": True,
                                 "risco": "alto"}], "opiniao": None}, ensure_ascii=False)
CORTADA = '{"alegacoes": [{"texto": "Chá de boldo cura hepatite.", "saude": true, "ri'


def _sequencia(*saidas):
    pedidos, fila = [], list(saidas)

    def chat(sistema, usuario):
        pedidos.append(usuario)
        return fila.pop(0)
    return chat, pedidos


def test_prompt_pede_no_maximo_8_alegacoes_com_as_de_saude_primeiro():
    assert "no máximo 8 alegações" in SISTEMA_EXTRACAO
    assert "as de saúde primeiro" in SISTEMA_EXTRACAO


def test_saida_cortada_tem_nova_tentativa_com_o_defeito_informado():
    chat, pedidos = _sequencia(CORTADA, BOA)
    e = extrair("Chá de boldo cura hepatite, e muito mais.", chat=chat)
    assert e.selecionada["texto"] == "Chá de boldo cura hepatite."
    assert len(pedidos) == 2 and pedidos[1].startswith(pedidos[0])
    assert "saída não é JSON" in pedidos[1] and "no máximo 8" in pedidos[1]


def test_saida_boa_nao_pede_de_novo():
    chat, pedidos = _sequencia(BOA)
    extrair("Chá de boldo cura hepatite.", chat=chat)
    assert len(pedidos) == 1


def test_duas_saidas_com_defeito_levantam():
    chat, pedidos = _sequencia(CORTADA, CORTADA)
    with pytest.raises(ValueError, match="saída não é JSON"):
        extrair("texto", chat=chat)
    assert len(pedidos) == 2


def test_prompt_trata_pergunta_com_afirmacao_como_alegacao():
    # fix-pergunta-e-conduta, D1: "Suco detox cura gripe?" é alegação.
    assert "Opinião, desabafo e pedido não são alegação." in SISTEMA_EXTRACAO
    assert '"Suco detox cura gripe?"' in SISTEMA_EXTRACAO
    assert '"O que devo fazer?"' in SISTEMA_EXTRACAO
    assert "pergunta e pedido não são alegação" not in SISTEMA_EXTRACAO
