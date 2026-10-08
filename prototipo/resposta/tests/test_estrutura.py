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
          "trecho": "Não há estudo que mostre que o jatobá cure câncer.", "score": 0.8,
          "apto_citacao": True}

FALSO = Veredito("falso", "O trecho T1 diz que não há estudo sobre o jatobá e o câncer.", [TRECHO])
VERDADEIRO = Veredito("verdadeiro", "O trecho T1 confirma.", [TRECHO])
SEM_TRECHO = Veredito(INSUFICIENTE, "Nenhum trecho recuperado cobre a alegação.",
                      rebaixado_por="nenhum trecho recuperado")

BLOCOS_FALSO = {
    # Blocos 1 e 2 como lista de frases com o trecho de cada uma (task 1.6).
    "bloco1": [{"frase": "Nenhum estudo mostra isso.", "trecho": "T1"}],
    "bloco2": [{"frase": "As checagens não acharam estudo sobre o jatobá e o câncer.", "trecho": "T1"},
               {"frase": "Não é verdade que a casca do jatobá cura o câncer.", "trecho": "T1"}],
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
    r = responder(MENSAGEM, ALEGACAO, v, chat=_chat(_com(bloco1="Uma frase [T1].")))
    assert r.blocos[0].startswith(abertura)


def test_modelo_nao_muda_o_veredito():
    # O modelo pode escrever "verdadeiro" no bloco 1; o rótulo da abertura é o da guarda.
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(_com(bloco1="Verdadeiro [T1].")))
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


@pytest.mark.parametrize("bloco", ["bloco3", "bloco4"])
def test_bloco_vazio_e_defeito(bloco):
    # Bloco 2 vazio na forma com evidência rebaixa o veredito (task 1.6); ver abaixo.
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(_com(**{bloco: " "})))
    assert f"{bloco} vazio" in r.defeitos


def test_bloco_3_sem_marcador_de_tecnica_e_defeito():
    r = responder(MENSAGEM, ALEGACAO, FALSO,
                  chat=_chat(_com(bloco3="Promete cura com algo caseiro.")))
    assert "bloco 3: nenhum rótulo marcado" in r.defeitos


def test_bloco_3_que_abre_com_rotulos_do_catalogo_ganha_o_marcador():
    # Bancada de 06/10: o modelo escreveu os rótulos certos sem "Técnica:" em 5 de
    # 6 casos da forense. O marcador sai do código (decisão 24).
    blocos = _com(bloco3="medo de dano oculto, urgência fabricada. A mensagem assusta e pede pressa.")
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(blocos))
    assert r.blocos[2].startswith("Técnica: medo de dano oculto, urgência fabricada.")
    assert r.defeitos == []


def test_marcador_nao_e_posto_quando_a_primeira_frase_nao_e_so_rotulo():
    r = responder(MENSAGEM, ALEGACAO, FALSO,
                  chat=_chat(_com(bloco3="Cura milagrosa é o que a mensagem promete.")))
    assert not r.blocos[2].startswith("Técnica:")
    assert "bloco 3: nenhum rótulo marcado" in r.defeitos


def test_marcador_nao_e_posto_em_veredito_verdadeiro():
    r = responder(MENSAGEM, ALEGACAO, VERDADEIRO,
                  chat=_chat(_com(bloco3="fora de contexto. Parece exagero.")))
    assert not r.blocos[2].startswith("Técnica:")


def test_bloco_2_que_ja_fala_de_opiniao_nao_ganha_a_frase():
    decomposicao = {"fatos": [ALEGACAO], "evidencias": [], "conclusao": None,
                    "opinioes": ["os laboratórios escondem isso"]}
    bloco2 = "O Inca não indica alimento contra câncer. Dizer que escondem é opinião."
    r = responder(MENSAGEM, ALEGACAO, FALSO, decomposicao=decomposicao,
                  chat=_chat(_com(bloco2=bloco2)))
    assert r.blocos[1] == bloco2


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
    blocos = _com(bloco2="Muita gente diz que a casca do jatobá triturada cura o câncer [T1].")
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(blocos))
    assert any(d.startswith("mito: menção sem marcação de falso") for d in r.defeitos)


def test_identificador_de_trecho_na_camada_visivel_e_defeito():
    r = responder(MENSAGEM, ALEGACAO, FALSO,
                  chat=_chat(_com(bloco2="O trecho T1 diz que não há estudo [T1].")))
    assert "identificador de trecho na camada visível: T1" in r.defeitos


