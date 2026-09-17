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
letras acentuadas maiúsculas do português. Ausência total de uma ou mais dessas
letras no arquivo inteiro MUST ser tratada como corrupção sistemática, e o
arquivo MUST NOT ser aprovado para uso em recuperação ou em citação.

A verificação SHALL ser registrada por arquivo, com a lista de caracteres
ausentes.

#### Scenario: Arquivo com classe inteira de caractere ausente

- **WHEN** `factckbr_normalizado.csv` é verificado e nove letras acentuadas
  maiúsculas têm zero ocorrência em todo o arquivo
- **THEN** o arquivo é reprovado para uso em citação
- **AND** a lista dos nove caracteres ausentes fica registrada como caveat
- **AND** o dataset permanece utilizável apenas para contagem de rótulo, não
  para exibição de texto

### Requirement: Correção da causa a montante

A filtragem de caractere do script de atualização do FACTCK.BR MUST aceitar as
maiúsculas acentuadas do português e o `ü`, ou ser substituída por normalização
Unicode que não descarte caractere. Reexecutar o script sem essa correção MUST
NOT ser aceito como caminho de atualização do dataset.

#### Scenario: Atualização executada com a filtragem original

- **WHEN** o script é executado com a allowlist que contém apenas acentuadas
  minúsculas
- **THEN** o resultado é rejeitado
- **AND** o motivo registrado aponta a allowlist como causa raiz
