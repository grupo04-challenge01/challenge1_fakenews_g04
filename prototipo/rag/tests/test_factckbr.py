"""Task 1.2 de mvp-copiloto-verificacao: FACTCK.BR indexado como fonte auxiliar.

Decisão 17 do design.md. O FACTCK.BR entra na busca sem filtro de tema, com todo
registro marcado como não apto a citação (integridade-textual revisada em
01/10/2026), e com cada veredito passando pelo mapa versionado de
`normalizacao-rotulos` antes de entrar no índice.
"""
import pandas as pd
import pytest

from prototipo.rag import corpus, esquema, unidades
from tratamento.vereditos import VeredictoDesconhecido

COLUNAS = ["URL", "Author", "datePublished", "claimReviewed", "reviewBody",
           "title", "ratingValue", "bestRating", "alternativeName"]


def _linha(**campos):
    base = {"URL": "https://aosfatos.org/noticias/exemplo/",
            "Author": "https:www.aosfatos.org", "datePublished": "2019-07-22",
            "claimReviewed": "Vacina causa autismo.",
            "reviewBody": "Não há estudo que sustente a associação.",
            "title": "Vacina não causa autismo | Aos Fatos", "ratingValue": "1",
            "bestRating": "5", "alternativeName": "falso"}
    base.update(campos)
    return base


def _df(*linhas):
    return pd.DataFrame(list(linhas), columns=COLUNAS)


@pytest.fixture(scope="module")
def indice():
    return unidades.construir_indice(corpus.ler_corpus(), corpus.ler_factckbr())


@pytest.fixture(scope="module")
def so_factcenter():
    return unidades.construir(corpus.ler_corpus())


# Leitura e portões --------------------------------------------------------

def test_leitura_confere_as_1313_linhas_declaradas():
    assert len(corpus.ler_factckbr()) == 1313


def test_leitura_com_contagem_divergente_e_rejeitada(tmp_path):
    origem = corpus.CAMINHO_FACTCKBR.read_text(encoding="utf-8").splitlines()
    truncado = tmp_path / "FACTCKBR.tsv"
    truncado.write_text("\n".join(origem[:50]) + "\n", encoding="utf-8")
    with pytest.raises(corpus.ErroDePortao):
        corpus.ler_factckbr(truncado)


def test_portao_de_integridade_confirma_que_nao_e_apto_a_citacao():
    laudo = corpus.verificar_integridade_auxiliar("factckbr")
    assert laudo["aprovado"] is False
    assert {"Ã", "Ç", "Ú"} <= {c["maiuscula"] for c in laudo["corrompidos"]}


def test_laudo_que_contradiz_o_esquema_interrompe(monkeypatch):
    """Se a recoleta da task 3.5 um dia aprovar o arquivo, alguém precisa trocar
    apto_citacao no esquema de propósito, e não descobrir pela saída."""
    original = esquema.carregar_esquema()
    original["x-corpora"]["factckbr"]["apto_citacao"] = True
    monkeypatch.setattr(esquema, "carregar_esquema", lambda *a, **k: original)
    with pytest.raises(corpus.ErroDePortao):
        corpus.verificar_integridade_auxiliar("factckbr")


# Rótulos normalizados ------------------------------------------------------

def test_veredito_fora_do_mapa_interrompe_o_corpus_inteiro():
    df = _df(_linha(), _linha(URL="https://aosfatos.org/outra/",
                              alternativeName="Meio verdade"))
    with pytest.raises(VeredictoDesconhecido):
        unidades.construir_factckbr(df, set())


def test_toda_chave_do_factckbr_esta_no_mapa(indice):
    from tratamento.vereditos import MAPA
    uni = [u for u in indice[0] if u["corpus"] == "factckbr"]
    assert {u["veredito_chave"] for u in uni} <= set(MAPA["entradas"])


def test_veredito_guarda_grafia_original_e_chave(indice):
    uni = [u for u in indice[0] if u["corpus"] == "factckbr"]
    sem_contexto = next(u for u in uni if u["veredito_original"] == "Sem contexto")
    assert sem_contexto["veredito_chave"] == "sem contexto"
    assert "rotulo" not in sem_contexto  # o mapa dos quatro rótulos não é do índice


# Construção ----------------------------------------------------------------

def test_linha_vazia_vai_para_quarentena_e_preserva_as_irmas():
    url = "https://piaui.folha.uol.com.br/lupa/2019/01/01/exemplo/"
    df = _df(_linha(URL=url, Author="https:piaui.folha.uol.com.brlupa",
                    claimReviewed=""),
             _linha(URL=url, Author="https:piaui.folha.uol.com.brlupa",
                    claimReviewed="Segunda alegação da mesma checagem."))
    uni, _, quarentena, _ = unidades.construir_factckbr(df, set())
    assert [u["indice_alegacao"] for u in uni] == [1]
    assert quarentena[0]["unidade_id"].endswith("-00")
    assert quarentena[0]["motivo"] == "campo_vazio"


