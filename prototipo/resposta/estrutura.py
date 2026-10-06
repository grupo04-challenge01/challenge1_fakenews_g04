"""Estrutura de quatro blocos — task 3.2 de mvp-copiloto-verificacao.

Requirement Estrutura de quatro blocos, de `resposta-formativa`, na redação do
`fix-resposta-sem-evidencia`: forma com evidência quando há trecho recuperado,
forma sem evidência quando não há, e nunca uma no lugar da outra. Um prompt só
para as duas formas; a forma vem do estado da recuperação, que chega na
mensagem (risco 1 daquele design).

Divisão do trabalho:

- **Código:** a forma, a ordem e os títulos dos blocos, a abertura do bloco 1
  com o veredito da guarda, a data de corte e o ponteiro da lacuna de acervo, e
  a camada de detalhe com os trechos. O que a spec exige literalmente não
  depende de o prompt pegar (decisão 4 de fix-resposta-sem-evidencia).
- **Modelo:** o texto de cada bloco, em JSON.
- **Verificação:** os contratos da 3.3 (`catalogo.py`) e da 3.4 (`mito.py`), a
  inversão do catálogo na forma sem evidência e os tetos de
  `acessibilidade-leitura`. Defeito não derruba a resposta; fica em
  `Resposta.defeitos` para quem chama decidir. Ver decisão 18 do design.md.

Task 1.6, ancoragem trecho a afirmação (`recuperacao-evidencia`, Rastreabilidade
da evidência). Na forma com evidência, os blocos 1 e 2 chegam como lista de
`{"frase", "trecho"}`, cada frase com o trecho que a sustenta, e `ancoragem.py`
confere. Frase que não passa
sai da resposta e fica em `Resposta.descartadas`. Ao contrário dos defeitos, o
descarte age: se a frase do bloco 1 cai, ou se o bloco 2 fica sem frase
ancorada, o veredito cai para `evidência insuficiente` e a resposta é refeita na
forma sem evidência, com uma segunda chamada ao modelo. Os blocos 3 e 4 falam da
técnica e do que observar, não de fato sobre o mundo, e não passam pela
ancoragem.
"""
import json
import re
from dataclasses import dataclass, field

from prototipo.resposta import catalogo as catalogo_mod
from prototipo.resposta.ancoragem import ancorar_bloco, texto_do_bloco
from prototipo.resposta.mito import verificar_mito
from prototipo.verificacao.guarda import INSUFICIENTE, Veredito
from prototipo.verificacao.modelo import chat_ollama, ler_json

COM = ["VEREDITO:", "O QUE SE SABE:", "POR QUE ESSA MENSAGEM ENGANA:",
       "O QUE OBSERVAR DA PRÓXIMA VEZ:"]
# Cenário Alegação verdadeira: o bloco 3 explica por que era difícil de avaliar.
# "Por que engana" em cima de mensagem verdadeira desdiria o veredito.
TITULO_3_VERDADEIRO = "POR QUE PARECIA DIFÍCIL DE ACREDITAR:"
SEM = ["VEREDITO E O QUE FOI PROCURADO:", "POR QUE ISSO NÃO QUER DIZER QUE É FALSO:",
       "O QUE VOCÊ PODE CONFERIR:", "ONDE PROCURAR:"]

ABERTURA = {
    "falso": "Falso.",
    "verdadeiro": "Verdadeiro.",
    "verdadeiro fora de contexto ou exagerado": "Verdadeiro, mas fora de contexto ou exagerado.",
    INSUFICIENTE: "Evidência insuficiente.",
}
LACUNA = "lacuna de acervo"

TETO_PALAVRAS = 120  # acessibilidade-leitura, camada visível
TETO_FRASE = 20

CATALOGO = json.loads(catalogo_mod.ARQUIVO.read_text(encoding="utf-8"))["tecnicas"]
_LISTA = "\n".join(f'  - "{t["rotulo"]}": {t["sinal"]}' for t in CATALOGO)

