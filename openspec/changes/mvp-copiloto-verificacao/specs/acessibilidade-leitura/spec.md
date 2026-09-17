# Delta para Acessibilidade e Legibilidade

## ADDED Requirements

### Requirement: Legibilidade da camada visível

A camada visível da resposta SHALL ter no máximo 120 palavras, frases de até 20
palavras e nenhum termo técnico sem tradução imediata entre parênteses. O
sistema MUST NOT usar jargão metodológico (por exemplo "revisão por pares",
"evidência preliminar") sem explicação em linguagem cotidiana.

#### Scenario: Evidência escrita em linguagem técnica
- **WHEN** o trecho recuperado usa vocabulário científico
- **THEN** a camada visível reescreve o conteúdo em linguagem cotidiana
- **AND** o termo técnico permanece disponível na camada de detalhe

### Requirement: Requisitos verificáveis de interface

A interface SHALL cumprir: contraste mínimo de 4,5:1 para texto, fonte base de
no mínimo 18px e responsiva ao ajuste de tamanho do sistema, alvo de toque de
no mínimo 44px, e uma única ação primária por tela.

#### Scenario: Usuário com fonte ampliada no sistema
- **WHEN** o dispositivo está com fonte ampliada
- **THEN** o texto acompanha o ajuste sem corte nem sobreposição
- **AND** a ação primária continua alcançável sem rolagem horizontal

### Requirement: Entrada sem barreira

O sistema SHALL aceitar texto colado ou encaminhado e link como entrada, e MUST
NOT exigir cadastro, login ou preenchimento de formulário antes da primeira
verificação.

#### Scenario: Primeira verificação
- **WHEN** uma pessoa usa o sistema pela primeira vez
- **THEN** colar a mensagem é suficiente para receber a resposta
- **AND** nenhum dado pessoal é solicitado
