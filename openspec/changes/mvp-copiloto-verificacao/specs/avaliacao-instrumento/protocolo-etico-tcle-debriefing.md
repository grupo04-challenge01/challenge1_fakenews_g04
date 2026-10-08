# Protocolo Ético, TCLE e Roteiro de Debriefing

**Projeto:** Copiloto de Verificação de Desinformação em Saúde  
**Task de Referência:** 6.3 (R1 Business Stakeholder — Breno)  
**Especificação Relacionada:** `openspec/changes/mvp-copiloto-verificacao/specs/avaliacao-instrumento/spec.md`  
**Conformidade:** Resolução CNS nº 510/2016 e nº 466/2012 (Conep/MS) | LGPD (Lei nº 13.709/2018)  
**Data da Versão:** 29/09/2026  

---

## 1. Contexto e Justificativa Ética

O teste do copiloto de verificação com usuários humanos (em especial com o público idoso, prioritário na vulnerabilidade à desinformação em saúde) envolve a exposição controlada a alegações de saúde falsas ou manipuladas, além de **4 a 6 itens-armadilha** (onde a IA intencionalmente fornece deduções incorretas ou ambíguas para aferir a taxa de aceitação cega e dependência cognitiva).

Por envolver desinformação em temas de saúde (vacinas, tratamentos farmacológicos, doenças crônicas e nutrição), a metodologia exige salvaguardas rígidas:
1. **Consentimento esclarecido prévio** sobre a natureza do teste e sobre a presença de simulações com falhas programadas.
2. **Ambiente estritamente supervisionado** (presencial ou teleconferência síncrona com pesquisador).
3. **Debriefing educacional obrigatório e imediato** ao final de cada sessão, garantindo a neutralização de qualquer crença errônea antes da liberação do participante.
4. **Privacidade garantida por design:** inferência e métricas processadas sem trânsito de dados pessoais por provedores externos de API comercial (conformidade com Decisão 8 do RAG).

---

## 2. Termo de Consentimento Livre e Esclarecido (TCLE)

*(Formato padrão para leitura e assinatura física ou digital na Plataforma Brasil)*

### TÍTULO DO PROJETO DE PESQUISA
**Avaliação de Usabilidade e Impacto Formativo de Assistente de Inteligência Artificial para Checagem de Informações de Saúde**

### IDENTIFICAÇÃO DOS PESQUISADORES
- **Equipe de Pesquisa:** Grupo 04 — Residência em Inteligência Artificial
- **Pesquisador Responsável (Contato do Participante):** Breno / Equipe Grupo 04
- **E-mail de Contato:** `pesquisa.saude.g04@projeto-ia.org` / Telefone institucional: `(XX) XXXX-XXXX`
- **Instituição Proponente:** Programa de Residência em Inteligência Artificial / Desafio 1 Fake News em Saúde

---

### INFORMAÇÕES AO PARTICIPANTE

Você está sendo convidado(a) a participar, como voluntário(a), de uma pesquisa científica aplicada. Antes de decidir, leia atentamente as informações a seguir. A equipe de pesquisadores está à disposição para esclarecer qualquer dúvida.

#### 1. Objetivo da Pesquisa
O objetivo deste estudo é entender como um assistente digital inteligente (copiloto de checagem) pode ajudar as pessoas a avaliarem mensagens, notícias e receitas de saúde que circulam em redes sociais (como WhatsApp), identificando sinais de boatos e aprendendo a buscar fontes confiáveis sem depender cegamente da tecnologia.

