import json

import pytest

from bancada import gravacao
from bancada.__main__ import carregar_casos, rodar_caso
from bancada.avaliacao import avaliar
from bancada.pipeline import etapa_de, executar
from prototipo.resposta import conferencia, estrutura
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
    # fix-limitacoes-mvp, D1: a conferência de sustentação, sem frase apontada.
    conferencia.SISTEMA: {"sem_base": []},
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
        "fronteira", "leitura", "extracao", "decomposicao", "recuperacao", "guarda", "resposta"]
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
    # A decomposição deixou de parar o fluxo (fix-pergunta-e-conduta, D7); a guarda para.
    saidas = {**SAIDAS, classificacao.SISTEMA: {"nada": 1}}
    rastro = executar("msg", Recuperador(), chat=chat_fixo(saidas))
    assert rastro["parou_em"] == "guarda" and rastro["motivo"] == "erro"
    assert "ValueError" in etapa_de(rastro, "guarda")["erro"]
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
    conhecidas = {"fronteira", "verificavel", "alegacao_contem", "unidade_no_topo", "rotulo", "forma",
                  "leitura"}
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
        "fronteira", "leitura", "extracao", "decomposicao", "recuperacao", "guarda", "resposta"]
    assert avisos == rastro["etapas"]


def test_ao_etapa_avisa_tambem_a_etapa_que_errou():
    def quebra(sistema, usuario):
        raise ConnectionError("ollama fora do ar")
    avisos = []
    rastro = executar("msg", Recuperador(), chat=quebra, ao_etapa=avisos.append)
    assert rastro["motivo"] == "erro"
    assert avisos == rastro["etapas"]
    assert "erro" in avisos[-1]


# ---- gerador da bancada (add-gerador-api-deepseek, task 4.1) -------------------------

def test_gerador_ollama_e_o_padrao_e_registra_o_modelo_local():
    from bancada.__main__ import descrever_gerador, escolher_gerador
    from prototipo.verificacao.modelo import MODELO, chat_ollama
    chat = escolher_gerador("ollama")
    assert chat is chat_ollama
    assert descrever_gerador("ollama", chat) == {"gerador": "ollama", "modelo": MODELO}


def test_gerador_deepseek_registra_o_modelo_devolvido_pela_api(monkeypatch):
    from bancada.__main__ import descrever_gerador, escolher_gerador
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-teste")
    chat = escolher_gerador("deepseek")
    chat.modelo_servido = "deepseek-v4.1-flash"
    chat.uso = {"chamadas": 90, "entrada": 120000, "entrada_cache": 80000, "saida": 12000}
    assert descrever_gerador("deepseek", chat) == {
        "gerador": "deepseek", "modelo": "deepseek-v4.1-flash",
        "uso": {"chamadas": 90, "entrada": 120000, "entrada_cache": 80000, "saida": 12000}}


def test_offline_registra_gerador_gravado(tmp_path, monkeypatch):
    import argparse
    import json

    from bancada import __main__ as bancada_main
    monkeypatch.setattr(bancada_main, "RELATORIOS", tmp_path)
    args = argparse.Namespace(offline=True, caso=["S1_goiabeira"], canal="web", k=5,
                              modo="hibrida", alfa=None, limiar=bancada_main.LIMIAR_EVIDENCIA,
                              sem_idioma=False, gerador="deepseek")
    bancada_main.rodar(args)
    (relatorio,) = tmp_path.glob("*.json")
    parametros = json.loads(relatorio.read_text(encoding="utf-8"))["parametros"]
    assert (parametros["gerador"], parametros["modelo"]) == ("gravacao", None)


def test_gerador_que_falha_no_teste_inicial_para_a_rodada_sem_regravar(tmp_path, monkeypatch):
    """Chave recusada não pode sobrescrever as gravações caso a caso (08/10/2026)."""
    import argparse

    from bancada import __main__ as bancada_main
    from prototipo.verificacao.modelo import ErroGerador

    def recusar(sistema, usuario):
        raise ErroGerador("DeepSeek respondeu 401")

    gravadas = []
    monkeypatch.setattr(bancada_main, "RELATORIOS", tmp_path)
    monkeypatch.setattr(bancada_main, "escolher_gerador", lambda nome: recusar)
    monkeypatch.setattr("prototipo.rag.__main__.carregar", lambda: object())
    monkeypatch.setattr(gravacao, "gravar", lambda *a: gravadas.append(a))
    args = argparse.Namespace(offline=False, caso=None, canal="web", k=5, modo="hibrida",
                              alfa=None, limiar=bancada_main.LIMIAR_EVIDENCIA,
                              sem_idioma=False, gerador="deepseek")
    assert bancada_main.rodar(args) == 2
    assert gravadas == [] and list(tmp_path.iterdir()) == []


# ---- critério por tipo de falha (add-gerador-api-deepseek, D10 revisto) --------------

