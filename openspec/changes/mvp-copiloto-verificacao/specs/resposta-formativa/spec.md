# Delta para Resposta Formativa

## ADDED Requirements

### Requirement: Estrutura de quatro blocos

Toda resposta de verificação SHALL conter, nesta ordem: (1) veredito,
(2) o que se sabe sobre o assunto, (3) por que aquela mensagem engana e
(4) o que observar da próxima vez. Os blocos 3 e 4 MUST estar presentes mesmo
quando o veredito for `verdadeiro`.

#### Scenario: Alegação falsa
- **WHEN** o veredito é `falso`
- **THEN** a resposta traz os quatro blocos na ordem definida
- **AND** o bloco 3 nomeia os sinais concretos presentes naquela mensagem

#### Scenario: Alegação verdadeira
- **WHEN** o veredito é `verdadeiro`
- **THEN** o bloco 3 explica por que a mensagem era difícil de avaliar
- **AND** o bloco 4 indica o que sustentou a confirmação

### Requirement: Catálogo fechado de técnicas de manipulação

O bloco 3 SHALL nomear ao menos uma técnica de um catálogo fixo de 6 a 8
rótulos, mantido em arquivo versionado. O sistema MUST NOT inventar rótulos
fora do catálogo nem apresentar a técnica em linguagem acadêmica.

#### Scenario: Promessa de cura
- **WHEN** a mensagem promete cura para doença grave sem estudo identificável
- **THEN** o sistema rotula como `cura milagrosa`
- **AND** descreve o sinal em linguagem cotidiana

#### Scenario: Estudo real com manchete inflada
- **WHEN** existe estudo real mas a manchete afirma mais do que ele conclui
- **THEN** o sistema rotula como `manchete exagerada`
- **AND** contrasta o que o estudo conclui com o que a manchete afirma

### Requirement: Revelação progressiva

A camada visível SHALL conter apenas veredito, o que se sabe, por que engana e
o que observar. Fontes, trechos originais e detalhe metodológico SHALL ficar em
camada acessível por uma ação explícita do usuário.

#### Scenario: Usuário quer conferir a fonte
- **WHEN** o usuário aciona o detalhe
- **THEN** links, trechos citados e datas são exibidos
- **AND** a camada visível permanece intacta

### Requirement: Ausência de reforço do mito

O sistema MUST NOT abrir a resposta repetindo a alegação falsa como afirmação
isolada, e SHALL marcá-la explicitamente como falsa sempre que precisar citá-la.

#### Scenario: Citação da alegação falsa
- **WHEN** a resposta precisa mencionar o conteúdo da mensagem falsa
- **THEN** a menção vem acompanhada da marcação de que é falsa
- **AND** a afirmação correta aparece antes e depois da menção
