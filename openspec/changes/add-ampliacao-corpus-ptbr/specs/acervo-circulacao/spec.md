# Delta para acervo-circulacao

## Purpose

Definir o que o projeto pode e o que não pode afirmar a partir de corpus de
conteúdo publicado por usuários, sem rótulo de veracidade, de modo que material
que atesta **difusão** nunca seja lido como material que atesta **fato**.

A capability nasce com o corpus de Telegram antivacina (jan/2020 a jun/2025,
CC BY-NC 4.0, DOI `10.25824/redu/5JIVDT`), mas os requisitos valem para qualquer
base de conteúdo de usuário que entre no pacote depois.

## ADDED Requirements

### Requirement: Conteúdo de usuário atesta circulação, não o fato

Item de acervo de circulação SHALL ser tratado como evidência de que um conteúdo
foi publicado, por qual canal e em qual data. MUST NOT ser apresentado como
evidência sobre a veracidade da alegação que veicula, nem como fonte de trecho
citado sobre o mérito.

O sistema PODE informar que uma narrativa circulou, com canal e data, desde que
a afirmação se limite à circulação.

#### Scenario: Alegação encontrada no acervo de circulação

- **GIVEN** uma alegação do usuário cujo teor aparece em itens do acervo de
  circulação
- **WHEN** o sistema compõe a resposta
- **THEN** informa que conteúdo semelhante circulou, com período e tipo de canal
- **AND** declara que a circulação não é evidência sobre a veracidade
- **AND** MUST NOT oferecer o item como fonte de trecho citado sobre o mérito

#### Scenario: Acervo de circulação como única correspondência

- **GIVEN** uma alegação sem correspondência no acervo com texto integral nem no
  índice de localização
- **AND** com correspondência no acervo de circulação
- **WHEN** o sistema responde
- **THEN** a resposta MUST NOT ser apresentada como verificação
- **AND** a lacuna de checagem permanece declarada conforme `frescor-corpus`

### Requirement: Proibição de veredito por proxy de canal

A origem de um item — canal, grupo, plataforma ou orientação editorial da fonte
— MUST NOT ser usada como fundamento de veredito de verdadeiro ou falso, nem
isolada nem como sinal ponderado em classificação de veracidade.

Quando a origem for apresentada ao usuário, SHALL vir nomeada como informação de
procedência, acompanhada da afirmação explícita de que procedência não determina
veracidade.

#### Scenario: Item proveniente de canal de desinformação conhecida

- **GIVEN** um item cujo canal de origem é reconhecidamente antivacina
- **WHEN** o sistema avalia a alegação que o item veicula
- **THEN** o veredito é sustentado em evidência sobre a alegação
- **AND** MUST NOT ser sustentado no canal de origem
- **AND** a menção ao canal, se houver, declara que não determina veracidade

#### Scenario: Conteúdo verdadeiro em canal de desinformação

- **GIVEN** uma alegação verdadeira que circulou em canal antivacina
- **WHEN** o sistema a avalia
- **THEN** a avaliação não é rebaixada por causa do canal

### Requirement: Rótulo derivado por modelo declarado como derivado

Campo de rótulo produzido por modelo, e não por anotação humana, SHALL ser
declarado como derivado onde quer que apareça, nomeando o modelo, o método e a
métrica de validação com o tamanho da amostra sobre a qual foi medida.

Rótulo derivado PODE ser usado como filtro de recorte. MUST NOT ser usado como
verdade sobre o item, nem agregado a rótulo de anotação humana sem que a origem
de cada um permaneça recuperável.

#### Scenario: Filtro de recorte por rótulo derivado

- **GIVEN** o campo `is_vaccine_related`, produzido por modelo com F1 de 0,90
  medido sobre 600 posts anotados
- **WHEN** o campo é usado para recortar o subconjunto de trabalho
- **THEN** o uso é declarado como recorte aproximado
- **AND** a taxa de erro medida e o tamanho da amostra de validação constam da
  documentação da base
- **AND** o campo MUST NOT ser apresentado como classificação verificada do item

#### Scenario: Combinação com anotação humana

- **GIVEN** rótulo derivado por modelo e rótulo de anotador humano no mesmo
  pacote
- **WHEN** ambos alimentam uma mesma análise
- **THEN** a origem de cada rótulo permanece recuperável por consulta
- **AND** a análise MUST NOT tratá-los como de mesma força probatória

### Requirement: Pseudonimização preservada e não revertida

A pseudonimização aplicada na origem SHALL ser preservada em todo derivado. O
projeto MUST NOT tentar reverter identificadores, cruzar o acervo com outras
bases para re-identificar autores, nem publicar texto de post individual
atribuível a uma conta.

Derivado versionado em repositório público SHALL ser agregado — contagem,
distribuição ou frequência de termo. Texto integral de post MUST NOT ser
versionado.

#### Scenario: Geração de derivado para o repositório público

- **WHEN** um derivado do acervo de circulação é gerado para versionamento
- **THEN** o derivado contém agregados, não texto de post individual
- **AND** o bruto permanece fora do git, reconstituível por checksum a partir da
  fonte primária

#### Scenario: Tentativa de exibir post individual ao usuário

- **GIVEN** um post individual do acervo de circulação
- **WHEN** ele é considerado para exibição ao usuário ou a participante de teste
- **THEN** é recusado, ou exibido sem identificador de autor e sem canal
  nominal, com o motivo registrado

### Requirement: Viés de amostra declarado e leitura de prevalência vedada

O acervo de circulação descreve o ecossistema de onde foi coletado, não a
população. A documentação da base SHALL declarar o critério de seleção dos
canais e o viés que ele produz.

Nenhum artefato do projeto MUST afirmar prevalência, alcance populacional ou
tendência de opinião pública a partir deste acervo.

#### Scenario: Leitura quantitativa do acervo

- **GIVEN** uma contagem obtida sobre o acervo de circulação
- **WHEN** ela é apresentada em qualquer artefato do projeto
- **THEN** vem acompanhada do critério de seleção dos canais
- **AND** é declarada como relativa ao conjunto coletado
- **AND** MUST NOT ser apresentada como estimativa sobre a população brasileira

#### Scenario: Lacuna conhecida da coleta

- **GIVEN** métricas ausentes por limitação declarada pelos autores, como
  reações anteriores a 30/12/2021, canais apagados durante a coleta e mensagens
  removidas por decisão judicial
- **WHEN** séries temporais são construídas sobre o acervo
- **THEN** as lacunas constam declaradas junto da série
- **AND** MUST NOT ser lidas como ausência do fenômeno no período

### Requirement: Restrição não comercial propagada

A base entra sob CC BY-NC 4.0. A restrição SHALL ser propagada a todo derivado e
declarada onde o derivado for publicado, incluindo a atribuição exigida pela
licença.

#### Scenario: Publicação de derivado

- **WHEN** um derivado do acervo de circulação é publicado ou apresentado
- **THEN** a atribuição aos autores e o DOI da fonte constam
- **AND** a cláusula não comercial consta declarada
