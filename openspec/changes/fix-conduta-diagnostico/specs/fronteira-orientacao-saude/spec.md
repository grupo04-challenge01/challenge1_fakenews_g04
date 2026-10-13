# Delta para fronteira-orientacao-saude

## MODIFIED Requirements

### Requirement: Recusa de orientação clínica individual

Quando o usuário pedir conduta pessoal ou diagnóstico — interromper, iniciar, dosar ou trocar medicamento/tratamento com base em boato, receita ou dúvida própria, interpretar exame ou saber se ele ou alguém próximo tem uma doença —, o sistema MUST NOT responder com orientação clínica nem com diagnóstico e SHALL recusar o pedido de forma acolhedora, na voz da Dona Checa, redirecionando para profissional ou serviço de saúde (UBS/médico de referência). A resposta padrão MUST NOT supor que o pedido é sobre remédio.

#### Scenario: Pedido de conduta sobre medicamento
- **GIVEN** uma conversa em qualquer canal
- **WHEN** o usuário pergunta se pode parar, iniciar ou trocar um medicamento
- **THEN** o sistema não emite parecer positivo nem negativo sobre a mudança
- **AND** declara explicitamente que só confere informação e não faz prescrição nem diagnóstico individual
- **AND** adverte sobre os riscos de alterar terapias por conta própria
- **AND** orienta procurar a UBS ou médico que acompanha o caso
- **AND** usa "meu bem" no máximo uma vez

#### Scenario: Pedido de diagnóstico
- **GIVEN** a mensagem "Estou com bolinhas no corpo"
- **WHEN** a fronteira classifica a mensagem como conduta individual
- **THEN** o sistema não diz o que a pessoa tem
- **AND** a resposta não cita "esse remédio"
- **AND** orienta procurar a UBS ou médico que acompanha o caso

##### Resposta Padrão — Web
> Ah, meu bem, entendo a sua preocupação. Mas eu só confiro informação: não receito, não dou diagnóstico e **não posso indicar nem mudar tratamento**.
> 
> Só quem examina a pessoa sabe dizer o que ela tem e o que fazer. E parar ou trocar remédio por conta própria pode trazer riscos sérios. Converse com o médico ou a equipe que te acompanha na sua **UBS**.

##### Resposta Padrão — WhatsApp
> Ah, meu bem, entendo a preocupação. Mas eu só *confiro informação*: não receito, não dou diagnóstico e **não posso indicar nem mudar tratamento de saúde**. 🩺
> 
> Só quem examina a pessoa sabe dizer o que ela tem. E parar ou trocar remédio por conta própria pode trazer riscos sérios.
> 
> ➡️ **O que fazer:** converse com o médico ou a equipe da sua **UBS (Posto de Saúde)**.

---
