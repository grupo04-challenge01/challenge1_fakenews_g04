"""Testes da recoleta do FACTCK.BR — change add-tratamento-datasets-ptbr, task 3.5.

Três coisas precisam ficar de pé, e o laudo versionado só vale se as três
forem reexecutáveis:

1. A captura é a que o navegador viu: SHA-256 de cada título e de cada
   projeção de `ClaimReview` confere com o calculado na coleta.
2. O script reparado rodou sobre os três feeds e o resultado — inclusive zero
   alegação — sai do próprio `get_claimReview()`, não de reimplementação.
3. A perda histórica é irreversível: aplicar o `re_char()` reparado ao
   `FACTCKBR.tsv` distribuído não devolve nenhuma maiúscula acentuada
   (`integridade-textual`, cenário «Reparo confundido com recuperação do acervo»).
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
CAMINHO_RUNNER = RAIZ / "datasets" / "scripts" / "recoletar_factckbr.py"


def _carregar_runner():
    spec = importlib.util.spec_from_file_location("recoletar_factckbr", CAMINHO_RUNNER)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module")
def runner():
    return _carregar_runner()


@pytest.fixture(scope="module")
def captura(runner):
    return runner.carregar_captura()


@pytest.fixture(scope="module")
def resultado(runner, captura):
    return runner.executar(captura)


def test_captura_confere_com_os_hashes_da_coleta(captura):
    paginas = [p for a in captura["agencias"] for p in a["paginas"]]
    assert len(paginas) == 40
    assert sum(len(p["blocos"]) for p in paginas) == 18


def test_captura_adulterada_e_recusada(runner, captura):
    adulterada = json.loads(json.dumps(captura))
    bloco = adulterada["agencias"][0]["paginas"][0]["blocos"][0]
    bloco["projecao"] = bloco["projecao"].replace("bilhões", "bilhoes")
    with pytest.raises(runner.ErroDeCaptura):
        runner.conferir_hashes(adulterada)


def test_os_tres_feeds_foram_consultados(captura):
    feeds = [a["feed_declarado"] for a in captura["agencias"]]
    assert feeds == [
        "https://aosfatos.org/noticias/feed/",
        "https://apublica.org/tag/truco/feed/",
        "https://piaui.folha.uol.com.br/lupa/feed/",
    ]


def test_script_reparado_nao_extrai_nenhuma_alegacao(resultado):
    linhas, laudo = resultado
    assert len(linhas) == 0
    assert laudo["total_alegacoes_extraidas"] == 0


def test_descarte_do_aos_fatos_e_pelo_author_em_lista(resultado):
    _, laudo = resultado
    aos_fatos = laudo["por_agencia"][0]
    assert aos_fatos["blocos_claimreview"] == 18
    assert aos_fatos["causas_de_descarte"] == {"my_dict['author']['url']": 18}


def test_truco_e_lupa_nao_publicam_claimreview(resultado):
    _, laudo = resultado
    for agencia in laudo["por_agencia"][1:]:
        assert agencia["paginas_com_claimreview"] == 0


def test_controle_author_como_objeto_e_extraido_com_acento(runner):
    """Prova que o zero vem do esquema, não do filtro de caractere."""
    script = runner.carregar_script()
    bloco = json.dumps({
        "author": {"url": "https://www.aosfatos.org/"},
        "datePublished": "2026-10-05",
        "claimReviewed": "É falso que o SUS acabou",
        "reviewBody": "Ação do Ministério da Saúde",
        "reviewRating": {"ratingValue": 1, "bestRating": 6, "alternateName": "falso"},
        "itemReviewed": {"@type": "CreativeWork"},
    }, ensure_ascii=False)
    pagina = {"url": "https://exemplo.test/", "title": "Ônibus | Teste", "blocos": [{"projecao": bloco}]}
    linhas = runner.extrair_pagina(script, pagina)
    assert len(linhas) == 1
    assert linhas[0][3] == "É falso que o SUS acabou"
    assert linhas[0][4] == "Ação do Ministério da Saúde"
    assert linhas[0][5] == "Ônibus | Teste"


def test_filtro_reparado_preserva_todo_texto_recoletado(resultado):
    _, laudo = resultado
    fid = laudo["fidelidade"]
    assert fid["blocos_identicos_apos_text_pre_proc"] == fid["blocos"] == 18
    assert fid["titulos_identicos_apos_re_char"] == fid["titulos"] == 20
    assert fid["maiusculas_acentuadas_na_recoleta"].get("É", 0) > 0


def test_perda_historica_e_irreversivel(resultado):
    _, laudo = resultado
    acervo = laudo["acervo_historico"]
    assert acervo["registros"] == 1313
    assert acervo["antes"]["Ã"] == 0 and acervo["antes"]["ã"] == 3625
    assert acervo["depois_do_re_char_reparado"] == acervo["antes"]
    assert acervo["maiusculas_acentuadas_recuperadas"] == 0
    assert acervo["aprovado_para_citacao"] is False


def test_laudo_versionado_e_reproduzivel(runner, resultado):
    _, laudo = resultado
    gravado = json.loads(runner.CAMINHO_LAUDO.read_text(encoding="utf-8"))
    assert gravado == laudo


def test_tsv_versionado_tem_o_cabecalho_do_script_e_zero_linhas(runner):
    texto = runner.CAMINHO_TSV.read_text(encoding="utf-8")
    assert texto.splitlines() == [
        "URL\tAuthor\tdatePublished\tclaimReviewed\treviewBody\ttitle\t"
        "ratingValue\tbestRating\talternativeName\tcontentType"
    ]
