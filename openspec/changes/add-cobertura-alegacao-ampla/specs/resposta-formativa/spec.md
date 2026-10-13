# Delta para resposta-formativa

## ADDED Requirements

### Requirement: Veredito por alegação mais ampla declarado

Quando o veredito `falso` vier de cobertura por alegação mais ampla
(`verificacao-alegacao`), a resposta SHALL seguir a forma com evidência, e o
bloco 1 SHALL abrir com a frase fixa abaixo, posta pelo código e MUST NOT ser
gerada nem reescrita pelo modelo. A frase conta no teto de palavras da camada
visível (`acessibilidade-leitura`). O bloco 1 SHALL dizer, em seguida, qual
alegação mais geral foi checada. O detalhe da resposta SHALL trazer, para cada
checagem citada, a alegação que a agência checou, com o texto literal da
agência, ao lado da agência, da data, do link e do veredito da agência. O
detalhe SHALL trazer também a ponte declarada no veredito.

Veredito de cobertura da mesma alegação MUST NOT usar essa abertura.

##### Texto — abertura_ampla
> Falso. Não achamos checagem desta versão, mas a ideia mais geral por trás dela já foi checada como falsa.

#### Scenario: Jacaré
- **GIVEN** o veredito `falso` por cobertura ampla para "Vacina de Covid-19 transformam pessoas em jacarés"
- **WHEN** a resposta é montada
- **THEN** o bloco 1 começa com a frase fixa `abertura_ampla`
- **AND** o bloco 1 diz qual alegação mais geral foi checada
- **AND** o detalhe traz a alegação checada por cada agência, literal, e a ponte

#### Scenario: Cobertura da mesma alegação
- **GIVEN** o veredito `falso` com checagem da mesma alegação
- **WHEN** a resposta é montada
- **THEN** o bloco 1 começa com "Falso." e não com a frase `abertura_ampla`

#### Scenario: Resposta rebaixada depois de montada
- **GIVEN** uma resposta de cobertura ampla rebaixada para a forma sem evidência pela ancoragem ou pela conferência de sustentação
- **WHEN** a resposta é montada de novo
- **THEN** a frase `abertura_ampla` não aparece
