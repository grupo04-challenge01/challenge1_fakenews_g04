"""Minimização antes do gerador remoto (add-gerador-api-deepseek, D9).

Telefone, CPF e e-mail no texto da pessoa viram `[telefone]`, `[cpf]` e
`[email]`. O endereço de um link fica como está, para a busca da página
continuar funcionando. Nome próprio não sai: sem modelo não há como reconhecer
nome sem apagar remédio ou cidade.
"""
import re

URL = re.compile(r"https?://\S+", re.IGNORECASE)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
TELEFONE = re.compile(
    r"(?:\+55\s?)?(?:\(\d{2}\)\s?|\b\d{2}\s)?\b9?\d{4}-\d{4}\b"  # com hífen
    r"|(?:\+55\s?)?\b(?:55)?\d{2}9?\d{8}\b")                    # só dígitos, com DDD


def _trocar(trecho):
    trecho = EMAIL.sub("[email]", trecho)
    trecho = CPF.sub("[cpf]", trecho)
    return TELEFONE.sub("[telefone]", trecho)


def minimizar(texto):
    partes, inicio = [], 0
    for m in URL.finditer(texto):
        partes += [_trocar(texto[inicio:m.start()]), m.group()]
        inicio = m.end()
    partes.append(_trocar(texto[inicio:]))
    return "".join(partes)
