import json

import pytest

from bancada import gravacao
from bancada.__main__ import carregar_casos, rodar_caso
from bancada.avaliacao import avaliar
from bancada.pipeline import etapa_de, executar
from prototipo.resposta import estrutura
from prototipo.verificacao import classificacao, decomposicao, extracao, fronteira

TRECHO = {"unidade_id": "u1-00", "fragmento_id": "u1-00-00", "score": 0.9,
          "agencia": "Aos Fatos", "data_publicacao": "2021-01-08", "url": "https://x",
          "alegacao": "jatobá cura câncer", "veredito_original": "falso",
          "trecho": "Não é verdade que a casca do jatobá trate o câncer.",
          "apto_citacao": True}

SAIDAS = {
    fronteira.SISTEMA: {"categorias": ["checagem"], "motivo": "pede checagem"},
    extracao.SISTEMA: {"alegacoes": [{"texto": "A casca do jatobá cura o câncer.",
                                      "saude": True, "risco": "alto"}], "opiniao": None},
    decomposicao.SISTEMA: {"fatos": ["A casca do jatobá cura o câncer."], "evidencias": [],
                           "opinioes": [], "conclusao": None},
    classificacao.SISTEMA: {"rotulo": "falso", "trechos": ["T1"],
                            "criterio": "T1 diz que a casca não trata câncer."},
    # Blocos 1 e 2 como lista de frase e trecho (task 1.6, decisão 26).
    estrutura.SISTEMA: {"bloco1": [{"frase": "A casca do jatobá não cura câncer.", "trecho": "T1"}],
                        "bloco2": [{"frase": "Não é verdade que a casca do jatobá trate o câncer.",
                                    "trecho": "T1"}],
                        "bloco3": "Técnica: cura milagrosa. Promete cura simples.",
                        "bloco4": "Desconfie de cura fácil."},
}


def chat_fixo(saidas=SAIDAS):
    chamadas = []

    def chat(sistema, usuario):
        chamadas.append(sistema)
        return json.dumps(saidas[sistema], ensure_ascii=False)
    chat.chamadas = chamadas
    return chat


class Recuperador:
    def __init__(self, trechos=(TRECHO,)):
        self.trechos, self.alfa, self.consultas = list(trechos), 0.9, []

    def buscar(self, consulta, k=10, modo="hibrida"):
        self.consultas.append((consulta, k, modo))
        return self.trechos[:k]

    def expandir(self, consulta, trechos, modo="hibrida"):
        self.consultas.append(("expandir", consulta, modo))
        return list(trechos)

    def recuperar(self, consulta, k=10, modo="hibrida"):
        from prototipo.rag.hibrida import Recuperacao
        self.consultas.append((consulta, k, modo))
        return Recuperacao("pt-BR", self.trechos[:k], bool(self.trechos), ("pt-BR",))


def test_fluxo_completo_registra_todas_as_etapas():
    rastro = executar("A casca do jatobá cura o câncer!", Recuperador(), chat=chat_fixo())
    assert [e["etapa"] for e in rastro["etapas"]] == [
        "fronteira", "extracao", "decomposicao", "recuperacao", "guarda", "resposta"]
    assert rastro["parou_em"] is None
    assert etapa_de(rastro, "guarda")["saida"]["rotulo"] == "falso"
    assert rastro["resposta"]["forma"] == "com evidência"
    assert rastro["resposta"]["texto"].startswith(f"{estrutura.BORDAO}\n\nVEREDITO: Falso.")
    assert rastro["resposta"]["defeitos"] == []


def test_recuperacao_usa_a_alegacao_selecionada_e_os_parametros():
    rec = Recuperador()
    executar("msg", rec, chat=chat_fixo(), k=3, modo="lexica", alfa=0.5)
    # Os vizinhos da decisão 29 usam a mesma alegação e o mesmo modo.
    assert rec.consultas == [("A casca do jatobá cura o câncer.", 3, "lexica"),
                             ("expandir", "A casca do jatobá cura o câncer.", "lexica")]
    assert rec.alfa == 0.5


def test_prioridade_de_idioma_vai_para_o_rastro():
    rastro = executar("msg", Recuperador(), chat=chat_fixo())
    s = etapa_de(rastro, "recuperacao")["saida"]
    assert (s["idioma"], s["coberto"], s["consultados"]) == ("pt-BR", True, ["pt-BR"])
    cru = etapa_de(executar("msg", Recuperador(), chat=chat_fixo(), idioma=False), "recuperacao")
    assert cru["saida"]["idioma"] is None and cru["saida"]["resultados"]


def test_bypass_encerra_sem_chamar_o_modelo():
    chat = chat_fixo()
    rastro = executar("Minha mãe está com dor no peito e falta de ar agora", Recuperador(), chat=chat)
    assert rastro["parou_em"] == "fronteira" and rastro["motivo"] == "bypass"
    assert rastro["resposta"]["forma"] == "fronteira" and rastro["resposta"]["texto"]
    assert chat.chamadas == []


