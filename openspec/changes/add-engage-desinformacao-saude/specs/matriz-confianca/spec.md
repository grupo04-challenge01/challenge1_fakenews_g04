# Delta para matriz-confianca

## ADDED Requirements

### Requirement: Dimensões com sinal, papel da IA e limite

A matriz de confiança MUST descrever cada dimensão com quatro elementos: nome da
dimensão, sinal observável, papel que a IA pode cumprir, e limite explícito do
que essa dimensão não é capaz de determinar.

Uma dimensão sem limite declarado MUST NOT ser incluída na matriz.

#### Scenario: Dimensão de enquadramento emocional

- WHEN a matriz inclui a dimensão de linguagem e enquadramento
- THEN o limite registrado explicita que texto sensacionalista pode ser verdadeiro
- AND o papel da IA é descrito como marcação de trecho, não como indicador de falsidade

### Requirement: Rubrica de três níveis por dimensão

Cada dimensão MUST ter uma rubrica que caracterize sinal forte, sinal fraco e
sinal ausente, de modo que dois avaliadores diferentes cheguem à mesma
classificação para o mesmo caso.

#### Scenario: Divergência entre avaliadores

- WHEN dois integrantes classificam a mesma dimensão do mesmo caso de forma diferente
- THEN a rubrica é revisada até que a divergência seja resolvida por texto
- AND a versão revisada é registrada com a data da alteração

### Requirement: Ausência de score agregado

A matriz MUST NOT produzir uma pontuação única, nota agregada ou selo consolidado
de confiabilidade. A saída da matriz é um conjunto de evidências por dimensão.

Esta restrição decorre dos princípios de auditabilidade e de transferência: um
score único não é auditável, porque esconde qual dimensão pesou, e não ensina
critério nenhum, porque não sobra nada de observável para a próxima mensagem.

#### Scenario: Tentativa de consolidação em nota

- WHEN uma proposta de somar ou ponderar as dimensões em uma nota é apresentada
- THEN a proposta é rejeitada e o motivo registrado no design
- AND a alternativa adotada é apresentar as dimensões lado a lado

### Requirement: Validação empírica contra os casos

Cada dimensão da matriz MUST discriminar pelo menos um dos casos analisados na
investigação forense.

Dimensões que não discriminam nenhum caso MUST ser removidas da versão 1 e
registradas como descartadas, com o motivo.

#### Scenario: Dimensão decorativa

- WHEN uma dimensão recebe a mesma classificação em todos os casos analisados
- THEN a dimensão é removida da matriz
- AND o registro de descarte permanece no portfólio de pesquisa

### Requirement: Separação entre confiabilidade de fonte e de afirmação

A matriz MUST tratar a confiabilidade do veículo e a sustentação da afirmação
específica como dimensões separadas.

#### Scenario: Veículo confiável com afirmação mal sustentada

- WHEN um veículo com bom histórico publica uma alegação sem sustentação no estudo citado
- THEN a matriz classifica proveniência como sinal forte
- AND classifica evidência como sinal fraco, sem que uma dimensão anule a outra
