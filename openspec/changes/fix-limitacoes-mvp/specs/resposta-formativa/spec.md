# Delta para resposta-formativa

## ADDED Requirements

### Requirement: Conferência de sustentação

Depois de montada a resposta, o sistema SHALL conferir, frase por frase, se
as frases dos blocos 1 e 2 são sustentadas pelos trechos das checagens e se as
frases do bloco 3 são sustentadas pela mensagem recebida. Frase sem base MUST
NOT chegar à pessoa: ela sai da resposta e fica registrada. Se o bloco 1 ou o
bloco 2 ficar sem frase do modelo, a resposta SHALL ser rebaixada para a forma
sem evidência. Se a conferência falhar, a resposta SHALL sair como estava, com
a falha registrada.

#### Scenario: Frase que distorce o trecho
- **GIVEN** um trecho que diz que a médica "nem de longe fala em 50% de óbitos"
- **AND** uma resposta com a frase "O número de 50% se refere a casos raros de reação grave"
- **WHEN** a conferência roda
- **THEN** a frase sai da resposta e fica registrada como sem base

#### Scenario: Frase sobre a mensagem que a mensagem não traz
- **GIVEN** uma página sobre a febre amarela sem opinião sobre vacina
- **AND** um bloco 3 que diz que a mensagem "misturava opiniões alarmantes sobre a vacina"
- **WHEN** a conferência roda
- **THEN** a frase sai do bloco 3

#### Scenario: Conferência indisponível
- **GIVEN** o gerador falhando na chamada da conferência
- **WHEN** a resposta é montada
- **THEN** a resposta sai sem a conferência, e o rastro registra a falha
