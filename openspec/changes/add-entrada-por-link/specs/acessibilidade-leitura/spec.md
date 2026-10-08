# Delta para Acessibilidade e Legibilidade

## MODIFIED Requirements

### Requirement: Entrada sem barreira

O sistema SHALL aceitar texto colado ou encaminhado e link como entrada, e MUST
NOT exigir cadastro, login ou preenchimento de formulário antes da primeira
verificação. Quando um link não puder ser lido, o sistema SHALL dizer em
linguagem cotidiana por que não leu e pedir o texto colado, e MUST NOT exibir
mensagem técnica de erro (código HTTP, nome de exceção, termo de rede).

#### Scenario: Primeira verificação
- **WHEN** uma pessoa usa o sistema pela primeira vez
- **THEN** colar a mensagem é suficiente para receber a resposta
- **AND** nenhum dado pessoal é solicitado

#### Scenario: Link como entrada
- **GIVEN** uma pessoa que cola só o link de uma notícia de saúde legível
- **WHEN** a mensagem é enviada
- **THEN** ela recebe a verificação do conteúdo da notícia

#### Scenario: Link que não abre
- **GIVEN** uma pessoa que cola o link de um site fora do ar
- **WHEN** a mensagem é enviada
- **THEN** a resposta explica que o link não abriu e pede o texto
- **AND** nenhum termo técnico aparece na resposta
