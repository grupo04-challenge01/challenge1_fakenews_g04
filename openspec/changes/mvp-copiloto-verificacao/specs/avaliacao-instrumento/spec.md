# Delta para Instrumento de Avaliação

## ADDED Requirements

### Requirement: Conjunto local de avaliação

O projeto SHALL manter um conjunto curado de 20 a 30 casos, com itens falsos
extraídos de checagens brasileiras e itens verdadeiros extraídos de fontes
oficiais e de divulgação científica. O conjunto SHALL incluir no mínimo quatro
itens verdadeiros contra-intuitivos. Itens verdadeiros MUST NOT vir de agências
de checagem.

#### Scenario: Montagem do conjunto
- **WHEN** o conjunto é fechado para uso em teste
- **THEN** cada item registra origem, veredito de referência e justificativa
- **AND** a proporção entre verdadeiros e falsos está documentada

### Requirement: Itens-armadilha para medir aceitação cega

De 4 a 6 itens SHALL ser configurados para que a saída da IA apresente evidência
ambígua ou dedução incorreta, com o objetivo de medir a taxa de aceitação cega.
Esses itens MUST ser usados apenas em sessão supervisionada com consentimento
prévio e debriefing.

#### Scenario: Item-armadilha em sessão de teste
- **WHEN** o participante recebe um item cuja saída da IA está errada
- **THEN** registra-se se ele aceitou, questionou ou consultou fonte externa
- **AND** o gabarito é apresentado no debriefing ao fim da sessão

### Requirement: Métricas de resultado e de guarda

O protocolo SHALL medir discernimento (acerto com a ferramenta), transferência
(acerto nos itens finais, sem a ferramenta), tempo até decisão fundamentada e
consulta a fonte externa. SHALL medir também as guardas: aceitação cega quando a
IA erra, falso positivo em conteúdo legítimo, queda de confiança em fonte
confiável e abandono por atrito.

#### Scenario: Bloco de transferência
- **WHEN** o participante chega ao bloco final da sessão
- **THEN** os itens são apresentados sem acesso à ferramenta
- **AND** o acerto nesse bloco é reportado separadamente

### Requirement: Protocolo ético

Toda sessão de teste SHALL ser precedida de Termo de Consentimento Livre e
Esclarecido e SHALL terminar com debriefing em que o participante recebe o
gabarito de todos os itens falsos a que foi exposto. Com participantes idosos, o
protocolo MUST ser submetido ao comitê de ética antes da coleta.

#### Scenario: Encerramento de sessão
- **WHEN** a sessão termina
- **THEN** o participante recebe o gabarito de cada item falso apresentado
- **AND** o registro do debriefing é arquivado com os dados da sessão