#### 2. Como Será a Minha Participação?
- Você participará de **uma sessão individual acompanhada por um pesquisador**, com duração aproximada de **30 a 45 minutos**.
- Durante a sessão, você receberá mensagens curtas sobre temas de saúde (como as que chegam no celular) e usará o protótipo do assistente para verificar o conteúdo.
- Ao final, haverá um pequeno bloco em que você avaliará algumas mensagens por conta própria, para verificar o que foi fixado.
- **Importante:** Para testar a atenção e a confiabilidade da ferramenta, **algumas respostas geradas pelo assistente durante a sessão conterão pequenas falhas propositais ou deduções incompletas programadas pelos pesquisadores**. O pesquisador estará ao seu lado durante todo o tempo e, ao final da sessão, todas as mensagens serão detalhadamente explicadas e esclarecidas com o gabarito oficial da medicina.

#### 3. Riscos e Desconfortos
- **Risco de cansaço ou dúvida:** A leitura de várias mensagens pode gerar cansaço visual momentâneo. Você poderá fazer pausas a qualquer momento.
- **Risco de desinformação:** Para evitar que qualquer informação incorreta permaneça em sua memória, **ao término imediato da atividade haverá uma etapa obrigatória de esclarecimento (Debriefing)**. O pesquisador entregará a você um folheto explicativo com a verdade científica comprovada de cada tema pelo Ministério da Saúde, Fiocruz e Anvisa.
- O estudo **não envolve qualquer procedimento físico, coleta biológica, teste de medicamento ou alteração de seus tratamentos pessoais**.

#### 4. Benefícios
- Você não terá benefícios financeiros diretos, mas aprenderá técnicas práticas e cotidianas para reconhecer notícias fraudulentas de saúde, proteger seus familiares e identificar fontes públicas seguras.
- Sua participação ajudará a ciência a desenvolver assistentes de inteligência artificial mais seguros, transparentes e acessíveis para a sociedade brasileira.

#### 5. Confidencialidade, Proteção de Dados (LGPD) e Processamento das Mensagens

- Sua identidade será mantida em **rigoroso sigilo**. Os relatórios e publicações apresentarão apenas dados estatísticos agregados (ex.: porcentagens de acerto, tempo médio de resposta), utilizando códigos anônimos (ex.: "Participante P-01").
- Nenhum dado médico pessoal seu será registrado ou compartilhado.
- Para a geração das respostas do copiloto, o projeto utiliza o mecanismo de IA definido no protocolo e em suas emendas aprovadas.

##### 5.1 Processamento das mensagens e uso de serviço externo de IA (Emenda 01)
A **Emenda 01**, referente ao uso da **API da DeepSeek** para geração das respostas, foi submetida e aprovada no âmbito desta simulação acadêmica. A partir da aprovação, o piloto está autorizado a utilizar a API da DeepSeek em substituição ao modelo local, conforme o design D6.

O uso da API implica que o **texto das mensagens de teste poderá ser transmitido para processamento por um serviço de IA operado por uma empresa estrangeira**. Essa alteração foi incorporada à avaliação de riscos do protocolo e ao presente Termo de Consentimento Livre e Esclarecido.

Para reduzir os riscos relacionados à proteção de dados:
- Os participantes não devem inserir nome, telefone, endereço, CPF, e-mail ou qualquer outro dado pessoal nas mensagens utilizadas durante o teste;
- Não devem ser inseridas informações sensíveis ou informações pessoais de terceiros;
- Os testes utilizam mensagens e estímulos previamente curados pela equipe de pesquisa;
- Os participantes são identificados no estudo por códigos, como `P-01` e `P-02`, sem associação direta ao conteúdo utilizado nos testes;
- O processamento pela API da DeepSeek fica restrito à finalidade de geração das respostas necessárias ao experimento.

O participante declara estar ciente de que, durante o piloto autorizado pela Emenda 01, o conteúdo das mensagens de teste poderá ser processado por um serviço de IA de empresa estrangeira.

##### 5.2 Alternativa durante a fase anterior à aprovação da Emenda 01
Antes da aprovação da Emenda 01, o modo piloto permaneceu utilizando o **Ollama local**, sem envio das mensagens de teste para a API da DeepSeek.

