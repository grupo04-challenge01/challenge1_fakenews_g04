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
