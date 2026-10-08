"""Task 5.3 de add-gerador-api-deepseek: minimização antes do gerador remoto.

Requirement Minimização antes do envio, de `gerador-modelo`, e decisão D9:
telefone, CPF e e-mail viram marcadores; números que não são contato ficam,
e o endereço de um link não é tocado.
"""
import pytest

from prototipo.entrada.minimizar import minimizar


@pytest.mark.parametrize("texto, esperado", [
    ("Me liga no (11) 98765-4321, chá de boldo cura hepatite",
     "Me liga no [telefone], chá de boldo cura hepatite"),
    ("zap 11 98765-4321", "zap [telefone]"),
    ("+55 11 98765-4321 manda pra todos", "[telefone] manda pra todos"),
    ("liga 11987654321", "liga [telefone]"),
    ("fixo (21) 3456-7890", "fixo [telefone]"),
    ("só o número 98765-4321", "só o número [telefone]"),
    ("meu CPF é 123.456.789-09", "meu CPF é [cpf]"),
    ("escreve pra maria.silva+saude@exemplo.com.br", "escreve pra [email]"),
])
def test_contato_vira_marcador(texto, esperado):
    assert minimizar(texto) == esperado


@pytest.mark.parametrize("texto", [
    "A vacina mata em 50% dos casos, desde 2017 e 2018.",
    "Cura a dengue em 24 horas, uma reação a cada 131 mil doses.",
    "Lei 13.709/2018 e portaria 1.234 de 2020.",
    "Dose de 500 mg, 3 vezes ao dia.",
])
def test_numero_que_nao_e_contato_fica(texto):
    assert minimizar(texto) == texto


def test_link_nao_e_tocado():
    texto = ("Olha https://g1.globo.com/noticia/2024/10/11987654321/x.ghtml?ref=a@b.com "
             "e me liga no 11 98765-4321")
    assert minimizar(texto) == ("Olha https://g1.globo.com/noticia/2024/10/11987654321/x.ghtml"
                                "?ref=a@b.com e me liga no [telefone]")
