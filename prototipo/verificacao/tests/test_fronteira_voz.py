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
    assert "não receito nem dou diagnóstico" in texto
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
