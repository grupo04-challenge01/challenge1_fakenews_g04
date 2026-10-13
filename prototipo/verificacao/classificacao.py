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
"evidência insuficiente": nenhum trecho fala desta alegação, nem de uma
  alegação mais geral da qual ela seja caso particular. Use este rótulo também
  quando o trecho for de assunto parecido sem essa relação. Exemplo: um trecho
  que desmente que a casca do jatobá cura o câncer não serve para a alegação
  "chá de folha de goiabeira cura a dengue".

Diga também a cobertura do trecho que sustenta o rótulo:
"mesma": o trecho checa esta alegação, mesmo com outras palavras.
"ampla": nenhum trecho checa esta alegação, mas algum trecho mostra que é falsa
  uma alegação mais geral, da qual esta é caso particular:
  se esta alegação fosse verdade, a mais geral também seria. Exemplo: "a vacina transforma
  pessoas em jacaré" é caso particular de "a vacina altera o DNA de quem a
  toma". Cobertura "ampla" só vale para o rótulo "falso".

NUNCA use o que você sabe de medicina ou de notícias. Se você sabe a resposta,
mas nenhum trecho a dá, o rótulo é "evidência insuficiente".

O veredito da agência vale para a alegação que a agência checou. Confira se é a
mesma alegação antes de usá-lo. Se for a mesma alegação e o veredito da agência
for falso, boato, enganoso ou fora de contexto, o rótulo NÃO pode ser "verdadeiro".
Se a alegação diz que algo acontece agora ("acabou de", "hoje") e o trecho mostra
que aconteceu antes, o rótulo é "verdadeiro fora de contexto ou exagerado".

Escreva:
- "rotulo": um dos quatro rótulos.
- "trechos": os identificadores dos trechos que sustentam o rótulo, como "T1".
  Para "evidência insuficiente", use a lista vazia.
- "criterio": em uma ou duas frases curtas, o que o trecho diz que decide o
  rótulo. Para "evidência insuficiente", diga o que não foi encontrado.
- "cobertura": "mesma" ou "ampla".
- "ponte": com cobertura "ampla", uma frase dizendo por que esta alegação é caso
  particular da alegação checada. Com "mesma", deixe vazio.
- "sujeito": com cobertura "ampla", o produto, a substância ou a intervenção de
  que esta alegação fala, com as palavras dela. Com "mesma", deixe vazio.

Responda só com JSON, neste formato:
{"rotulo": "falso", "trechos": ["T1"], "criterio": "...", "cobertura": "mesma", "ponte": "", "sujeito": ""}"""

ID_TRECHO = re.compile(r"T[1-9]\d*")

# add-cobertura-alegacao-ampla, D1: a classificação declara se o trecho checa a
# mesma alegação ou uma mais geral. Ausente conta como `mesma`, o comportamento
# anterior; quem decide se a cobertura ampla vale é a guarda.
COBERTURAS = ("mesma", "ampla")
INSUFICIENTE = "evidência insuficiente"


@dataclass
class Classificacao:
    rotulo: str
    trechos: list
    criterio: str
    cobertura: str = "mesma"
    ponte: str = ""
    sujeito: str = ""


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


def _texto(dados, campo):
    return str(dados.get(campo) or "").strip()


def _cobertura(dados):
    return _texto(dados, "cobertura").lower() or "mesma"


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
    if _rotulo(dados) != INSUFICIENTE:
        cobertura = _cobertura(dados)
        if cobertura not in COBERTURAS:
            achados.append(f"cobertura fora de mesma e ampla: {dados.get('cobertura')}")
        elif cobertura == "ampla":
            for campo in ("ponte", "sujeito"):
                if not _texto(dados, campo):
                    achados.append(f"cobertura ampla sem {campo}")
    return achados


def interpretar(bruto):
    achados = defeitos(bruto)
    if achados:
        raise ValueError("; ".join(achados))
    dados = ler_json(bruto)
    rotulo = _rotulo(dados)
    if rotulo == INSUFICIENTE:
        return Classificacao(rotulo, [t.strip() for t in dados["trechos"]],
                             dados["criterio"].strip())
    cobertura = _cobertura(dados)
    ampla = cobertura == "ampla"
    return Classificacao(rotulo, [t.strip() for t in dados["trechos"]],
                         dados["criterio"].strip(), cobertura,
                         _texto(dados, "ponte") if ampla else "",
                         _texto(dados, "sujeito") if ampla else "")


def classificar(alegacao, trechos, chat=chat_ollama):
    return interpretar(chat(SISTEMA, mensagem(alegacao, trechos)))
