"""Task 4.1 de mvp-copiloto-verificacao: classificador de pedido de conduta clínica individual.

Contrato da task 4.2 em `specs/fronteira-orientacao-saude/spec.md`: classificador
antes do LLM, respostas padrão por canal e bypass da checagem em menos de 500 ms
para risco imediato e sofrimento psíquico.
"""
import json
import time

import pytest

from prototipo.verificacao.fronteira import (
    CATEGORIAS, SISTEMA, carregar_respostas, classificar, por_regras, responder)


def _explode(sistema, usuario):
    raise AssertionError("o modelo não pode ser chamado no bypass")


def _modelo(*categorias):
    def chat(sistema, usuario):
        return json.dumps({"categorias": list(categorias), "motivo": "teste"})
    return chat


# --- respostas padrão, lidas da spec -------------------------------------------------

def test_respostas_padrao_saem_da_spec_nos_dois_canais():
    r = carregar_respostas()
    for chave in ("conduta_individual", "risco_imediato", "sofrimento_psiquico",
                  "veredito_sem_prescricao"):
        assert set(r[chave]) == {"web", "whatsapp"}, chave
    assert "SAMU (192)" in r["risco_imediato"]["web"]
    assert "CVV" in r["sofrimento_psiquico"]["whatsapp"]
    assert "Disque Saúde 136" in r["veredito_sem_prescricao"]["whatsapp"]


def test_resposta_unica_para_web_e_whatsapp_vale_nos_dois():
    r = carregar_respostas()
    assert r["sofrimento_psiquico"]["web"] == r["sofrimento_psiquico"]["whatsapp"]


def test_resposta_padrao_sem_marcador_de_citacao():
    assert not carregar_respostas()["conduta_individual"]["web"].startswith(">")


# --- regras ---------------------------------------------------------------------------

@pytest.mark.parametrize("texto, categoria", [
    ("Minha mãe está com dor no peito e falta de ar agora, vi que boldo resolve", "risco_imediato"),
    ("Ele desmaiou depois de tomar o chá que mandaram no grupo", "risco_imediato"),
    ("Tô com febre há 5 dias e manchas vermelhas", "risco_imediato"),
    ("Não aguento mais, quero morrer", "sofrimento_psiquico"),
    ("Vou tomar a cartela inteira pra acabar com tudo", "sofrimento_psiquico"),
    ("Meu avô pode trocar remédio de pressão por alho?", "conduta_individual"),
    ("Posso parar a insulina se tomar chá de pata de vaca?", "conduta_individual"),
    ("Qual a dose de ivermectina para prevenir covid?", "conduta_individual"),
    ("Meu exame de glicemia deu 130, é diabetes?", "conduta_individual"),
])
def test_regras_reconhecem(texto, categoria):
    assert categoria in por_regras(texto)


@pytest.mark.parametrize("texto", [
    "Mandaram no grupo que dor no peito se cura com água gelada. Procede?",
    "Recebi que a vacina da covid causa suicídio em jovens. É verdade?",
    "É verdade que ivermectina previne covid?",
    "Recebi que chá de alho baixa a pressão. É verdade?",
    # "esta" de "esta mensagem" não é "está com".
    "Esta mensagem diz que falta de ar passa com chá de hortelã.",
    "O estudo teve casos de desmaio entre os voluntários?",
])
def test_regras_nao_disparam_em_pedido_de_checagem(texto):
    assert por_regras(texto) == set()


def test_nao_acordar_e_sofrimento_nao_sintoma():
    # Sonda de 29/09, F10: "não acordar" casava com o sintoma "não acorda" e mandava
    # ao SAMU quem precisava do CVV.
    texto = "Estou muito triste desde que perdi meu emprego, às vezes penso que seria melhor não acordar mais"
    assert por_regras(texto) == {"sofrimento_psiquico"}


# --- classificação --------------------------------------------------------------------

def test_categorias_na_ordem_de_prioridade():
    assert CATEGORIAS == ("risco_imediato", "sofrimento_psiquico", "conduta_individual", "checagem")


def test_prompt_define_as_quatro_categorias():
    for c in CATEGORIAS:
        assert f'"{c}"' in SISTEMA


def test_risco_imediato_faz_bypass_sem_chamar_o_modelo_em_menos_de_500ms():
    inicio = time.perf_counter()
    i = classificar("Meu pai está com dor no peito agora", chat=_explode)
    assert (time.perf_counter() - inicio) < 0.5
    assert i.bypass
    assert i.categorias == ("risco_imediato",)
    assert i.via == "regras"


