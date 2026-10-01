"""Task 3.2 de mvp-copiloto-verificacao: estrutura de quatro blocos.

Requirement Estrutura de quatro blocos, de `resposta-formativa`, na redação do
`fix-resposta-sem-evidencia`: duas formas, escolhidas pelo estado da
recuperação, nunca trocadas. O modelo escreve o conteúdo dos blocos; ordem,
títulos, veredito, data de corte e ponteiro saem do código. Os testes trocam o
modelo por uma função que devolve JSON fixo.
"""
import json

import pytest

from prototipo.resposta import estrutura
from prototipo.resposta.estrutura import COM, SEM, responder
from prototipo.verificacao.guarda import INSUFICIENTE, Veredito

ALEGACAO = "A casca triturada do fruto do jatobá cura o câncer."
MENSAGEM = "Repassem! A casca do jatobá triturada cura o câncer, um médico confirmou."

TRECHO = {"fragmento_id": "c7a4591df5-00-00", "agencia": "aos fatos",
          "url": "https://www.aosfatos.org/jatoba", "data_publicacao": "2021-01-08",
          "veredito_original": "falso",
          "trecho": "Não há estudo que mostre que o jatobá cure câncer.", "score": 0.8}

FALSO = Veredito("falso", "O trecho T1 diz que não há estudo sobre o jatobá e o câncer.", [TRECHO])
VERDADEIRO = Veredito("verdadeiro", "O trecho T1 confirma.", [TRECHO])
SEM_TRECHO = Veredito(INSUFICIENTE, "Nenhum trecho recuperado cobre a alegação.",
                      rebaixado_por="nenhum trecho recuperado")

BLOCOS_FALSO = {
    "bloco1": "Nenhum estudo mostra isso.",
    "bloco2": "As checagens não acharam estudo sobre o jatobá e o câncer. "
              "Não é verdade que a casca do jatobá cura o câncer.",
    "bloco3": "Técnica: cura milagrosa. A mensagem promete curar doença grave com algo caseiro.",
    "bloco4": "Desconfie de promessa de cura simples. Pergunte quem fez o estudo.",
}

BLOCOS_SEM = {
    "bloco1": "Procuramos checagens sobre chá de goiabeira e dengue.",
    "bloco2": "Não encontrar uma checagem não quer dizer que a mensagem seja falsa.",
    "bloco3": "Veja se a mensagem diz quem fez o estudo. Procure a notícia em outro site.",
    "bloco4": "Consulte o site do Ministério da Saúde.",
}


def _chat(blocos):
    chamadas = []

    def chat(sistema, usuario):
        chamadas.append((sistema, usuario))
        return json.dumps(blocos, ensure_ascii=False)
    chat.chamadas = chamadas
    return chat


def _com(**mudancas):
    return {**BLOCOS_FALSO, **mudancas}


def _sem(**mudancas):
    return {**BLOCOS_SEM, **mudancas}


# ---- escolha da forma ------------------------------------------------------

def test_veredito_com_trecho_usa_a_forma_com_evidencia():
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(BLOCOS_FALSO))
    assert r.forma == "com evidência"
    assert r.titulos == COM


def test_evidencia_insuficiente_usa_a_forma_sem_evidencia():
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, chat=_chat(BLOCOS_SEM))
    assert r.forma == "sem evidência"
    assert r.titulos == SEM


def test_lacuna_de_acervo_usa_a_forma_sem_evidencia():
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, lacuna={"corte": "2021"},
                  chat=_chat(_sem(bloco4="")))
    assert r.forma == "sem evidência"


def test_lacuna_com_veredito_com_trecho_e_recusada():
    # Forma sem evidência quando há trecho é troca de forma, que a spec proíbe.
    with pytest.raises(ValueError, match="lacuna"):
        responder(MENSAGEM, ALEGACAO, FALSO, lacuna={"corte": "2021"}, chat=_chat(BLOCOS_FALSO))


