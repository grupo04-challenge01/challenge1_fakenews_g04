# Delta para arquitetura-recuperacao

## Purpose

Fixar como a recuperação é construída, em complemento a `recuperacao-evidencia`,
que define o que ela precisa entregar, para que a linha de base não seja
subdimensionada em recall nem superdimensionada em infraestrutura.

## ADDED Requirements

### Requirement: Recuperação híbrida como linha de base

A recuperação SHALL combinar busca léxica e busca densa desde a primeira versão
executável, com fusão de listas. Versão apenas densa MUST NOT ser tratada como
linha de base aceitável.

#### Scenario: Consulta com nome próprio de baixa frequência

- **GIVEN** uma alegação que menciona termo raro no corpus, como nome comercial
  de vacina ou de medicamento
- **WHEN** a recuperação é executada
- **THEN** a busca léxica participa do resultado
- **AND** o termo não depende de vizinhança semântica para ser recuperado

#### Scenario: Proposta de simplificar para apenas denso

- **WHEN** a remoção da busca léxica é proposta
- **THEN** a proposta é acompanhada de medição de recall nas duas configurações
- **AND** a remoção é recusada se o recall cair

### Requirement: Índice dimensionado à escala real do corpus

A escolha da estrutura de índice SHALL declarar o número de unidades indexadas
que a sustenta. Enquanto o corpus permanecer na ordem de milhares de unidades, a
busca SHALL ser exata, e serviço externo de banco vetorial MUST NOT ser
introduzido sem medição que demonstre necessidade.

#### Scenario: Inspeção da decisão de índice

- **WHEN** a decisão de índice é inspecionada
- **THEN** consta a contagem de unidades indexadas
- **AND** consta que a busca é exata, não aproximada
- **AND** consta a condição de reabertura da decisão por crescimento do corpus

### Requirement: Unidade de indexação preserva proveniência

A unidade indexada SHALL ser a alegação com seu veredito e sua justificativa, e
SHALL carregar agência de origem, data e endereço da checagem. Fragmentação por
tamanho fixo que separe a alegação do seu veredito MUST NOT ser usada.

#### Scenario: Checagem longa excede o tamanho de fragmento

- **GIVEN** uma checagem cujo texto excede o tamanho de fragmento adotado
- **WHEN** a unidade de indexação é construída
- **THEN** a alegação permanece junto do veredito que a resolve
- **AND** agência, data e endereço acompanham cada fragmento gerado

#### Scenario: Indexação não autoriza reprodução

- **GIVEN** uma checagem indexada com seu texto integral
- **WHEN** a evidência dela é usada em uma resposta
- **THEN** a resposta traz citação curta acompanhada de paráfrase, conforme
  `recuperacao-evidencia`
- **AND** a disponibilidade do texto integral no índice não é tratada como
  autorização para reproduzi-lo ao usuário

#### Scenario: Registro que cobre mais de uma alegação

- **GIVEN** um registro do corpus com mais de uma alegação, conforme
  `normalizacao-rotulos`
- **WHEN** a indexação é executada
- **THEN** cada alegação gera unidade própria
- **AND** nenhuma unidade recebe veredito de alegação diferente da sua

### Requirement: Limiar calibrado sobre o score fundido

O limiar de `evidência insuficiente` SHALL ser calibrado sobre o score resultante
da fusão das listas, com conjunto de casos de calibração declarado. O limiar MUST
NOT ser fixado por similaridade de cosseno bruta nem por valor adotado sem
medição.

#### Scenario: Inspeção da calibração

- **WHEN** a calibração do limiar é inspecionada
- **THEN** constam os casos usados e a decisão esperada em cada um
- **AND** constam casos de pauta ausente do corpus, conforme `frescor-corpus`
- **AND** o valor do limiar é reproduzível a partir dos casos declarados