def test_mais_de_120_palavras_e_defeito():
    # Uma frase só: o corte de fix-teto-resposta não tem o que tirar, e o defeito fica.
    longo = " ".join(["Confira a fonte antes de repassar"] * 25) + "."
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
    # Quando o modelo esquece, o código completa o bloco 2 (decisão 25).
    r = responder(MENSAGEM, ALEGACAO, FALSO, decomposicao=decomposicao, chat=_chat(BLOCOS_FALSO))
    assert r.blocos[1].endswith(estrutura.FRASE_OPINIAO)
    assert "bloco 2 não separa a opinião da mensagem" not in r.defeitos
    ok = _com(bloco2=BLOCOS_FALSO["bloco2"] + [{"frase": "Que os médicos escondem isso é opinião.",
                                                 "trecho": ""}])
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


# ---- ancoragem trecho a afirmação: task 1.6 --------------------------------

def _chat_em_sequencia(*saidas):
    """Uma saída por chamada. No rebaixamento são três: a primeira, a refeita com
    o aviso da conferência (decisão 29) e a da forma sem evidência."""
    chamadas = []

    def chat(sistema, usuario):
        chamadas.append((sistema, usuario))
        return json.dumps(saidas[len(chamadas) - 1], ensure_ascii=False)
    chat.chamadas = chamadas
    return chat


def test_marca_de_ancora_nao_aparece_na_camada_visivel():
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(BLOCOS_FALSO))
    assert "[T1]" not in r.texto
    assert r.blocos[1] == ("As checagens não acharam estudo sobre o jatobá e o câncer. "
                           "Não é verdade que a casca do jatobá cura o câncer.")
    assert r.descartadas == [] and r.rebaixada_por is None


def test_frase_sem_ancora_some_do_bloco_2_e_fica_registrada():
    blocos = _com(bloco2="Não há estudo sobre o jatobá [T1]. Um médico de Goiânia foi punido.")
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(blocos))
    assert r.forma == "com evidência"
    assert "Goiânia" not in r.texto
    assert r.descartadas == [{"bloco": 2, "frase": "Um médico de Goiânia foi punido.",
                              "motivo": "sem âncora"}]


def test_termo_inventado_com_marca_tambem_some():
    blocos = _com(bloco2="Não há estudo sobre o jatobá [T1]. O Inca testou 300 pacientes [T1].")
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(blocos))
    assert "300" not in r.texto
    assert r.descartadas[0]["motivo"] == "termo fora do trecho: inca, 300"


def test_bloco_1_sem_ancora_rebaixa_para_a_forma_sem_evidencia():
    falha = _com(bloco1="A checagem foi feita em 2019.")
    chat = _chat_em_sequencia(falha, falha, BLOCOS_SEM)
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=chat)
    assert r.forma == "sem evidência" and r.titulos == SEM
    assert r.blocos[0].startswith("Evidência insuficiente.")
    assert r.rebaixada_por == "ancoragem: bloco 1: sem âncora"
    assert r.descartadas == [{"bloco": 1, "frase": "A checagem foi feita em 2019.",
                              "motivo": "sem âncora"}]
    assert len(chat.chamadas) == 3
    assert f"ESTADO DA RECUPERAÇÃO: {INSUFICIENTE}" in chat.chamadas[2][1]
    assert r.detalhe == []


def test_bloco_2_sem_frase_ancorada_rebaixa():
    falha = _com(bloco2="Isso nunca foi estudado.")
    chat = _chat_em_sequencia(falha, falha, BLOCOS_SEM)
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=chat)
    assert r.forma == "sem evidência"
    assert r.rebaixada_por == "ancoragem: bloco 2 sem frase ancorada"


def test_bloco_2_vazio_rebaixa():
    falha = _com(bloco2=" ")
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat_em_sequencia(falha, falha, BLOCOS_SEM))
    assert r.rebaixada_por == "ancoragem: bloco 2 sem frase ancorada"


def test_bloco_2_so_com_opiniao_rebaixa():
    decomposicao = {"fatos": [], "evidencias": [], "opinioes": ["os médicos escondem isso"],
                    "conclusao": None}
    falha = _com(bloco2="Que os médicos escondem isso é opinião.")
    chat = _chat_em_sequencia(falha, falha, BLOCOS_SEM)
    r = responder(MENSAGEM, ALEGACAO, FALSO, decomposicao=decomposicao, chat=chat)
    assert r.rebaixada_por == "ancoragem: bloco 2 sem frase ancorada"


def test_rebaixamento_leva_as_referencias_do_veredito():
    ref = {"agencia": "lupa", "data_publicacao": "2020-01-01", "url": "https://l/1",
           "veredito_original": "falso"}
    v = Veredito("falso", "critério", [TRECHO], referencias=[ref])
    chat = _chat_em_sequencia(_com(bloco1="Sem marca."), _com(bloco1="Sem marca."), BLOCOS_SEM)
    r = responder(MENSAGEM, ALEGACAO, v, chat=chat)
    assert r.rebaixada_por is not None
    assert r.veredito.referencias == [ref]


