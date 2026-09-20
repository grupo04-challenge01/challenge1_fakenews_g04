"""Testes de integridade textual — change add-tratamento-datasets-ptbr, bloco 3.

Capability `integridade-textual`. Arquivo com classe de caractere sistematicamente
perdida MUST NOT ser aprovado para recuperação nem citação; e todo trecho citado
SHALL ser idêntico ao texto correspondente no corpus.
"""
from __future__ import annotations

import pytest

from tratamento import integridade, leitura


def test_corpus_de_checagens_e_aprovado():
    laudo = integridade.verificar("factcenter_subset_saude.csv")

    assert laudo["aprovado"] is True
    assert laudo["corrompidos"] == []


def test_ausencia_isolada_de_maiuscula_sem_minuscula_frequente_nao_reprova():
    """O `Ü` tem zero ocorrência no corpus por ortografia, não por corrupção.

    O trema foi abolido em 1990 e o corpus cobre 2013 a 2021. Reprovar por
    ausência total bloquearia corpus íntegro.
    """
    laudo = integridade.verificar("factcenter_subset_saude.csv")

    assert "Ü" in laudo["ausentes"]
    assert laudo["aprovado"] is True


def test_factckbr_e_reprovado_para_citacao():
    laudo = integridade.verificar("factckbr_normalizado.csv")

    assert laudo["aprovado"] is False
    corrompidos = {c["maiuscula"] for c in laudo["corrompidos"]}
    assert {"Ã", "Ç", "Í", "Ê", "Ó", "Õ", "Ú"} <= corrompidos


def test_arquivo_reprovado_interrompe_quando_exigido():
    with pytest.raises(integridade.ErroDeIntegridade) as erro:
        integridade.exigir_aprovado("factckbr_normalizado.csv")

    assert "citação" in str(erro.value)


def test_verificacao_e_registrada_por_arquivo_com_a_lista_de_ausentes():
    laudos = integridade.verificar_todos()

    assert set(laudos) == set(integridade.ARQUIVOS_PT_BR)
    for nome, laudo in laudos.items():
        assert "ausentes" in laudo and "aprovado" in laudo
        assert laudo["arquivo"] == nome


def test_trecho_citado_e_identico_ao_texto_de_origem():
    df = leitura.ler_corpus().head(500)
    laudo = integridade.verificar_fidelidade_dos_trechos(df)

    assert laudo["fragmentos"] > 0
    assert laudo["infieis"] == 0


def test_trecho_alterado_e_reprovado_pela_verificacao_de_fidelidade():
    assert integridade.trecho_e_fiel("Sistema Único", "no Sistema Único de Saúde")
    assert not integridade.trecho_e_fiel("Sistema nico", "no Sistema Único de Saúde")


def test_laudo_separa_perda_de_caractere_de_texto_transformado():
    """Reprovar não basta: o laudo precisa dizer por quê.

    `factckbr_normalizado.csv` perdeu caractere por allowlist a montante.
    Os derivados da FakeRecogna reprovam por outra razão — o texto chega
    lematizado e sem caixa na origem. Tratar os dois como o mesmo defeito
    põe no portfólio a acusação errada contra a base errada.
    """
    factckbr = integridade.verificar("factckbr_normalizado.csv")
    fakerecogna = integridade.verificar("fakerecogna_subset_saude_ciencia.csv")

    assert factckbr["causa_provavel"] == "perda seletiva de caractere"
    assert fakerecogna["causa_provavel"] == "texto transformado na origem"
    assert factckbr["aprovado"] is False and fakerecogna["aprovado"] is False


def test_corrompido_traz_a_ocorrencia_esperada_pela_razao_de_caixa_do_arquivo():
    laudo = integridade.verificar("factckbr_normalizado.csv")
    cedilha = next(c for c in laudo["corrompidos"] if c["maiuscula"] == "Ç")

    assert cedilha["ocorrencias_esperadas"] > 20
