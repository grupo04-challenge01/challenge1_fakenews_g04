"""Tratamento dos datasets para uso em PT-BR — change `add-tratamento-datasets-ptbr`.

Pacote de curadoria de pesquisa, não módulo de produto. Reúne o que as quatro
capabilities do change exigem antes de qualquer dado ser indexado, citado ou
oferecido como estímulo:

- `leitura`      — contrato de leitura dos derivados (`normalizacao-rotulos`)
- `integridade`  — perda sistemática de caractere (`integridade-textual`)
- `vereditos`    — parser e mapa versionado de veredito (`normalizacao-rotulos`)
- `frescor`      — cobertura temporal e temática medida (`frescor-corpus`)
"""
