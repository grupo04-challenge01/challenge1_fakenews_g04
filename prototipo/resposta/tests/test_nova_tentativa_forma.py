"""fix-qualidade-gerador-remoto, D5: defeito da resposta tem uma nova tentativa.

Antes, só a ancoragem pedia de novo; defeito de forma (teto de palavras, frase
longa, mito sem marca) saía para a pessoa. A tentativa é uma só no total.
"""
import json

from prototipo.resposta.estrutura import responder
from prototipo.resposta.tests.test_estrutura import ALEGACAO, BLOCOS_FALSO, FALSO, MENSAGEM

LONGA = ("Promete curar doença grave com algo caseiro que qualquer pessoa encontra no quintal "
         "de casa sem precisar de receita nem de consulta com médico algum.")
COM_DEFEITO = {**BLOCOS_FALSO, "bloco3": f"Técnica: cura milagrosa. {LONGA}"}
PIOR = {**COM_DEFEITO, "bloco4": f"Desconfie. {LONGA} {LONGA}"}
SEM_ANCORA = {**BLOCOS_FALSO, "bloco1": [{"frase": "Nenhum estudo mostra isso.", "trecho": "T9"}]}


def _em_sequencia(*saidas):
    pedidos = []
    fila = [json.dumps(s, ensure_ascii=False) for s in saidas]

    def chat(sistema, usuario):
        pedidos.append(usuario)
        return fila.pop(0)
    return chat, pedidos


def test_defeito_de_forma_pede_de_novo_com_o_defeito_informado():
    chat, pedidos = _em_sequencia(COM_DEFEITO, BLOCOS_FALSO)
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=chat)
    assert r.defeitos == []
    assert len(pedidos) == 2
    assert pedidos[1].startswith(pedidos[0])
    assert "frase com mais de 20 palavras" in pedidos[1]
    assert "--- refeita por defeito da resposta ---" in r.bruto


def test_sem_defeito_nao_pede_de_novo():
    chat, pedidos = _em_sequencia(BLOCOS_FALSO)
    assert responder(MENSAGEM, ALEGACAO, FALSO, chat=chat).defeitos == []
    assert len(pedidos) == 1


def test_segunda_saida_com_mais_defeitos_mantem_a_primeira():
    chat, pedidos = _em_sequencia(COM_DEFEITO, PIOR)
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=chat)
    assert len(pedidos) == 2
    assert LONGA in r.blocos[2] and LONGA not in r.blocos[3]
    assert "--- refeita por defeito da resposta ---" in r.bruto


def test_ancoragem_que_ja_pediu_de_novo_nao_pede_outra():
    # Primeira sem âncora no bloco 1; a refeita pela ancoragem vem com frase longa.
    chat, pedidos = _em_sequencia(SEM_ANCORA, COM_DEFEITO)
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=chat)
    assert len(pedidos) == 2
    assert any(d.startswith("frase com mais de 20 palavras") for d in r.defeitos)


def test_prompt_pede_80_palavras_nos_blocos():
    from prototipo.resposta.estrutura import SISTEMA
    assert "Os quatro blocos somam no máximo 80 palavras." in SISTEMA
    assert "90 palavras" not in SISTEMA


def test_aviso_de_tamanho_diz_quantas_palavras_cortar():
    curtas = " ".join(["Desconfie de promessa de cura simples."] * 12)
    chat, pedidos = _em_sequencia({**BLOCOS_FALSO, "bloco4": curtas}, BLOCOS_FALSO)
    responder(MENSAGEM, ALEGACAO, FALSO, chat=chat)
    total = int(pedidos[1].split("camada visível teve ")[1].split(" ")[0])
    assert total > 120
    assert f"Corte pelo menos {total - 120 + 10} palavras dos blocos." in pedidos[1]