def test_conduta_redireciona_e_segue_a_checagem():
    saidas = {**SAIDAS, fronteira.SISTEMA: {"categorias": ["conduta_individual"], "motivo": "x"}}
    rastro = executar("Posso trocar o remédio por jatobá?", Recuperador(), chat=chat_fixo(saidas))
    assert rastro["redirecionamentos"]
    assert rastro["parou_em"] is None


def test_sem_alegacao_verificavel_para_na_extracao():
    saidas = {**SAIDAS, extracao.SISTEMA: {"alegacoes": [], "opiniao": "que vergonha"}}
    rec = Recuperador()
    rastro = executar("Que vergonha.", rec, chat=chat_fixo(saidas))
    assert rastro["parou_em"] == "extracao"
    assert rec.consultas == []


def test_limiar_derruba_para_insuficiente():
    rastro = executar("msg", Recuperador(), chat=chat_fixo(), limiar=0.95)
    g = etapa_de(rastro, "guarda")["saida"]
    assert g["rotulo"] == "evidência insuficiente"
    assert "limiar" in g["rebaixado_por"]
    assert rastro["resposta"]["forma"] == "sem evidência"


def test_erro_de_etapa_fica_no_rastro_e_para():
    saidas = {**SAIDAS, decomposicao.SISTEMA: {"nada": 1}}
    rastro = executar("msg", Recuperador(), chat=chat_fixo(saidas))
    assert rastro["parou_em"] == "decomposicao" and rastro["motivo"] == "erro"
    assert "ValueError" in etapa_de(rastro, "decomposicao")["erro"]
    checks = avaliar({"esperado": {}}, rastro)
    assert any(c["check"] == "sem erro" and not c["ok"] for c in checks)


def test_avaliacao_compara_cada_etapa():
    rastro = executar("msg", Recuperador(), chat=chat_fixo())
    caso = {"esperado": {"fronteira": "checagem", "verificavel": True,
                         "alegacao_contem": ["jatoba"], "unidade_no_topo": "u1-00",
                         "rotulo": ["falso"], "forma": "com evidência"}}
    falhas = [c for c in avaliar(caso, rastro) if not c["ok"]]
    assert falhas == []
    errado = avaliar({"esperado": {"rotulo": "verdadeiro", "unidade_no_topo": "zz"}}, rastro)
    assert [c["ok"] for c in errado if c["check"] != "sem defeitos"] == [False, False]


def test_gravacao_reproduz_o_mesmo_rastro():
    dados = gravacao.vazio()
    chat, rec = gravacao.gravando(dados, chat_fixo(), Recuperador())
    real = executar("msg", rec, chat=chat)
    chat2, rec2 = gravacao.reproduzindo(json.loads(json.dumps(dados)), alfa=0.9)
    copia = executar("msg", rec2, chat=chat2)
    sem_tempo = lambda r: [{k: v for k, v in e.items() if k != "segundos"} for e in r["etapas"]]
    assert sem_tempo(copia) == sem_tempo(real)


def test_reproducao_sem_gravacao_vira_erro_no_rastro():
    chat, rec = gravacao.reproduzindo(gravacao.vazio(), alfa=0.9)
    rastro = executar("msg", rec, chat=chat)
    assert rastro["parou_em"] == "fronteira" and rastro["motivo"] == "erro"
    assert "GravacaoAusente" in rastro["etapas"][-1]["erro"]


def test_casos_tem_id_unico_e_chaves_conhecidas():
    casos = carregar_casos()
    ids = [c["id"] for c in casos]
    assert len(ids) == len(set(ids))
    conhecidas = {"fronteira", "verificavel", "alegacao_contem", "unidade_no_topo", "rotulo", "forma"}
    for c in casos:
        assert c["mensagem"] and set(c["esperado"]) <= conhecidas, c["id"]


@pytest.mark.parametrize("caso", carregar_casos(), ids=lambda c: c["id"])
def test_caso_roda_com_modelo_fixo(caso):
    r = rodar_caso(caso, chat_fixo(), Recuperador())
    assert r["rastro"]["etapas"]


# ---- aviso por etapa (decisão 4 de add-interface-chat-web) ---------------------------

def test_ao_etapa_avisa_cada_etapa_na_ordem_com_o_registro_do_rastro():
    avisos = []
    rastro = executar("A casca do jatobá cura o câncer!", Recuperador(), chat=chat_fixo(),
                      ao_etapa=avisos.append)
    assert [a["etapa"] for a in avisos] == [
        "fronteira", "extracao", "decomposicao", "recuperacao", "guarda", "resposta"]
    assert avisos == rastro["etapas"]


def test_ao_etapa_avisa_tambem_a_etapa_que_errou():
    def quebra(sistema, usuario):
        raise ConnectionError("ollama fora do ar")
    avisos = []
    rastro = executar("msg", Recuperador(), chat=quebra, ao_etapa=avisos.append)
    assert rastro["motivo"] == "erro"
    assert avisos == rastro["etapas"]
    assert "erro" in avisos[-1]