def test_forma_sem_evidencia_nao_passa_pela_ancoragem():
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, chat=_chat(BLOCOS_SEM))
    assert r.descartadas == [] and r.rebaixada_por is None
    assert r.blocos[1] == BLOCOS_SEM["bloco2"]


def test_prompt_pede_a_ancora_em_campo_proprio_nos_blocos_1_e_2():
    assert '{"frase": "Nenhum estudo mostra isso.", "trecho": "T1"}' in estrutura.SISTEMA
    assert '"bloco2": [{"frase": "...", "trecho": "T1"}' in estrutura.SISTEMA


def test_marca_inline_continua_aceita():
    # Formato da primeira versão; o modelo pode voltar a ele.
    blocos = _com(bloco1="Nenhum estudo mostra isso [T1].",
                  bloco2="Não há estudo sobre o jatobá [T1].")
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(blocos))
    assert r.rebaixada_por is None
    assert r.blocos[1] == "Não há estudo sobre o jatobá."


def test_lista_na_forma_sem_evidencia_vira_texto():
    blocos = _sem(bloco1=[{"frase": "Procuramos checagens sobre goiabeira.", "trecho": ""}])
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, chat=_chat(blocos))
    assert r.blocos[0] == "Evidência insuficiente. Procuramos checagens sobre goiabeira."
    assert "frase" not in r.texto


# ---- referências inaptas na camada de detalhe: decisão 17, task 1.6 --------

REFERENCIA = {"agencia": "lupa", "data_publicacao": "2020-01-01", "url": "https://l/1",
              "veredito_original": "falso"}


def test_referencia_vai_ao_detalhe_depois_dos_trechos_e_sem_texto():
    v = Veredito("falso", "critério", [TRECHO], referencias=[REFERENCIA])
    r = responder(MENSAGEM, ALEGACAO, v, chat=_chat(BLOCOS_FALSO))
    assert r.detalhe[0]["trecho"] == TRECHO["trecho"]
    assert r.detalhe[1] == {**REFERENCIA, "trecho": None}
    assert REFERENCIA["url"] not in r.texto


def test_so_referencias_vao_ao_detalhe_da_forma_sem_evidencia():
    # Guarda sem trecho apto: insuficiente, mas a agência e o link continuam auditáveis.
    v = Veredito(INSUFICIENTE, "Nenhum trecho recuperado cobre a alegação.",
                 rebaixado_por="nenhum trecho apto a citação", referencias=[REFERENCIA])
    r = responder(MENSAGEM, ALEGACAO, v, chat=_chat(BLOCOS_SEM))
    assert r.forma == "sem evidência"
    assert r.detalhe == [{**REFERENCIA, "trecho": None}]


def test_referencia_continua_no_detalhe_depois_do_rebaixamento():
    v = Veredito("falso", "critério", [TRECHO], referencias=[REFERENCIA])
    falha = _com(bloco1="Sem marca.")
    r = responder(MENSAGEM, ALEGACAO, v, chat=_chat_em_sequencia(falha, falha, BLOCOS_SEM))
    assert r.rebaixada_por is not None
    assert r.detalhe == [{**REFERENCIA, "trecho": None}]


def test_saida_crua_do_modelo_fica_na_resposta():
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(BLOCOS_FALSO))
    assert json.loads(r.bruto) == BLOCOS_FALSO


def test_rebaixamento_guarda_as_tres_saidas_do_modelo():
    primeira = _com(bloco2="Isso nunca foi estudado.")
    segunda = _com(bloco2="Isso nunca foi pesquisado.")
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat_em_sequencia(primeira, segunda, BLOCOS_SEM))
    antes, depois = r.bruto.split("\n\n--- refeita na forma sem evidência ---\n\n")
    um, dois = antes.split("\n\n--- refeita com o aviso da conferência ---\n\n")
    assert json.loads(um) == primeira and json.loads(dois) == segunda
    assert json.loads(depois) == BLOCOS_SEM


# ---- nova tentativa antes do rebaixamento: decisão 29 ----------------------

def test_segunda_tentativa_ancorada_mantem_o_veredito():
    # F06 da bancada: o bloco 2 veio só com a opinião, e o "falso" caía.
    decomposicao = {"fatos": [], "evidencias": [], "opinioes": ["os médicos escondem isso"],
                    "conclusao": None}
    falha = _com(bloco2=[{"frase": "Que os médicos escondem isso é opinião.", "trecho": ""}])
    chat = _chat_em_sequencia(falha, BLOCOS_FALSO)
    r = responder(MENSAGEM, ALEGACAO, FALSO, decomposicao=decomposicao, chat=chat)
    assert r.forma == "com evidência" and r.rebaixada_por is None
    assert len(chat.chamadas) == 2
    assert r.veredito.rotulo == "falso"


