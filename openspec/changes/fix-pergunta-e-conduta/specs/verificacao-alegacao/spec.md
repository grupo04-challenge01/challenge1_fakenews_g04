# Delta para verificacao-alegacao

## MODIFIED Requirements

### Requirement: Extração da alegação verificável

O sistema SHALL extrair a alegação central de saúde do texto recebido antes de
recuperar qualquer evidência, e SHALL exibir ao usuário qual alegação foi
extraída. A extração SHALL listar no máximo 8 alegações, as de saúde primeiro,
e saída com defeito SHALL ter uma nova tentativa, com o defeito informado ao
modelo, antes de virar erro. Pergunta que traz uma afirmação SHALL ter a
afirmação como alegação; pergunta sem afirmação MUST NOT virar alegação.

#### Scenario: Mensagem com várias alegações
- **WHEN** o texto recebido contém mais de uma alegação verificável
- **THEN** o sistema seleciona a alegação de saúde de maior risco potencial
- **AND** informa qual alegação está sendo verificada
- **AND** oferece verificar as demais

#### Scenario: Texto sem alegação verificável
- **WHEN** o texto é opinião, desabafo ou não contém afirmação factual de saúde
- **THEN** o sistema explica a diferença entre opinião e alegação verificável
- **AND** não emite veredito

#### Scenario: Página com muitas alegações
- **GIVEN** uma página com mais de 20 afirmações, de saúde e de outros assuntos
- **WHEN** a extração roda
- **THEN** a lista tem no máximo 8 alegações
- **AND** uma primeira saída cortada antes do fim do JSON tem uma nova tentativa

#### Scenario: Alegação em forma de pergunta
- **GIVEN** a mensagem "Suco detox cura gripe?"
- **WHEN** a extração roda
- **THEN** a alegação selecionada é "Suco detox cura gripe." ou equivalente
- **AND** a verificação segue para a recuperação
