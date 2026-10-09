"""fix-teto-resposta: teto de 120 palavras garantido em código.

Requirement Legibilidade da camada visível, de `acessibilidade-leitura`, na
redação deste change: passando do teto, saem frases do fim dos blocos 3 e 4,
com pelo menos uma em cada; blocos 1 e 2 nunca; corte que cria defeito de mito
é desfeito.
"""
import json

from prototipo.resposta.estrutura import TETO_PALAVRAS, responder
from prototipo.resposta.tests.test_estrutura import ALEGACAO, BLOCOS_FALSO, FALSO, MENSAGEM

DICA = "Pergunte sempre quem fez o estudo citado."  # 7 palavras


def _em_sequencia(*saidas):
    pedidos = []
    fila = [json.dumps(s, ensure_ascii=False) for s in saidas]

    def chat(sistema, usuario):
        pedidos.append(usuario)
        return fila.pop(0)
    return chat, pedidos


def _sempre(saida):
    def chat(sistema, usuario):
        return json.dumps(saida, ensure_ascii=False)
    return chat


def _palavras(r):
    return len(r.texto.split())


def test_resposta_acima_do_teto_perde_frases_do_fim_dos_blocos_3_e_4():
    longa = {**BLOCOS_FALSO, "bloco4": " ".join([DICA] * 12)}
    sem_corte = responder(MENSAGEM, ALEGACAO, FALSO, chat=_sempre(BLOCOS_FALSO))
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_sempre(longa))
    assert _palavras(r) <= TETO_PALAVRAS
    assert r.blocos[:2] == sem_corte.blocos[:2]
    assert r.cortadas and all(f == DICA for f in r.cortadas)
    assert not any(d.startswith("camada visível") for d in r.defeitos)


def test_corte_alterna_pelo_bloco_com_mais_frases_e_deixa_uma_em_cada():
    longa = {**BLOCOS_FALSO, "bloco3": "Técnica: cura milagrosa. " + " ".join([DICA] * 8),
             "bloco4": " ".join([DICA] * 8)}
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_sempre(longa))
    assert _palavras(r) <= TETO_PALAVRAS
    assert r.blocos[2].count(DICA) >= 1 and r.blocos[3].count(DICA) >= 1
    assert abs(r.blocos[2].count(DICA) - r.blocos[3].count(DICA)) <= 1


def test_sem_frase_para_tirar_o_defeito_de_tamanho_fica():
    gigante = " ".join(["palavra"] * 130) + "."
    # Bloco 2 com uma frase só: depois de fix-limitacoes-mvp (D3) ele também é cortável.
    longa = {**BLOCOS_FALSO, "bloco2": BLOCOS_FALSO["bloco2"][:1],
             "bloco3": "Técnica: cura milagrosa.", "bloco4": gigante}
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_sempre(longa))
    assert r.cortadas == []
    assert any(d.startswith("camada visível") for d in r.defeitos)


def test_corte_que_tiraria_a_afirmacao_correta_e_desfeito():
    # A menção marcada fica no fim do bloco 4; só a frase depois dela afirma o correto.
    mencao = "Não é verdade que a casca do jatobá cura o câncer."
    correta = "O Inca diz que nenhum alimento cura câncer."
    base = responder(MENSAGEM, ALEGACAO, FALSO, chat=_sempre(BLOCOS_FALSO))
    fixo = _palavras(base) - len(base.blocos[3].split())
    # Fillers até passar do teto por menos que o tamanho da frase correta: um corte basta.
    k = next(k for k in range(30)
             if 0 < fixo + 7 * k + 19 - TETO_PALAVRAS < len(correta.split()))
    longa = {**BLOCOS_FALSO, "bloco4": " ".join([DICA] * k + [mencao, correta])}
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_sempre(longa))
    assert r.cortadas == []
    assert r.blocos[3].endswith(correta)
    assert any(d.startswith("camada visível") for d in r.defeitos)
    assert not any(d.startswith("mito:") for d in r.defeitos)


def test_corte_roda_depois_da_nova_tentativa():
    longa = {**BLOCOS_FALSO, "bloco4": " ".join([DICA] * 12)}
    chat, pedidos = _em_sequencia(longa, longa)
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=chat)
    assert len(pedidos) == 2
    assert _palavras(r) <= TETO_PALAVRAS and r.cortadas


# ---- corte no bloco 2 (fix-limitacoes-mvp, D3) ---------------------------------------

def test_blocos_3_e_4_curtos_cortam_o_fim_do_bloco_2_e_nunca_o_bloco_1():
    frase = {"frase": "As checagens não acharam estudo sobre o jatobá e o câncer.", "trecho": "T1"}
    longa = {**BLOCOS_FALSO, "bloco2": [frase] * 9, "bloco3": "Técnica: cura milagrosa.",
             "bloco4": "Desconfie de promessa de cura simples."}
    sem_corte_b1 = responder(MENSAGEM, ALEGACAO, FALSO, chat=_sempre(BLOCOS_FALSO)).blocos[0]
    r = responder(MENSAGEM, ALEGACAO, FALSO, chat=_sempre(longa))
    assert _palavras(r) <= TETO_PALAVRAS
    assert r.blocos[0] == sem_corte_b1
    assert r.blocos[1].count("As checagens") >= 1
    assert r.cortadas and all("As checagens" in f for f in r.cortadas)
