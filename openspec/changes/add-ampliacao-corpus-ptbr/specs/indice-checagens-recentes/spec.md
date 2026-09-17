# Delta para indice-checagens-recentes

## Purpose

Permitir que o sistema localize e atribua checagem publicada fora da janela do
acervo, apresentando agência, data, veredito e endereço da fonte, sem
redistribuir o texto jornalístico de terceiro.

## ADDED Requirements

### Requirement: Índice de localização, nunca de citação

Item proveniente do índice MUST NOT ser apresentado como trecho citado, resumo
do conteúdo da checagem ou evidência textual. O sistema SHALL apresentá-lo como
referência, contendo agência, data da checagem, veredito textual da agência e
endereço da publicação original.

#### Scenario: Item do índice apresentado ao usuário

- **GIVEN** uma alegação cuja checagem só existe no índice
- **WHEN** o sistema apresenta o resultado
- **THEN** constam agência, data, veredito textual e endereço da publicação
- **AND** nenhum trecho do texto da checagem é reproduzido
- **AND** o usuário é encaminhado à publicação original para ler o argumento

#### Scenario: Tentativa de uso do índice como fonte de citação

- **GIVEN** um pedido de evidência textual para sustentar uma resposta
- **WHEN** o material disponível é apenas item de índice
- **THEN** o sistema declara que não possui o texto da checagem
- **AND** MUST NOT sintetizar um trecho a partir do título ou do veredito

### Requirement: Veredito atribuído nominalmente à agência

O veredito textual vindo do índice SHALL ser atribuído à agência que o emitiu,
com a grafia da agência preservada. O sistema MUST NOT apresentá-lo como
conclusão própria, e MUST marcar como derivação qualquer normalização para o
vocabulário interno de rótulos.

#### Scenario: Veredito exibido com atribuição

- **WHEN** um veredito de agência é exibido a partir do índice
- **THEN** a agência emissora está nomeada junto ao veredito
- **AND** a grafia original do veredito está preservada
- **AND** o veredito não é apresentado como saída do sistema

#### Scenario: Normalização de vocabulário de agência

- **GIVEN** um veredito de agência mapeado para o vocabulário interno
- **WHEN** o item é exibido
- **THEN** o rótulo normalizado está marcado como derivação
- **AND** o veredito original permanece recuperável

### Requirement: Cobertura do índice medida e declarada

O índice SHALL declarar a data de corte da coleta, a distribuição de itens por
ano e as agências alcançadas. A declaração MUST ser verificável por reexecução
do script de coleta, e o script MUST estar versionado.

#### Scenario: Inspeção da declaração de cobertura do índice

- **WHEN** a declaração de cobertura do índice é inspecionada
- **THEN** consta a data de corte da coleta
- **AND** consta a contagem de itens por ano
- **AND** constam as agências alcançadas, nomeadas

#### Scenario: Reexecução da coleta

- **GIVEN** o script de coleta versionado
- **WHEN** a coleta é reexecutada com os mesmos parâmetros
- **THEN** os parâmetros de consulta usados estão registrados junto ao snapshot
- **AND** a data de corte do novo snapshot é registrada como distinta

### Requirement: Ausência no índice distinguida de ausência no mundo

WHEN uma alegação não encontra correspondência no índice, o sistema SHALL
informar que não houve correspondência no acervo consultado, nomeando seu
alcance. O sistema MUST NOT afirmar que não existe checagem publicada sobre a
alegação.

#### Scenario: Alegação sem correspondência no índice

- **GIVEN** uma alegação sem item correspondente no índice
- **WHEN** o sistema responde
- **THEN** a resposta declara que a busca foi no acervo indexado
- **AND** nomeia a data de corte e as agências alcançadas
- **AND** MUST NOT concluir que a alegação nunca foi checada
