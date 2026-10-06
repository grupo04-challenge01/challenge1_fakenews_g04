"""Task 1.6 de mvp-copiloto-verificacao: conferência frase × trecho.

`recuperacao-evidencia`, requirement Rastreabilidade da evidência: toda
afirmação factual SHALL estar ancorada em um trecho recuperado. Decisão tomada
antes do código (Samara, 06/10/2026): o modelo declara a âncora de cada frase,
e o código confere que o trecho é apto e contém os termos verificáveis da
frase — números, meses, quantidades por extenso e nomes próprios. Paráfrase
sem esses termos passa: a conferência pega o detalhe inventado, não o sentido.

Os trechos abaixo são excertos literais do índice, dos casos da sonda da
resposta (decisão 18).
"""
from prototipo.resposta.ancoragem import ancorada, ancorar_bloco, sem_suporte, termos

JATOBA = {"agencia": "aos fatos", "data_publicacao": "2021-01-08", "apto_citacao": True,
          "trecho": "Não existe um alimento comprovadamente capaz de prevenir ou curar a "
                    "doença, segundo o Ministério da Saúde, o Inca (Instituto Nacional do "
                    "Câncer) e um oncologista ouvido por Aos Fatos. O conteúdo enganoso "
                    "reunia ao menos 172 mil compartilhamentos no Facebook."}
CAIXAO = {"agencia": "COMPROVA", "data_publicacao": "2020-05-27", "apto_citacao": True,
          "trecho": "O procedimento de lacrar o caixão é padrão em casos de óbitos "
                    "confirmados ou com suspeitas de coronavírus. O resultado do exame foi "
                    "divulgado somente uma semana depois e o teste deu negativo. O caso "
                    "ocorreu na cidade de Touros, no Rio Grande do Norte, no dia 19 de maio."}
COVAS = {"agencia": "COMPROVA", "data_publicacao": "2020-07-31", "apto_citacao": True,
         "trecho": "o deputado usa como se fosse de agora um vídeo gravado em 9 de abril no "
                   "qual o prefeito de São Paulo anuncia a inclusão da cloroquina no "
                   "protocolo, mas isso já é feito desde 5 de maio"}


# Termos verificáveis ---------------------------------------------------------

def test_parafrase_sem_numero_nem_nome_nao_tem_termo_a_conferir():
    assert termos("Órgãos de saúde afirmam que nenhum alimento previne ou cura essa doença.") == []


def test_maiuscula_de_inicio_de_frase_nao_e_nome_proprio():
    assert termos("O procedimento era padrão.") == []


def test_extrai_numero_mes_quantidade_e_nome():
    achados = termos("O exame saiu uma semana depois, em maio de 2020, em Touros.")
    assert achados == ["uma semana", "maio", "2020", "touros"]


def test_um_e_uma_sozinhos_sao_artigo_nao_quantidade():
    assert termos("A checagem confirmou que uma criança foi enterrada.") == []


def test_numero_por_extenso_conta():
    assert termos("O teste saiu dois dias depois.") == ["dois dias"]


# Casos reais da sonda: frase sustentada passa ---------------------------------

def test_r3_uma_semana_depois_esta_no_trecho():
    assert ancorada("O exame negativo só saiu uma semana depois.", CAIXAO)


def test_r4_ano_vem_da_data_da_fonte():
    # "2020" não está no texto do trecho; está na data de publicação da checagem.
    assert ancorada("O prefeito fez esse anúncio em abril de 2020, não agora.", COVAS)


def test_r1_parafrase_passa():
    assert ancorada("Órgãos de saúde afirmam que nenhum alimento previne ou cura essa doença.",
                    JATOBA)


def test_acento_e_caixa_nao_impedem():
    assert ancorada("Segundo o INCA e o ministerio da saude, nada cura.", JATOBA)


def test_numero_com_milhar():
    assert ancorada("A mensagem teve 172 mil compartilhamentos.", JATOBA)


# Detalhe inventado: frase cai ---------------------------------------------------

def test_prazo_inventado_cai():
    assert sem_suporte("O exame saiu dois dias depois.", CAIXAO) == ["dois dias"]
    assert not ancorada("O exame saiu dois dias depois.", CAIXAO)


