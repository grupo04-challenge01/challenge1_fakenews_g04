"""Tasks 1.1 a 1.5 de add-identidade-dona-checa: textos da persona.

Requirements de `identidade-dona-checa`: os textos fixos saem da própria spec
e a pergunta de confiança nunca aparece em sessão de piloto.
"""
import pytest

from prototipo.identidade import pergunta_confianca, textos

ABERTURA = ("Oi, meu bem! Recebeu alguma coisa no zap e ficou na dúvida? "
            "Manda pra mim antes de passar adiante.")
PERGUNTA = "Antes, me conta: de 1 a 10, quanto você confia nessa mensagem agora?"
OPCOES = ["1 a 3", "4 a 6", "7 a 10"]
CHAMADA = "Antes de passar adiante, passa aqui."


def test_textos_da_persona_saem_da_spec():
    t = textos()
    assert t["abertura"] == ABERTURA
    assert t["pergunta_confianca"] == PERGUNTA
    assert t["opcoes_confianca"] == "\n".join(OPCOES)
    assert t["chamada"] == CHAMADA


def test_pergunta_de_confianca_some_no_piloto():
    assert pergunta_confianca(piloto=True) is None


def test_pergunta_de_confianca_fora_do_piloto_traz_pergunta_e_tres_opcoes():
    assert pergunta_confianca(piloto=False) == {"pergunta": PERGUNTA, "opcoes": OPCOES}


def test_pergunta_de_confianca_exige_dizer_se_e_piloto():
    with pytest.raises(TypeError):
        pergunta_confianca()
    with pytest.raises(TypeError):
        pergunta_confianca(False)


def _defeitos_de_voz(texto):
    """Requirement Nome e tratamento: "meu bem" no máximo uma vez, sem título de saúde."""
    achados = []
    if texto.lower().count("meu bem") > 1:
        achados.append("meu bem repetido")
    if any(t in texto for t in ("Dra.", "Doutora", "Dr.", "Doutor")):
        achados.append("título de profissional de saúde")
    return achados


def test_conferencia_de_voz_acusa_os_dois_defeitos():
    assert _defeitos_de_voz("Meu bem, Doutora Checa aqui, meu bem.") == [
        "meu bem repetido", "título de profissional de saúde"]


@pytest.mark.parametrize("capacidade", ["identidade-dona-checa", "resposta-formativa"])
def test_textos_da_persona_respeitam_nome_e_tratamento(capacidade):
    for chave, texto in textos(capacidade).items():
        assert _defeitos_de_voz(texto) == [], chave
