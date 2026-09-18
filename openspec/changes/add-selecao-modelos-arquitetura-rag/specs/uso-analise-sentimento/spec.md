# Delta para uso-analise-sentimento

## Purpose

Fixar o estatuto da análise de sentimento e de emoção neste projeto — explicativa
e descritiva, nunca evidenciária — para que o pedido de pesquisá-la seja atendido
sem produzir um sinal que contradiz `verificacao-alegacao`.

## ADDED Requirements

### Requirement: Sentimento não participa do veredito

Sinal de sentimento ou de emoção MUST NOT integrar a decisão de veredito, nem
como atributo de classificador, nem como ajuste de confiança, nem como critério
de ordenação da evidência recuperada.

#### Scenario: Mensagem verdadeira com carga emocional alta

- **GIVEN** um alerta verdadeiro de surto redigido em tom alarmante
- **WHEN** a verificação é executada
- **THEN** o veredito é determinado apenas pela evidência recuperada
- **AND** a carga emocional não rebaixa o veredito

#### Scenario: Mensagem falsa em tom calmo e técnico

- **GIVEN** um texto de desinformação redigido em tom neutro e pseudo-técnico
- **WHEN** a verificação é executada
- **THEN** a ausência de carga emocional não eleva o veredito
- **AND** a ausência de carga emocional não reduz o rigor da recuperação

### Requirement: Emoção nomeada como conteúdo formativo

Quando técnica de manipulação por emoção for detectada, o sistema SHALL nomeá-la
ao usuário no bloco de técnicas da resposta, em linguagem cotidiana e a partir do
catálogo fechado. O sistema MUST NOT apresentar a técnica detectada como razão do
veredito.

#### Scenario: Apelo ao medo em alegação falsa

- **GIVEN** uma alegação falsa que usa apelo ao medo
- **WHEN** a resposta é composta
- **THEN** a técnica é nomeada ao usuário
- **AND** a justificativa do veredito continua sendo o trecho recuperado
- **AND** o texto distingue "usa esta técnica" de "é falso por usar esta técnica"

#### Scenario: Apelo ao medo em alegação verdadeira

- **GIVEN** uma alegação verdadeira que usa apelo ao medo
- **WHEN** a resposta é composta
- **THEN** a técnica é nomeada
- **AND** o veredito permanece `verdadeiro`
- **AND** a coexistência entre técnica de persuasão e conteúdo verdadeiro é
  explicitada ao usuário

### Requirement: Granularidade de emoção discreta

A análise adotada SHALL classificar emoção nomeada, tal como medo, raiva ou
urgência. Polaridade positivo, negativo ou neutro MUST NOT ser usada como saída
apresentada ao usuário, por não ser acionável para o propósito formativo.

#### Scenario: Inspeção do vocabulário apresentado

- **WHEN** o vocabulário de emoção apresentado ao usuário é inspecionado
- **THEN** os rótulos são emoções nomeadas
- **AND** nenhum rótulo é `positivo`, `negativo` ou `neutro`
- **AND** cada rótulo corresponde a entrada do catálogo de técnicas

### Requirement: Uso descritivo separado do caminho de resposta

A análise de sentimento SHALL ser admitida como instrumento de caracterização do
corpus de circulação, e o resultado desse uso MUST permanecer no portfólio de
pesquisa, sem alimentar o caminho de verificação em tempo de resposta.

#### Scenario: Caracterização do corpus de circulação

- **GIVEN** o corpus de Telegram de `acervo-circulacao`
- **WHEN** a distribuição de emoção é medida sobre ele
- **THEN** o resultado é registrado como achado de pesquisa
- **AND** o resultado não é usado para treinar nem ajustar o verificador
