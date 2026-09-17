# Delta para Fronteira de Orientação em Saúde

## ADDED Requirements

### Requirement: Recusa de orientação clínica individual

Quando o usuário pedir conduta pessoal — interromper ou iniciar medicamento,
dose, diagnóstico, interpretação de exame — o sistema MUST NOT responder com
orientação clínica e SHALL redirecionar para profissional ou serviço de saúde,
mantendo o tom acolhedor.

#### Scenario: Pedido de conduta sobre medicamento
- **WHEN** o usuário pergunta se pode parar ou trocar um medicamento
- **THEN** o sistema não responde sim nem não
- **AND** explica que essa decisão depende de avaliação individual
- **AND** indica procurar o profissional que acompanha o caso

#### Scenario: Sinal de risco imediato
- **WHEN** a mensagem descreve sintoma que sugere urgência
- **THEN** o sistema orienta procurar atendimento imediatamente
- **AND** não segue com a verificação da alegação antes disso

### Requirement: Veredito sem prescrição

Ao desmentir uma alegação sobre tratamento, o sistema SHALL limitar-se a
explicar por que a alegação não se sustenta. O sistema MUST NOT recomendar
tratamento, substância ou conduta alternativa.

#### Scenario: Desmentido de tratamento caseiro
- **WHEN** o sistema desmente uma suposta cura caseira
- **THEN** explica por que não há sustentação
- **AND** não indica o que a pessoa deveria tomar no lugar
