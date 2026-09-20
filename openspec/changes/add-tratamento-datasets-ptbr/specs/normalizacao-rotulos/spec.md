# Delta para normalizacao-rotulos

## Purpose

Definir como o veredito publicado pelas agências brasileiras de checagem é lido,
normalizado e reconciliado antes de qualquer uso, de modo que um registro do
corpus nunca seja confundido com uma alegação única e que nenhum rótulo entre no
índice sem mapeamento declarado.

## ADDED Requirements

### Requirement: Contrato de leitura do corpus

O corpus SHALL ser lido com delimitador `;` e com quoting que preserve os
newlines internos do campo `text_news`. A contagem de registros obtida SHALL ser
conferida contra a contagem declarada no `datasets/README.md`, e divergência MUST
ser tratada como erro de leitura, nunca corrigida por normalização posterior.

#### Scenario: Leitura com delimitador default

- **WHEN** `factcenter_subset_saude.csv` é lido com o delimitador default e sem
  tratamento de newline interno
- **THEN** a leitura falha com erro de parser, contra 4.063 registros declarados
  em 48.392 linhas físicas
- **AND** a leitura é rejeitada como inválida
- **AND** nenhum derivado é gerado a partir dela

#### Scenario: Leitura que descarta linha defeituosa em silêncio

- **WHEN** a leitura é feita com descarte de linha defeituosa, de modo que não
  levante erro
- **THEN** a contagem obtida é 25.670 registros de uma única coluna
- **AND** a leitura é rejeitada como inválida
- **AND** a divergência MUST NOT ser corrigida por normalização posterior

### Requirement: Interpretação do campo de veredito

O campo `rating` SHALL ser interpretado como lista de vereditos, não como
string. Cada elemento SHALL receber uma chave canônica normalizada por caixa, e o
valor textual original MUST ser preservado ao lado da chave para rastreabilidade
até a agência.

#### Scenario: Valor serializado

- **WHEN** o campo contém `"['FALSO', 'VERDADEIRO, MAS']"`
- **THEN** são reconhecidos dois vereditos distintos
- **AND** as duas grafias originais permanecem registradas
- **AND** o registro não recebe um veredito único

### Requirement: Mapa explícito de vocabulário por agência

MUST existir mapa versionado que associe cada valor de veredito observado a um
dos quatro rótulos de `verificacao-alegacao` ou a `nao_mapeavel`. Valor ausente
do mapa MUST interromper o processamento e exigir decisão registrada; MUST NOT
receber rótulo por semelhança de string.

A contagem que o mapa precisa cobrir é a de **valores de veredito**, não a de
strings do campo. Medido no corpus: 285 strings serializadas distintas, que se
resolvem em 26 grafias e 19 chaves canônicas sob dobra de caixa e acento. O mapa
SHALL ser indexado pela chave canônica, e a grafia original MUST permanecer
recuperável ao lado dela.

O valor `boato`, que responde por 43% dos registros, MUST NOT ser mapeado para
`falso` sem registro explícito de que a agência de origem publica apenas rumor e
que o rótulo não gradua intensidade.

#### Scenario: Veredito novo após atualização do corpus

- **WHEN** uma atualização introduz um valor de veredito que não consta do mapa
- **THEN** o processamento é interrompido
- **AND** o valor novo é listado para decisão
- **AND** nenhum registro afetado entra no índice até a decisão ser registrada

#### Scenario: Rótulo sem gradação

- **WHEN** o mapa é inspecionado na entrada `boato`
- **THEN** consta o registro de que a agência publica apenas rumor
- **AND** consta o que se perde ao tratá-lo como equivalente a `falso`

### Requirement: Registro que cobre mais de uma alegação

Registro cujo campo de veredito contém mais de um elemento MUST NOT ser tratado
como alegação única. Registro com vereditos divergentes entre si SHALL ser
marcado como `misto` e reservado como caso de teste da decomposição fato,
evidência e opinião.

Divergência SHALL ser avaliada sobre o rótulo de destino, não sobre a grafia:
dois vereditos de grafia diferente que caem no mesmo rótulo não tornam o
registro misto. Medido sob o mapa versão 1.0.0: 587 registros multi-alegação,
dos quais 245 são mistos.

#### Scenario: Vereditos divergentes no mesmo registro

- **WHEN** o registro traz `['FALSO', 'SUBESTIMADO', 'VERDADEIRO', 'VERDADEIRO']`
- **THEN** o registro é marcado como `misto`
- **AND** não recebe rótulo consolidado
- **AND** entra no conjunto reservado de casos de teste

#### Scenario: Compilado de muitas alegações

- **WHEN** o registro traz mais de vinte vereditos, como os compilados
  periódicos de uma agência
- **THEN** o registro é excluído do banco de estímulos
- **AND** o motivo da exclusão é registrado como caveat

### Requirement: Ausência de itens verdadeiros no corpus

O corpus MUST NOT ser usado como fonte de itens de veredito `verdadeiro`: 21
registros consolidam em `verdadeiro` e 22 têm chave única `verdadeiro` ou
`verdadeiro, mas`, em 4.063. A
carência SHALL constar dos caveats do dataset, e a coleta desses itens SHALL ser
tratada como trabalho manual à parte.

#### Scenario: Tentativa de amostrar itens verdadeiros do corpus

- **WHEN** uma amostragem de itens verdadeiros é pedida ao corpus
- **THEN** o caveat da carência é apresentado
- **AND** a amostragem não é executada sobre este corpus
