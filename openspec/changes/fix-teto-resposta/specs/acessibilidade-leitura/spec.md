# Delta para acessibilidade-leitura

## MODIFIED Requirements

### Requirement: Legibilidade da camada visível

A camada visível da resposta SHALL ter no máximo 120 palavras, frases de até 20
palavras e nenhum termo técnico sem tradução imediata entre parênteses. O
sistema MUST NOT usar jargão metodológico (por exemplo "revisão por pares",
"evidência preliminar") sem explicação em linguagem cotidiana. Quando a
resposta do modelo passar de 120 palavras, o sistema SHALL tirar frases do fim
dos blocos 3 e 4, mantendo pelo menos uma em cada, e MUST NOT cortar os blocos
1 e 2.

#### Scenario: Evidência escrita em linguagem técnica
- **WHEN** o trecho recuperado usa vocabulário científico
- **THEN** a camada visível reescreve o conteúdo em linguagem cotidiana
- **AND** o termo técnico permanece disponível na camada de detalhe

#### Scenario: Resposta acima do teto
- **GIVEN** uma resposta de 126 palavras com três frases no bloco 4
- **WHEN** a resposta é montada
- **THEN** a camada visível tem no máximo 120 palavras
- **AND** os blocos 1 e 2 ficam iguais
- **AND** as frases tiradas ficam registradas no rastro

#### Scenario: Corte que tiraria a afirmação correta
- **GIVEN** uma resposta acima do teto em que a última frase do bloco 4 é a única afirmação correta depois da menção ao mito
- **WHEN** a resposta é montada
- **THEN** a resposta sai sem corte, com o defeito de tamanho registrado
