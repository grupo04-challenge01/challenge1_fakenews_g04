# Delta para procedencia-substituicao

## Purpose

Definir o que precisa ser verdade para uma base do pacote de datasets ser
trocada por versão mais nova sem quebrar a auditoria da coleta, de modo que a
troca continue reconstituível por terceiro a partir das fontes primárias.

## ADDED Requirements

### Requirement: Substituição registrada com motivo

Toda substituição de base SHALL ser registrada nomeando a base removida, a base
que entra, a data da troca e o motivo. O registro MUST ficar no repositório, não
apenas no histórico de commits.

#### Scenario: Inspeção do registro de substituição

- **GIVEN** uma base do pacote substituída por versão mais nova
- **WHEN** a documentação de fontes é inspecionada
- **THEN** constam a base removida e a base que entrou
- **AND** consta a data da substituição
- **AND** consta o motivo da troca

### Requirement: Licença conferida na fonte primária

A licença da base que entra SHALL ser conferida no release dos autores ou no
registro de publicação. Metadado de agregador ou de repositório de modelos MUST
NOT ser aceito como prova de licença.

#### Scenario: Licença anunciada por agregador

- **GIVEN** uma base cujo cartão em repositório de terceiro anuncia uma licença
- **WHEN** a base é incorporada ao pacote
- **THEN** a licença foi conferida na fonte primária dos autores
- **AND** a fonte conferida está citada na documentação
- **AND** divergência entre agregador e fonte primária é registrada como caveat

### Requirement: Derivados regerados a partir da base nova

Todo derivado produzido a partir da base removida SHALL ser regerado a partir da
base que entra, por script versionado. MUST NOT sobreviver no pacote derivado
cuja origem seja a base removida.

#### Scenario: Derivado órfão após substituição

- **GIVEN** uma base removida que tinha derivados versionados
- **WHEN** a substituição é concluída
- **THEN** cada derivado foi regerado a partir da base nova
- **AND** o script que o gera está versionado
- **AND** nenhum derivado remanescente aponta para a base removida

### Requirement: Ausência de referência órfã verificável

Após a substituição, os arquivos de documentação, de checksum e de contagem MUST
NOT referenciar caminho ou soma de verificação da base removida. A ausência SHALL
ser verificável por busca de termo, sem leitura integral dos arquivos.

#### Scenario: Verificação por busca

- **WHEN** o nome da base removida é buscado na documentação do pacote
- **THEN** as ocorrências restantes são apenas as do registro histórico de
  substituição
- **AND** nenhuma ocorrência a apresenta como fonte corrente

### Requirement: Texto transformado declarado e vedado como fonte

Base cujo texto tenha passado por transformação — sumarização, truncamento,
reescrita ou normalização com descarte — SHALL declarar a transformação por
item ou por classe de itens, nomeando qual foi. Texto transformado MUST NOT ser
usado como fonte de trecho citado, e MUST NOT ser apresentado a participante de
teste como o texto que circulou na origem.

Texto produzido por modelo generativo MUST ser identificado como tal onde quer
que apareça, inclusive quando derivado de material autêntico.

#### Scenario: Base com itens sumarizados

- **GIVEN** uma base em que uma das classes teve o texto sumarizado
- **WHEN** a base é incorporada ao pacote
- **THEN** a declaração nomeia qual classe foi transformada e por qual método
- **AND** os itens transformados são identificáveis por consulta
- **AND** a base não consta entre as fontes de trecho citado

#### Scenario: Seleção de estímulo para teste com usuário

- **GIVEN** um item cujo texto foi transformado
- **WHEN** o item é considerado como estímulo
- **THEN** ou o texto exibido é composto de linguagem publicada na origem
- **AND** a transformação sofrida acompanha o registro do estímulo
- **OR** o item é recusado como estímulo, com o motivo registrado

#### Scenario: Texto gerado por modelo no pacote

- **WHEN** texto produzido por modelo generativo entra no pacote
- **THEN** está marcado como gerado, distinto de texto de origem humana
- **AND** MUST NOT ser oferecido como citação nem como estímulo autêntico

### Requirement: Perda declarada quando a substituição destrói seleção anterior

WHEN a substituição invalida uma seleção previamente feita sobre a base antiga,
o registro SHALL declarar o que se perdeu e o que foi refeito. A perda MUST NOT
ficar implícita na regeração.

#### Scenario: Amostra por semente refeita sobre base nova

- **GIVEN** uma amostra versionada, extraída da base antiga com semente fixa
- **WHEN** a base é substituída e a amostra é regerada
- **THEN** o registro declara que a seleção anterior não é reproduzível
- **AND** declara se houve curadoria manual sobre a amostra antiga
- **AND** nomeia o que precisa ser refeito em consequência
