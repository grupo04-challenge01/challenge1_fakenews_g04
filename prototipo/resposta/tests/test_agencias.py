"""Task 4.1 de fix-robustez-demo: nome legível da agência (D4)."""
import pytest

from prototipo.resposta.agencias import nome


@pytest.mark.parametrize("cru, esperado", [
    ("boatos", "Boatos.org"),
    ("lupa", "Agência Lupa"),
    ("https:piaui.folha.uol.com.brlupa", "Agência Lupa"),
    ("COMPROVA", "Projeto Comprova"),
    ("aos fatos", "Aos Fatos"),
    ("https:www.aosfatos.org", "Aos Fatos"),
    ("ESTADAO_VERIFICA", "Estadão Verifica"),
    ("fato-ou-fake", "Fato ou Fake"),
    ("https:apublica.org", "Agência Pública"),
])
def test_valor_do_indice_vira_nome_da_agencia(cru, esperado):
    assert nome(cru) == esperado


@pytest.mark.parametrize("cru", ["Agência Nova", "", None])
def test_valor_desconhecido_passa_como_veio(cru):
    assert nome(cru) == cru
