# Delta para anotacao-especialista-ptbr

## Purpose

Definir o que o projeto pode e não pode afirmar a partir de rótulo de veracidade
emitido por profissional de saúde sobre material em português, e tornar a
discordância entre anotadores um ativo declarado em vez de ruído descartado.

## ADDED Requirements

### Requirement: Proveniência da anotação declarada

Toda base cujo rótulo venha de anotação humana especializada SHALL declarar o
número de anotadores, sua qualificação, a regra de agregação dos votos e a
medida de concordância obtida. A declaração MUST acompanhar o dado no pacote de
datasets, e não apenas o artigo de origem.

#### Scenario: Inspeção da declaração de anotação

- **GIVEN** uma base com rótulo de anotador especializado no pacote
- **WHEN** a declaração de proveniência é inspecionada
- **THEN** constam o número de anotadores e sua qualificação profissional
- **AND** consta a regra de agregação usada para fechar o rótulo
- **AND** consta a medida de concordância entre anotadores

### Requirement: Faixa de empate preservada como caso ambíguo

Itens em que os anotadores não alcançaram a maioria exigida pela regra de
agregação MUST NOT ser descartados do pacote nem receber rótulo forçado. O
sistema SHALL preservá-los como classe própria, identificável por consulta, e
disponibilizá-los como material de curadoria de caso ambíguo.

#### Scenario: Item sem maioria entre anotadores

- **GIVEN** um item cujo veredito ficou empatado entre os anotadores
- **WHEN** o pacote de datasets é montado
- **THEN** o item permanece no pacote
- **AND** está marcado como empate, distinto de verdadeiro e de falso
- **AND** é recuperável por consulta sem inspeção manual arquivo a arquivo

#### Scenario: Uso da faixa de empate na curadoria

- **WHEN** casos de evidência ambígua são selecionados para o instrumento
- **THEN** a faixa de empate é uma das fontes candidatas
- **AND** a seleção registra que a ambiguidade é atestada por discordância entre
  especialistas, não presumida pelo grupo

### Requirement: Anotação clínica não serve como alvo de treino

A anotação por especialista MUST NOT ser usada como alvo de treino de
classificador de veredito. Os usos permitidos SHALL ser calibração de rubrica,
seleção de caso e referência de comparação para saída assistiva.

#### Scenario: Tentativa de uso como alvo de treino

- **GIVEN** uma base com rótulo de especialista clínico
- **WHEN** um uso previsto é registrado no pacote
- **THEN** o uso declarado é calibração, seleção de caso ou comparação
- **AND** treino de classificador de veredito consta como uso vedado

### Requirement: Validade temporal do rótulo declarada

O rótulo de especialista SHALL ser declarado como consenso clínico do período de
anotação, com esse período nomeado. O sistema MUST NOT apresentá-lo como verdade
atemporal quando a evidência sobre o tema tiver mudado depois da anotação.

#### Scenario: Alegação cuja evidência mudou após a anotação

- **GIVEN** um item anotado como desinformação em um período declarado
- **WHEN** o item é reapresentado para uso corrente
- **THEN** o período da anotação acompanha o rótulo
- **AND** o rótulo não é apresentado como veredito atual sobre o tema
