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
"""
from dataclasses import dataclass, field

from prototipo.rag.hibrida import LIMIAR_EVIDENCIA
from prototipo.verificacao import classificacao
from prototipo.verificacao.modelo import chat_ollama

INSUFICIENTE = "evidência insuficiente"


@dataclass
class Veredito:
    rotulo: str
    criterio: str
    trechos: list = field(default_factory=list)
    rebaixado_por: str | None = None
    original: dict | None = None
    referencias: list = field(default_factory=list)


REFERENCIA = ("agencia", "data_publicacao", "url", "veredito_original")


def _insuficiente(motivo):
    return Veredito(INSUFICIENTE, "Nenhum trecho recuperado cobre a alegação.", rebaixado_por=motivo)


def _verificar(alegacao, trechos, chat, limiar):
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
    return _classificar(alegacao, trechos, chat), referencias


def verificar(alegacao, trechos, chat=chat_ollama, limiar=LIMIAR_EVIDENCIA):
    v, referencias = _verificar(alegacao, trechos, chat, limiar)
    v.referencias = referencias
    return v


def _classificar(alegacao, trechos, chat):
    c = classificacao.classificar(alegacao, trechos, chat=chat)
    original = {"rotulo": c.rotulo, "trechos": c.trechos, "criterio": c.criterio}
    if c.rotulo == INSUFICIENTE:
        return Veredito(c.rotulo, c.criterio, original=original)

    recuperados = {f"T{n}": t for n, t in enumerate(trechos, 1)}
    inventados = [t for t in c.trechos if t not in recuperados]
    if not c.trechos:
        motivo = f"veredito {c.rotulo} sem trecho citado"
    elif inventados:
        motivo = f"veredito {c.rotulo} cita trecho não recuperado: {', '.join(inventados)}"
    else:
        return Veredito(c.rotulo, c.criterio, [recuperados[t] for t in c.trechos],
                        original=original)
    v = _insuficiente(motivo)
    v.original = original
    return v