Após a aprovação registrada em **07/10/2026**, o uso da API da DeepSeek passou a estar autorizado para o piloto, observadas as salvaguardas descritas neste protocolo e no dossiê de submissão.

> **Registro simulado:** A Emenda 01 foi aprovada em 07/10/2026, sob o protocolo simulado `RES-IA-G04-2026-EM01`, com parecer simulado nº `RES-IA-G04-2026-PARECER-EM01`.

#### 6. Voluntariedade e Liberdade de Recusa
Sua participação é totalmente voluntária. Você tem o direito de não participar, recusar-se a responder a qualquer pergunta ou desistir em qualquer momento da sessão, sem qualquer penalidade, custo ou perda de benefícios presentes ou futuros.

#### 7. Contato com o Comitê de Ética em Pesquisa (CEP)
Se você tiver dúvidas sobre os seus direitos como participante de pesquisa, poderá entrar em contato com o Comitê de Ética em Pesquisa institucional:
- **Comitê de Ética em Pesquisa (CEP):** [Nome do Comitê Institucional]  
- **Endereço:** [Endereço institucional do CEP]  
- **Telefone:** [Telefone do CEP] | **E-mail:** [cep@instituicao.edu.br]

---

### DECLARAÇÃO DE CONSENTIMENTO

Eu, ____________________________________________________________________, portador(a) do documento de identidade nº __________________, declaro que li (ou tive lido para mim) o presente Termo de Consentimento Livre e Esclarecido, compreendi os objetivos, métodos, riscos e benefícios da pesquisa e tive a oportunidade de fazer perguntas.

Aceito, de forma livre e esclarecida, participar desta pesquisa. Fico ciente de que receberei uma via assinada deste documento.

Local e Data: __________________________, ______ de __________________ de 2026.

_______________________________________________  
Assinatura do(a) Participante (ou Responsável Legal)

_______________________________________________  
Assinatura do(a) Pesquisador(a) Responsável

---

## 3. Roteiro Operacional de Debriefing Supervisionado

O debriefing é **obrigatório por especificação (Task 6.3 / spec `avaliacao-instrumento`)**. Nenhuma sessão de teste pode ser concluída sem a execução integral deste roteiro pelo pesquisador aplicador.

### Objetivos do Debriefing
1. Desarmar a ilusão experimental dos itens-armadilha de forma acolhedora, sem fazer o participante se sentir "enganado" ou "testado na inteligência".
2. Sanar toda e qualquer dúvida factual de saúde suscitada pelas mensagens vistas.
3. Consolidar o aprendizado das técnicas de checagem.
4. Entregar o Gabarito de Saúde Oficial impresso/digital.

---

### Passo a Passo do Pesquisador

#### Etapa 1: Acolhimento e Agradecimento (2 minutos)
* **Fala do pesquisador:**
  > "Parabéns e muito obrigado por concluir as atividades! Antes de encerrarmos, temos o momento mais importante da nossa sessão: o momento do nosso bate-papo de esclarecimento, chamado *debriefing*. Aqui vamos abrir os bastidores do teste e ver o gabarito oficial de cada assunto que vimos na tela."

#### Etapa 2: Abertura dos Itens-Armadilha (5 a 7 minutos)
* **Objetivo pedagógico:** Evidenciar que a IA comete erros e que a postura crítica é a atitude correta.
* **Fala do pesquisador:**
  > "Durante o teste, você deve ter notado algumas mensagens em que o assistente deu uma resposta estranha ou que parecia incompleta (especificamente os itens X e Y). 
  > 
  > Nós programamos propositalmente essas falhas no sistema. Fizemos isso porque uma das perguntas mais importantes da nossa pesquisa científica é: *quando a Inteligência Artificial erra ou deduz algo errado, o usuário percebe ou aceita cegamente?*
  > 
  > [Se o participante questionou a IA na hora]: Você percebeu e desconfiou — isso é excelente! Mostra que você não terceirizou o seu pensamento crítico.
  > [Se o participante aceitou a IA]: Não se preocupe se você concordou na hora com o que ela disse. É exatamente por isso que estamos estudando: as IAs usam uma linguagem muito convincente e segura, mesmo quando estão equivocadas. Esse teste nos ajuda a desenhar alertas para que a ferramenta nunca confunda o usuário."

