# Delta para guiding-questions

## ADDED Requirements

### Requirement: Critério de qualidade da guiding question

Uma guiding question MUST ser pesquisável, MUST NOT admitir resposta binária, e
MUST alterar alguma decisão do projeto quando respondida.

Perguntas que não satisfazem os três critérios MUST ser descartadas e o descarte
registrado.

#### Scenario: Pergunta que não muda decisão

- WHEN uma pergunta candidata é avaliada e nenhuma decisão do projeto depende da resposta
- THEN a pergunta é descartada
- AND o descarte é registrado com o motivo

#### Scenario: Pergunta binária reformulada

- WHEN uma pergunta candidata admite resposta sim ou não
- THEN a pergunta é reformulada para uma forma investigativa
- AND a versão original é mantida no registro para rastreabilidade

### Requirement: Rastreabilidade até o brainstorming

Cada guiding question MUST estar associada ao quadro do brainstorming que a
originou: Problema, Público, Específicas, Solução ou Sucesso — os cinco quadros
que existem no board.

Agrupamentos de notas que não geram nenhuma pergunta pesquisável MUST ser
marcados como opinião e removidos do escopo de pesquisa.

#### Scenario: Agrupamento sem pergunta derivada

- WHEN um agrupamento de notas adesivas não produz nenhuma pergunta pesquisável
- THEN o agrupamento é marcado como opinião do grupo
- AND não é levado para a fase Investigate como item de pesquisa

### Requirement: Priorização por impacto e incerteza

As guiding questions MUST ser priorizadas em uma matriz de impacto por
incerteza. Esforço MUST NOT ser usado como eixo nesta fase.

A priorização MUST ocorrer depois da classificação, e GQ classificada como
`fechada` ou `descartada` MUST NOT ser plotada na matriz.

#### Scenario: Abertura da fase Investigate

- WHEN a priorização é concluída
- THEN as perguntas de alto impacto e alta incerteza são marcadas como abertura
  das semanas 2 e 3
- AND as de alto impacto e baixa incerteza são registradas como candidatas a
  escopo de protótipo

### Requirement: Fechamento do backlog na fase Engage

Ao final de 11/09, o backlog MUST conter entre 8 e 12 guiding questions
priorizadas, sendo no mínimo 3 marcadas como abertura do Investigate.

#### Scenario: Backlog abaixo do mínimo

- WHEN o backlog priorizado contém menos de 8 perguntas
- THEN uma nova rodada de divergência é conduzida antes do fechamento da fase
- AND o change não é considerado completo

### Requirement: Classificação da GQ pela fonte que a responde

Cada guiding question MUST receber exatamente uma classificação quanto ao que
responderia a pergunta:

- `dados` — respondível pelos datasets já coletados. O registro MUST nomear o
  arquivo derivado que sustenta a análise.
- `literatura` — respondível por revisão bibliográfica, sem coleta nova.
- `usuario` — respondível apenas por teste com participantes.
- `fechada` — já respondida por decisão registrada. O registro MUST citar a
  capability ou o documento que a fechou.
- `descartada` — falha o critério de qualidade da guiding question.

GQ classificada como `dados` cujo arquivo nomeado não sustente a análise
pretendida MUST ser reclassificada, e MUST NOT ser mantida como `dados` por
conveniência de escopo.

#### Scenario: Pergunta já respondida por decisão registrada

- WHEN uma pergunta candidata já tem resposta em capability aprovada ou em
  decisão registrada de design
- THEN a pergunta é classificada como `fechada`
- AND o registro cita a decisão que a fechou
- AND a pergunta não consome tempo de pesquisa da fase Investigate

#### Scenario: Análise exige campo que nenhum dataset possui

- WHEN a análise pretendida por uma GQ `dados` depende de um campo que nenhum
  dataset coletado contém
- THEN a GQ é reclassificada como `literatura`, `usuario` ou `descartada`
- AND o campo ausente é registrado como caveat do dataset correspondente
