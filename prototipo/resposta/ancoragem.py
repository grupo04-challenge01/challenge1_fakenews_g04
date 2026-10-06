"""Conferência frase × trecho — task 1.6 de mvp-copiloto-verificacao.

`recuperacao-evidencia`, requirement Rastreabilidade da evidência: toda
afirmação factual SHALL estar ancorada em um trecho recuperado, com fonte e
data acessíveis, e o sistema MUST NOT apresentar afirmação sem trecho de origem.

Decisão tomada antes do código (Samara, 06/10/2026): o modelo declara a âncora
de cada frase e o código confere. A conferência não julga sentido. Ela exige
que os **termos verificáveis** da frase estejam na fonte:

- número escrito em algarismos (`2020`, `172`), casado inteiro — `9` não casa
  dentro de `19`;
- mês (`maio`);
- quantidade por extenso: número seguido de unidade de tempo (`uma semana`,
  `dois dias`) ou número por extenso solto, exceto `um`/`uma`, que são artigo;
- nome próprio: palavra com maiúscula que não abre a frase.

"Na fonte" é o texto do trecho ou os metadados que acompanham a citação:
agência e data de publicação. Sem isso, "abril de 2020" seria descartado numa
checagem de julho de 2020 cujo texto só diz "9 de abril".

Maiúscula e acento não contam. Trecho com `apto_citacao` diferente de `True` não
ancora nada, nem frase sem termo (decisão 17).

Limite declarado: paráfrase sem termo verificável passa sempre. Frase que
inverte o sentido do trecho com as mesmas palavras ("o exame deu positivo")
não é pega aqui.
"""
import re
import unicodedata

MESES = ("janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro")
EXTENSO = ("dois", "duas", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez",
           "onze", "doze", "treze", "catorze", "quatorze", "quinze", "vinte", "trinta",
           "quarenta", "cinquenta", "cem", "cento", "mil", "milhao", "milhoes")
UNIDADES = r"(?:dias?|semanas?|m[eê]s|meses|anos?|horas?|minutos?)"
_QUANTIDADE = re.compile(
    rf"\b(?:um|uma|{'|'.join(EXTENSO)}|tr[eê]s)\s+{UNIDADES}\b", re.IGNORECASE)
_TOKEN = re.compile(r"\d+(?:[.,]\d+)*|[^\W\d_]+")
_ABRE_FRASE = re.compile(r"(?:^|[.!?:;\n])\s*[\"'“(]*$")


def normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento.casefold()).strip()


def termos(frase):
    """Termos verificáveis da frase, normalizados, na ordem em que aparecem."""
    achados = []
    ocupado = []
    for m in _QUANTIDADE.finditer(frase):
        achados.append((m.start(), normalizar(m.group())))
        ocupado.append(range(m.start(), m.end()))
    for m in _TOKEN.finditer(frase):
        if any(m.start() in r for r in ocupado):
            continue
        bruto, termo = m.group(), normalizar(m.group())
        if bruto[0].isdigit():
            achados.append((m.start(), termo))
        elif termo in MESES or termo in EXTENSO:
            achados.append((m.start(), termo))
        elif bruto[0].isupper() and not _ABRE_FRASE.search(frase[: m.start()]):
            achados.append((m.start(), termo))
    vistos, ordem = set(), []
    for _, termo in sorted(achados):
        if termo not in vistos:
            vistos.add(termo)
            ordem.append(termo)
    return ordem


def _fonte(trecho):
    partes = [trecho.get("trecho") or "", trecho.get("agencia") or ""]
    data = str(trecho.get("data_publicacao") or "")
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", data)
    if m:
        ano, mes, dia = m.groups()
        partes += [ano, MESES[int(mes) - 1], str(int(dia))]
    return normalizar(" ".join(partes))


def _contem(texto, termo):
    return re.search(rf"(?<![\w]){re.escape(termo)}(?![\w])", texto) is not None


def sem_suporte(frase, trecho):
    """Termos da frase que não estão no trecho nem na agência e data da fonte."""
    fonte = _fonte(trecho)
    return [t for t in termos(frase) if not _contem(fonte, t)]


def ancorada(frase, trecho):
    return trecho.get("apto_citacao") is True and not sem_suporte(frase, trecho)