def test_sofrimento_psiquico_faz_bypass_sem_chamar_o_modelo():
    i = classificar("Não aguento mais, quero morrer", chat=_explode)
    assert i.bypass and i.categorias == ("sofrimento_psiquico",)


def test_psiquico_com_risco_traz_os_dois_na_ordem():
    i = classificar("Tomei a cartela inteira pra acabar com tudo e estou com falta de ar", chat=_explode)
    assert i.categorias == ("risco_imediato", "sofrimento_psiquico")


def test_modelo_pega_conduta_que_as_regras_nao_pegam():
    i = classificar("Minha mãe quer largar a quimio, o que você acha?", chat=_modelo("conduta_individual"))
    assert i.categorias == ("conduta_individual",)
    assert i.via == "modelo"
    assert not i.bypass


def test_modelo_pega_risco_que_as_regras_nao_pegam_e_faz_bypass():
    i = classificar("Penso que seria melhor não acordar mais", chat=_modelo("sofrimento_psiquico"))
    assert i.bypass


def test_conduta_das_regras_se_soma_ao_modelo():
    i = classificar("Posso parar o remédio de pressão?", chat=_modelo("checagem"))
    assert i.categorias == ("conduta_individual",)
    assert i.via == "regras+modelo"


def test_checagem_pura():
    i = classificar("É verdade que ivermectina previne covid?", chat=_modelo("checagem"))
    assert i.categorias == ("checagem",)
    assert not i.bypass


def test_checagem_ao_lado_de_outra_categoria_some():
    i = classificar("x", chat=_modelo("checagem", "conduta_individual"))
    assert i.categorias == ("conduta_individual",)


def test_modelo_com_saida_malformada_fica_com_as_regras():
    i = classificar("Posso parar o remédio?", chat=lambda s, u: "nada")
    assert i.categorias == ("conduta_individual",)
    assert i.via == "regras (modelo inválido)"


def test_modelo_com_categoria_inventada_e_saida_invalida():
    i = classificar("x", chat=_modelo("dieta"))
    assert i.categorias == ("checagem",)
    assert i.via == "regras (modelo inválido)"


# --- resposta -------------------------------------------------------------------------

def test_responder_usa_o_canal():
    i = classificar("Meu pai está com dor no peito agora", chat=_explode)
    web, zap = responder(i, "web"), responder(i, "whatsapp")
    assert web == [carregar_respostas()["risco_imediato"]["web"]]
    assert zap == [carregar_respostas()["risco_imediato"]["whatsapp"]]


def test_responder_empilha_na_ordem_de_prioridade():
    i = classificar("Tomei a cartela inteira pra acabar com tudo e estou com falta de ar", chat=_explode)
    r = carregar_respostas()
    assert responder(i, "web") == [r["risco_imediato"]["web"], r["sofrimento_psiquico"]["web"]]


def test_checagem_nao_tem_resposta_padrao():
    assert responder(classificar("x", chat=_modelo("checagem")), "web") == []


def test_canal_desconhecido_e_recusado():
    with pytest.raises(ValueError):
        responder(classificar("x", chat=_modelo("checagem")), "sms")


# ---- ferimento recente é urgência (fix-pergunta-e-conduta, D4) -----------------------

@pytest.mark.parametrize("texto", [
    "Cortei o pé com uma enxada, o que devo fazer?",
    "Me cortei feio com a faca da cozinha",
    "Meu neto se cortou no vidro da janela",
    "Pisei num prego enferrujado ontem",
    "Queimei a mão no óleo quente, passo pasta de dente?",
    "Minha mãe caiu e bateu a cabeça",
    "Acho que quebrei o braço",
    "Fui mordido por um cachorro na rua",
])
def test_ferimento_recente_e_risco_imediato_pelas_regras(texto):
    assert "risco_imediato" in por_regras(texto)


@pytest.mark.parametrize("texto", [
    "Recebi que corte de enxada se cura com borra de café, é verdade?",
    "Dizem que queimadura se trata com pasta de dente. Procede?",
    "Mandaram que mordida de cachorro não precisa de vacina, é verdade?",
])
def test_ferimento_citado_em_noticia_nao_e_risco_pelas_regras(texto):
    assert "risco_imediato" not in por_regras(texto)


def test_prompt_cita_ferimento_recente_no_risco_imediato():
    assert "ferimento recente" in SISTEMA