def _falha(id_, *checks):
    return {"id": id_, "passou": False,
            "checks": [{"etapa": e, "check": c, "esperado": None, "obtido": o, "ok": False}
                       for e, c, o in checks]}


def test_tipos_de_falha_e_criterio():
    from bancada.__main__ import resumir
    resultados = [
        {"id": "ok", "passou": True, "checks": []},
        _falha("T1", ("resposta", "sem defeitos", ["camada visível com 121 palavras, teto 120"])),
        _falha("T2", ("resposta", "sem defeitos", ["frase com mais de 20 palavras: x"])),
        _falha("A1", ("resposta", "forma", "sem evidência")),
    ]
    r = resumir(resultados)
    assert r["por_tipo"] == {"tamanho": ["T1", "T2"], "acerto": ["A1"]}
    assert r["criterio"] == {"eliminatorias": [], "demais": ["A1", "T1", "T2"], "cumpre": True}


def test_mito_rotulo_erro_e_fronteira_sao_eliminatorios():
    from bancada.__main__ import resumir
    resultados = [
        _falha("M", ("resposta", "sem defeitos",
                     ["mito: menção sem marcação de falso: y", "camada visível com 130 palavras, teto 120"])),
        _falha("R", ("guarda", "rótulo", "falso")),
        _falha("E", ("extracao", "sem erro", "ValueError: saída não é JSON")),
        _falha("F", ("fronteira", "primeira categoria", "checagem")),
        _falha("V", ("resposta", "sem defeitos", ["técnica nomeada sem evidência: cura milagrosa"])),
    ]
    r = resumir(resultados)
    assert r["criterio"]["eliminatorias"] == ["E", "F", "M", "R", "V"]
    assert r["criterio"]["cumpre"] is False
    assert r["por_tipo"]["mito"] == ["M"] and r["por_tipo"]["tamanho"] == ["M"]


def test_quatro_falhas_nao_eliminatorias_nao_cumprem():
    from bancada.__main__ import resumir
    resultados = [_falha(f"T{n}", ("resposta", "sem defeitos", ["camada visível com 121 palavras, teto 120"]))
                  for n in range(4)]
    assert resumir(resultados)["criterio"]["cumpre"] is False


def test_resumo_conta_casos_com_corte():
    # fix-teto-resposta, task 2.1.
    from bancada.__main__ import resumir

    def caso(id_, cortadas):
        return {"id": id_, "passou": True, "checks": [], "rastro": {"etapas": [
            {"etapa": "resposta", "saida": {"cortadas": cortadas}}]}}
    r = resumir([caso("A", ["Dica."]), caso("B", []), {"id": "C", "passou": True, "checks": []}])
    assert r["cortes"] == ["A"]


# ---- decomposição que falha não derruba a resposta (fix-pergunta-e-conduta, D7) -------

def test_decomposicao_que_falha_duas_vezes_segue_sem_ela():
    base = chat_fixo()

    def chat(sistema, usuario):
        if sistema == decomposicao.SISTEMA:
            return '{"fatos": ["cortado no meio'
        return base(sistema, usuario)
    rastro = executar("A casca do jatobá cura o câncer!", Recuperador(), chat=chat)
    assert rastro["motivo"] != "erro"
    assert rastro["resposta"]["forma"] == "com evidência"
    registro = etapa_de(rastro, "decomposicao")
    assert "erro" not in registro
    assert registro["saida"] == {"omitida": "saída não é JSON"}


# ---- conferência de sustentação no pipeline (fix-limitacoes-mvp, D1) -----------------

def test_conferencia_roda_na_resposta_e_tira_a_frase_apontada():
    base = chat_fixo()

    def chat(sistema, usuario):
        if sistema == conferencia.SISTEMA:
            n = next(int(l.split("]")[0][2:]) for l in usuario.splitlines()
                     if "Técnica" not in l and "(mensagem)" in l)
            return json.dumps({"sem_base": [{"n": n, "motivo": "a mensagem não diz isso"}]})
        return base(sistema, usuario)
    rastro = executar("A casca do jatobá cura o câncer!", Recuperador(), chat=chat)
    saida = etapa_de(rastro, "resposta")["saida"]
    assert saida["conferencia"] == "ok"
    assert saida["sem_base"] and saida["sem_base"][0]["bloco"] == 3
    assert saida["sem_base"][0]["frase"] not in rastro["resposta"]["texto"]


def test_resumo_conta_casos_com_frase_tirada_pela_conferencia():
    from bancada.__main__ import resumir

    def caso(id_, sem_base):
        return {"id": id_, "passou": True, "checks": [], "rastro": {"etapas": [
            {"etapa": "resposta", "saida": {"cortadas": [], "sem_base": sem_base}}]}}
    r = resumir([caso("A", [{"bloco": 2, "frase": "x", "motivo": "y"}]), caso("B", [])])
    assert r["sem_base"] == ["A"]
