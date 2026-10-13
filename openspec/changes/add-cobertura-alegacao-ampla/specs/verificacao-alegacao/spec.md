# Delta para verificacao-alegacao

## MODIFIED Requirements

### Requirement: Classificação com incerteza explícita

O sistema SHALL classificar a alegação em exatamente um de quatro rótulos:
`falso`, `verdadeiro`, `verdadeiro fora de contexto ou exagerado`, ou
`evidência insuficiente`. O sistema MUST usar `evidência insuficiente` quando a
recuperação não retornar fonte que cubra a alegação, e MUST NOT emitir veredito
a partir apenas do conhecimento paramétrico do modelo. Uma fonte cobre a
alegação quando checa a mesma alegação ou, só para o rótulo `falso`, quando
checa uma alegação mais ampla nos termos do requirement "Cobertura por alegação
mais ampla". Todo veredito SHALL declarar qual das duas coberturas o sustenta.

#### Scenario: Sem evidência recuperada
- **WHEN** nenhum documento recuperado sustenta ou refuta a alegação
- **THEN** o sistema responde `evidência insuficiente`
- **AND** explica o que especificamente não foi encontrado
- **AND** sugere onde a pessoa pode procurar

#### Scenario: Alegação verdadeira contra-intuitiva
- **WHEN** a alegação soa implausível mas a evidência recuperada a sustenta
- **THEN** o sistema classifica como `verdadeiro`
- **AND** não rebaixa o veredito por implausibilidade aparente

#### Scenario: Mesmo assunto, alegação que não decorre da checada
- **GIVEN** a alegação "Tomar hidroxicloroquina toda semana previne a covid"
- **AND** só uma checagem sobre outra alegação a respeito da cloroquina
- **WHEN** o sistema classifica
- **THEN** o rótulo é `evidência insuficiente`

#### Scenario: Veredito declara a cobertura
- **GIVEN** um veredito diferente de `evidência insuficiente`
- **WHEN** o veredito é registrado
- **THEN** o rastro informa se a cobertura é da mesma alegação ou de alegação mais ampla

## ADDED Requirements

### Requirement: Cobertura por alegação mais ampla

Quando nenhuma checagem recuperada tratar da alegação da pessoa (P), mas houver
checagem de uma alegação mais geral (G) da qual P é caso particular, o sistema
SHALL poder classificar P como `falso`, desde que todas as condições abaixo se
cumpram. Se qualquer uma falhar, o rótulo MUST ser `evidência insuficiente`, e
o rastro MUST registrar qual condição falhou.

1. P implica G: se P fosse verdade, G seria necessariamente verdade. Essa
   implicação SHALL ser confirmada por uma verificação independente da
   classificação, que responde só se a implicação vale.
2. Toda checagem citada classifica G como falso, boato ou fake. Checagem com
   veredito enganoso, fora de contexto ou verdadeiro MUST NOT sustentar
   cobertura ampla.
3. As checagens citadas vêm de pelo menos duas agências distintas.
4. O sujeito de P (o produto, a substância ou a intervenção de que P fala)
   aparece no texto de P e no texto de cada checagem citada.
5. O veredito traz, por escrito, a ponte: por que P é caso particular de G.

Cobertura ampla MUST NOT sustentar os rótulos `verdadeiro` e `verdadeiro fora
de contexto ou exagerado`. O sistema SHALL ter uma configuração que desliga a
cobertura ampla; desligada, todo veredito de cobertura ampla vira `evidência
insuficiente`.

#### Scenario: Versão exagerada de alegação já checada
- **GIVEN** a alegação "Vacina de Covid-19 transformam pessoas em jacarés"
- **AND** checagens de duas agências que classificam como falso ou boato que a vacina contra a covid-19 altera o DNA ou transforma as pessoas em seres geneticamente modificados
- **WHEN** o sistema classifica
- **THEN** o rótulo é `falso`
- **AND** a cobertura declarada é de alegação mais ampla
- **AND** o veredito traz a ponte e cita as duas checagens

#### Scenario: Regra parecida para outra doença
- **GIVEN** a alegação "Chá de folha de goiabeira cura a dengue em 24 horas"
- **AND** checagens de duas agências que classificam como falso que a casca do jatobá cura o câncer
- **WHEN** o sistema classifica
- **THEN** o rótulo é `evidência insuficiente`

#### Scenario: Vizinha sem implicação
- **GIVEN** a alegação "Vacinas causam autismo"
- **AND** só checagens de que vacinas não alteram o DNA
- **WHEN** o sistema classifica
- **THEN** o rótulo é `evidência insuficiente`

#### Scenario: Uma agência só
- **GIVEN** uma alegação que implica uma alegação mais geral checada como falsa
- **AND** todas as checagens citadas vêm da mesma agência
- **WHEN** o sistema classifica
- **THEN** o rótulo é `evidência insuficiente`
- **AND** o rastro registra a falta da segunda agência

#### Scenario: Checagem da alegação geral com veredito enganoso
- **GIVEN** uma alegação que implica uma alegação mais geral
- **AND** uma das checagens citadas classifica a alegação geral como enganosa
- **WHEN** o sistema classifica
- **THEN** o rótulo é `evidência insuficiente`

#### Scenario: Generalização verdadeira
- **GIVEN** uma alegação particular
- **AND** checagens que classificam como verdadeira uma alegação mais geral
- **WHEN** o sistema classifica
- **THEN** o rótulo não é `verdadeiro` por cobertura ampla

#### Scenario: Verificação de implicação discorda
- **GIVEN** um veredito `falso` com cobertura ampla que cumpre as condições 2 a 5
- **WHEN** a verificação independente responde que a implicação não vale, ou não responde
- **THEN** o rótulo é `evidência insuficiente`
- **AND** o rastro registra a resposta da verificação

#### Scenario: Cobertura ampla desligada
- **GIVEN** a cobertura ampla desligada na configuração
- **WHEN** a classificação devolve `falso` com cobertura ampla
- **THEN** o rótulo é `evidência insuficiente`
