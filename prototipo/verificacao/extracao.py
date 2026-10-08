"""Extração da alegação verificável — task 2.1 de mvp-copiloto-verificacao.

Spec `verificacao-alegacao`, requirement Extração da alegação verificável. O modelo
lista as alegações e dá a cada uma um nível de risco; a seleção da alegação de
maior risco é feita em código, para que a regra de desempate seja fixa e testável.
Ver decisão 8 do design.md.
"""
from dataclasses import dataclass, field

from prototipo.verificacao.modelo import chat_ollama, ler_json

RISCOS = ("alto", "medio", "baixo")

SISTEMA = """Você lê mensagens que as pessoas recebem sobre saúde e separa as alegações que podem ser verificadas.

Alegação verificável é uma afirmação sobre o mundo que uma checagem pode confirmar
ou desmentir. Opinião, desabafo e pedido não são alegação. Pergunta que traz
uma afirmação ("Suco detox cura gripe?", "É verdade que a vacina causa
autismo?") tem como alegação a afirmação, escrita como frase ("Suco detox cura
gripe."). Pergunta sem afirmação ("O que devo fazer?") não é alegação.

Para cada alegação da mensagem, escreva:
- "texto": a alegação em uma frase curta, com as palavras da mensagem. Não corrija
  a alegação e NÃO diga se ela é verdadeira ou falsa.
- "saude": true se a alegação é sobre saúde, doença, remédio, vacina, alimento ou
  corpo; false se não é.
- "risco": o dano possível se a pessoa acreditar.
  "alto": leva a agir sobre o corpo — tomar, parar ou recusar remédio, vacina ou
    tratamento — ou a demorar para procurar atendimento.
  "medio": causa medo ou desconfiança sobre saúde, sem pedir uma ação.
  "baixo": o resto.

Cada alegação precisa ser entendida sozinha, sem ler a mensagem. Troque todo
pronome ("ela", "isso", "ele") pelo nome a que ele se refere.
Se a mensagem diz que uma pessoa, um órgão ou um estudo afirmou algo, a alegação
inclui quem afirmou: "o presidente da Anvisa disse que a vacina é um risco". NÃO
separe quem afirmou do que foi afirmado.

Se a mensagem tiver opinião, copie a opinião em "opiniao". Se não tiver, use null.
Se a mensagem não tiver nenhuma alegação, devolva a lista vazia.
Liste no máximo 8 alegações, as de saúde primeiro, na ordem em que aparecem
na mensagem.

Responda só com JSON, neste formato:
{"alegacoes": [{"texto": "...", "saude": true, "risco": "alto"}], "opiniao": null}"""


@dataclass
class Extracao:
    selecionada: dict | None
    demais: list = field(default_factory=list)
    opiniao: str | None = None

    @property
    def verificavel(self):
        return self.selecionada is not None


def mensagem(texto):
    return f"MENSAGEM RECEBIDA:\n\"\"\"{texto}\"\"\""


def defeitos(bruto):
    """Defeitos de forma da saída do modelo; lista vazia quando está em ordem."""
    dados = ler_json(bruto)
    if dados is None:
        return ["saída não é JSON"]
    alegacoes = dados.get("alegacoes")
    if not isinstance(alegacoes, list):
        return ["falta a lista `alegacoes`"]
    achados = []
    for n, a in enumerate(alegacoes, 1):
        if not isinstance(a, dict) or not str(a.get("texto") or "").strip():
            achados.append(f"alegação {n} sem texto")
            continue
        if not isinstance(a.get("saude"), bool):
            achados.append(f"alegação {n} sem `saude` booleano")
        if a.get("risco") not in RISCOS:
            achados.append(f"alegação {n} com risco fora de alto/medio/baixo")
    return achados


def selecionar(alegacoes):
    """Alegação de saúde de maior risco; empate fica com a primeira da mensagem."""
    de_saude = [a for a in alegacoes if a["saude"]]
    if not de_saude:
        return None
    return min(de_saude, key=lambda a: RISCOS.index(a["risco"]))


def interpretar(bruto):
    achados = defeitos(bruto)
    if achados:
        raise ValueError("; ".join(achados))
    dados = ler_json(bruto)
    alegacoes = dados["alegacoes"]
    escolhida = selecionar(alegacoes)
    demais = [a for a in alegacoes if a is not escolhida]
    return Extracao(selecionada=escolhida, demais=demais, opiniao=dados.get("opiniao"))


def _aviso(achados):
    return ("AVISO DA CONFERÊNCIA: a extração anterior foi recusada.\n"
            + "\n".join(f"- {a}" for a in achados)
            + "\nRefaça no mesmo formato JSON, com no máximo 8 alegações.")


def extrair(texto, chat=chat_ollama):
    """Uma nova tentativa com o defeito informado; JSON cortado é o caso comum
    (fix-qualidade-gerador-remoto, D6). A segunda saída com defeito levanta."""
    pedido = mensagem(texto)
    bruto = chat(SISTEMA, pedido)
    achados = defeitos(bruto)
    if not achados:
        return interpretar(bruto)
    return interpretar(chat(SISTEMA, f"{pedido}\n\n{_aviso(achados)}"))
