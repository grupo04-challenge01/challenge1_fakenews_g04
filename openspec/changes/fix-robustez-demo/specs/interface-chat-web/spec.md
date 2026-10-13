# Delta para interface-chat-web

## ADDED Requirements

### Requirement: Gerador local com tempo-limite

Cada chamada ao gerador `ollama` SHALL ter tempo-limite. Chamada que estoura o
tempo-limite SHALL falhar com erro do gerador, a página SHALL receber a
mensagem de erro, e o servidor SHALL aceitar o pedido seguinte sem reinício.

#### Scenario: Gerador local preso
- **GIVEN** o servidor com gerador `ollama`
- **AND** uma chamada ao modelo que não responde dentro do tempo-limite
- **WHEN** a verificação roda
- **THEN** a página recebe a mensagem de erro
- **AND** o pedido seguinte é atendido