#### Etapa 3: Leitura e Entrega do Gabarito de Saúde (10 minutos)
* **Ação do pesquisador:** Colocar na frente do participante a **Ficha-Gabarito de Fatos em Saúde** e repassar item a item, confirmando verbalmente a compreensão.

| Item do Teste | O que a mensagem afirmava | Veredito Real | Evidência Científica / Fonte Oficial |
| :--- | :--- | :---: | :--- |
| **Caso A (Ex.: Inhame/Dengue)** | "Suco de inhame cru cura dengue em 24h aumentando plaquetas." | **FALSO** | Não existe remédio ou alimento milagroso para dengue. O tratamento exige hidratação orientada por médico no posto de saúde. *(Fonte: Ministério da Saúde / Fiocruz)* |
| **Caso B (Ex.: Bula e Autismo)** | "Bula de vacina comprova que causa autismo." | **FALSO** | Trata-se de distorção de notificação de eventos sem nexo causal. Mais de 30 estudos mundiais já comprovaram que vacinas não causam autismo. *(Fonte: Anvisa / OMS)* |
| **Caso C (Item-Armadilha)** | [Exemplo de item com dedução ambígua simulada da IA] | **ESCLARECIDO** | [Apresentar o fato correto e explicar detalhadamente qual era a armadilha contida no texto da IA]. |
| **Caso D (Ex.: Vacina Febre Amarela)** | "Lote contaminado sendo aplicado nos postos." | **FALSO** | Boato reciclado. Os lotes do SUS passam por controle estrito de qualidade em Bio-Manguinhos. *(Fonte: Fiocruz)* |

#### Etapa 4: Sondagem de Dúvidas Pessoais de Saúde (3 minutos)
* **Pergunta obrigatória do pesquisador:**
  > "Ficou alguma dúvida sobre alguma dessas doenças, vacinas ou tratamentos que você viu aqui hoje? Você costuma tomar algum medicamento ou conhecia alguém que tomava algo baseado nessas notícias?"
* **Direcionamento seguro:** Se o participante manifestar dúvidas pessoais de conduta médica, aplicar a diretriz da fronteira de saúde: orientá-lo a procurar o médico da sua UBS e nunca suspender medicações por conta de testes ou correntes.

#### Etapa 5: Entrega do Guia de Fontes Seguras e Fechamento (2 minutos)
* Entregar o cartão de bolso / link com canais confiáveis:
  * **Disque Saúde 136** (ligação gratuita do SUS);
  * **Portal Saúde com Ciência** (`gov.br/saude`);
  * **Agência Fiocruz de Notícias** e **Anvisa**.
* Registrar a conclusão do debriefing na ficha de acompanhamento da sessão com assinatura do pesquisador aplicador.

---

## 4. Registro de Conformidade no Dossiê do CEP

| Requisito do CEP (Conep) | Atendimento no Protocolo do Grupo 04 |
| :--- | :--- |
| **Minimização de Vulnerabilidade** | Idosos recebem apoio visual de acessibilidade (fonte ampliada, contraste) e sessão 100% assistida. |
| **Neutralização de Risco de Engano** | Debriefing obrigatório com entrega da tabela de verdades científicas baseadas em fontes oficiais. |
| **Garantia de Não-Prejuízo Clínico** | Diretriz estrita de fronteira de saúde: o sistema recusa pedidos de prescrição e direciona à rede SUS. |
| **Proteção de Dados Sensíveis** | Inferência local (Gemma 4 12B QAT) e armazenamento de logs anonimizados, sem envio a APIs proprietárias. |