def test_lugar_inventado_cai():
    assert sem_suporte("O caso aconteceu em Natal.", CAIXAO) == ["natal"]


def test_numero_inventado_cai():
    assert not ancorada("A mensagem teve 500 mil compartilhamentos.", JATOBA)


def test_mes_inventado_cai():
    assert not ancorada("O anúncio foi feito em março.", COVAS)


def test_numero_parcial_nao_conta():
    # "19" está no trecho; "9" sozinho não pode casar dentro de "19".
    assert not ancorada("Foi no dia 9.", CAIXAO)


# Trecho inapto nunca é âncora -------------------------------------------------

def test_trecho_inapto_nao_ancora_nem_frase_sem_termo():
    inapto = dict(JATOBA, apto_citacao=False)
    assert not ancorada("Nenhum alimento cura essa doença.", inapto)


def test_trecho_sem_a_marca_nao_ancora():
    sem_marca = {k: v for k, v in JATOBA.items() if k != "apto_citacao"}
    assert not ancorada("Nenhum alimento cura essa doença.", sem_marca)


# Bloco inteiro: marca inline, frase a frase ----------------------------------


def test_marca_sai_do_texto_e_frase_ancorada_fica():
    mantidas, descartadas, _ = ancorar_bloco(
        "O exame saiu uma semana depois [T1]. O caixão era lacrado por padrão [T1].", [CAIXAO])
    assert mantidas == ["O exame saiu uma semana depois.", "O caixão era lacrado por padrão."]
    assert descartadas == []


def test_marca_depois_do_ponto_tambem_vale():
    mantidas, _, _ = ancorar_bloco("O exame saiu uma semana depois. [T1]", [CAIXAO])
    assert mantidas == ["O exame saiu uma semana depois."]


def test_frase_sem_marca_cai():
    mantidas, descartadas, _ = ancorar_bloco(
        "O caixão era lacrado [T1]. Isso acontece em todo o país.", [CAIXAO])
    assert mantidas == ["O caixão era lacrado."]
    assert descartadas == [{"frase": "Isso acontece em todo o país.", "motivo": "sem âncora"}]


def test_frase_com_termo_fora_do_trecho_cai_com_o_termo_no_motivo():
    _, descartadas, _ = ancorar_bloco("O exame saiu dois dias depois [T1].", [CAIXAO])
    assert descartadas == [{"frase": "O exame saiu dois dias depois.",
                            "motivo": "termo fora do trecho: dois dias"}]


def test_marca_de_trecho_que_nao_existe_cai():
    _, descartadas, _ = ancorar_bloco("O caixão era lacrado [T2].", [CAIXAO])
    assert descartadas[0]["motivo"] == "âncora inexistente: T2"


def test_duas_marcas_somam_as_fontes():
    # "Touros" está no CAIXAO; "abril" no COVAS. Cada termo precisa estar em alguma das duas.
    mantidas, _, _ = ancorar_bloco("Em Touros, como em abril [T1][T2].", [CAIXAO, COVAS])
    assert mantidas == ["Em Touros, como em abril."]


def test_marca_em_trecho_inapto_cai():
    _, descartadas, _ = ancorar_bloco("Nenhum alimento cura [T1].", [dict(JATOBA, apto_citacao=False)])
    assert descartadas[0]["motivo"] == "trecho inapto a citação: T1"


def test_frase_de_opiniao_sem_marca_fica_so_quando_ha_opiniao():
    texto = "Nenhum alimento cura [T1]. A parte sobre laboratórios é opinião."
    com, _, ancoradas = ancorar_bloco(texto, [JATOBA], opiniao=True)
    sem, descartadas, _ = ancorar_bloco(texto, [JATOBA], opiniao=False)
    assert com == ["Nenhum alimento cura.", "A parte sobre laboratórios é opinião."]
    assert ancoradas == 1  # a de opinião fica, mas não sustenta nada
    assert sem == ["Nenhum alimento cura."]
    assert descartadas[0]["motivo"] == "sem âncora"


def test_bloco_vazio_nao_tem_frase():
    assert ancorar_bloco("  ", [JATOBA]) == ([], [], 0)
