"""Verificação de implicação — add-cobertura-alegacao-ampla, D4.

Requirement Cobertura por alegação mais ampla, de `verificacao-alegacao`,
condição 1: a implicação "se P fosse verdade, G seria necessariamente verdade"
é confirmada por uma chamada independente da classificação. O pedido é cego:
o modelo vê só as duas frases, sem a ponte, o critério ou o rótulo que a
classificação deu, para não ser levado a concordar com ela.

Só "sim" confirma. "não", "incerto", saída fora do formato e erro do gerador
não confirmam, e a guarda volta ao comportamento anterior. Uma tentativa só.
"""
from prototipo.verificacao.modelo import chat_ollama, ler_json

SISTEMA = """Você confere uma relação lógica entre duas frases.

Pergunta: se a FRASE A fosse verdade, a FRASE B seria necessariamente verdade?

Responda "sim" só quando A não pode ser verdade sem que B também seja.
Responda "não" quando A pode ser verdade com B falsa, ou quando as frases
falam de coisas diferentes. Responda "incerto" se não der para decidir.
Não julgue se as frases são verdadeiras: só a relação entre elas.

Responda só com JSON, neste formato:
{"resposta": "sim"}"""

RESPOSTAS = ("sim", "não", "incerto")


def confirmar(p, g, chat=chat_ollama):
    """(confirmada, resposta registrada) para a implicação de `p` em `g`."""
    try:
        bruto = chat(SISTEMA, f"FRASE A:\n{p}\n\nFRASE B:\n{g}")
    except Exception as e:  # erro do gerador não confirma (D4)
        return False, f"erro: {type(e).__name__}"
    dados = ler_json(bruto)
    resposta = str((dados or {}).get("resposta") or "").strip().lower()
    if resposta not in RESPOSTAS:
        return False, "saída inválida"
    return resposta == "sim", resposta
