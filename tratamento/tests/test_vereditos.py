"""Testes da normalização de veredito — change add-tratamento-datasets-ptbr, bloco 2.

Capability `normalizacao-rotulos`. O campo `rating` é lista, não string; o mapa
é versionado e explícito; valor fora do mapa interrompe o processamento em vez
de receber palpite por semelhança de string.
"""
from __future__ import annotations

import pytest

from tratamento import leitura, vereditos


def test_campo_serializado_vira_dois_vereditos_com_a_grafia_preservada():
    lidos = vereditos.ler_campo("['FALSO', 'VERDADEIRO, MAS']")

    assert [v.original for v in lidos] == ["FALSO", "VERDADEIRO, MAS"]
    assert [v.chave for v in lidos] == ["falso", "verdadeiro, mas"]


def test_chave_canonica_dobra_caixa_e_acento():
    assert vereditos.chave_canonica("INSUSTENTÁVEL") == "insustentavel"
    assert vereditos.chave_canonica("insustentável") == "insustentavel"


def test_valor_fora_do_mapa_interrompe_o_processamento():
    with pytest.raises(vereditos.VeredictoDesconhecido) as erro:
        vereditos.rotular("meia verdade sazonal")

    assert "meia verdade sazonal" in str(erro.value)


def test_nenhum_valor_do_corpus_fica_fora_do_mapa():
    df = leitura.ler_corpus()
    fora = sorted({v.chave
                   for bruto in df["rating"]
                   for v in vereditos.ler_campo(bruto)
                   if v.chave not in vereditos.MAPA["entradas"]})
    assert fora == []


def test_boato_carrega_o_registro_do_que_se_perde():
    entrada = vereditos.MAPA["entradas"]["boato"]

    assert entrada["rotulo"] == "falso"
    assert entrada["nota"], "boato MUST NOT ser equiparado a falso sem registro"
    assert "rumor" in entrada["nota"].lower()


def test_registro_com_vereditos_divergentes_e_marcado_misto():
    registro = vereditos.classificar_registro(
        "['FALSO', 'SUBESTIMADO', 'VERDADEIRO', 'VERDADEIRO']")

    assert registro.misto is True
    assert registro.rotulo_consolidado is None
    assert registro.caso_de_teste_de_decomposicao is True


def test_registro_de_veredito_unico_recebe_rotulo_consolidado():
    registro = vereditos.classificar_registro("['boato']")

    assert registro.misto is False
    assert registro.rotulo_consolidado == "falso"


def test_compilado_com_mais_de_vinte_vereditos_sai_do_banco_de_estimulos():
    registro = vereditos.classificar_registro(str(["FALSO"] * 21))

    assert registro.excluido_do_banco_de_estimulos is True
    assert "compilado" in registro.motivo_da_exclusao.lower()


def test_amostrar_itens_verdadeiros_do_corpus_e_recusado():
    with pytest.raises(vereditos.CaveatDeCarencia) as erro:
        vereditos.amostrar_verdadeiros(leitura.ler_corpus())

    assert "4.063" in str(erro.value)
