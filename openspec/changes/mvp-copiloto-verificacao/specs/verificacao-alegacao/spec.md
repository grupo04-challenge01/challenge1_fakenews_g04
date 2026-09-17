# Delta para Verificação de Alegação

## ADDED Requirements

### Requirement: Extração da alegação verificável

O sistema SHALL extrair a alegação central de saúde do texto recebido antes de
recuperar qualquer evidência, e SHALL exibir ao usuário qual alegação foi
extraída.

#### Scenario: Mensagem com várias alegações
- **WHEN** o texto recebido contém mais de uma alegação verificável
- **THEN** o sistema seleciona a alegação de saúde de maior risco potencial
- **AND** informa qual alegação está sendo verificada
- **AND** oferece verificar as demais

#### Scenario: Texto sem alegação verificável
- **WHEN** o texto é opinião, desabafo ou não contém afirmação factual de saúde
- **THEN** o sistema explica a diferença entre opinião e alegação verificável
- **AND** não emite veredito

### Requirement: Veredito antes do método

A resposta SHALL abrir com o veredito em no máximo duas frases. O sistema MUST
NOT exigir do usuário qualquer pergunta, cadastro ou etapa intermediária antes
de apresentar o veredito.

#### Scenario: Alegação com checagem existente
- **WHEN** a recuperação retorna checagem que cobre a alegação
- **THEN** a primeira linha da resposta é o veredito
- **AND** a justificativa e o critério vêm depois, na mesma resposta

#### Scenario: Interação reflexiva
- **WHEN** o sistema tem perguntas reflexivas a oferecer ao usuário
- **THEN** essas perguntas aparecem apenas após o veredito
- **AND** respondê-las é opcional

### Requirement: Classificação com incerteza explícita

O sistema SHALL classificar a alegação em exatamente um de quatro rótulos:
`falso`, `verdadeiro`, `verdadeiro fora de contexto ou exagerado`, ou
`evidência insuficiente`. O sistema MUST usar `evidência insuficiente` quando a
recuperação não retornar fonte que cubra a alegação, e MUST NOT emitir veredito
a partir apenas do conhecimento paramétrico do modelo.

#### Scenario: Sem evidência recuperada
- **WHEN** nenhum documento recuperado sustenta ou refuta a alegação
- **THEN** o sistema responde `evidência insuficiente`
- **AND** explica o que especificamente não foi encontrado
- **AND** sugere onde a pessoa pode procurar

#### Scenario: Alegação verdadeira contra-intuitiva
- **WHEN** a alegação soa implausível mas a evidência recuperada a sustenta
- **THEN** o sistema classifica como `verdadeiro`
- **AND** não rebaixa o veredito por implausibilidade aparente

### Requirement: Separação entre tipo de afirmação e valor de verdade

O sistema SHALL decompor a mensagem distinguindo **fato** (afirmação
verificável), **evidência** (o que sustenta a afirmação, e com que força) e
**opinião** (juízo que não se resolve por verificação). A decomposição SHALL
aparecer no bloco 2 da resposta, definido em `resposta-formativa`, e SHALL ser
independente do veredito: o sistema MUST NOT tratar presença de opinião como
indício de falsidade, nem evidência fraca como veredito `falso`.

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
