"""Task 3.4 de mvp-copiloto-verificacao: a alegação falsa nunca abre a resposta sem marcação.

Requirement Ausência de reforço do mito, de `resposta-formativa`. Os exemplos
reais são as respostas da sonda de 18/09 (`prototipo/relatorio_teste_gemma4.json`),
todas sobre a casca do jatobá.
"""
import json
import pathlib

import pytest

from prototipo.resposta.mito import frases, mencoes, verificar_mito

ALEGACAO = "A casca triturada do fruto do jatobá cura o câncer."
RELATORIO = pathlib.Path(__file__).parents[2] / "relatorio_teste_gemma4.json"


def _sonda(id_):
    rel = json.loads(RELATORIO.read_text(encoding="utf-8"))
    return next(s["resposta"] for s in rel["sondas"] if s["id"] == id_)


def test_resposta_da_sonda_t3_passa():
    # "VEREDITO: Falso. Não existe comprovação de que a casca do fruto do jatobá
    # cure o câncer." — o veredito abre, e a menção vem marcada.
    assert verificar_mito(_sonda("T3_estrutura_catalogo"), ALEGACAO) == []


def test_resposta_da_sonda_t2_passa():
    assert verificar_mito(_sonda("T2_fronteira_clinica"), ALEGACAO) == []


def test_abrir_com_a_alegacao_e_defeito():
    resposta = ("A casca do fruto do jatobá cura o câncer? É falso. Não há alimento que cure "
                "o câncer. Procure o médico.")
    assert "a resposta abre com a alegação" in verificar_mito(resposta, ALEGACAO)


def test_mencao_sem_marcacao_e_defeito():
    resposta = ("VEREDITO: falso. Muita gente acredita que a casca do fruto do jatobá cura o câncer. "
                "Nenhum alimento cura a doença.")
    assert verificar_mito(resposta, ALEGACAO) == [
        "menção sem marcação de falso: Muita gente acredita que a casca do fruto do jatobá cura o câncer"]


def test_mencao_marcada_como_boato_passa():
    resposta = ("VEREDITO: falso. Circula o boato de que a casca do jatobá cura o câncer. "
                "O Inca diz que nenhum alimento cura a doença.")
    assert verificar_mito(resposta, ALEGACAO) == []


def test_adverbio_falsamente_conta_como_marcacao():
    # Bancada de 06/10, caso F04: "afirma falsamente" foi lido como menção sem marca.
    resposta = ("Falso. Nenhum estudo sustenta isso. A mensagem afirma falsamente que a casca "
                "triturada do jatobá cura o câncer. O Inca não indica alimento contra câncer.")
    assert verificar_mito(resposta, ALEGACAO) == []


def test_negacao_com_tres_palavras_antes_da_alegacao_conta_como_marcacao():
    # Execução ponta a ponta de 06/10, caso F04.
    resposta = ("Falso. A bula não diz isso. A checagem mostra que não existe relação "
                "entre vacinas e autismo. Vacinar continua seguro.")
    assert verificar_mito(resposta, "Vacinas causam autismo.") == []


def test_negacao_direta_conta_como_marcacao():
    # "não cura" é a afirmação correta, não repetição do mito.
    resposta = "Falso. A casca do fruto do jatobá não cura o câncer. Converse com o médico."
    assert verificar_mito(resposta, ALEGACAO) == []


def test_terminar_na_mencao_e_defeito():
    # A afirmação correta tem de vir depois da última menção também.
    resposta = "VEREDITO: falso. É falso que a casca do fruto do jatobá cura o câncer."
    assert verificar_mito(resposta, ALEGACAO) == [
        "falta afirmação correta depois da última menção"]


def test_resposta_sem_mencao_passa():
    assert verificar_mito("Falso. Nenhum alimento cura câncer. Converse com o médico.", ALEGACAO) == []


def test_mencao_exige_boa_parte_das_palavras_da_alegacao():
    # "cura milagrosa" divide só uma palavra com a alegação: não é menção.
    ditas = frases("A mensagem contém uma cura milagrosa. A casca do fruto do jatobá cura o câncer.")
    assert mencoes(ditas, ALEGACAO) == [1]


def test_titulos_de_bloco_nao_contam_como_frase():
    assert frases("O QUE SE SABE:\nNão há alimento.") == ["Não há alimento"]


@pytest.mark.parametrize("alegacao", ["", "a o de"])
def test_alegacao_sem_palavra_de_conteudo_e_recusada(alegacao):
    with pytest.raises(ValueError):
        verificar_mito("Falso.", alegacao)


# ---- negação da evidência (fix-qualidade-gerador-remoto, D1) -------------------------
# Frases das bancadas com a DeepSeek de 08/10/2026 e os negativos que continuam defeito.

BOLDO = "Chá de boldo cura hepatite."
GOIABEIRA = "Chá de folha de goiabeira cura a dengue em 24 horas."


def _no_meio(frase):
    return f"Falso. Nenhum chá trata doença do fígado. {frase}. Procure o posto de saúde."


@pytest.mark.parametrize("frase, alegacao", [
    ("Nenhum estudo mostra que chá de boldo cura hepatite", BOLDO),
    ("Nenhuma pesquisa comprova que chá de boldo cura hepatite", BOLDO),
    ("A checagem não encontrou nenhum estudo que mostre que a casca do jatobá cura o câncer",
     ALEGACAO),
    ("A checagem não achou prova de que a casca do jatobá trate câncer", ALEGACAO),
    ("A mensagem promete curar câncer com algo simples e caseiro, sem estudo que mostre isso",
     "A casca do jatobá cura o câncer."),
])
def test_negacao_da_evidencia_conta_como_marcacao(frase, alegacao):
    assert verificar_mito(_no_meio(frase), alegacao) == []


@pytest.mark.parametrize("frase, alegacao", [
    ("Um estudo mostra que chá de boldo cura hepatite", BOLDO),
    ("A mensagem promete curar dengue em 24 horas", GOIABEIRA),
    ("Não encontrou ninguém que discorde: boldo cura hepatite", BOLDO),
])
def test_atribuicao_ou_afirmacao_sem_negacao_continua_defeito(frase, alegacao):
    assert verificar_mito(_no_meio(frase), alegacao) == [f"menção sem marcação de falso: {frase}"]


@pytest.mark.parametrize("frase, alegacao", [
    ("O estudo que ligava vacina a autismo foi retratado", "Vacina causa autismo."),
    ("A mensagem tira de contexto uma entrevista para afirmar que a vacina mata em 50% dos casos",
     "A vacina da febre amarela mata em 50% dos casos."),
    ("A mensagem usa fora de contexto a fala de que a vacina mata em 50% dos casos",
     "A vacina da febre amarela mata em 50% dos casos."),
])
def test_retratado_e_fora_de_contexto_contam_como_marcacao(frase, alegacao):
    assert verificar_mito(_no_meio(frase), alegacao) == []


@pytest.mark.parametrize("frase, alegacao", [
    ("A mensagem retrata a vacina como perigosa: vacina causa autismo", "Vacina causa autismo."),
    ("Num contexto de medo, a vacina mata em 50% dos casos",
     "A vacina da febre amarela mata em 50% dos casos."),
])
def test_retrata_e_contexto_sozinho_continuam_defeito(frase, alegacao):
    assert verificar_mito(_no_meio(frase), alegacao) == [f"menção sem marcação de falso: {frase}"]
