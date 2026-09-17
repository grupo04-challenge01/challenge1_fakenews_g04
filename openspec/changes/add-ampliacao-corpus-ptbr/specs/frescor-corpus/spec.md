# Delta para frescor-corpus

Este delta reescreve dois requirements introduzidos por
`add-tratamento-datasets-ptbr`. O terceiro requirement daquela capability,
`Caminho de atualização com cobertura declarada`, permanece como está.

## MODIFIED Requirements

### Requirement: Cobertura declarada e verificável

O corpus SHALL ter cobertura declarada e versionada em **dois níveis
distintos**, nomeados como tais:

- **acervo com texto integral** — material cujo texto o projeto possui
  **inteiro e não transformado**, e por isso pode citar, com janela temporal,
  concentração por ano e lista de pautas verificadas como ausentes por busca de
  termo, declaradas por base;
- **acervo com texto transformado** — material cujo texto foi sumarizado,
  truncado ou reescrito na origem. Conta para cobertura temporal e serve como
  estímulo, e MUST NOT ser contado no nível citável;
- **índice de localização** — material do qual o projeto possui apenas
  referência, com data de corte e agências alcançadas.

A declaração MUST ser verificável por reexecução da medição, e MUST NOT
apresentar os três níveis como cobertura equivalente. Nenhuma janela SHALL ser
declarada antes de medida: base recém-incorporada entra na declaração com a
janela contada, não com a janela anunciada pela fonte.

#### Scenario: Inspeção da declaração de cobertura

- **WHEN** a declaração de cobertura é inspecionada
- **THEN** os três níveis constam nomeados e separados
- **AND** para cada base do acervo constam a janela medida e a concentração por
  ano
- **AND** consta, por base, se o texto é integral ou transformado
- **AND** consta a lista de termos de pauta verificados por busca, com a
  contagem obtida por termo
- **AND** para o índice consta a data de corte

#### Scenario: Base incorporada sem medição

- **GIVEN** uma base recém-incorporada ao pacote
- **WHEN** a declaração de cobertura é atualizada
- **THEN** a janela declarada é a medida sobre o arquivo baixado
- **AND** a janela anunciada pela fonte, quando divergente, consta como caveat

#### Scenario: Distinção entre os níveis na citação

- **WHEN** material do índice de localização é considerado para citação
- **THEN** a declaração de cobertura o identifica como nível sem texto
- **AND** o material não é oferecido como fonte de trecho citado

#### Scenario: Base de texto transformado não promovida a citável

- **GIVEN** uma base cujo texto foi sumarizado na origem
- **WHEN** a cobertura temporal do acervo é declarada
- **THEN** a base conta para a janela temporal
- **AND** consta no nível de texto transformado, não no nível citável
- **AND** ampliar a janela por meio dela MUST NOT ser apresentado como ampliar o
  acervo citável

### Requirement: Lacuna de cobertura distinguida de ausência de evidência

WHEN a alegação trata de pauta que o acervo com texto integral não alcança, o
sistema SHALL distinguir **três** situações, e MUST NOT colapsá-las em
`evidência insuficiente`:

1. **checagem localizada** — existe item no índice: o sistema informa que não
   possui o texto, apresenta a referência e encaminha à fonte;
2. **sem correspondência no acervo consultado** — não há item no índice: o
   sistema informa o alcance da busca e sua data de corte;
3. **fora da janela declarada** — a pauta é posterior à data de corte de ambos
   os níveis: o sistema informa que a lacuna é do acervo, não do mundo.

Em nenhuma das três o sistema MUST apresentar a lacuna como ausência de checagem
publicada.

#### Scenario: Alegação com checagem apenas no índice

- **GIVEN** uma alegação posterior à janela do acervo com texto integral
- **AND** um item correspondente no índice de localização
- **WHEN** o usuário envia a alegação
- **THEN** o sistema informa que não possui o texto da checagem
- **AND** apresenta agência, data, veredito da agência e endereço da publicação
- **AND** encaminha o usuário à fonte para ler o argumento

#### Scenario: Alegação sem correspondência em nenhum nível

- **GIVEN** uma alegação sobre pauta de surto posterior à data de corte
- **WHEN** o usuário envia a alegação
- **THEN** o sistema informa que a lacuna é de cobertura do acervo
- **AND** nomeia a data de corte do acervo e a do índice
- **AND** distingue isso de não haver checagem publicada
- **AND** indica onde a pessoa pode procurar checagem recente

#### Scenario: Lacuna não apresentada como veredito

- **WHEN** qualquer uma das três situações de lacuna ocorre
- **THEN** o sistema MUST NOT apresentar a alegação como não verificada por
  falta de mérito
- **AND** MUST NOT emitir veredito de verdadeiro ou falso sustentado na lacuna
