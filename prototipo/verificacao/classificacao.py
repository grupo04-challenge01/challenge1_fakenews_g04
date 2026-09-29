"""Classificação nos quatro rótulos — task 2.2 de mvp-copiloto-verificacao.

Spec `verificacao-alegacao`, requirement Classificação com incerteza explícita. O
modelo recebe a alegação e os trechos recuperados, numerados T1, T2..., e devolve
o rótulo, os trechos que o sustentam e o critério. Veredito sem critério é
defeito: o veredito é permitido, nunca nu.

Aqui só se confere a forma da saída. A regra de que veredito sem trecho não vale
fica na guarda (`guarda.py`, task 2.3), que não confia no prompt para isso.
Ver decisão 11 do design.md.
"""
import re
from dataclasses import dataclass

from prototipo.verificacao.modelo import chat_ollama, ler_json

ROTULOS = ("falso", "verdadeiro", "verdadeiro fora de contexto ou exagerado",
           "evidência insuficiente")

SISTEMA = """Você classifica uma alegação de saúde usando SOMENTE os trechos de checagem recuperados.

Escolha exatamente um rótulo, escrito igual:
"falso": algum trecho mostra que a alegação não é verdade.
"verdadeiro": algum trecho mostra que a alegação é verdade. Isso vale mesmo que
  a alegação pareça absurda: não rebaixe o rótulo porque a alegação soa estranha.
"verdadeiro fora de contexto ou exagerado": algum trecho mostra que a base da
  alegação existe, mas a alegação muda a data, corta o contexto ou afirma mais do
  que a base diz.
"evidência insuficiente": nenhum trecho fala desta alegação. Use este rótulo
  também quando o trecho for de assunto parecido, mas não da mesma alegação.

NUNCA use o que você sabe de medicina ou de notícias. Se você sabe a resposta,
mas nenhum trecho a dá, o rótulo é "evidência insuficiente".

O veredito da agência vale para a alegação que a agência checou. Confira se é a
mesma alegação antes de usá-lo.

Escreva:
- "rotulo": um dos quatro rótulos.
- "trechos": os identificadores dos trechos que sustentam o rótulo, como "T1".
  Para "evidência insuficiente", use a lista vazia.
- "criterio": em uma ou duas frases curtas, o que o trecho diz que decide o
  rótulo. Para "evidência insuficiente", diga o que não foi encontrado.

Responda só com JSON, neste formato:
{"rotulo": "falso", "trechos": ["T1"], "criterio": "..."}"""

ID_TRECHO = re.compile(r"T[1-9]\d*")


@dataclass
class Classificacao:
    rotulo: str
    trechos: list
    criterio: str


def mensagem(alegacao, trechos):
    partes = [f"ALEGAÇÃO:\n{alegacao}"]
    if not trechos:
        partes.append("TRECHOS RECUPERADOS: nenhum.")
    else:
        linhas = ["TRECHOS RECUPERADOS:"]
        for n, t in enumerate(trechos, 1):
            linhas.append(f"[T{n}] {t['agencia']}, {t['data_publicacao']} — veredito da agência: "
                          f"{t['veredito_original']}\n\"\"\"{t['trecho']}\"\"\"")
        partes.append("\n\n".join(linhas))
    return "\n\n".join(partes)


def _rotulo(dados):
    return str(dados.get("rotulo") or "").strip().lower()


def defeitos(bruto):
    """Defeitos de forma da saída do modelo; lista vazia quando está em ordem."""
    dados = ler_json(bruto)
    if dados is None:
        return ["saída não é JSON"]
    achados = []
    if _rotulo(dados) not in ROTULOS:
        achados.append(f"rótulo fora dos quatro: {dados.get('rotulo')}")
    if not str(dados.get("criterio") or "").strip():
        achados.append("veredito sem critério")
    trechos = dados.get("trechos")
    if not isinstance(trechos, list):
        achados.append("falta a lista `trechos`")
    elif not all(isinstance(t, str) and ID_TRECHO.fullmatch(t.strip()) for t in trechos):
        achados.append("trecho citado não é identificador T1, T2...")
    return achados


def interpretar(bruto):
    achados = defeitos(bruto)
    if achados:
        raise ValueError("; ".join(achados))
    dados = ler_json(bruto)
    return Classificacao(_rotulo(dados), [t.strip() for t in dados["trechos"]],
                         dados["criterio"].strip())


def classificar(alegacao, trechos, chat=chat_ollama):
    return interpretar(chat(SISTEMA, mensagem(alegacao, trechos)))
