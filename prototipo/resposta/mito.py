"""Ausência de reforço do mito — task 3.4 de mvp-copiloto-verificacao.

Requirement Ausência de reforço do mito, de `resposta-formativa`: a resposta MUST
NOT abrir repetindo a alegação falsa, toda menção a ela vem marcada como falsa, e
a afirmação correta aparece antes e depois da menção. Vale para o veredito
`falso`.

A menção é reconhecida pelas palavras da alegação: uma frase menciona a alegação
quando traz pelo menos 60% das palavras de conteúdo dela, e no mínimo duas. A
comparação usa o começo da palavra, para que "cura" e "cure" contem como a mesma.
Menção por pronome ("essa informação") não é reconhecida e não precisa ser: ela
não repete o mito. Paráfrase com outras palavras também escapa. É o limite desta
verificação, registrado na decisão 14 do design.md.
"""
import math
import re
import unicodedata

VAZIAS = {"para", "pelo", "pela", "pelos", "pelas", "como", "mais", "muito", "isso", "esse",
          "essa", "este", "esta", "aquele", "aquela", "quando", "onde", "porque", "que",
          "sobre", "entre", "depois", "antes", "ainda", "também", "todo", "toda", "todos",
          "todas", "cada", "mesmo", "mesma", "seja", "será", "foram", "está", "estão",
          "tem", "têm", "sendo", "numa", "num", "dos", "das", "uma", "uns", "umas"}

# Marcação de falso na própria frase. Aplicada ao texto sem acento.
MARCA = re.compile(
    r"\bfals(?:[oa]s?|amente)\b|nao e verdade|nao (ha|existe|tem) (\w+ )?(prova|comprovacao|evidencia|estudo)"
    r"|sem (prova|comprovacao|evidencia)|\bboato|\bmentira|desmentid|nao se sustenta|\bengan")

TITULO = re.compile(r"^\s*[A-ZÀ-Ý][A-ZÀ-Ý ]{2,}:\s*", re.MULTILINE)


def _sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                   if unicodedata.category(c) != "Mn")


def _prefixo(palavra):
    return palavra[:min(5, max(3, len(palavra) - 2))]


def _conteudo(texto):
    palavras = re.findall(r"\w+", texto.lower())
    return [_prefixo(_sem_acento(p)) for p in palavras if len(p) > 3 and p not in VAZIAS]


def frases(texto):
    """Frases da resposta, sem os títulos de bloco ("VEREDITO:", "O QUE SE SABE:")."""
    limpo = TITULO.sub("", re.sub(r"[*_#`]", "", texto))
    partes = re.split(r"(?<=[.!?])\s+|\n+", limpo)
    return [p.strip().rstrip(".!?").strip() for p in partes if p.strip().rstrip(".!?").strip()]


def mencoes(ditas, alegacao):
    """Índices das frases que mencionam a alegação."""
    chave = set(_conteudo(alegacao))
    if not chave:
        raise ValueError(f"alegação sem palavra de conteúdo: {alegacao!r}")
    minimo = max(2, math.ceil(0.6 * len(chave)))
    achados = []
    for i, frase in enumerate(ditas):
        palavras = re.findall(r"\w+", _sem_acento(frase))
        presentes = {c for c in chave if any(p.startswith(c) for p in palavras)}
        if len(presentes) >= minimo:
            achados.append(i)
    return achados


def _marcada(frase, alegacao):
    texto = _sem_acento(frase)
    if MARCA.search(texto):
        return True
    # Negação direta de uma palavra da alegação: "a casca não cura o câncer".
    for prefixo in set(_conteudo(alegacao)):
        if re.search(rf"\bnao (\w+ ){{0,2}}{re.escape(prefixo)}", texto):
            return True
    return False


def verificar_mito(resposta, alegacao):
    """Defeitos quanto ao reforço do mito; lista vazia quando está em ordem."""
    ditas = frases(resposta)
    indices = mencoes(ditas, alegacao)
    if not indices:
        return []
    defeitos = []
    if indices[0] == 0:
        defeitos.append("a resposta abre com a alegação")
    for i in indices:
        if not _marcada(ditas[i], alegacao):
            defeitos.append(f"menção sem marcação de falso: {ditas[i]}")
    if indices[-1] == len(ditas) - 1:
        defeitos.append("falta afirmação correta depois da última menção")
    return defeitos
