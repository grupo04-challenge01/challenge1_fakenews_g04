"""Catálogo fechado de técnicas — tasks 3.1 e 3.3 de mvp-copiloto-verificacao.

O catálogo vive em `catalogo_tecnicas.json`, versionado. O bloco 3 da forma com
evidência declara a técnica depois do marcador `Técnica:`; a validação lê só o
que vem depois do marcador, porque sem ele não há como separar o rótulo do uso
comum das mesmas palavras.

A validação confere **pertinência** ao catálogo, não **adequação** do rótulo ao
caso: `manchete exagerada` numa promessa de cura passa aqui. Ver decisão 10 de
add-selecao-modelos-arquitetura-rag.
"""
import json
import pathlib
import re

ARQUIVO = pathlib.Path(__file__).parent / "catalogo_tecnicas.json"
MARCADOR = re.compile(r"t[ée]cnicas?\s*:", re.IGNORECASE)


def carregar_catalogo(arquivo=ARQUIVO):
    """Lista de rótulos do catálogo. Recusa catálogo fora de 6 a 8 rótulos únicos."""
    dados = json.loads(pathlib.Path(arquivo).read_text(encoding="utf-8"))
    rotulos = [t["rotulo"] for t in dados["tecnicas"]]
    if not 6 <= len(rotulos) <= 8 or len(set(rotulos)) != len(rotulos):
        raise ValueError(f"catálogo precisa de 6 a 8 rótulos únicos, tem {rotulos}")
    ambiguos = [r for r in rotulos if "," in r or " e " in r]
    if ambiguos:
        raise ValueError(f"rótulo com vírgula ou ' e ' não é separável no bloco 3: {ambiguos}")
    return rotulos


def _limpo(rotulo):
    return re.sub(r"[*_`\"'“”«».;:]", "", rotulo).strip().lower()


def rotulos_marcados(texto):
    """Rótulos declarados depois de cada `Técnica:`, até o fim da frase."""
    achados = []
    limpo = re.sub(r"[*_`]", "", texto)
    for m in MARCADOR.finditer(limpo):
        frase = re.split(r"[.!?\n]", limpo[m.end():], maxsplit=1)[0]
        for parte in re.split(r",|\se\s", frase):
            if _limpo(parte):
                achados.append(_limpo(parte))
    return achados


def validar_rotulos(texto, catalogo):
    """Defeitos do bloco 3 quanto ao catálogo; lista vazia quando está em ordem."""
    marcados = rotulos_marcados(texto)
    if not marcados:
        return ["nenhum rótulo marcado"]
    permitidos = {r.lower() for r in catalogo}
    return [f"rótulo fora do catálogo: {r}" for r in marcados if r not in permitidos]


def validar_sem_evidencia(texto, catalogo=None):
    """Defeitos da forma sem evidência quanto ao catálogo; lista vazia quando em ordem.

    Task 3.3 de fix-resposta-sem-evidencia: sob evidência insuficiente ou lacuna
    de acervo, qualquer técnica nomeada é tratada como defeito, conforme o
    scenario 'Técnica nomeada sem evidência recuperada' de resposta-formativa.
    """
    marcados = rotulos_marcados(texto)
    if marcados:
        return [f"técnica nomeada sob evidência insuficiente: {r}" for r in marcados]
    if catalogo:
        limpo = re.sub(r"[*_`]", "", texto).lower()
        achados = [r for r in catalogo if re.search(r"\b" + re.escape(r.lower()) + r"\b", limpo)]
        if achados:
            return [f"técnica do catálogo mencionada sob evidência insuficiente: {r}" for r in achados]
    return []

