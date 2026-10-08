# Delta para resposta-formativa

## MODIFIED Requirements

### Requirement: Ausência de reforço do mito

O sistema MUST NOT abrir a resposta repetindo a alegação falsa como afirmação
isolada, e SHALL marcá-la explicitamente como falsa sempre que precisar citá-la.
Negar explicitamente que exista evidência da alegação ("nenhum estudo mostra
que…", "a checagem não encontrou prova de que…") SHALL contar como marcação,
assim como dizer que a fonte da alegação foi retratada ou que a mensagem a
tirou de contexto.
Atribuir a alegação à mensagem sem negá-la ("a mensagem promete…") MUST NOT
contar como marcação.

#### Scenario: Citação da alegação falsa
- **WHEN** a resposta precisa mencionar o conteúdo da mensagem falsa
- **THEN** a menção vem acompanhada da marcação de que é falsa
- **AND** a afirmação correta aparece antes e depois da menção

#### Scenario: Negação da evidência como marcação
- **GIVEN** a alegação falsa "chá de boldo cura hepatite"
- **WHEN** a resposta diz "Nenhum estudo mostra que chá de boldo cura hepatite"
- **THEN** a menção conta como marcada

#### Scenario: Atribuição sem negação
- **GIVEN** a alegação falsa "chá de goiabeira cura dengue em 24 horas"
- **WHEN** a resposta diz "A mensagem promete curar dengue em 24 horas"
- **THEN** a menção conta como não marcada
