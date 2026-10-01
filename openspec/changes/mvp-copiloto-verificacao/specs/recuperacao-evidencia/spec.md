# Delta para Recuperação de Evidência

## ADDED Requirements

### Requirement: Corpus e prioridade de idioma

O sistema SHALL indexar checagens em português (FactCenter, recorte de saúde, e
FACTCK.BR) e comunicados de fontes oficiais brasileiras. A recuperação SHALL
esgotar as fontes em português antes de recorrer a fontes em inglês.

#### Scenario: Alegação já checada em português
- **WHEN** existe checagem em PT-BR que cobre a alegação
- **THEN** essa checagem é usada como evidência primária
- **AND** nenhuma fonte em inglês é necessária na camada visível

### Requirement: Rastreabilidade da evidência

Toda afirmação factual da resposta SHALL estar ancorada em um trecho recuperado,
com fonte e data acessíveis. O sistema MUST NOT apresentar afirmação factual sem
trecho de origem.

#### Scenario: Trecho recuperado não sustenta a afirmação
- **WHEN** a síntese produziria afirmação que nenhum trecho recuperado sustenta
- **THEN** a afirmação é removida da resposta
- **AND** o veredito cai para `evidência insuficiente` se ela era essencial

### Requirement: Auditabilidade da tradução

Quando a evidência estiver em inglês, o sistema SHALL exibir a paráfrase em
português na camada visível e SHALL disponibilizar o trecho original em inglês
na camada de detalhe.

#### Scenario: Evidência vinda de texto em inglês
- **WHEN** a única evidência disponível está em inglês
- **THEN** a resposta traz a paráfrase em português
- **AND** o trecho original fica acessível sem sair da conversa

### Requirement: Atribuição às agências de checagem

O sistema SHALL nomear a agência de origem e ligar para a checagem original. O
sistema MUST NOT reproduzir o texto integral da checagem, limitando-se a citação
curta acompanhada de paráfrase.

#### Scenario: Evidência vinda de agência
- **WHEN** a evidência principal é uma checagem de agência
- **THEN** a resposta nomeia a agência e traz o link
- **AND** o texto original não é reproduzido na íntegra

### Requirement: Fontes oficiais aceitas

O sistema SHALL aceitar comunicados e notas técnicas exclusivamente de órgãos
oficiais brasileiros listados em arquivo versionado (`fontes_oficiais.json`):
Ministério da Saúde, Fundação Oswaldo Cruz (Fiocruz) e Agência Nacional de
Vigilância Sanitária (Anvisa), restritos a seus domínios institucionais
auditáveis (`.gov.br` e `.fiocruz.br`).

Comunicados oficiais MUST ser classificados com `tipo_fonte: "comunicado_oficial"`
e MUST NOT portar veredito de agência, servindo exclusivamente como evidência de
orientação científica e sanitária.

#### Scenario: Evidência de órgão oficial homologado
- **WHEN** a evidência recuperada provém de domínio oficial do Ministério da Saúde, Fiocruz ou Anvisa
- **THEN** o sistema atribui o órgão oficial como fonte institucional
- **AND** a informação é indexada como comunicado_oficial sem veredito

#### Scenario: Fonte de esfera não homologada ou domínio comercial
- **WHEN** uma publicação provém de domínio de terceiro ou de órgão governamental fora da lista homologada
- **THEN** o texto não é admitido como comunicado oficial

