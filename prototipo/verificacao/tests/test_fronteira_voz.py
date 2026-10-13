"""Tasks 3.1 a 3.3 de add-identidade-dona-checa: respostas padrão na voz da Dona Checa.

Delta de `fronteira-orientacao-saude` no change: recusa de conduta e desmentido
de tratamento caseiro mudam de voz sem perder conteúdo obrigatório; urgência e
sofrimento psíquico ficam como estão na spec de mvp-copiloto-verificacao.
"""
import pytest

from prototipo.verificacao import fronteira
from prototipo.verificacao.fronteira import carregar_respostas

CANAIS = ("web", "whatsapp")
MVP = fronteira.RAIZ / ("openspec/changes/mvp-copiloto-verificacao/specs/"
                        "fronteira-orientacao-saude/spec.md")


@pytest.mark.parametrize("canal", CANAIS)
def test_recusa_de_conduta_na_voz_da_dona_checa(canal):
    assert carregar_respostas()["conduta_individual"][canal].startswith("Ah, meu bem")


@pytest.mark.parametrize("canal", CANAIS)
def test_desmentido_na_voz_da_dona_checa(canal):
    assert "Olha, meu bem" in carregar_respostas()["veredito_sem_prescricao"][canal]


@pytest.mark.skipif(not MVP.exists(), reason="mvp-copiloto-verificacao já arquivado")
@pytest.mark.parametrize("chave", ["risco_imediato", "sofrimento_psiquico"])
def test_urgencia_e_sofrimento_nao_mudam(chave):
    assert carregar_respostas()[chave] == fronteira.ler_respostas(MVP)[chave]


@pytest.mark.parametrize("canal", CANAIS)
def test_recusa_de_conduta_mantem_o_conteudo_obrigatorio(canal):
    texto = carregar_respostas()["conduta_individual"][canal]
    assert "confiro informação" in texto
    assert "não receito" in texto
    assert "não dou diagnóstico" in texto
    assert "riscos sérios" in texto
    assert "UBS" in texto
    assert texto.lower().count("meu bem") == 1


@pytest.mark.parametrize("canal", CANAIS)
def test_desmentido_mantem_o_conteudo_obrigatorio(canal):
    texto = carregar_respostas()["veredito_sem_prescricao"][canal]
    assert "não tem comprovação científica" in texto
    assert "UBS" in texto
    assert "136" in texto
    assert texto.lower().count("meu bem") == 1


@pytest.mark.parametrize("canal", CANAIS)
def test_recusa_de_conduta_nao_cita_um_remedio_e_negrita_a_recusa(canal):
    # fix-conduta-diagnostico, D1: o pedido pode ser de vacina ou de exame.
    texto = carregar_respostas()["conduta_individual"][canal]
    assert "esse remédio" not in texto
    assert "entendo a sua dúvida" in texto
    assert "**não receito, não dou diagnóstico e não posso indicar nem mudar tratamento" in texto


@pytest.mark.parametrize("canal", CANAIS)
def test_diagnostico_acolhe_antes_de_recusar(canal):
    # fix-conduta-diagnostico, D4: "estou com bolinhas no corpo".
    texto = carregar_respostas()["diagnostico"][canal]
    assert texto.startswith("Ah, meu bem, sinto muito")
    assert texto.index("sinto muito") < texto.index("não dou diagnóstico")
    assert "Só quem examina a pessoa sabe dizer o que ela tem" in texto
    assert "UBS" in texto and "UPA" in texto and "SAMU (192)" in texto
    assert texto.lower().count("meu bem") == 1


@pytest.mark.parametrize("canal", CANAIS)
def test_pergunta_geral_encaminha_sem_responder(canal):
    # fix-conduta-diagnostico, D5: idade de vacina não é conduta.
    texto = carregar_respostas()["informacao_geral"][canal]
    assert "sinto muito" not in texto
    assert "UBS" in texto and "Disque Saúde (136)" in texto
    assert "cola aqui" in texto
    assert texto.lower().count("meu bem") == 1
