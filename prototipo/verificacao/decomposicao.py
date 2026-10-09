"""Decomposição fato / evidência / opinião — task 2.5 de mvp-copiloto-verificacao.

Spec `verificacao-alegacao`, requirement Separação entre tipo de afirmação e valor
de verdade. A decomposição alimenta o bloco 2 da resposta e é independente do
veredito: ela diz que tipo de afirmação cada parte é, nunca se é verdadeira.
Veredito dentro dela é defeito. Ver decisão 9 do design.md.
"""
import re
from dataclasses import dataclass

from prototipo.verificacao.modelo import chat_ollama, ler_json

FORCAS = ("forte", "fraca", "ausente")

SISTEMA = """Você lê mensagens que as pessoas recebem sobre saúde e separa as partes da mensagem.

Separe em:
- "fatos": afirmações que uma checagem pode confirmar ou desmentir. Uma frase
  curta cada, com as palavras da mensagem.
- "evidencias": o que a própria mensagem apresenta para sustentar os fatos
  (estudo, especialista, documento, vídeo, experiência pessoal). Para cada uma,
  "texto" e "forca":
  "forte": estudo ou documento identificado, que dá para localizar.
  "fraca": alguém sem nome, relato pessoal, vídeo, "dizem que".
  "ausente": a mensagem afirma sem apresentar nada.
  A força diz se dá para localizar a evidência, não se ela sustenta a
  conclusão. Isso é o "salto", abaixo.
- "opinioes": juízos, gostos e sentimentos que nenhuma checagem resolve. Frase
  com "eu acho", "na minha opinião" ou "para mim" é opinião.
- "conclusao": se a mensagem tira uma conclusão a partir dos fatos, escreva
  "texto" (a conclusão), "decorre" (true se a conclusão sai dos fatos
  apresentados, false se ela vai além deles) e "salto" (quando "decorre" é false,
  explique em uma frase o que falta entre o fato e a conclusão; senão, null).
  Se a mensagem não tira conclusão, use null.

Cada frase da mensagem vai para um lugar só: o que é opinião não entra em fatos.
Liste no máximo 6 fatos, 4 evidências e 4 opiniões, as que mais importam para o
que a mensagem quer convencer.
Pergunta ou exclamação de quem mandou a mensagem ("Isso é verdade?",
"Absurdo!") não é fato, opinião nem conclusão: deixe de fora.
O salto explica o que falta entre fato e conclusão.
Não diga se algo é verdadeiro ou falso nele.

NÃO diga se os fatos são verdadeiros ou falsos. NÃO use as palavras "falso",
"verdadeiro", "mentira" ou "boato" para julgar. Opinião não é indício de que a
mensagem é falsa, e evidência fraca não quer dizer que o fato é falso.

Responda só com JSON, neste formato:
{"fatos": ["..."], "evidencias": [{"texto": "...", "forca": "fraca"}],
 "opinioes": ["..."], "conclusao": {"texto": "...", "decorre": false, "salto": "..."}}"""

# Julgamento de verdade, não a palavra solta: "o verdadeiro remédio" não é veredito.
VEREDITO = re.compile(
    r"\b(é|são|seria|parece)\s+(fals[oa]s?|verdadeir[oa]s?)\b|\bmentira\b|\bboato\b|\bfake\b",
    re.IGNORECASE)


@dataclass
class Decomposicao:
    fatos: list
    evidencias: list
    opinioes: list
    conclusao: dict | None
    refeita_por: str | None = None


def mensagem(texto):
    return f"MENSAGEM RECEBIDA:\n\"\"\"{texto}\"\"\""


def _normal(t):
    return re.sub(r"[^\w\s]", "", t).lower().split()


def _repetidas(fatos, opinioes):
    """Fatos cujo texto está contido numa opinião, como na sonda de 29/09, D1."""
    for f in fatos:
        pf = " ".join(_normal(f))
        if pf and any(pf in " ".join(_normal(o)) for o in opinioes):
            yield f


def _textos(dados):
    """(onde, texto) de todo campo livre, para procurar veredito."""
    for campo in ("fatos", "opinioes"):
        for t in dados.get(campo) or []:
            yield campo, t
    for e in dados.get("evidencias") or []:
        yield "evidencias", e.get("texto") if isinstance(e, dict) else e
    c = dados.get("conclusao")
    if isinstance(c, dict):
        yield "salto", c.get("salto")


def _conclusao(dados):
    """Conclusão da saída; o objeto com todos os campos vazios conta como ausente.

    Sem conclusão na mensagem, o modelo às vezes devolve `{"texto": null,
    "decorre": null, "salto": null}` em vez de `null` (bancada de 06/10,
    decisão 24). Conclusão parcial continua defeito.
    """
    c = dados.get("conclusao")
    if isinstance(c, dict) and not any(v not in (None, "") for v in c.values()):
        return None
    return c


def defeitos(bruto):
    """Defeitos de forma e vazamento de veredito; lista vazia quando está em ordem."""
    dados = ler_json(bruto)
    if dados is None:
        return ["saída não é JSON"]
    achados = [f"falta `{c}`" for c in ("fatos", "evidencias", "opinioes")
               if not isinstance(dados.get(c), list)]
    if achados:
        return achados
    for campo in ("fatos", "opinioes"):
        for n, t in enumerate(dados[campo], 1):
            if not isinstance(t, str) or not t.strip():
                achados.append(f"{campo}: item {n} vazio")
    for n, e in enumerate(dados["evidencias"], 1):
        if not isinstance(e, dict) or not str(e.get("texto") or "").strip():
            achados.append(f"evidência {n} sem texto")
        elif e.get("forca") not in FORCAS:
            achados.append(f"evidência {n} com força fora de forte/fraca/ausente")
    c = _conclusao(dados)
    if c is not None:
        if not isinstance(c, dict) or not str(c.get("texto") or "").strip():
            achados.append("conclusão sem texto")
        elif not isinstance(c.get("decorre"), bool):
            achados.append("conclusão sem `decorre` booleano")
        elif c["decorre"] is False and not str(c.get("salto") or "").strip():
            achados.append("conclusão que não decorre sem o salto explicado")
    textos_ok = lambda c: [t for t in dados[c] if isinstance(t, str) and t.strip()]
    for f in _repetidas(textos_ok("fatos"), textos_ok("opinioes")):
        achados.append(f"opinião repetida como fato: {f}")
    for onde, t in _textos(dados):
        if isinstance(t, str) and VEREDITO.search(t):
            achados.append(f"veredito dentro da decomposição ({onde}): {t}")
    return achados


def interpretar(bruto):
    achados = defeitos(bruto)
    if achados:
        raise ValueError("; ".join(achados))
    d = ler_json(bruto)
    return Decomposicao(d["fatos"], d["evidencias"], d["opinioes"], _conclusao(d))


def _aviso(achados):
    return ("AVISO DA CONFERÊNCIA: a decomposição anterior foi recusada.\n"
            + "\n".join(f"- {a}" for a in achados)
            + "\nRefaça seguindo as regras, no mesmo formato JSON.")


def decompor(texto, chat=chat_ollama):
    """Uma nova tentativa com os defeitos informados, como em `estrutura.responder`
    (fix-qualidade-gerador-remoto, D2). A segunda saída com defeito levanta."""
    pedido = mensagem(texto)
    bruto = chat(SISTEMA, pedido)
    achados = defeitos(bruto)
    if not achados:
        return interpretar(bruto)
    d = interpretar(chat(SISTEMA, f"{pedido}\n\n{_aviso(achados)}"))
    d.refeita_por = "; ".join(achados)
    return d
