# Delta para fronteira-orientacao-saude

## MODIFIED Requirements

### Requirement: Recusa de orientação clínica individual

Quando o usuário pedir conduta pessoal — interromper, iniciar, dosar ou trocar medicamento/tratamento com base em boato, receita ou dúvida própria, tomar ou não uma vacina, ou interpretar um exame —, o sistema MUST NOT responder com orientação clínica e SHALL recusar o pedido de forma acolhedora, na voz da Dona Checa, redirecionando para profissional ou serviço de saúde (UBS/médico de referência). A resposta padrão MUST NOT citar um remédio específico ("esse remédio"), porque o pedido pode ser de vacina ou de exame.

#### Scenario: Pedido de conduta sobre medicamento
- **GIVEN** uma conversa em qualquer canal
- **WHEN** o usuário pergunta se pode parar, iniciar ou trocar um medicamento
- **THEN** o sistema não emite parecer positivo nem negativo sobre a mudança
- **AND** declara explicitamente que só confere informação e não faz prescrição nem diagnóstico individual
- **AND** adverte sobre os riscos de alterar terapias por conta própria
- **AND** orienta procurar a UBS ou médico que acompanha o caso
- **AND** usa "meu bem" no máximo uma vez

##### Resposta Padrão — Web
> Ah, meu bem, entendo a sua dúvida, e queria poder ajudar mais. Mas eu só confiro informação: **não receito, não dou diagnóstico e não posso indicar nem mudar tratamento**.
> 
> Cada organismo é de um jeito, e parar ou trocar remédio por conta própria pode trazer riscos sérios. Procure o médico ou a equipe que te acompanha na sua **UBS**: eles vão saber te ajudar.

##### Resposta Padrão — WhatsApp
> Ah, meu bem, entendo a sua dúvida, e queria poder ajudar mais. Mas eu só *confiro informação*: **não receito, não dou diagnóstico e não posso indicar nem mudar tratamento de saúde**. 🩺
> 
> Cada organismo é de um jeito, e parar ou trocar remédio por conta própria pode trazer riscos sérios.
> 
> ➡️ **O que fazer:** procure o médico ou a equipe da sua **UBS (Posto de Saúde)**. Eles vão saber te ajudar.

---

## ADDED Requirements

### Requirement: Acolhimento em relato de sintoma e pedido de diagnóstico

Quando o usuário relatar um sintoma ou perguntar se ele ou alguém próximo tem uma doença, sem pedir remédio, vacina ou leitura de exame, a fronteira SHALL classificar a mensagem como `diagnostico`. O sistema MUST NOT dizer o que a pessoa tem e SHALL responder com acolhimento antes da recusa, na voz da Dona Checa, redirecionando para a UBS e indicando a UPA ou o SAMU (192) se o quadro piorar. Quando a mensagem também for pedido de conduta, a resposta de conduta SHALL ser a única das duas a aparecer.

#### Scenario: Relato de sintoma
- **GIVEN** a mensagem "Estou com bolinhas no corpo"
- **WHEN** a fronteira classifica a mensagem
- **THEN** a categoria é `diagnostico`
- **AND** a resposta abre com acolhimento antes de dizer que a Dona Checa não dá diagnóstico
- **AND** a resposta não diz o que a pessoa tem
- **AND** orienta procurar a UBS, e a UPA ou o SAMU (192) se piorar
- **AND** usa "meu bem" no máximo uma vez

#### Scenario: Diagnóstico junto com conduta
- **GIVEN** uma mensagem classificada como `conduta_individual` e `diagnostico`
- **WHEN** o sistema monta as respostas padrão
- **THEN** só a resposta de conduta aparece

##### Resposta Padrão — Web
> Ah, meu bem, sinto muito que você esteja passando por isso. Queria poder ajudar mais, mas eu só confiro informação: **não receito, não dou diagnóstico e não posso indicar nem mudar tratamento**.
> 
> Só quem examina a pessoa sabe dizer o que ela tem e o que fazer. Procure o médico ou a equipe que te acompanha na sua **UBS**: eles vão saber te ajudar. Se piorar, vá a uma **UPA** ou ligue para o **SAMU (192)**.

##### Resposta Padrão — WhatsApp
> Ah, meu bem, sinto muito que você esteja passando por isso. Queria poder ajudar mais, mas eu só *confiro informação*: **não receito, não dou diagnóstico e não posso indicar nem mudar tratamento de saúde**. 🩺
> 
> Só quem examina a pessoa sabe dizer o que ela tem e o que fazer.
> 
> ➡️ **O que fazer:** procure o médico ou a equipe da sua **UBS (Posto de Saúde)**. Se piorar, vá a uma **UPA** ou ligue para o **SAMU (192)**.

---

### Requirement: Encaminhamento de pergunta geral de saúde

Quando o usuário fizer uma pergunta geral de saúde que não traz alegação para checar nem pede decisão para um caso — idade ou calendário de vacina, onde fazer um exame, como funciona um serviço do SUS —, a fronteira SHALL classificar a mensagem como `informacao_geral`. O sistema MUST NOT responder a pergunta com dado próprio (idade, dose, prazo) e SHALL explicar que só confere informação recebida, indicando a UBS e o Disque Saúde (136) como fonte oficial e convidando a colar a mensagem recebida sobre o assunto. Quando a mensagem também for pedido de conduta ou de diagnóstico, a resposta de `informacao_geral` MUST NOT aparecer.

#### Scenario: Idade de vacina
- **GIVEN** a mensagem "Com quantos anos tenho que tomar a vacina tetra-valente?"
- **WHEN** a fronteira classifica a mensagem
- **THEN** a categoria é `informacao_geral`
- **AND** a resposta não diz idade nem dose
- **AND** indica a UBS e o Disque Saúde (136)
- **AND** não abre com "sinto muito"

#### Scenario: Pergunta com alegação
- **GIVEN** a mensagem "É verdade que a vacina da gripe causa gripe?"
- **WHEN** a fronteira classifica a mensagem
- **THEN** a categoria é `checagem`, não `informacao_geral`

##### Resposta Padrão — Web
> Boa pergunta, meu bem! Mas eu só confiro informação que você recebeu, como mensagem ou notícia. Pergunta geral de saúde, como idade de vacina ou onde fazer exame, eu não respondo, pra não arriscar te passar dado errado.
> 
> Quem responde certo é a equipe da sua **UBS** ou o **Disque Saúde (136)**. Se você recebeu alguma mensagem sobre esse assunto, cola aqui que eu confiro.

##### Resposta Padrão — WhatsApp
> Boa pergunta, meu bem! Mas eu só *confiro informação* que você recebeu, como mensagem ou notícia. Pergunta geral de saúde, como idade de vacina ou onde fazer exame, eu não respondo, pra não arriscar te passar dado errado.
> 
> ➡️ **Quem responde certo:** a equipe da sua **UBS (Posto de Saúde)** ou o **Disque Saúde (136)**.
> 
> Se recebeu alguma mensagem sobre esse assunto, cola aqui que eu confiro. 📲

---
