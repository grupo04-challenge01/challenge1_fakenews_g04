"""Task 1.1 de mvp-copiloto-verificacao: o índice segue o esquema de indexação.

Os testes de mutação partem de registros reais do índice e quebram uma regra por
vez, para mostrar que o validador acusa cada uma, e não só aprova o que vê.
"""
import copy
import json

import pytest

from prototipo.rag import corpus, esquema, unidades


@pytest.fixture(scope="module")
def indice():
    return unidades.construir(corpus.ler_corpus())


@pytest.fixture
def amostra(indice):
    """Uma unidade de dois fragmentos com seus fragmentos, em cópia."""
    uni, frags, _, _ = indice
    alvo = next(u for u in uni if u["fragmentos"] == 2)
    return (copy.deepcopy([alvo]),
            copy.deepcopy([f for f in frags if f["unidade_id"] == alvo["unidade_id"]]))


def _violacoes(uni, frags, quarentena=None):
    return esquema.validar(uni, frags, quarentena)["violacoes"]


def test_esquema_e_draft7_valido():
    from jsonschema import Draft7Validator

    Draft7Validator.check_schema(esquema.carregar_esquema())


def test_indice_do_factcenter_esta_no_esquema(indice):
    uni, frags, quarentena, manifesto = indice
    laudo = esquema.validar(uni, frags, quarentena)
    assert laudo["aprovado"], laudo["violacoes"]
    assert manifesto["esquema"] == {"arquivo": "prototipo/indice/esquema_indexacao.json",
                                    "versao": esquema.versao(), "aprovado": True}
    contagem = laudo["por_corpus"]["factcenter_saude"]
    assert contagem["registros_com_unidade"] + contagem["registros_em_quarentena"] == 4063
    assert (laudo["unidades"], laudo["fragmentos"]) == (5089, 22463)


def test_chaves_da_afericao_continuam_validas(indice):
    consultas = json.loads((esquema.RAIZ / "prototipo/rag/consultas_afericao.json")
                           .read_text(encoding="utf-8"))["consultas"]
    registros = {u["registro_id"] for u in indice[0]}
    assert {c["registro_id"] for c in consultas} <= registros


def test_alegacao_sem_justificativa_vai_para_quarentena(indice):
    uni, _, quarentena, _ = indice
    uid = "4ce7e4777f-04"  # Lupa, câncer de pele: texto raspado termina na alegação
    assert uid not in {u["unidade_id"] for u in uni}
    assert any(q.get("unidade_id") == uid and q["motivo"] == "justificativa_ausente"
               for q in quarentena)
    assert {"4ce7e4777f-00", "4ce7e4777f-03"} <= {u["unidade_id"] for u in uni}


def test_todo_fragmento_carrega_proveniencia_do_mvp(indice):
    for f in indice[1][:200]:
        assert f["corpus"] == "factcenter_saude" and f["idioma"] == "pt-BR"
        assert f["tipo_fonte"] == "checagem" and f["apto_citacao"] is True
        assert f["agencia_nome"] and f["url"] and f["data_publicacao"]


def test_fragmento_sem_cabecalho_e_acusado(amostra):
    uni, frags = amostra
    frags[0]["texto"] = frags[0]["trecho"]
    assert "I4" in _violacoes(uni, frags)


def test_veredito_alheio_no_fragmento_e_acusado(amostra):
    uni, frags = amostra
    frags[1]["veredito_original"] = "VERDADEIRO" if uni[0]["veredito_original"] != "VERDADEIRO" else "FALSO"
    assert "I3" in _violacoes(uni, frags)


def test_trecho_reescrito_e_acusado(amostra):
    uni, frags = amostra
    trecho = frags[0]["trecho"]
    reescrito = corpus.sem_acento(trecho) if corpus.sem_acento(trecho) != trecho else trecho + " (editado)"
    frags[0]["trecho"] = reescrito
    frags[0]["texto"] = frags[0]["texto"].rsplit("\n", 1)[0] + "\n" + reescrito
    assert "I5" in _violacoes(uni, frags)


def test_fragmento_faltando_e_acusado(amostra):
    uni, frags = amostra
    assert "I6" in _violacoes(uni, frags[:1])


def test_campo_fora_do_esquema_e_recusado(amostra):
    uni, frags = amostra
    uni[0]["rotulo"] = "falso"  # o mapa dos quatro rótulos não é deste esquema
    assert "forma:unidade" in _violacoes(uni, frags)


def test_comunicado_oficial_nao_tem_veredito(amostra):
    uni, frags = amostra
    uni[0]["tipo_fonte"] = "comunicado_oficial"
    assert "forma:unidade" in _violacoes(uni, frags)


def test_mesma_url_em_dois_corpora_e_acusada(amostra):
    uni, frags = amostra
    gemea = copy.deepcopy(uni[0])
    gemea.update(corpus="factckbr", apto_citacao=False,
                 registro_id=esquema.registro_id("factckbr", gemea["url"]))
    gemea["unidade_id"] = f'{gemea["registro_id"]}-00'
    assert "I10" in _violacoes(uni + [gemea], frags)


def test_agencia_fora_do_registro_interrompe():
    with pytest.raises(esquema.ErroDeEsquema):
        esquema.atributos_de_corpus("factcenter_saude", "agencia inventada")


def test_factckbr_mapeado_nao_e_apto_a_citacao():
    attrs = esquema.atributos_de_corpus("factckbr", "https:apublica.org")
    assert attrs["apto_citacao"] is False
    assert attrs["agencia_nome"] == "Truco (Agência Pública)"
    assert esquema.registro_id("factckbr", "https://x").startswith("fb-")
