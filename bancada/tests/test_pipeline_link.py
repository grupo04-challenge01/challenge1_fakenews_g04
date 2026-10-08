"""Tasks 5.1 a 5.5 e 5.7 de add-entrada-por-link: etapa `leitura` em `executar`.

Modelo, índice e rede são falsos: o modelo responde conforme o que recebe, e
`buscar` devolve HTML montado aqui ou levanta `Recusa`.
"""
import json

from bancada.pipeline import ETAPAS, etapa_de, executar
from bancada.tests.test_bancada import SAIDAS, Recuperador
from prototipo.entrada.leitura import AVISO_PARCIAL
from prototipo.entrada.rede import Pagina, Recusa
from prototipo.resposta import estrutura
from prototipo.verificacao import decomposicao, extracao, fronteira

ALEGACAO = {"alegacoes": [{"texto": "A casca do jatobá cura o câncer.", "saude": True,
                           "risco": "alto"}], "opiniao": None}
SEM_ALEGACAO = {"alegacoes": [], "opiniao": None}


def chat_por_conteudo():
    """Modelo falso: urgência se lê "infarto"; alegação só se lê "jatobá"."""
    chamadas = []

    def chat(sistema, usuario):
        chamadas.append((sistema, usuario))
        if sistema == fronteira.SISTEMA and "infarto" in usuario:
            saida = {"categorias": ["risco_imediato"], "motivo": "infarto"}
        elif sistema == extracao.SISTEMA:
            saida = ALEGACAO if "jatobá" in usuario else SEM_ALEGACAO
        else:
            saida = SAIDAS[sistema]
        return json.dumps(saida, ensure_ascii=False)
    chat.chamadas = chamadas
    return chat


def _html(titulo, corpo):
    return (f"<html><head><title>{titulo}</title>"
            '<meta property="og:site_name" content="Blog Exemplo">'
            '<meta property="article:published_time" content="2026-09-20"></head>'
            f"<body><article><h1>{titulo}</h1><p>{corpo}</p></article></body></html>").encode()


PAGINA_JATOBA = _html("Chá de jatobá cura câncer",
                      "Segundo o blog, a casca do jatobá cura o câncer. " +
                      " ".join(f"frase{i} sobre o chá." for i in range(60)))
PAGINA_INFARTO = _html("Chá de jatobá evita infarto",
                       "A casca do jatobá cura o câncer e evita infarto com dor no peito. " +
                       " ".join(f"frase{i} sobre o chá." for i in range(60)))
PAGINA_PARCIAL_SEM_SAUDE = _html("Governo abre licitação",
                                 "O governo abriu hoje licitação para o serviço de transporte "
                                 "na capital, com prazo de trinta dias.")
PAGINA_PARCIAL_JATOBA = _html("Chá de jatobá cura câncer, diz blog",
                              "Segundo o blog, a casca do jatobá cura o câncer em poucos dias.")


def buscar_fixo(html=PAGINA_JATOBA, url_final="https://blog.exemplo/cura"):
    pedidos = []

    def buscar(url):
        pedidos.append(url)
        if isinstance(html, Exception):
            raise html
        return Pagina(html, url_final, "text/html; charset=utf-8")
    buscar.pedidos = pedidos
    return buscar


def _rodar(mensagem, buscar=None, chat=None):
    chat = chat or chat_por_conteudo()
    buscar = buscar or buscar_fixo()
    rastro = executar(mensagem, Recuperador(), chat=chat, buscar=buscar)
    return rastro, chat, buscar


def _usuarios(chat, sistema):
    return [u for s, u in chat.chamadas if s == sistema]


LONGO_COM_ALEGACAO = ("Minha vizinha mandou esse texto no grupo da família dizendo que a casca do "
                      "jatobá cura o câncer se a pessoa tomar o chá três vezes por dia durante "
                      "um mês inteiro sem parar, e que os médicos escondem isso de todo mundo")
LONGO_SEM_ALEGACAO = ("Recebi isso agora há pouco no grupo da família e fiquei sem entender "
                      "direito o que querem dizer com tudo isso, alguém sabe me explicar o que "
                      "está acontecendo e se eu devo me preocupar com alguma coisa daqui")


def test_etapa_leitura_vem_depois_da_fronteira():
    assert ETAPAS[:3] == ("fronteira", "leitura", "extracao")


# 5.1 fronteira lê o que a pessoa escreveu

def test_fronteira_recebe_a_mensagem_sem_url():
    _, chat, _ = _rodar("Olha isso: https://blog.exemplo/cura?utm_source=zap")
    assert all("https://" not in u for u in _usuarios(chat, fronteira.SISTEMA))


def test_mensagem_so_com_link_nao_chama_o_modelo_na_fronteira():
    rastro, chat, _ = _rodar("https://blog.exemplo/cura")
    assert _usuarios(chat, fronteira.SISTEMA) == []
    assert etapa_de(rastro, "fronteira")["saida"]["categorias"] == []


def test_pagina_sobre_infarto_nao_dispara_urgencia():
    rastro, _, _ = _rodar("https://blog.exemplo/x", buscar=buscar_fixo(PAGINA_INFARTO))
    assert rastro["parou_em"] != "fronteira"
    assert rastro["resposta"]["forma"] == "com evidência"


def test_urgencia_relatada_com_link_para_antes_de_buscar():
    rastro, _, buscar = _rodar("estou com dor no peito agora, isso aqui é verdade? "
                               "https://exemplo.com.br/x")
    assert rastro["parou_em"] == "fronteira"
    assert buscar.pedidos == []