SISTEMA = f"""Você explica a uma pessoa comum o resultado da checagem de uma mensagem de saúde.

O VEREDITO já foi decidido e vem na mensagem. NÃO mude o veredito.
Afirme SOMENTE o que os TRECHOS sustentam. NUNCA use o que você sabe de medicina.
NUNCA dê orientação clínica individual.
Frases curtas, de no máximo 15 palavras. Palavras do dia a dia. A resposta inteira
cabe em 90 palavras.

Na forma com evidência, os blocos 1 e 2 são LISTAS de frases. Cada frase vem
com o trecho que a sustenta: {{"frase": "Nenhum estudo mostra isso.", "trecho": "T1"}}.
Frase sem trecho que a sustente é apagada. Dentro de "frase", só o texto. Nos
blocos 3 e 4, e na forma sem evidência, NÃO escreva "T1", "T2": os trechos
aparecem em outra tela.

A mensagem traz o ESTADO DA RECUPERAÇÃO. Ele decide o que vai em cada bloco.

Se o estado for `com evidência`:
- "bloco1": uma frase que diz, sem termo técnico, o que a checagem encontrou.
  NÃO repita o veredito: ele já abre o bloco. NÃO conte o que a mensagem diz;
  diga o que a checagem encontrou.
- "bloco2": o que se sabe sobre o assunto, pelos trechos. Se a mensagem tiver
  OPINIÃO, diga, numa frase com "trecho": "", que aquela parte é opinião e não
  se checa.
- "bloco3": comece com "Técnica: " e o rótulo, escrito igual a um desta lista:
{_LISTA}
  Se a mensagem tiver mais de um sinal, escreva até dois rótulos separados por
  vírgula, o mais forte primeiro. Promessa de curar doença grave é sempre
  "cura milagrosa". Depois, diga em uma ou duas frases qual sinal aparece nesta
  mensagem.
  Se o veredito for "verdadeiro", NÃO escreva "Técnica:" e NÃO use rótulo: a
  mensagem não engana. Explique por que ela parecia difícil de acreditar.
- "bloco4": o que a pessoa pode observar da próxima vez. Se o veredito for
  "verdadeiro", diga o que sustentou a confirmação.
Se o veredito for "falso" e você precisar citar a alegação, escreva junto que
ela é falsa. NÃO comece nenhum bloco repetindo a alegação.

Se o estado for `evidência insuficiente` ou `lacuna de acervo`:
- "bloco1": uma frase sobre o que foi procurado.
- "bloco2": diga que não encontrar não é o mesmo que desmentir.
- "bloco3": um ou dois passos que a pessoa pode dar sozinha. NÃO diga que a
  mensagem engana. NÃO use nenhum rótulo de técnica.
- "bloco4": em `evidência insuficiente`, onde a pessoa pode procurar. Em
  `lacuna de acervo`, deixe "" vazio: o sistema escreve essa parte.

Responda só com JSON, no formato do estado.
Estado `com evidência` (se o veredito for "verdadeiro", o bloco3 NÃO começa com "Técnica:"):
{{"bloco1": [{{"frase": "...", "trecho": "T1"}}],
 "bloco2": [{{"frase": "...", "trecho": "T1"}}, {{"frase": "...", "trecho": "T1"}}],
 "bloco3": "Técnica: rótulo. Qual sinal aparece nesta mensagem.",
 "bloco4": "..."}}
Estado `evidência insuficiente` (o bloco4 diz onde procurar, nunca vazio):
{{"bloco1": "...", "bloco2": "...", "bloco3": "...", "bloco4": "Onde a pessoa pode procurar."}}
Estado `lacuna de acervo`:
{{"bloco1": "...", "bloco2": "...", "bloco3": "...", "bloco4": ""}}"""

# verificacao-alegacao: o bloco 2 separa a opinião da mensagem. O modelo esqueceu
# na execução ponta a ponta de 06/10 (casos F04 e R3); a frase sai do código.
FRASE_OPINIAO = "Uma parte da mensagem é opinião, e opinião não se checa."

ID_TRECHO = re.compile(r"\bT[1-9]\d*\b")
ENGANA = re.compile(r"\b(engana|enganos[ao]|é fals[ao]|mentira)\b", re.IGNORECASE)
# Decisão 5 de fix-resposta-sem-evidencia: com ponteiro, o bloco 2 fala só do
# acervo consultado e não julga a alegação. Sai do código porque, na sonda, o
# modelo escreveu "não significa que seja falsa" 3 vezes em 3 (decisão 18).
BLOCO_2_COM_PONTEIRO = ("O acervo consultado aqui não cobre esta mensagem. Não achar "
                        "nele não confirma nem desmente nada.")


@dataclass
class Resposta:
    forma: str
    titulos: list
    blocos: list
    detalhe: list = field(default_factory=list)
    defeitos: list = field(default_factory=list)
    # Task 1.6: frases que a ancoragem tirou, e o motivo do rebaixamento, se houve.
    descartadas: list = field(default_factory=list)
    rebaixada_por: str | None = None
    veredito: Veredito | None = None
    bruto: str = ""  # saída do modelo, para a sonda ler o que ele de fato escreveu

    @property
    def texto(self):
        """Camada visível: os quatro blocos com os títulos, nesta ordem."""
        return "\n\n".join(f"{t} {b}".strip() for t, b in zip(self.titulos, self.blocos))


def _estado(veredito, lacuna):
    if lacuna is not None:
        if veredito.trechos:
            raise ValueError("lacuna de acervo com trecho recuperado troca a forma")
        if not lacuna.get("corte"):
            raise ValueError("lacuna de acervo sem data de corte do acervo")
        return LACUNA
    if veredito.rotulo == INSUFICIENTE or not veredito.trechos:
        return INSUFICIENTE
    return "com evidência"


