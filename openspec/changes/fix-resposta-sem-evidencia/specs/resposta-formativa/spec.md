# Delta para resposta-formativa

## Purpose

Dar forma declarada à resposta quando não há evidência recuperada que sustente
afirmação sobre a mensagem, de modo que a estrutura de quatro blocos deixe de
exigir do sistema aquilo que o próprio veredito acabou de dizer que não se sabe.

Decidido em 19/09/2026 pela saída A registrada na `proposal.md`: forma própria,
e não apenas afrouxamento do catálogo.

## MODIFIED Requirements

### Requirement: Estrutura de quatro blocos

Toda resposta de verificação SHALL conter quatro blocos, e a forma dos blocos
SHALL depender de haver ou não evidência recuperada que sustente afirmação sobre
a mensagem.

Quando **há** evidência recuperada, os blocos são, nesta ordem: (1) veredito,
(2) o que se sabe sobre o assunto, (3) por que aquela mensagem engana e (4) o
que observar da próxima vez. Os blocos 3 e 4 MUST estar presentes mesmo quando o
veredito for `verdadeiro`.

Quando **não há** evidência recuperada — veredito `evidência insuficiente` ou
resposta de lacuna de acervo — os blocos são, nesta ordem: (1) veredito e o que
foi procurado, (2) por que isso não equivale a dizer que a mensagem é falsa,
(3) o que a pessoa pode conferir por conta própria e (4) onde procurar. O bloco
3 MUST NOT afirmar que a mensagem engana, e o bloco 4 MUST estar presente mesmo
quando não houver ponteiro a oferecer, declarando que não há.

O sistema MUST NOT emitir a forma com evidência quando não houver trecho
recuperado, nem a forma sem evidência quando houver.

#### Scenario: Alegação falsa

- **WHEN** o veredito é `falso`
- **THEN** a resposta traz os quatro blocos da forma com evidência, na ordem
  definida
- **AND** o bloco 3 nomeia os sinais concretos presentes naquela mensagem

#### Scenario: Alegação verdadeira

- **WHEN** o veredito é `verdadeiro`
- **THEN** o bloco 3 explica por que a mensagem era difícil de avaliar
- **AND** o bloco 4 indica o que sustentou a confirmação

#### Scenario: Nenhuma fonte recuperada cobre a alegação

- **WHEN** o veredito é `evidência insuficiente`
- **THEN** a resposta traz os quatro blocos da forma sem evidência
- **AND** o bloco 2 declara que não encontrar não é desmentir
- **AND** o bloco 3 oferece o que conferir, sem nomear técnica de manipulação

#### Scenario: Estrutura com evidência aplicada sem evidência

- **WHEN** o sistema produz o bloco "por que aquela mensagem engana" sem ter
  trecho recuperado que o sustente
- **THEN** a resposta é rejeitada como defeito
- **AND** o motivo registrado é afirmação sobre a mensagem sem evidência

### Requirement: Catálogo fechado de técnicas de manipulação

O bloco 3 da forma **com evidência** SHALL nomear ao menos uma técnica de um
catálogo fixo de 6 a 8 rótulos, mantido em arquivo versionado. O sistema MUST
NOT inventar rótulos fora do catálogo nem apresentar a técnica em linguagem
acadêmica.

A obrigação de nomear técnica MUST NOT se aplicar à forma sem evidência.
Nomear técnica ali afirma sobre a mensagem exatamente o que o veredito declarou
desconhecido, e MUST ser tratado como defeito e não como preenchimento.

#### Scenario: Promessa de cura

- **WHEN** a mensagem promete cura para doença grave sem estudo identificável
- **THEN** o sistema rotula como `cura milagrosa`
- **AND** descreve o sinal em linguagem cotidiana

#### Scenario: Estudo real com manchete inflada

- **WHEN** existe estudo real mas a manchete afirma mais do que ele conclui
- **THEN** o sistema rotula como `manchete exagerada`
- **AND** contrasta o que o estudo conclui com o que a manchete afirma

#### Scenario: Técnica nomeada sem evidência recuperada

- **WHEN** o veredito é `evidência insuficiente` e a resposta nomeia uma técnica
  do catálogo
- **THEN** a resposta é rejeitada
- **AND** o rótulo é removido em vez de substituído por outro do catálogo

## ADDED Requirements

### Requirement: Lacuna de acervo distinguida na resposta

WHEN a pauta da alegação é posterior à janela declarada do acervo, o sistema
SHALL responder com lacuna de acervo, e MUST NOT apresentá-la como `evidência
insuficiente`. A distinção SHALL aparecer na camada visível, e não apenas nos
metadados da resposta.

A resposta de lacuna de acervo SHALL informar a data de corte do acervo, e o
bloco 4 SHALL apresentar o ponteiro para a checagem localizada — agência, data,
veredito textual da agência e endereço — quando `indice-checagens-recentes`
devolver correspondência.

#### Scenario: Pauta posterior ao acervo com checagem localizada

- **GIVEN** um acervo cuja janela termina em 2021
- **WHEN** o usuário envia alegação sobre a vacina Qdenga e o índice devolve
  checagem publicada
- **THEN** a resposta é de lacuna de acervo, não de evidência insuficiente
- **AND** o bloco 1 informa a data de corte do acervo
- **AND** o bloco 4 traz agência, data e endereço da checagem localizada
- **AND** o texto da checagem de terceiro não é reproduzido

#### Scenario: Pauta ausente do acervo e do índice

- **GIVEN** uma pauta sem correspondência no acervo nem no índice
- **WHEN** a resposta é produzida
- **THEN** a resposta é de lacuna de acervo
- **AND** o bloco 4 declara que não há checagem localizada em português
- **AND** a ausência de ponteiro MUST NOT ser apresentada como ausência de
  checagem no mundo

### Requirement: Forma sem evidência cabe no teto da camada visível

A forma sem evidência SHALL respeitar o mesmo teto de palavras da camada visível
definido por `acessibilidade-leitura`. O ponteiro do bloco 4 SHALL contar para
esse teto, e MUST NOT ser empurrado para a camada de detalhe, porque é o que
torna a resposta acionável.

#### Scenario: Resposta sem evidência excede o teto

- **WHEN** a forma sem evidência ultrapassa o teto de palavras da camada visível
- **THEN** o texto dos blocos 2 e 3 é reduzido
- **AND** o ponteiro do bloco 4 permanece na camada visível
