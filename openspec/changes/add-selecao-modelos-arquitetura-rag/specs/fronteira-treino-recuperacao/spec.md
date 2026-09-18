# Delta para fronteira-treino-recuperacao

## Purpose

Separar o que o sistema pode aprender em peso do que precisa vir de trecho
recuperado, para que a mescla entre fine-tuning e RAG seja uma decisão de
arquitetura e não uma erosão silenciosa da auditabilidade exigida por
`openspec/project.md`.

## ADDED Requirements

### Requirement: Conhecimento factual reside na recuperação

Afirmação factual sobre alegação de saúde SHALL ter origem em trecho recuperado.
Conhecimento factual sobre o domínio MUST NOT ser introduzido por treino de
pesos, seja por fine-tuning, seja por escolha de modelo cuja especialização de
domínio substitua a recuperação.

#### Scenario: Ganho de acurácia proposto por fine-tuning factual

- **GIVEN** uma proposta de fine-tuning com pares de alegação e veredito
- **WHEN** a proposta é avaliada
- **THEN** a proposta é recusada
- **AND** o motivo registrado é a perda de rastreabilidade até a fonte
- **AND** o ganho de acurácia não é aceito como compensação

#### Scenario: Modelo especializado no domínio proposto como atalho

- **GIVEN** um modelo cuja especialização de domínio permitiria responder sem
  recuperar
- **WHEN** a adoção é avaliada
- **THEN** a capacidade de responder sem recuperar é registrada como risco, não
  como vantagem
- **AND** a guarda da task 2.3 de `mvp-copiloto-verificacao` permanece exigida

### Requirement: Treino de pesos limitado a comportamento

Fine-tuning SHALL ser admitido apenas para forma de resposta, vocabulário fechado
do catálogo de técnicas, recusa de conduta clínica e nível de leitura. Fine-tuning
de classificador de veredito MUST NOT ser realizado, em qualquer rótulo e sobre
qualquer dataset.

#### Scenario: Dataset de rótulo binário proposto como alvo de treino

- **GIVEN** um dataset de rótulo binário presente em `datasets/`
- **WHEN** o uso como alvo de treino é proposto
- **THEN** o uso é recusado
- **AND** o dataset permanece disponível como banco de estímulos

#### Scenario: Fine-tuning de classificador auxiliar

- **GIVEN** a proposta de treinar o detector de pedido de conduta clínica da task
  4.1 de `mvp-copiloto-verificacao`
- **WHEN** a proposta é avaliada
- **THEN** o treino é admitido por classificar comportamento e não valor de
  verdade
- **AND** a admissão fica condicionada à medição prévia do desempenho por prompt

### Requirement: Linha de base sem treino antes de qualquer treino

O projeto SHALL dispor de versão executável sem nenhum fine-tuning, com
desempenho medido, antes de iniciar qualquer treino de pesos. Treino iniciado sem
essa medição MUST NOT ser incorporado ao entregável.

#### Scenario: Treino proposto antes da linha de base

- **WHEN** um fine-tuning é proposto e a linha de base sem treino ainda não foi
  medida
- **THEN** o treino é adiado
- **AND** a medição da linha de base é registrada como pré-requisito

### Requirement: Fronteira auditável na resposta

Para qualquer resposta emitida, SHALL ser possível identificar qual afirmação veio
de trecho recuperado. Afirmação factual sem trecho identificável MUST ser
removida, conforme `recuperacao-evidencia`.

A auditoria percorre a resposta inteira, camada visível e camada de detalhe. O
vínculo entre afirmação e trecho MUST existir sempre, mas MUST NOT ser exibido
na camada visível: sua apresentação obedece à revelação progressiva de
`resposta-formativa`. Rastreabilidade é propriedade do sistema; exibição é
decisão de interface.

#### Scenario: Auditoria de resposta emitida

- **GIVEN** uma resposta já emitida pelo sistema
- **WHEN** a auditoria percorre suas afirmações factuais
- **THEN** cada uma tem trecho de origem identificável
- **AND** afirmação sem trecho é reportada como defeito, não como estilo

#### Scenario: Vínculo existente mas não exibido

- **GIVEN** uma afirmação factual na camada visível
- **WHEN** o usuário não acionou a camada de detalhe
- **THEN** o trecho de origem não aparece na camada visível
- **AND** o vínculo continua registrado e recuperável pela auditoria