def test_lacuna_sem_data_de_corte_e_recusada():
    with pytest.raises(ValueError, match="corte"):
        responder(MENSAGEM, ALEGACAO, SEM_TRECHO, lacuna={}, chat=_chat(BLOCOS_SEM))


def test_estado_vai_ao_modelo_na_mensagem_com_um_prompt_so():
    com, sem = _chat(BLOCOS_FALSO), _chat(BLOCOS_SEM)
    responder(MENSAGEM, ALEGACAO, FALSO, chat=com)
    responder(MENSAGEM, ALEGACAO, SEM_TRECHO, chat=sem)
    assert com.chamadas[0][0] == sem.chamadas[0][0] == estrutura.SISTEMA
    assert "ESTADO DA RECUPERAÇÃO: com evidência" in com.chamadas[0][1]
    assert f"ESTADO DA RECUPERAÇÃO: {INSUFICIENTE}" in sem.chamadas[0][1]


# ---- o que sai do código, não do modelo -----------------------------------

def test_verdadeiro_nao_leva_o_titulo_engana():
    # Spec, cenário Alegação verdadeira: o bloco 3 explica por que era difícil de avaliar.
    r = responder(MENSAGEM, ALEGACAO, VERDADEIRO, chat=_chat(_com(bloco3="Parecia exagero.")))
    assert r.titulos[2] == estrutura.TITULO_3_VERDADEIRO
    assert "ENGANA" not in r.texto


def test_quatro_blocos_em_ordem_com_os_titulos():
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(BLOCOS_FALSO))
    posicoes = [r.texto.find(t) for t in COM]
    assert -1 not in posicoes and posicoes == sorted(posicoes)


@pytest.mark.parametrize("rotulo, abertura", [
    ("falso", "Falso."),
    ("verdadeiro", "Verdadeiro."),
    ("verdadeiro fora de contexto ou exagerado", "Verdadeiro, mas fora de contexto ou exagerado."),
])
def test_bloco_1_abre_com_o_veredito_da_classificacao(rotulo, abertura):
    v = Veredito(rotulo, "critério", [TRECHO])
    r = responder(MENSAGEM, ALEGACAO, v, chat=_chat(_com(bloco1="Uma frase.")))
    assert r.blocos[0].startswith(abertura)


def test_modelo_nao_muda_o_veredito():
    # O modelo pode escrever "verdadeiro" no bloco 1; o rótulo da abertura é o da guarda.
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(_com(bloco1="Verdadeiro.")))
    assert r.blocos[0].startswith("Falso.")


def test_lacuna_abre_com_a_data_de_corte_escrita_pelo_codigo():
    # Decisão 4 de fix-resposta-sem-evidencia: o modelo omitiu a data 9 vezes em 9.
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, lacuna={"corte": "2021"},
                  chat=_chat(_sem(bloco1="Procuramos a vacina.", bloco4="")))
    assert r.blocos[0].startswith("Lacuna de acervo. As checagens consultadas vão só até 2021.")
    assert INSUFICIENTE not in r.texto.lower()


def test_lacuna_com_ponteiro_vai_inteiro_no_bloco_4():
    ponteiro = {"agencia": "Aos Fatos", "data": "02/02/2024", "veredito": "falso",
                "endereco": "https://www.aosfatos.org/dengue"}
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, lacuna={"corte": "2021", "ponteiro": ponteiro},
                  chat=_chat(_sem(bloco4="")))
    for valor in ponteiro.values():
        assert valor in r.blocos[3]


def test_lacuna_sem_ponteiro_declara_que_nao_localizou():
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, lacuna={"corte": "2021"},
                  chat=_chat(_sem(bloco4="")))
    assert "não foi localizada checagem em português" in r.blocos[3].lower()
    assert "não existe" not in r.blocos[3].lower()


