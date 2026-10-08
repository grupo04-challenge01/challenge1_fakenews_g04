# Delta para verificacao-alegacao

## MODIFIED Requirements

### Requirement: Extração da alegação verificável

O sistema SHALL extrair a alegação central de saúde do texto recebido antes de
recuperar qualquer evidência, e SHALL exibir ao usuário qual alegação foi
extraída. A extração SHALL listar no máximo 8 alegações, as de saúde primeiro,
e saída com defeito SHALL ter uma nova tentativa, com o defeito informado ao
modelo, antes de virar erro.

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

### Requirement: Separação entre tipo de afirmação e valor de verdade

O sistema SHALL decompor a mensagem distinguindo **fato** (afirmação
verificável), **evidência** (o que sustenta a afirmação, e com que força) e
**opinião** (juízo que não se resolve por verificação). A decomposição SHALL
aparecer no bloco 2 da resposta, definido em `resposta-formativa`, e SHALL ser
independente do veredito: o sistema MUST NOT tratar presença de opinião como
indício de falsidade, nem evidência fraca como veredito `falso`. Pergunta ou
exclamação de quem mandou a mensagem MUST NOT entrar como fato, opinião ou
conclusão. Decomposição com defeito SHALL ter uma nova tentativa, com os
defeitos informados ao modelo, antes de virar erro.

#### Scenario: Mensagem que mistura os três
- **WHEN** a mensagem combina fato verificável, evidência frágil e opinião no
  mesmo texto
- **THEN** o sistema mostra qual parte é fato, qual é a evidência apresentada e
  qual é opinião
- **AND** verifica apenas a parte factual
- **AND** explica que a parte de opinião não é objeto de verificação

#### Scenario: Fato verdadeiro sustentando conclusão que não decorre
- **WHEN** a mensagem apoia-se em fato verdadeiro para concluir algo que a
  evidência não sustenta
- **THEN** o sistema confirma o fato
- **AND** aponta que o salto está entre a evidência e a conclusão, não no fato
- **AND** não classifica a mensagem inteira como `verdadeiro`

#### Scenario: Pergunta de quem mandou
- **GIVEN** a mensagem "Absurdo: enterraram uma menina em caixão lacrado como covid e depois o exame deu negativo. Isso é verdade?"
- **WHEN** a decomposição roda
- **THEN** "Isso é verdade?" não aparece em fatos, opiniões nem conclusão

#### Scenario: Nova tentativa
- **GIVEN** uma primeira saída com opinião repetida como fato
- **WHEN** a decomposição roda
- **THEN** o modelo recebe um segundo pedido com o defeito listado
- **AND** a segunda saída sem defeito é usada
