# Delta para selecao-modelo

## Purpose

Tornar a escolha de modelo uma decisão registrada e auditável, decomposta por
papel, para que a fase Act não inicie com infraestrutura escolhida por tentativa
e para que os descartes fiquem disponíveis ao portfólio de pesquisa com o motivo
que os produziu.

## ADDED Requirements

### Requirement: Decisão por papel, não por produto

A seleção SHALL registrar uma escolha para cada um dos três papéis —
recuperação, geração e classificação auxiliar — com o critério que a sustenta.
A seleção MUST NOT registrar um único modelo como resposta para o conjunto dos
papéis sem demonstrar que ele atende ao critério de cada um.

#### Scenario: Inspeção do registro de seleção

- **WHEN** o registro de seleção é inspecionado
- **THEN** os três papéis aparecem nomeados
- **AND** cada papel tem modelo escolhido e critério declarado
- **AND** o critério de recuperação é distinto do critério de geração

#### Scenario: Modelo único proposto para mais de um papel

- **GIVEN** um modelo candidato a cumprir dois papéis
- **WHEN** a seleção é registrada
- **THEN** o registro demonstra o atendimento ao critério de cada papel
  separadamente
- **AND** a economia de operação não é aceita como único motivo

### Requirement: Critério de recuperação ancorado em objetivo de treino

O critério de seleção para o papel de recuperação SHALL ser o desempenho em
tarefa de recuperação em português medido em benchmark público, e MUST NOT ser a
especialização do modelo em língua portuguesa tomada isoladamente.

#### Scenario: Candidato específico de português proposto para recuperação

- **GIVEN** um modelo pré-treinado em português proposto para o papel de
  recuperação
- **WHEN** a seleção é avaliada
- **THEN** o desempenho do candidato em tarefa de recuperação é consultado
- **AND** o candidato é recusado se o desempenho for inferior ao de multilíngue
  ajustado para recuperação
- **AND** a recusa não impede o mesmo candidato de ser escolhido para
  classificação auxiliar

### Requirement: Descarte registrado com motivo verificável

Todo candidato descartado SHALL constar do registro com o motivo do descarte, e
o motivo MUST ser verificável na documentação oficial do candidato ou em spec
deste projeto. Preferência de ferramenta MUST NOT ser aceita como motivo.

#### Scenario: Descarte do MedGemma

- **WHEN** o registro de descarte é inspecionado
- **THEN** o MedGemma consta como descartado
- **AND** constam a modalidade de treino, a limitação de idioma e a ausência de
  avaliação multi-turno, atribuídas ao model card oficial
- **AND** consta a colisão com a task 2.3 de `mvp-copiloto-verificacao`
- **AND** consta que a orientação de usar modelo pronto foi adotada, não
  descartada

### Requirement: Licença conferida antes da adoção

A licença de cada modelo adotado SHALL constar do registro pelo nome, com a
verificação de que permite o uso previsto no challenge. Modelo cuja licença não
tenha sido conferida MUST NOT ser adotado em entregável.

#### Scenario: Candidato sob termos proprietários

- **GIVEN** um candidato distribuído sob termos próprios do fornecedor
- **WHEN** a adoção é avaliada
- **THEN** os termos são lidos e o registro nomeia a licença
- **AND** a restrição encontrada consta do registro