def test_trechos_vao_para_a_camada_de_detalhe():
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(BLOCOS_FALSO))
    assert r.detalhe == [{"agencia": "aos fatos", "data_publicacao": "2021-01-08",
                          "url": "https://www.aosfatos.org/jatoba",
                          "veredito_original": "falso", "trecho": TRECHO["trecho"]}]
    assert TRECHO["url"] not in r.texto


# ---- defeitos: contratos das tasks 3.3 e 3.4 e de acessibilidade-leitura ---

def test_resposta_falsa_em_ordem_nao_tem_defeito():
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(BLOCOS_FALSO))
    assert r.defeitos == []


def test_resposta_sem_evidencia_em_ordem_nao_tem_defeito():
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, chat=_chat(BLOCOS_SEM))
    assert r.defeitos == []


def test_saida_que_nao_e_json_e_defeito():
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=lambda s, u: "Falso. A casca não cura.")
    assert r.defeitos == ["saída não é JSON"]


@pytest.mark.parametrize("bloco", ["bloco2", "bloco3", "bloco4"])
def test_bloco_vazio_e_defeito(bloco):
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(_com(**{bloco: " "})))
    assert f"{bloco} vazio" in r.defeitos


def test_bloco_3_sem_marcador_de_tecnica_e_defeito():
    r = responder(MENSAGEM, ALEGACAO, FALSO,
                  chat=_chat(_com(bloco3="Promete cura com algo caseiro.")))
    assert "bloco 3: nenhum rótulo marcado" in r.defeitos


def test_tecnica_fora_do_catalogo_e_defeito():
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(_com(bloco3="Técnica: apelo ao medo.")))
    assert "bloco 3: rótulo fora do catálogo: apelo ao medo" in r.defeitos


def test_tecnica_fora_do_bloco_3_nao_conta():
    r = responder(MENSAGEM, ALEGACAO, FALSO,
                  chat=_chat(_com(bloco3="Promete cura.", bloco4="Técnica: cura milagrosa.")))
    assert "bloco 3: nenhum rótulo marcado" in r.defeitos


def test_verdadeiro_nao_nomeia_tecnica():
    # Técnica de manipulação em mensagem verdadeira desdiria o veredito (decisão 18).
    sem_tecnica = _com(bloco3="Parece exagero, mas a checagem confirma.")
    assert responder(MENSAGEM, ALEGACAO, VERDADEIRO, chat=_chat(sem_tecnica)).defeitos == []
    com_tecnica = _com(bloco3="Técnica: fora de contexto. Parece exagero.")
    assert "técnica nomeada em veredito verdadeiro: fora de contexto" in \
        responder(MENSAGEM, ALEGACAO, VERDADEIRO, chat=_chat(com_tecnica)).defeitos


def test_dois_rotulos_do_catalogo_passam():
    blocos = _com(bloco3="Técnica: cura milagrosa, fonte sem nome. Promete cura e cita médico sem nome.")
    assert responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(blocos)).defeitos == []


def test_tecnica_na_forma_sem_evidencia_e_defeito():
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO,
                  chat=_chat(_sem(bloco3="Técnica: cura milagrosa. Desconfie.")))
    assert "técnica nomeada sem evidência: cura milagrosa" in r.defeitos


def test_rotulo_do_catalogo_sem_marcador_tambem_e_defeito_sem_evidencia():
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO,
                  chat=_chat(_sem(bloco3="Isso tem cara de cura milagrosa. Desconfie.")))
    assert "técnica nomeada sem evidência: cura milagrosa" in r.defeitos


def test_bloco_3_sem_evidencia_que_diz_que_engana_e_defeito():
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO,
                  chat=_chat(_sem(bloco3="Essa mensagem engana quem lê. Confira a fonte.")))
    assert "bloco 3 da forma sem evidência afirma que a mensagem engana" in r.defeitos