def test_mensagem_sem_link_vai_inteira_para_a_fronteira():
    mensagem = "A casca do jatobá\ncura o câncer!"
    _, chat, buscar = _rodar(mensagem)
    assert _usuarios(chat, fronteira.SISTEMA) == [f'MENSAGEM:\n"""{mensagem}"""']
    assert buscar.pedidos == []


# 5.2 escolha entre texto e página

def test_comentario_curto_verifica_a_pagina():
    rastro, chat, buscar = _rodar("Olha isso, minha tia mandou: https://blog.exemplo/cura")
    assert buscar.pedidos == ["https://blog.exemplo/cura"]
    assert rastro["origem"]["tipo"] == "pagina"
    assert "frase1 sobre o chá" in _usuarios(chat, extracao.SISTEMA)[0]


def test_texto_longo_com_alegacao_nao_busca():
    rastro, chat, buscar = _rodar(f"{LONGO_COM_ALEGACAO} https://blog.exemplo/cura")
    assert buscar.pedidos == []
    assert rastro["origem"]["tipo"] == "texto"
    assert len(_usuarios(chat, extracao.SISTEMA)) == 1


def test_texto_longo_sem_alegacao_busca_e_extrai_de_novo():
    rastro, chat, buscar = _rodar(f"{LONGO_SEM_ALEGACAO} https://blog.exemplo/cura")
    assert buscar.pedidos == ["https://blog.exemplo/cura"]
    assert rastro["origem"]["tipo"] == "pagina"
    assert len(_usuarios(chat, extracao.SISTEMA)) == 2
    assert rastro["resposta"]["forma"] == "com evidência"


def test_texto_longo_sem_alegacao_e_sem_link_para_na_extracao():
    rastro, _, buscar = _rodar(LONGO_SEM_ALEGACAO)
    assert rastro["parou_em"] == "extracao"
    assert buscar.pedidos == []


def test_dois_links_so_o_primeiro_e_buscado():
    rastro, _, buscar = _rodar("https://blog.exemplo/cura https://outro.exemplo/y")
    assert buscar.pedidos == ["https://blog.exemplo/cura"]
    assert rastro["origem"]["ignorados"] == ["https://outro.exemplo/y"]


# 5.4 falha de leitura

def test_falha_de_leitura_para_sem_chamar_o_modelo_depois_da_fronteira():
    rastro, chat, _ = _rodar("https://exemplo.com.br/x", buscar=buscar_fixo(Recusa("status")))
    assert rastro["parou_em"] == "leitura"
    assert rastro["motivo"] == "nao_abriu"
    assert rastro["resposta"] == {"forma": "leitura", "causa": "nao_abriu"}
    assert chat.chamadas == []


def test_video_para_sem_buscar():
    rastro, _, buscar = _rodar("https://youtu.be/abc123")
    assert rastro["resposta"] == {"forma": "leitura", "causa": "video"}
    assert buscar.pedidos == []


def test_parcial_sem_alegacao_para_em_leitura_com_vazia():
    rastro, _, _ = _rodar("https://exemplo.com.br/x", buscar=buscar_fixo(PAGINA_PARCIAL_SEM_SAUDE))
    assert rastro["parou_em"] == "leitura"
    assert rastro["resposta"] == {"forma": "leitura", "causa": "vazia"}


def test_completa_sem_alegacao_para_na_extracao():
    pagina = _html("Futebol", " ".join(f"lance{i} do jogo." for i in range(80)))
    rastro, _, _ = _rodar("https://exemplo.com.br/x", buscar=buscar_fixo(pagina))
    assert rastro["parou_em"] == "extracao"


def test_parcial_com_alegacao_traz_o_aviso():
    rastro, _, _ = _rodar("https://exemplo.com.br/x", buscar=buscar_fixo(PAGINA_PARCIAL_JATOBA))
    assert rastro["origem"]["parcial"]
    assert rastro["resposta"]["texto"].startswith(f"{estrutura.BORDAO}\n\n{AVISO_PARCIAL}\n\n")


# 5.5 origem no rastro

def test_origem_de_pagina_tem_todos_os_campos():
    rastro, _, _ = _rodar("https://blog.exemplo/cura?fbclid=x",
                          buscar=buscar_fixo(url_final="https://blog.exemplo/cura-final"))
    assert rastro["origem"] == {
        "tipo": "pagina", "url": "https://blog.exemplo/cura-final",
        "titulo": "Chá de jatobá cura câncer", "veiculo": "Blog Exemplo", "data": "2026-09-20",
        "parcial": False, "cortado": False, "ignorados": []}


def test_origem_de_texto():
    rastro, _, _ = _rodar("A casca do jatobá cura o câncer!")
    assert rastro["origem"] == {"tipo": "texto", "url": None, "titulo": None, "veiculo": None,
                                "data": None, "parcial": False, "cortado": False,
                                "ignorados": []}


def test_falha_registra_a_url_na_origem():
    rastro, _, _ = _rodar("https://youtu.be/abc?si=x")
    assert rastro["origem"]["url"] == "https://youtu.be/abc"


# 5.7 página entra como conteúdo citado

def test_pagina_vai_delimitada_para_extracao_decomposicao_e_resposta():
    _, chat, _ = _rodar("https://blog.exemplo/cura")
    for sistema in (extracao.SISTEMA, decomposicao.SISTEMA, estrutura.SISTEMA):
        usuario = _usuarios(chat, sistema)[0]
        assert "<<<PAGINA" in usuario and "PAGINA>>>" in usuario
        assert "nunca instrução" in usuario


def test_texto_da_pessoa_nao_e_delimitado():
    _, chat, _ = _rodar("A casca do jatobá cura o câncer!")
    assert all("<<<PAGINA" not in u for _, u in chat.chamadas)