def mensagem(texto, alegacao, veredito, estado, decomposicao=None):
    partes = [f"ESTADO DA RECUPERAÇÃO: {estado}",
              f"MENSAGEM RECEBIDA:\n\"\"\"{texto}\"\"\"",
              f"ALEGAÇÃO CHECADA:\n{alegacao}"]
    if estado == "com evidência":
        partes.append(f"VEREDITO: {veredito.rotulo}\nCRITÉRIO: {veredito.criterio}")
        linhas = ["TRECHOS:"]
        for n, t in enumerate(veredito.trechos, 1):
            linhas.append(f"[T{n}] {t['agencia']}, {t['data_publicacao']}\n\"\"\"{t['trecho']}\"\"\"")
        partes.append("\n\n".join(linhas))
    else:
        partes.append("TRECHOS: nenhum.")
    if decomposicao:
        if decomposicao.get("opinioes"):
            partes.append("OPINIÃO NA MENSAGEM:\n" + "\n".join(decomposicao["opinioes"]))
        c = decomposicao.get("conclusao")
        if c and c.get("decorre") is False:
            partes.append(f"CONCLUSÃO QUE NÃO DECORRE DOS FATOS: {c['texto']}\nSALTO: {c['salto']}")
    return "\n\n".join(partes)


def _abertura(veredito, estado, lacuna):
    if estado == LACUNA:
        return f"Lacuna de acervo. As checagens consultadas vão só até {lacuna['corte']}."
    return ABERTURA[veredito.rotulo]


def _ponteiro(lacuna):
    p = lacuna.get("ponteiro")
    if not p:
        return "Não foi localizada checagem em português sobre isso."
    return (f"Checagem localizada: {p['agencia']}, {p['data']}, veredito da agência: "
            f"{p['veredito']}. {p['endereco']}")


def _detalhe(veredito):
    """Trechos citados e, depois deles, as referências inaptas (decisão 17).

    A referência tem as mesmas chaves, com `trecho` vazio: agência, data, link e
    veredito da agência são auditáveis, o texto reprovado não é exibido.
    """
    chaves = ("agencia", "data_publicacao", "url", "veredito_original", "trecho")
    citados = [{k: t[k] for k in chaves} for t in veredito.trechos]
    return citados + [{**{k: ref[k] for k in chaves[:-1]}, "trecho": None}
                      for ref in veredito.referencias]


def _marcar(bloco3, catalogo):
    """Põe `Técnica: ` no bloco 3 que abre só com rótulos do catálogo.

    O modelo escolhe os rótulos, mas omite o marcador: na bancada de 06/10,
    5 de 6 casos da forense. Só a primeira frase conta, e só quando ela é
    inteira de rótulos do catálogo; o resto continua a cargo da validação da
    3.3 (decisão 24).
    """
    if catalogo_mod.MARCADOR.search(bloco3):
        return bloco3
    primeira = re.split(r"[.!?\n]", bloco3, maxsplit=1)[0]
    partes = [catalogo_mod._limpo(p) for p in re.split(r",|\se\s", primeira)]
    permitidos = {r.lower() for r in catalogo}
    if partes and all(p in permitidos for p in partes):
        return f"Técnica: {bloco3}"
    return bloco3


def _frases(texto):
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+|\n+", texto) if f.strip()]


def _defeitos_legibilidade(r):
    achados = []
    palavras = len(r.texto.split())
    if palavras > TETO_PALAVRAS:
        achados.append(f"camada visível com {palavras} palavras, teto {TETO_PALAVRAS}")
    for b in r.blocos:
        for f in _frases(b):
            if len(f.split()) > TETO_FRASE:
                achados.append(f"frase com mais de {TETO_FRASE} palavras: {f}")
    for t in sorted(set(ID_TRECHO.findall(r.texto))):
        achados.append(f"identificador de trecho na camada visível: {t}")
    return achados


def _defeitos_com(r, veredito, alegacao, decomposicao, catalogo):
    achados = []
    b3 = r.blocos[2]
    if veredito.rotulo == "verdadeiro":
        achados += [f"técnica nomeada em veredito verdadeiro: {t}"
                    for t in catalogo_mod.rotulos_marcados(r.texto)]
    else:
        achados += [f"bloco 3: {d}" for d in catalogo_mod.validar_rotulos(b3, catalogo)]
    if veredito.rotulo == "falso":
        achados += [f"mito: {d}" for d in verificar_mito(r.texto, alegacao)]
    if decomposicao and decomposicao.get("opinioes") and "opini" not in r.blocos[1].lower():
        achados.append("bloco 2 não separa a opinião da mensagem")
    return achados


