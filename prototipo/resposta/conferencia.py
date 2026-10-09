"""Conferência de sustentação — change fix-limitacoes-mvp, D1.

Requirement Conferência de sustentação, de `resposta-formativa`. A ancoragem
(`ancoragem.py`) confere termos verificáveis e declara o limite: paráfrase e
frase que inverte o trecho com as mesmas palavras passam. Esta conferência pede
ao modelo, numa chamada, as frases sem base: blocos 1 e 2 contra os trechos,
bloco 3 contra a mensagem. Frase apontada sai da resposta e fica em
`Resposta.sem_base`. Bloco 1 ou 2 sem frase do modelo rebaixa a resposta pelo
mesmo caminho da ancoragem. Falha da chamada deixa a resposta como estava.

O que o código escreveu não é conferido: a abertura do bloco 1 ("Falso."), a
frase sobre opinião e o rótulo da técnica ("Técnica: …").
"""
import logging
from dataclasses import replace

from prototipo.resposta import catalogo as catalogo_mod
from prototipo.resposta.estrutura import (
    ABERTURA, FRASE_OPINIAO, _defeitos_conteudo, _frases, rebaixar)
from prototipo.verificacao.modelo import ler_json

log = logging.getLogger(__name__)

SISTEMA = """Você confere uma resposta de checagem de saúde antes de ela chegar a uma pessoa idosa.

Você recebe TRECHOS de checagens publicadas (T1, T2…), a MENSAGEM que a pessoa
recebeu e FRASES numeradas da resposta (F1, F2…), cada uma com um tipo:
- (fato): só tem base se algum trecho diz isso, ou algo que implica isso
  diretamente. O que você sabe de medicina não conta. Frase que distorce,
  exagera ou inverte o que o trecho diz não tem base.
- (mensagem): descreve a mensagem recebida, o que ela diz ou como tenta
  convencer. Só tem base se a mensagem traz o que a frase descreve.

Na dúvida entre ter e não ter base, marque como sem base.

Responda só com JSON, neste formato:
{"sem_base": [{"n": 2, "motivo": "uma frase curta"}]}
Se todas as frases têm base, responda {"sem_base": []}."""

TIPO = {0: "fato", 1: "fato", 2: "mensagem"}


def _conferivel(indice, frase):
    if indice == 0 and frase in ABERTURA.values():
        return False
    return frase != FRASE_OPINIAO and not frase.startswith("Técnica:")


def _pedido(trechos, mensagem, frases):
    linhas = ["TRECHOS:"]
    for n, t in enumerate(trechos, 1):
        linhas.append(f"[T{n}] {t.get('agencia')}, {t.get('data_publicacao')}\n\"\"\"{t.get('trecho') or ''}\"\"\"")
    linhas += ["", f"MENSAGEM:\n\"\"\"{mensagem}\"\"\"", "", "FRASES:"]
    linhas += [f"[F{n}] ({TIPO[b]}) {f}" for n, (b, f) in enumerate(frases, 1)]
    return "\n".join(linhas)


def _apontadas(bruto, total):
    dados = ler_json(bruto)
    if dados is None or not isinstance(dados.get("sem_base"), list):
        raise ValueError("saída sem a lista `sem_base`")
    apontadas = {}
    for item in dados["sem_base"]:
        n = item.get("n") if isinstance(item, dict) else None
        if not isinstance(n, int) or not 1 <= n <= total:
            raise ValueError(f"frase fora da lista: {n!r}")
        apontadas[n] = str(item.get("motivo") or "").strip()
    return apontadas


def aplicar(r, mensagem, *, chat, refazer, alegacao=None, decomposicao=None, catalogo=None):
    """Resposta conferida. `refazer(veredito)` monta a resposta rebaixada."""
    if r.forma != "com evidência":
        return r
    frases = [(b, f) for b in (0, 1, 2) for f in _frases(r.blocos[b]) if _conferivel(b, f)]
    if not frases:
        r.conferencia = "ok"
        return r
    trechos = getattr(r, "trechos_vistos", None) or list(r.veredito.trechos)
    try:
        apontadas = _apontadas(chat(SISTEMA, _pedido(trechos, mensagem, frases)), len(frases))
    except Exception as e:  # conferência é barreira a mais: falhando, a resposta sai como estava
        log.warning("conferência não rodou: %s", type(e).__name__)
        r.conferencia = f"não rodou: {type(e).__name__}"
        return r

    registros = [{"bloco": frases[n - 1][0] + 1, "frase": frases[n - 1][1], "motivo": m}
                 for n, m in sorted(apontadas.items())]
    fora = {(frases[n - 1][0], frases[n - 1][1]) for n in apontadas}
    blocos = list(r.blocos)
    for b in (0, 1, 2):
        blocos[b] = " ".join(f for f in _frases(r.blocos[b]) if (b, f) not in fora)

    restam = lambda b: [f for f in _frases(blocos[b]) if _conferivel(b, f)]  # noqa: E731
    vazio = next((b for b in (0, 1) if not restam(b)), None)
    if vazio is not None:
        motivo = f"conferência: bloco {vazio + 1} sem frase com base"
        novo = refazer(rebaixar(r.veredito, motivo))
        novo.sem_base, novo.conferencia = registros, "ok"
        return novo

    defeitos_extras = []
    if not _frases(blocos[2]):  # o bloco 3 não fica vazio: a frase fica, com o defeito
        blocos[2] = r.blocos[2]
        defeitos_extras = [f"frase sem base: {x['frase']}" for x in registros if x["bloco"] == 3]
        registros = [x for x in registros if x["bloco"] != 3]

    novo = replace(r, blocos=blocos, sem_base=registros, conferencia="ok")
    if alegacao is not None:
        catalogo = catalogo or catalogo_mod.carregar_catalogo()
        antes = _defeitos_conteudo(r, alegacao, decomposicao, catalogo)
        fixos = [d for d in r.defeitos if d not in antes]
        novo.defeitos = fixos + _defeitos_conteudo(novo, alegacao, decomposicao, catalogo)
    novo.defeitos = list(novo.defeitos) + defeitos_extras
    return novo
