# frescor-corpus Specification

## Purpose

Tornar explícita a cobertura temporal e temática do corpus de checagens e definir
o que o sistema deve dizer quando a alegação do usuário trata de pauta que o
corpus não alcança, para que lacuna de cobertura não seja confundida com
ausência de checagem no mundo.

## Requirements

### Requirement: Cobertura declarada e verificável

O corpus SHALL ter cobertura declarada e versionada, contendo a janela temporal,
a concentração por ano e a lista de pautas de saúde verificadas como ausentes por
busca de termo. A declaração MUST ser verificável por reexecução da busca.

#### Scenario: Inspeção da declaração de cobertura

- **WHEN** a declaração de cobertura é inspecionada
- **THEN** consta a janela de 2013 a 2021
- **AND** consta que 54% dos registros são de 2020 e 56% mencionam covid
- **AND** consta a lista de termos com zero ocorrência, entre eles `qdenga`,
  `mpox`, `oropouche` e `semaglutida`

### Requirement: Lacuna de cobertura distinguida de ausência de evidência

WHEN a alegação trata de pauta posterior à janela do corpus, o sistema SHALL
informar que a lacuna é de cobertura do acervo, e MUST NOT apresentar
`evidência insuficiente` como se nenhuma checagem existisse no mundo.

#### Scenario: Alegação sobre pauta posterior ao corpus

- **GIVEN** um corpus cuja janela termina em 2021
- **WHEN** o usuário envia alegação sobre a vacina Qdenga
- **THEN** o sistema informa que o acervo não cobre o período da alegação
- **AND** distingue isso de não haver checagem publicada
- **AND** indica onde a pessoa pode procurar checagem recente

### Requirement: Caminho de atualização com cobertura declarada

O caminho de atualização do corpus SHALL declarar quais agências alcança. MUST
constar que o script de atualização do FACTCK.BR cobre três feeds contra as seis
agências presentes no corpus principal, e o caminho MUST NOT ser apresentado como
atualização do corpus completo.

O script MUST ser reparado antes do uso, por depender de API de biblioteca
removida em versão maior.

#### Scenario: Atualização apresentada como cobertura total

- **WHEN** o caminho de atualização é documentado
- **THEN** as três agências alcançadas estão nomeadas
- **AND** as agências não alcançadas estão nomeadas
- **AND** a dependência quebrada consta como pré-requisito de reparo