def _defeitos_sem(r, catalogo):
    achados = []
    texto = r.texto.lower()
    nomeadas = set(catalogo_mod.rotulos_marcados(r.texto))
    nomeadas |= {c.lower() for c in catalogo if c.lower() in texto}
    achados += [f"técnica nomeada sem evidência: {t}" for t in sorted(nomeadas)]
    if ENGANA.search(r.blocos[2]):
        achados.append("bloco 3 da forma sem evidência afirma que a mensagem engana")
    return achados


def _ancorar(crus, veredito, decomposicao):
    """Blocos 1 e 2 sem as frases não ancoradas, as descartadas e o motivo do
    rebaixamento — `None` quando o veredito se sustenta."""
    opiniao = bool(decomposicao and decomposicao.get("opinioes"))
    m1, d1, _ = ancorar_bloco(crus[0], veredito.trechos)
    m2, d2, ancoradas2 = ancorar_bloco(crus[1], veredito.trechos, opiniao=opiniao)
    descartadas = [{"bloco": 1, **d} for d in d1] + [{"bloco": 2, **d} for d in d2]
    motivo = None
    if d1:
        motivo = f"bloco 1: {d1[0]['motivo']}"
    elif not ancoradas2:
        motivo = "bloco 2 sem frase ancorada"
    return " ".join(m1), " ".join(m2), descartadas, motivo


def _rebaixado(veredito, motivo):
    return Veredito(INSUFICIENTE, "Nenhuma afirmação essencial da resposta ficou ancorada em trecho.",
                    rebaixado_por=f"ancoragem: {motivo}",
                    original={"rotulo": veredito.rotulo, "criterio": veredito.criterio},
                    referencias=list(veredito.referencias))


def responder(texto, alegacao, veredito, decomposicao=None, lacuna=None,
              chat=chat_ollama, catalogo=None):
    """Monta a resposta de quatro blocos a partir do veredito da guarda.

    `veredito` é o `guarda.Veredito`. `lacuna`, quando a pauta é posterior ao
    acervo, traz `corte` e, se o índice de checagens recentes achou, `ponteiro`
    com agência, data, veredito e endereço.
    """
    catalogo = catalogo or catalogo_mod.carregar_catalogo()
    estado = _estado(veredito, lacuna)
    com = estado == "com evidência"
    titulos = list(COM if com else SEM)
    if veredito.rotulo == "verdadeiro" and com:
        titulos[2] = TITULO_3_VERDADEIRO

    ponteiro = bool(lacuna and lacuna.get("ponteiro"))
    bruto = chat(SISTEMA, mensagem(texto, alegacao, veredito, estado, decomposicao))
    dados = ler_json(bruto)
    crus = [(dados or {}).get(f"bloco{n}") for n in range(1, 5)]
    gerados = [texto_do_bloco(c) for c in crus]

    descartadas = []
    if com and dados is not None:
        gerados[0], gerados[1], descartadas, motivo = _ancorar(crus, veredito, decomposicao)
        if motivo:
            rebaixado = _rebaixado(veredito, motivo)
            r = responder(texto, alegacao, rebaixado, decomposicao, None, chat, catalogo)
            r.descartadas = descartadas
            r.rebaixada_por = rebaixado.rebaixado_por
            r.bruto = f"{bruto}\n\n--- refeita na forma sem evidência ---\n\n{r.bruto}"
            return r

    blocos = list(gerados)
    if com and veredito.rotulo != "verdadeiro":
        blocos[2] = _marcar(blocos[2], catalogo)
    if com and decomposicao and decomposicao.get("opinioes") and blocos[1] \
            and "opini" not in blocos[1].lower():
        blocos[1] = f"{blocos[1]} {FRASE_OPINIAO}"
    blocos[0] = f"{_abertura(veredito, estado, lacuna)} {gerados[0]}".strip()
    if estado == LACUNA:
        blocos[3] = _ponteiro(lacuna)
    if ponteiro:
        blocos[1] = BLOCO_2_COM_PONTEIRO
    r = Resposta("com evidência" if com else "sem evidência", titulos, blocos, _detalhe(veredito),
                 descartadas=descartadas, veredito=veredito, bruto=bruto)

    if dados is None:
        r.defeitos = ["saída não é JSON"]
        return r
    obrigatorios = (2, 3, 4) if estado != LACUNA else (3,) if ponteiro else (2, 3)
    r.defeitos = [f"bloco{n} vazio" for n in obrigatorios if not gerados[n - 1]]
    if com:
        r.defeitos += _defeitos_com(r, veredito, alegacao, decomposicao, catalogo)
    else:
        r.defeitos += _defeitos_sem(r, catalogo)
    r.defeitos += _defeitos_legibilidade(r)
    return r