def test_url_com_todas_as_linhas_vazias_vai_inteira_para_quarentena():
    _, _, quarentena, _ = unidades.construir_factckbr(_df(_linha(reviewBody="  ")), set())
    assert len(quarentena) == 1 and "unidade_id" not in quarentena[0]


def test_url_ja_indexada_no_factcenter_nao_entra(indice):
    uni, _, quarentena, _ = indice
    no_factcenter = {esquema.normalizar_url(u["url"]) for u in uni
                     if u["corpus"] == "factcenter_saude"}
    assert not any(esquema.normalizar_url(u["url"]) in no_factcenter
                   for u in uni if u["corpus"] == "factckbr")
    duplicatas = [q for q in quarentena if q.get("motivo") == "duplicata_factcenter"]
    assert len(duplicatas) == 74


def test_data_com_hora_e_truncada():
    uni, _, _, _ = unidades.construir_factckbr(
        _df(_linha(datePublished="2019-07-22 17:16:52")), set())
    assert uni[0]["data_publicacao"] == "2019-07-22"


def test_url_com_varias_alegacoes_vira_segmentada_por_claim_review():
    url = "https://apublica.org/2018/10/exemplo/"
    df = _df(*[_linha(URL=url, Author="https:apublica.org",
                      claimReviewed=f"Alegação número {i}.") for i in range(3)])
    uni, _, _, _ = unidades.construir_factckbr(df, set())
    assert {u["disposicao"] for u in uni} == {"segmentada"}
    assert {u["origem_alegacao"] for u in uni} == {"claim_review"}
    assert {u["alegacoes_no_registro"] for u in uni} == {3}
    assert not any(u["cobre_multiplas_alegacoes"] for u in uni)


def test_cabecalho_usa_o_nome_exibivel_da_agencia():
    _, frags, _, _ = unidades.construir_factckbr(_df(_linha()), set())
    assert frags[0]["texto"].split("\n")[1].startswith("Veredito de Aos Fatos em")


# Índice inteiro ------------------------------------------------------------

def test_indice_dos_dois_corpora_passa_no_esquema(indice):
    laudo = esquema.validar(indice[0], indice[1], indice[2])
    assert laudo["aprovado"], laudo["violacoes"]
    fb = laudo["por_corpus"]["factckbr"]
    assert fb["registros_com_unidade"] + fb["registros_em_quarentena"] == 984


def test_todo_registro_do_factckbr_e_nao_apto_a_citacao(indice):
    uni, frags, _, _ = indice
    do_fb = [r for r in uni + frags if r["corpus"] == "factckbr"]
    assert do_fb and all(r["apto_citacao"] is False for r in do_fb)
    assert {r["agencia_nome"] for r in do_fb} == {
        "Agência Lupa", "Aos Fatos", "Truco (Agência Pública)"}


def test_factcenter_continua_identico_e_na_frente(indice, so_factcenter):
    """A matriz densa só pode ser estendida, e não refeita, se os fragmentos do
    FactCenter continuarem os mesmos e na mesma ordem, à frente do FACTCK.BR."""
    _, frags_fc, _, _ = so_factcenter
    _, frags, _, _ = indice
    assert len(frags_fc) == 22463
    assert [f["fragmento_id"] for f in frags[:len(frags_fc)]] == \
        [f["fragmento_id"] for f in frags_fc]
    assert [f["texto"] for f in frags[:len(frags_fc)]] == [f["texto"] for f in frags_fc]
    assert all(f["corpus"] == "factckbr" for f in frags[len(frags_fc):])


# Matriz densa ---------------------------------------------------------------

def _gravar_jsonl(caminho, registros):
    import json
    caminho.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n"
                               for r in registros), encoding="utf-8")


def test_matriz_so_e_estendida_sobre_prefixo_identico(tmp_path, monkeypatch):
    import numpy as np

    from prototipo.rag import __main__ as cli

    antigos = [{"fragmento_id": f"a-{i}", "texto": f"t{i}"} for i in range(3)]
    novos = antigos + [{"fragmento_id": "fb-x", "texto": "novo"}]
    _gravar_jsonl(tmp_path / "fragmentos.jsonl", antigos)
    np.save(tmp_path / "densa.npy", np.zeros((3, 4), dtype="float32"))
    monkeypatch.setattr(cli, "SAIDA", tmp_path)
    monkeypatch.setattr(cli, "MATRIZ", tmp_path / "densa.npy")

    assert cli._prefixo_reaproveitavel(novos) == 3
    alterado = [dict(f) for f in novos]
    alterado[1]["texto"] = "t1 reescrito"
    assert cli._prefixo_reaproveitavel(alterado) == 0
    np.save(tmp_path / "densa.npy", np.zeros((2, 4), dtype="float32"))
    assert cli._prefixo_reaproveitavel(novos) == 0  # matriz desalinhada do .jsonl