def test_mito_sem_marcacao_e_defeito_no_falso():
    blocos = _com(bloco2="Muita gente diz que a casca do jatobá triturada cura o câncer.")
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(blocos))
    assert any(d.startswith("mito: menção sem marcação de falso") for d in r.defeitos)


def test_identificador_de_trecho_na_camada_visivel_e_defeito():
    r = responder(MENSAGEM, ALEGACAO, FALSO,
                  chat=_chat(_com(bloco2="O trecho T1 diz que não há estudo.")))
    assert "identificador de trecho na camada visível: T1" in r.defeitos


def test_mais_de_120_palavras_e_defeito():
    longo = " ".join(["Confira a fonte antes de repassar."] * 25)
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(_com(bloco4=longo)))
    assert any(d.startswith("camada visível com") and "120" in d for d in r.defeitos)


def test_frase_de_mais_de_20_palavras_e_defeito():
    frase = ("Antes de repassar qualquer mensagem sobre saúde que chega pelo celular vale a pena "
             "conferir com calma quem escreveu e de onde veio a informação.")
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(_com(bloco4=frase)))
    assert any(d.startswith("frase com mais de 20 palavras") for d in r.defeitos)


def test_opiniao_da_mensagem_tem_de_aparecer_no_bloco_2():
    # verificacao-alegacao: a decomposição aparece no bloco 2.
    decomposicao = {"fatos": ["a casca cura o câncer"], "evidencias": [],
                    "opinioes": ["os médicos escondem isso"], "conclusao": None}
    r = responder(MENSAGEM, ALEGACAO, FALSO, decomposicao=decomposicao, chat=_chat(BLOCOS_FALSO))
    assert "bloco 2 não separa a opinião da mensagem" in r.defeitos
    ok = _com(bloco2=BLOCOS_FALSO["bloco2"] + " Que os médicos escondem isso é opinião.")
    assert responder(MENSAGEM, ALEGACAO, FALSO, decomposicao=decomposicao,
                     chat=_chat(ok)).defeitos == []


# ---- lacuna com ponteiro: decisão 5 de fix-resposta-sem-evidencia ----------

PONTEIRO = {"agencia": "Aos Fatos", "data": "02/02/2024", "veredito": "falso",
            "endereco": "https://www.aosfatos.org/dengue"}
COM_PONTEIRO = {"corte": "2021", "ponteiro": PONTEIRO}


def test_veredito_do_ponteiro_nao_vai_ao_modelo():
    chat = _chat(_sem(bloco4=""))
    responder(MENSAGEM, ALEGACAO, SEM_TRECHO, lacuna=COM_PONTEIRO, chat=chat)
    assert PONTEIRO["endereco"] not in chat.chamadas[0][1]


def test_bloco_2_com_ponteiro_sai_do_codigo_sem_julgar_a_alegacao():
    # Na sonda, o modelo escreveu "não significa que seja falsa" 3 vezes em 3,
    # ao lado de um ponteiro com veredito falso (decisão 18).
    blocos = _sem(bloco2="Não encontrar dados não significa que a informação seja falsa.",
                  bloco4="")
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, lacuna=COM_PONTEIRO, chat=_chat(blocos))
    assert r.blocos[1] == estrutura.BLOCO_2_COM_PONTEIRO
    assert "fals" not in r.blocos[1].lower() and "verdadeir" not in r.blocos[1].lower()
    assert "acervo" in r.blocos[1].lower()
    assert r.defeitos == []


def test_com_ponteiro_o_modelo_pode_deixar_o_bloco_2_vazio():
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, lacuna=COM_PONTEIRO,
                  chat=_chat(_sem(bloco2="", bloco4="")))
    assert r.defeitos == []


def test_sem_ponteiro_o_bloco_2_ainda_pode_dizer_que_nao_e_desmentir():
    # A regra da decisão 5 vale só com ponteiro; sem ele, vale o bloco 2 da spec.
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, chat=_chat(BLOCOS_SEM))
    assert r.defeitos == []
