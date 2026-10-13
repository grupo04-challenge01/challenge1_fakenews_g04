"""Guarda contra veredito por conhecimento paramétrico — task 2.3 de mvp-copiloto-verificacao.

Spec `verificacao-alegacao`: o sistema MUST usar `evidência insuficiente` quando a
recuperação não retornar fonte que cubra a alegação, e MUST NOT emitir veredito
só pelo conhecimento do modelo. O prompt da classificação já pede isso, mas a
guarda não depende dele. Ela vale em três pontos, todos em código:

1. Sem trecho, o modelo não é chamado. Não há como ele responder de memória.
2. Trecho de score abaixo de `limiar` conta como não recuperado. O padrão é
   `LIMIAR_EVIDENCIA`, calibrado na task 1.5 (decisão 27); `limiar=None`
   desliga o corte.
3. Veredito que não cita trecho recuperado, ou que cita trecho que não existe,
   cai para `evidência insuficiente`, e o que o modelo disse fica registrado.

O que a guarda não pega: veredito que cita um trecho real que não cobre a
alegação. Isso depende do prompt e é o que a sonda mede. Ver decisão 12 do
design.md.

Task 1.6: só trecho com `apto_citacao` verdadeiro chega ao modelo e pode ser
âncora. O inapto (o FACTCK.BR, decisão 17) é só metadado — agência, data, link
e veredito da agência — e sai em `Veredito.referencias`, sem o texto. Marca
ausente conta como inapta: o índice que não diz se o trecho é citável não
autoriza citá-lo. Sem trecho apto, o modelo não é chamado, como no ponto 1.

add-cobertura-alegacao-ampla (D2 a D4): veredito que a classificação declara de
cobertura `ampla` (a checagem é de alegação mais geral, da qual a da pessoa é
caso particular) só sobrevive a seis travas, nesta ordem: ligada, rótulo
`falso`, veredito da agência `falso`/`boato`/`fake` em todo trecho citado, duas
agências distintas, sujeito presente na alegação e em cada checagem citada, e
implicação confirmada por chamada cega (`implicacao.py`). A primeira que falha
rebaixa para `evidência insuficiente` e vai para `rebaixado_por`.
"""
import re
from dataclasses import dataclass, field

from prototipo.rag.hibrida import LIMIAR_EVIDENCIA
from prototipo.resposta.ancoragem import normalizar
from prototipo.verificacao import classificacao, implicacao
from prototipo.verificacao.modelo import chat_ollama

INSUFICIENTE = "evidência insuficiente"

# add-cobertura-alegacao-ampla, D2: vereditos de agência que sustentam cobertura
# ampla. São as chaves que `tratamento/mapa_vereditos.json` leva a `falso`; o
# teste confere que batem.
VEREDITOS_AMPLA = ("falso", "boato", "fake")


@dataclass
class Veredito:
    rotulo: str
    criterio: str
    trechos: list = field(default_factory=list)
    rebaixado_por: str | None = None
    original: dict | None = None
    referencias: list = field(default_factory=list)
    # add-cobertura-alegacao-ampla, D2: `mesma` ou `ampla` quando há veredito;
    # None em `evidência insuficiente`.
    cobertura: str | None = None
    ponte: str = ""
    sujeito: str = ""
    # Resposta da verificação de implicação (D4); None quando não foi pedida.
    implicacao: str | None = None


REFERENCIA = ("agencia", "data_publicacao", "url", "veredito_original")


def _insuficiente(motivo):
    return Veredito(INSUFICIENTE, "Nenhum trecho recuperado cobre a alegação.", rebaixado_por=motivo)


def _verificar(alegacao, trechos, chat, limiar, ampla):
    if not trechos:
        return _insuficiente("nenhum trecho recuperado"), []
    if limiar is not None:
        trechos = [t for t in trechos if t["score"] >= limiar]
        if not trechos:
            return _insuficiente(f"nenhum trecho acima do limiar {limiar}"), []

    referencias = [{k: t[k] for k in REFERENCIA}
                   for t in trechos if t.get("apto_citacao") is not True]
    trechos = [t for t in trechos if t.get("apto_citacao") is True]
    if not trechos:
        return _insuficiente("nenhum trecho apto a citação"), referencias
    return _classificar(alegacao, trechos, chat, ampla), referencias