def test_aviso_diz_o_motivo_e_as_frases_descartadas():
    falha = _com(bloco2=[{"frase": "O Inca testou 300 pacientes.", "trecho": "T1"}])
    chat = _chat_em_sequencia(falha, BLOCOS_FALSO)
    responder(MENSAGEM, ALEGACAO, FALSO, chat=chat)
    aviso = chat.chamadas[1][1]
    assert chat.chamadas[1][1].startswith(chat.chamadas[0][1])
    assert "bloco 2 sem frase ancorada" in aviso
    assert "O Inca testou 300 pacientes." in aviso and "termo fora do trecho: inca, 300" in aviso


def test_frase_descartada_na_segunda_tentativa_e_a_que_fica_registrada():
    segunda = _com(bloco2=BLOCOS_FALSO["bloco2"] + [{"frase": "Um médico de Goiânia foi punido.",
                                                     "trecho": ""}])
    chat = _chat_em_sequencia(_com(bloco2="Isso nunca foi estudado."), segunda)
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=chat)
    assert r.rebaixada_por is None
    assert [d["frase"] for d in r.descartadas] == ["Um médico de Goiânia foi punido."]


# ---- fragmentos vizinhos da checagem citada: decisão 29 --------------------

VIZINHO = {**TRECHO, "fragmento_id": "c7a4591df5-00-03",
           "trecho": "O boato circula desde abril de 2020, segundo a checagem.", "score": 0.4}
OUTRO_VIZINHO = {**TRECHO, "fragmento_id": "c7a4591df5-00-04",
                 "trecho": "A checagem ouviu o Inca.", "score": 0.3}


def _expandir(trechos):
    return list(trechos) + [VIZINHO, OUTRO_VIZINHO]


def test_vizinhos_chegam_ao_modelo_depois_dos_trechos_do_veredito():
    chat = _chat(BLOCOS_FALSO)
    responder(MENSAGEM, ALEGACAO, FALSO, chat=chat, expandir=_expandir)
    usuario = chat.chamadas[0][1]
    assert "[T1]" in usuario and "[T2]" in usuario and "[T3]" in usuario
    assert usuario.index(TRECHO["trecho"]) < usuario.index(VIZINHO["trecho"])


def test_frase_ancorada_no_vizinho_fica_e_o_vizinho_vai_ao_detalhe():
    blocos = _com(bloco2=BLOCOS_FALSO["bloco2"] + [{"frase": "O boato circula desde abril de 2020.",
                                                    "trecho": "T2"}])
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(blocos), expandir=_expandir)
    assert "abril de 2020" in r.texto and r.descartadas == []
    assert [d["trecho"] for d in r.detalhe] == [TRECHO["trecho"], VIZINHO["trecho"]]


def test_vizinho_que_nao_ancora_nada_fica_fora_do_detalhe():
    # recuperacao-evidencia: o texto da checagem não é reproduzido na íntegra.
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(BLOCOS_FALSO), expandir=_expandir)
    assert [d["trecho"] for d in r.detalhe] == [TRECHO["trecho"]]


def test_veredito_da_resposta_continua_com_os_trechos_da_guarda():
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_chat(BLOCOS_FALSO), expandir=_expandir)
    assert r.veredito.trechos == [TRECHO]


def test_sem_expandir_nada_muda():
    chat = _chat(BLOCOS_FALSO)
    responder(MENSAGEM, ALEGACAO, FALSO, chat=chat)
    assert "[T2]" not in chat.chamadas[0][1]


def test_forma_sem_evidencia_nao_expande():
    def explode(trechos):
        raise AssertionError("sem trecho não há o que expandir")
    r = responder(MENSAGEM, ALEGACAO, SEM_TRECHO, chat=_chat(BLOCOS_SEM), expandir=explode)
    assert r.forma == "sem evidência"


def test_prompt_tem_um_formato_por_estado():
    # Sonda de 06/10, 10:01: com um formato só para a forma sem evidência, o S1
    # deixou o bloco 4 vazio 3 vezes em 3; sem o prefixo no exemplo, o R4 escreveu
    # o rótulo sem "Técnica:" 3 vezes em 3.
    for estado in ("`com evidência`", f"`{INSUFICIENTE}`", "`lacuna de acervo`"):
        assert f"Estado {estado}" in estrutura.SISTEMA
    assert '"bloco3": "Técnica: rótulo.' in estrutura.SISTEMA
    assert '"bloco4": "Onde a pessoa pode procurar."' in estrutura.SISTEMA
