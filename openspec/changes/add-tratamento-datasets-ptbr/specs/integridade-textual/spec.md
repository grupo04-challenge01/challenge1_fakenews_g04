# Delta para integridade-textual

## Purpose

Garantir que o texto em português que chega ao usuário como citação seja fiel ao
que a agência publicou, e que arquivos com perda sistemática de caractere sejam
reprovados antes do uso em vez de descobertos na saída do produto.

## ADDED Requirements

### Requirement: Fidelidade do trecho citado

Todo trecho citado ao usuário SHALL ser idêntico ao texto correspondente no
corpus, sem reescrita, sem remoção de acento e sem normalização silenciosa. O
corpus SHALL preservar a acentuação completa do português, incluindo maiúsculas
acentuadas.

#### Scenario: Trecho com maiúscula acentuada

- **WHEN** o texto da fonte contém `Sistema Único de Saúde`
- **THEN** o trecho citado preserva o `Ú`
- **AND** o trecho não é exibido se o corpus armazenar `Sistema nico de Saúde`

### Requirement: Verificação de perda de caractere antes do uso

Cada arquivo derivado em português MUST ser verificado quanto à presença das
letras acentuadas maiúsculas do português e do `ü`. A verificação SHALL ser
registrada por arquivo, com a lista de caracteres ausentes.

Ausência total de uma letra MUST NOT bastar, sozinha, para reprovar o arquivo.
O critério de corrupção sistemática SHALL exigir as duas condições juntas: a
maiúscula com zero ocorrências **e** a minúscula correspondente frequente no
mesmo arquivo. Satisfeito o critério, o arquivo MUST NOT ser aprovado para uso
em recuperação ou em citação.

A precisão é necessária porque a leitura literal reprova corpus íntegro:
`factcenter_subset_saude.csv` tem zero `Ü` em 21,5 milhões de caracteres porque
o trema foi abolido em 1990, e o `ü` minúsculo aparece 57 vezes no mesmo
arquivo — prova de que o pipeline não descarta o caractere.

#### Scenario: Arquivo com classe inteira de caractere ausente

- **WHEN** `factckbr_normalizado.csv` é verificado e onze letras acentuadas
  maiúsculas têm zero ocorrência em todo o arquivo, sete delas com a minúscula
  correspondente frequente
- **THEN** o arquivo é reprovado para uso em citação
- **AND** a lista dos caracteres ausentes fica registrada como caveat
- **AND** o dataset permanece utilizável apenas para contagem de rótulo, não
  para exibição de texto

#### Scenario: Letra ausente por ortografia, não por corrupção

- **WHEN** um arquivo tem zero ocorrência de `Ü` e a minúscula `ü` aparece
  poucas dezenas de vezes
- **THEN** a ausência é registrada sem reprovar o arquivo
- **AND** o arquivo permanece aprovado para recuperação e citação

### Requirement: Perda de caractere distinguida de texto transformado

Arquivo reprovado no portão de caractere SHALL ter a causa provável registrada,
distinguindo perda seletiva de caractere de texto que a fonte já entregou
transformado — lematizado, sem caixa ou sem stopwords. As duas reprovam para
citação, e MUST NOT ser registradas como o mesmo defeito.

O catálogo de formatos SHALL declarar, por arquivo, se o texto chega
transformado na origem, e o laudo MUST usar essa declaração para nomear a causa.

#### Scenario: Base entregue com texto lematizado

- **WHEN** `fakerecogna_subset_saude_ciencia.csv` é verificado e reprova por
  `Ç` com zero ocorrência contra 27.450 `ç`
- **THEN** a causa registrada é texto transformado na origem, não perda de
  caractere
- **AND** o arquivo é reprovado como fonte de trecho citado
- **AND** permanece utilizável como estímulo, com a transformação declarada

### Requirement: Correção da causa a montante

A filtragem de caractere do script de atualização do FACTCK.BR MUST aceitar as
maiúsculas acentuadas do português e o `ü`, ou ser substituída por normalização
Unicode que não descarte caractere. Reexecutar o script sem essa correção MUST
NOT ser aceito como caminho de atualização do dataset.

A correção vale para coleta futura e MUST NOT ser apresentada como reparo do
acervo existente: a perda já está no `FACTCKBR.tsv` distribuído pelos autores,
com os mesmos números do derivado. Reconstituir a acentuação por inferência
ortográfica MUST NOT ser feito, por ser adivinhação em texto que vira citação.

#### Scenario: Reparo confundido com recuperação do acervo

- **WHEN** o script corrigido é reexecutado sobre o `FACTCKBR.tsv` distribuído
- **THEN** as maiúsculas acentuadas continuam ausentes, porque não estão na fonte
- **AND** o arquivo permanece reprovado para citação
- **AND** a perda histórica é registrada como irreversível

#### Scenario: Atualização executada com a filtragem original

- **WHEN** o script é executado com a allowlist que contém apenas acentuadas
  minúsculas
- **THEN** o resultado é rejeitado
- **AND** o motivo registrado aponta a allowlist como causa raiz