def verificar(alegacao, trechos, chat=chat_ollama, limiar=LIMIAR_EVIDENCIA, ampla=True):
    """`ampla=False` desliga a cobertura por alegação mais ampla (D5)."""
    v, referencias = _verificar(alegacao, trechos, chat, limiar, ampla)
    v.referencias = referencias
    return v


# D3: palavras que não identificam o sujeito.
VAZIAS = frozenset("a o as os de da do das dos e em no na nos nas para por pelo pela "
                   "com contra um uma uns umas que".split())


def _palavras(texto):
    """Palavras normalizadas, sem o `s` final, para que "vacinas" case com "vacina"."""
    return {p[:-1] if len(p) > 3 and p.endswith("s") else p
            for p in re.findall(r"\w+", normalizar(texto))}


def sujeito_ausente(sujeito, alegacao, citados):
    """Trava 5 (D3): motivo de falha da âncora do sujeito, ou None.

    Cada palavra do sujeito, fora as vazias, precisa estar na alegação da
    pessoa e no texto de cada checagem citada (título e trecho).
    """
    palavras = _palavras(sujeito) - VAZIAS
    if not palavras:
        return f"sujeito {sujeito} vazio"
    if not palavras <= _palavras(alegacao):
        return f"sujeito {sujeito} ausente da alegação"
    for t in citados:
        if not palavras <= _palavras(f"{t.get('alegacao', '')} {t.get('trecho', '')}"):
            return f"sujeito {sujeito} ausente de {t['agencia']}"
    return None


def _trava_ampla(c, citados, ampla, alegacao):
    """Primeira trava de código da cobertura ampla que falha, ou None (D2)."""
    if not ampla:
        return "cobertura ampla desligada"
    if c.rotulo != "falso":
        return "cobertura ampla só vale para falso"
    for t in citados:
        if t.get("veredito_chave") not in VEREDITOS_AMPLA:
            return f"cobertura ampla com veredito da agência {t.get('veredito_chave')}"
    if len({t["agencia"] for t in citados}) < 2:
        return "cobertura ampla com uma agência só"
    return sujeito_ausente(c.sujeito, alegacao, citados)


def _classificar(alegacao, trechos, chat, ampla=True):
    c = classificacao.classificar(alegacao, trechos, chat=chat)
    original = {"rotulo": c.rotulo, "trechos": c.trechos, "criterio": c.criterio,
                "cobertura": c.cobertura, "ponte": c.ponte, "sujeito": c.sujeito}
    if c.rotulo == INSUFICIENTE:
        return Veredito(c.rotulo, c.criterio, original=original)

    recuperados = {f"T{n}": t for n, t in enumerate(trechos, 1)}
    inventados = [t for t in c.trechos if t not in recuperados]
    resposta = None
    if not c.trechos:
        motivo = f"veredito {c.rotulo} sem trecho citado"
    elif inventados:
        motivo = f"veredito {c.rotulo} cita trecho não recuperado: {', '.join(inventados)}"
    else:
        citados = [recuperados[t] for t in c.trechos]
        motivo = _trava_ampla(c, citados, ampla, alegacao) if c.cobertura == "ampla" else None
        if c.cobertura == "ampla" and motivo is None:
            # Trava 6, a única que custa chamada, por último (D2). G é a
            # alegação checada pelo trecho citado de maior score.
            geral = max(citados, key=lambda t: t["score"])["alegacao"]
            confirmada, resposta = implicacao.confirmar(alegacao, geral, chat)
            if not confirmada:
                motivo = f"implicação não confirmada: {resposta}"
        if motivo is None:
            return Veredito(c.rotulo, c.criterio, citados, original=original,
                            cobertura=c.cobertura, ponte=c.ponte, sujeito=c.sujeito,
                            implicacao=resposta)
    v = _insuficiente(motivo)
    v.original = original
    v.implicacao = resposta
    return v
