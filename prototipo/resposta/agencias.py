"""Nome legível da agência de checagem (fix-robustez-demo, D4).

O índice guarda a agência como veio de cada corpus, e alguns valores trazem o
endereço colado (`https:apublica.org`). A troca vale só para o que a pessoa vê
e para o pedido ao modelo; índice, guarda e rastro seguem com o valor cru.
"""
NOMES = {
    "boatos": "Boatos.org",
    "lupa": "Agência Lupa",
    "https:piaui.folha.uol.com.brlupa": "Agência Lupa",
    "COMPROVA": "Projeto Comprova",
    "aos fatos": "Aos Fatos",
    "https:www.aosfatos.org": "Aos Fatos",
    "ESTADAO_VERIFICA": "Estadão Verifica",
    "fato-ou-fake": "Fato ou Fake",
    "https:apublica.org": "Agência Pública",
}


def nome(cru):
    """Nome da agência, ou o valor como veio quando não há nome conhecido."""
    return NOMES.get(cru, cru)