# ---- bloco inteiro ----------------------------------------------------------
#
# O bloco chega como lista de {"frase": ..., "trecho": "T1"}: a âncora tem campo
# próprio. A primeira versão pedia a marca inline, no estilo de citação ("Nenhum
# estudo mostra isso [T1]."), e na sonda de 06/10 o modelo marcou o bloco 1 e
# deixou o bloco 2 sem marca em 11 de 12 respostas. A marca inline continua
# aceita, no texto e dentro de "frase", e sai do texto visível. Frase sem
# marca, com marca para trecho que não existe ou inapto, ou com termo que
# nenhum dos trechos marcados contém, é descartada. A única frase que pode ficar
# sem marca é a que separa a opinião da mensagem, e só quando a decomposição
# achou opinião: ela não afirma fato, diz que aquela parte não se checa.

MARCA = re.compile(r"\s*\[(T[1-9]\d*)\]")
_MARCA_APOS_PONTO = re.compile(r"([.!?])((?:\s*\[T[1-9]\d*\])+)")


def _frases(texto):
    texto = _MARCA_APOS_PONTO.sub(r"\2\1", texto)
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+|\n+", texto) if f.strip()]


def _limpa(frase):
    return re.sub(r"\s+([.!?,;:])", r"\1", MARCA.sub("", frase)).strip()


def conferir(frase, marcas, trechos):
    """Motivo do descarte, ou `None` se a frase está ancorada nos trechos marcados."""
    if not marcas:
        return "sem âncora"
    fontes = []
    for m in marcas:
        n = int(m[1:])
        if n > len(trechos):
            return f"âncora inexistente: {m}"
        if trechos[n - 1].get("apto_citacao") is not True:
            return f"trecho inapto a citação: {m}"
        fontes.append(trechos[n - 1])
    faltam = [t for t in termos(frase) if all(t in sem_suporte(frase, f) for f in fontes)]
    return f"termo fora do trecho: {', '.join(faltam)}" if faltam else None


_ID = re.compile(r"T[1-9]\d*")


def _itens(conteudo):
    """(frase com eventual marca inline, marcas do campo `trecho`) de cada frase."""
    if isinstance(conteudo, str):
        return [(f, []) for f in _frases(conteudo)]
    itens = []
    for item in conteudo or []:
        if isinstance(item, str):
            itens += [(f, []) for f in _frases(item)]
        elif isinstance(item, dict) and str(item.get("frase") or "").strip():
            campo = item.get("trecho")
            campo = " ".join(map(str, campo)) if isinstance(campo, list) else str(campo or "")
            itens.append((str(item["frase"]).strip(), _ID.findall(campo)))
    return itens


def texto_do_bloco(conteudo):
    """Texto visível de um bloco que veio como texto ou como lista de frases."""
    if isinstance(conteudo, list):
        return " ".join(f for f, _ in ((_limpa(b), m) for b, m in _itens(conteudo)) if f)
    return _limpa(str(conteudo or "")) if conteudo else ""


def ancorar_bloco(conteudo, trechos, opiniao=False, usadas=None):
    """Frases que ficam (sem a marca), frases descartadas com o motivo, e
    quantas das que ficam estão ancoradas — a de opinião fica, mas não conta.

    `conteudo` é a lista de {"frase", "trecho"} ou texto com marca inline.
    `trechos` é a lista na ordem em que foi numerada T1, T2... para o modelo.
    `usadas`, se dado, recebe o número de cada trecho que ancora frase que fica.
    """
    mantidas, descartadas, ancoradas = [], [], 0
    for bruta, do_campo in _itens(conteudo):
        marcas = list(dict.fromkeys(do_campo + MARCA.findall(bruta)))
        frase = _limpa(bruta)
        if not marcas and opiniao and "opini" in frase.lower():
            mantidas.append(frase)
            continue
        motivo = conferir(frase, marcas, trechos)
        if motivo:
            descartadas.append({"frase": frase, "motivo": motivo})
        else:
            mantidas.append(frase)
            ancoradas += 1
            if usadas is not None:
                usadas.update(int(m[1:]) for m in marcas)
    return mantidas, descartadas, ancoradas
