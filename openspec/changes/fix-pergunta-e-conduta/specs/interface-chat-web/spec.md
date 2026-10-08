# Delta para Interface de Chat Web

## MODIFIED Requirements

### Requirement: Mensagem sem alegação de saúde

Quando a extração não achar alegação de saúde verificável, a página SHALL
responder com o texto abaixo, sem bordão. Quando a fronteira tiver
classificado a mensagem como pedido de conduta individual, a página SHALL
mostrar o texto de conduta da fronteira no lugar do texto abaixo.

##### Texto — sem_alegacao
> Meu bem, não achei nessa mensagem nada de saúde pra conferir. Assunto fora da saúde eu não sei responder. Se tiver algo de saúde aí, cola aqui o trecho que te deixou na dúvida.

#### Scenario: Mensagem sem saúde
- **GIVEN** uma mensagem sobre futebol
- **WHEN** o fluxo para na extração
- **THEN** a página mostra o texto `sem_alegacao` da spec

#### Scenario: Pedido de conduta sem alegação
- **GIVEN** a mensagem "Cortei o pé com uma enxada, o que devo fazer?"
- **WHEN** a fronteira classifica como conduta individual e o fluxo para na extração
- **THEN** a página mostra o texto de conduta da fronteira
- **AND** o texto `sem_alegacao` não aparece
