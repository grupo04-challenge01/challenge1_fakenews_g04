"""Testes da adaptação dos instrumentos em inglês — bloco 5 do change.

Capability `adaptacao-criterios-en`: adaptação validada contra casos
brasileiros, nunca tradução literal; os dois conjuntos do FakeHealth MUST NOT
ser tratados como um só; exemplares de few-shot SHALL estar em português.
"""
from __future__ import annotations

from tratamento import criterios, leitura


def test_os_dois_conjuntos_sao_extraidos_separados_com_dez_perguntas_cada():
    conjuntos = criterios.extrair_conjuntos(
        leitura.ler_derivado("fakehealth_criterios_long.csv"))

    assert set(conjuntos) == {"HealthStory", "HealthRelease"}
    assert len(conjuntos["HealthStory"]) == 10
    assert len(conjuntos["HealthRelease"]) == 10


def test_conjuntos_nao_sao_consolidados_num_unico():
    conjuntos = criterios.extrair_conjuntos(
        leitura.ler_derivado("fakehealth_criterios_long.csv"))
    so_de_story = set(conjuntos["HealthStory"]) - set(conjuntos["HealthRelease"])

    assert so_de_story, "os conjuntos não são idênticos e a diferença importa"


def test_rubrica_tem_tres_niveis_em_todo_criterio():
    for criterio in criterios.RUBRICA:
        assert len(criterio.niveis) == 3
        assert set(criterio.niveis) == {"atende", "atende em parte", "nao atende"}


def test_rubrica_esta_em_portugues_e_nao_repete_a_pergunta_em_ingles():
    for criterio in criterios.RUBRICA:
        assert criterio.pergunta_pt
        assert criterio.pergunta_pt != criterio.pergunta_en
        assert "Does the" not in criterio.pergunta_pt


def test_todo_criterio_da_rubrica_declara_de_qual_conjunto_veio():
    for criterio in criterios.RUBRICA:
        assert criterio.conjunto_de_origem in {"HealthStory", "HealthRelease", "ambos"}


def test_criterio_removido_carrega_o_motivo_da_remocao():
    for criterio in criterios.REMOVIDOS:
        assert criterio.motivo_da_remocao


def test_validacao_mede_cobertura_de_cada_criterio_no_corpus_brasileiro():
    validacao = criterios.validar_contra_corpus(leitura.ler_corpus().head(800))

    assert set(validacao["por_criterio"]) == {c.id for c in criterios.RUBRICA}
    for medida in validacao["por_criterio"].values():
        assert 0.0 <= medida["proporcao"] <= 1.0


def test_forca_da_afirmacao_tem_nome_em_portugues_para_cada_nivel():
    assert set(criterios.FORCA_DA_AFIRMACAO) == {"0", "1", "2", "3"}
    for nome in criterios.FORCA_DA_AFIRMACAO.values():
        assert nome == nome.lower() or nome[0].isupper()
        assert " " in nome or nome.isalpha()


def test_comparacao_de_forca_liga_ao_catalogo_de_tecnicas():
    assert criterios.COMPARACAO_DE_FORCA["exaggerates"]["tecnica"] == "manchete exagerada"
    assert criterios.COMPARACAO_DE_FORCA["exaggerates"]["rotulo_pt"]
    assert criterios.COMPARACAO_DE_FORCA["same"]["tecnica"] == ""


def test_pool_de_fewshot_vem_do_corpus_brasileiro_e_nao_de_traducao():
    pool = criterios.pool_fewshot(leitura.ler_corpus(), por_rotulo=5, semente=42)

    assert len(pool) > 0
    assert set(pool["idioma"]) == {"pt-BR"}
    assert (pool["origem"] == "factcenter_subset_saude.csv").all()


def test_pool_de_fewshot_e_reproduzivel_pela_semente():
    a = criterios.pool_fewshot(leitura.ler_corpus(), por_rotulo=5, semente=42)
    b = criterios.pool_fewshot(leitura.ler_corpus(), por_rotulo=5, semente=42)

    assert list(a["url"]) == list(b["url"])


def test_pool_de_fewshot_nao_usa_registro_misto_nem_compilado():
    pool = criterios.pool_fewshot(leitura.ler_corpus(), por_rotulo=5, semente=42)

    assert (pool["n_vereditos"] == 1).all()
    assert pool["rotulo_consolidado"].ne("").all()


def test_proxy_de_vocabulario_nao_separa_mantidos_de_removidos():
    """O proxy foi medido e reprovado. Este teste trava a conclusão.

    Medir cobertura de vocabulário sobre a alegação dá 0,029 para `linguagem`
    e 0,063 para `novidade` — ou seja, sob qualquer piso único o proxy remove
    um critério central de desinformação e mantém um que não tem objeto. O
    número entra no registro como evidência contra o método, não a favor das
    remoções, que se sustentam no argumento de unidade de análise.
    """
    validacao = criterios.validar_contra_corpus(leitura.ler_corpus())

    mantidos = [m["proporcao"] for m in validacao["por_criterio"].values()]
    removidos = [m["proporcao"] for m in validacao["removidos_medidos"].values()]

    assert min(mantidos) < max(removidos), (
        "se o proxy passar a separar, a decisão de 5.4 pode ser revista — "
        "mas hoje ele não separa, e o registro precisa dizer isso")
    assert validacao["proxy_valido_como_regra"] is False


def test_validacao_mede_sobre_a_alegacao_e_nao_sobre_a_analise_da_agencia():
    validacao = criterios.validar_contra_corpus(leitura.ler_corpus())
    assert "title" in validacao["objeto_medido"]
    assert "text_news" not in validacao["objeto_medido"]
