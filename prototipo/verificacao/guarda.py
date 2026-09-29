"""Guarda contra veredito por conhecimento paramétrico — task 2.3 de mvp-copiloto-verificacao.

Spec `verificacao-alegacao`: o sistema MUST usar `evidência insuficiente` quando a
recuperação não retornar fonte que cubra a alegação, e MUST NOT emitir veredito
só pelo conhecimento do modelo. O prompt da classificação já pede isso, mas a
guarda não depende dele. Ela vale em três pontos, todos em código:

1. Sem trecho, o modelo não é chamado. Não há como ele responder de memória.
2. Com `limiar`, trecho de score abaixo dele conta como não recuperado. O valor
   do limiar é a task 1.5; até lá o parâmetro fica sem valor padrão.
3. Veredito que não cita trecho recuperado, ou que cita trecho que não existe,
   cai para `evidência insuficiente`, e o que o modelo disse fica registrado.

O que a guarda não pega: veredito que cita um trecho real que não cobre a
alegação. Isso depende do prompt e é o que a sonda mede. Ver decisão 11 do
design.md.
"""
from dataclasses import dataclass, field

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


def _insuficiente(motivo):
    return Veredito(INSUFICIENTE, "Nenhum trecho recuperado cobre a alegação.", rebaixado_por=motivo)


def verificar(alegacao, trechos, chat=chat_ollama, limiar=None):
    if limiar is not None:
        trechos = [t for t in trechos if t["score"] >= limiar]
        if not trechos:
            return _insuficiente(f"nenhum trecho acima do limiar {limiar}")
    if not trechos:
        return _insuficiente("nenhum trecho recuperado")

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
