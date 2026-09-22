"""Testes dos derivados de veredito — bloco 2, tasks 2.2, 2.6, 2.7 e 2.8."""
from __future__ import annotations

from tratamento import leitura, relatorios


def test_marcacao_cobre_todo_registro_sem_rotulo_padrao_silencioso():
    marcado = relatorios.marcar_registros(leitura.ler_corpus())

    assert len(marcado) == 4063
    assert marcado["rotulo_consolidado"].isin(
        ["falso", "verdadeiro", "verdadeiro fora de contexto ou exagerado",
         "nao_mapeavel", ""]).all()
    # Registro misto não recebe consolidado; registro simples sempre recebe.
    assert (marcado.loc[marcado["misto"], "rotulo_consolidado"] == "").all()
    assert (marcado.loc[~marcado["misto"], "rotulo_consolidado"] != "").all()


def test_grafia_original_permanece_recuperavel_no_derivado():
    marcado = relatorios.marcar_registros(leitura.ler_corpus())
    assert "rating" in marcado.columns
    assert marcado["rating"].str.contains("VERDADEIRO, MAS").any()


def test_relatorio_conta_as_grafias_e_as_chaves_separadamente():
    relatorio = relatorios.relatorio_de_vereditos(leitura.ler_corpus())

    assert relatorio["strings_brutas_distintas"] == 285
    assert relatorio["grafias_distintas"] == 26
    assert relatorio["chaves_canonicas_distintas"] == 19
    assert sum(relatorio["por_agencia"][a]["registros"]
               for a in relatorio["por_agencia"]) == 4063
