# Delta para adaptacao-criterios-en

## Purpose

Definir como os instrumentos em inglês atravessam para o português: por adaptação
validada contra casos brasileiros, e não por tradução de texto corrido, porque o
que precisa cruzar a fronteira de idioma é vocabulário de critério e não conteúdo
exibido ao usuário.

## ADDED Requirements

### Requirement: Adaptação validada em vez de tradução literal

Os critérios de qualidade do FakeHealth SHALL ser adaptados para o português com
rubrica de três níveis compatível com a capability `matriz-confianca`, e MUST NOT
ser traduzidos literalmente. Cada critério adaptado SHALL ser testado contra
casos brasileiros do corpus de checagens.

Critério que não discrimine nenhum caso brasileiro MUST ser removido, com o
motivo registrado.

#### Scenario: Critério que não discrimina caso brasileiro

- **WHEN** um critério adaptado é aplicado aos casos do corpus e não separa
  nenhum caso de nenhum outro
- **THEN** o critério é removido da rubrica
- **AND** o motivo da remoção fica registrado

### Requirement: Os dois conjuntos de critérios são distintos

O FakeHealth contém 20 perguntas em dois conjuntos distintos, um para notícia e
um para comunicado institucional, não 10 perguntas. O change MUST escolher um dos
conjuntos ou registrar o mapeamento manual entre eles, e MUST NOT tratar os dois
como um conjunto único.

#### Scenario: Consolidação indevida dos conjuntos

- **WHEN** uma contagem por critério é produzida somando os dois conjuntos como
  se fossem o mesmo
- **THEN** a contagem é rejeitada
- **AND** a separação entre os conjuntos é restabelecida antes de qualquer
  calibragem da matriz

### Requirement: Exemplares de few-shot em português

Os exemplares usados como few-shot SHALL estar em português. O pool derivado do
PUBHEALTH MUST NOT ser usado como exemplar por tradução; a substituição por casos
do corpus brasileiro SHALL ser o caminho adotado, e a decisão MUST ficar
registrada com o motivo.

#### Scenario: Exemplar traduzido do inglês

- **WHEN** um exemplar do pool em inglês é traduzido para compor o prompt
- **THEN** o exemplar é rejeitado
- **AND** um caso equivalente do corpus brasileiro é usado em seu lugar

### Requirement: Vocabulário de força da afirmação em português

Os rótulos de comparação entre estudo e manchete SHALL receber nomes em
português, ligados ao rótulo `verdadeiro fora de contexto ou exagerado` de
`verificacao-alegacao` e ao catálogo de técnicas de `resposta-formativa`. Os
pares em inglês MUST NOT ser exibidos ao usuário como exemplo.

#### Scenario: Definição operacional aproveitada sem o texto

- **WHEN** a definição de força da afirmação é adotada a partir dos pares em
  inglês
- **THEN** os nomes dos rótulos usados no produto estão em português
- **AND** os exemplos mostrados ao usuário vêm de casos brasileiros
