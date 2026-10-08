# Parecer sobre o termo de consentimento (LGPD)

| Campo | Registro |
| --- | --- |
| Autor | Antônio Augusto Marques, Analista Jurídico |
| Data da assinatura | 08/10/2026 |
| Documento revisado | [Revisão do termo de consentimento (LGPD)](revisao-termo-lgpd.md) |
| Change e issue | `add-gerador-api-deepseek`, task 5.1 (#196) |

Transcrição do parecer recebido pelo grupo. Como o grupo aplicou o parecer
está registrado no fim desta página.

---

## Parecer de Conformidade e Revisão Jurídica (LGPD)

**Projeto:** Dona Checa — Chat Web de Checagem de Desinformação em Saúde

**Mudança:** `add-gerador-api-deepseek` (Issue #196)

**Contato indicado:** `donacheca@checatudo.com`

### Visão Geral da Avaliação

A arquitetura orientada ao **Privacy by Design** (sem banco de dados, sem logs de identificadores e com mascaramento prévio de telefone, CPF e e-mail) demonstra alto rigor de proteção de dados.

O uso da **API da DeepSeek (China)** envolve dois pontos centrais da LGPD:

1. **Tratamento de dados sensíveis de saúde** (Art. 5º, II e Art. 11);
2. **Transferência internacional de dados** (Art. 33, VIII).

Abaixo estão a **minuta revisada dos textos** e a **análise jurídica detalhada das 10 perguntas**.

### 1. Minuta Revisada dos Textos (Seção 4 do Documento)

#### A. Texto do Termo na Tela (Modal / Banner de Entrada)

> Antes de começar, meu bem: para checar sua mensagem, eu envio o texto dela para a DeepSeek, um serviço de inteligência artificial localizado na China.
> Nós apagamos automaticamente números de telefone, CPF e e-mail antes de enviar. Porém, **como nomes próprios no meio do texto não são apagados automaticamente, pedimos que você não inclua seu nome, telefone, CPF ou informações sobre sua saúde**.
> A DeepSeek recebe e trata o texto conforme as regras do serviço dela. Do nosso lado, nada fica guardado: ao fechar ou recarregar a página, a conversa apaga.
> Este serviço é mantido pela **Residência em IA (UnB / Instituto Eldorado — Grupo 04)**. Se tiver dúvidas, fale conosco em **donacheca@checatudo.com**.
> Você aceita que o texto da sua mensagem seja enviado para a DeepSeek?

**Botões:** `[ Aceito ]` | `[ Não aceito ]` *(Ambos desmarcados por padrão; campo de entrada bloqueado até a escolha).*

#### B. Resposta em Caso de Recusa ("Não aceito")

- **Sem modelo local disponível:**

  > Tudo bem, meu bem. Sem o seu aceite eu não consigo checar a mensagem por aqui. Você pode pesquisar a checagem diretamente nos sites de agências públicas, como a *Lupa*, o *Aos Fatos* ou o *Fato ou Fake*.

- **Com modelo local disponível no servidor:**

  > Tudo bem, meu bem. Vou checar aqui no computador do projeto, sem mandar sua mensagem para fora. Essa opção é mais privativa, mas pode demorar cerca de dois minutos.

#### C. Aviso Fixo no Rodapé (Durante toda a conversa)

> Para responder, sua mensagem é enviada a um serviço de IA na China. Não digite nomes, números de telefone, CPF ou dados de saúde. Contato: **donacheca@checatudo.com**.

### 2. Resposta Estruturada às 10 Perguntas da Seção 9

#### 1. O texto do termo atende aos Arts. 11, I e 33, VIII da LGPD?

**Sim, desde que com as correções propostas.**

- **Art. 11, I (Dados Sensíveis):** Exige consentimento fornecido de forma **destacada** e para **finalidades específicas**. O bloqueio prévio da interface garante que o consentimento seja destacado.
- **Art. 33, VIII (Transferência Internacional):** Exige consentimento específico com **informação prévia sobre o caráter internacional da operação**. Ao citar expressamente a *DeepSeek* e a *China*, o termo preenche o requisito legal de informação clara sobre o destino dos dados.

#### 2. O tom informal ("meu bem") compromete a validade?

**Não.** O Art. 9º, *caput*, e o Art. 11, I, exigem linguagem **clara, acessível e transparente**. Como o público-alvo é composto por pessoas idosas, o uso de linguagem humanizada e empática favorece a compreensão do termo, atendendo ao **Princípio da Transparência (Art. 6º, VI)**.

#### 3. A frase "sem seu nome e sem seu telefone" deve ser alterada?

**Sim, obrigatoriamente.** Afirmar que a mensagem vai "sem seu nome" quando o sistema não remove nomes próprios no corpo do texto cria uma **falsa expectativa de anonimização**, violando o dever de informação (Art. 6º, VI e Art. 9º). A versão revisada explica claramente que CPF, e-mail e telefone são filtrados automaticamente, mas orienta o usuário a não digitar nomes nem dados de saúde.

#### 4. Quem deve figurar como controlador e qual contato utilizar?

Grupos de trabalho ou turmas acadêmicas não possuem personalidade jurídica. O controlador legal é a **instituição/programa responsável pela Residência em IA** (Universidade de Brasília — UnB / Instituto Eldorado).

- **No termo:** Identificar como *"Residência em IA (UnB / Instituto Eldorado — Grupo 04)"*.
- **Contato oficial:** Utilizar o e-mail do grupo: **`donacheca@checatudo.com`**.

#### 5. O registro do aceite sem identificação da pessoa é suficiente?

**Sim.** O Art. 8º, § 2º da LGPD atribui ao controlador o ônus de provar o consentimento. Em aplicações públicas e sem cadastro, registramos a conformidade por meio do **Privacy by Design / Minimização (Art. 6º, III)**:

1. Log do evento com marca temporal, versão do termo e status (`consent_v1_granted`);
2. Bloqueio lógico na API (o servidor recusa chamadas que não acompanhem a flag de aceite da versão vigente).

Coletar dados pessoais (como IP ou cookies) exclusivamente para "provar o aceite" contrariaria o princípio da minimização.

#### 6. A alternativa local é obrigatória para o consentimento ser "livre"?

**Não obrigatoriamente**, mas é a melhor prática. Se o modelo local estiver indisponível, o consentimento continua sendo livre, pois o usuário não sofre prejuízo sanção ou perda de direitos ao recusar — o serviço é gratuito e voluntário. Informar alternativas públicas (como links das agências de checagem) satisfaz o requisito de autonomia do titular.

#### 7. O consentimento basta para a transferência internacional ou são necessárias Cláusulas-Padrão (CPCs)?

**O consentimento (Art. 33, VIII) é base legal suficiente e autônoma.** As Cláusulas-Padrão Contratuais (Resolução CD/ANPD nº 19/2024) aplicam-se prioritariamente a contratos formais corporativos. Para uma API de uso geral em projeto acadêmico sem canal de negociação com a DeepSeek, o consentimento prévio, destacado e informado é o mecanismo adequado previsto na lei.

#### 8. No modo Piloto, o TCLE dispensa o termo da página?

**Não, ambos devem coexistir.**

- **TCLE (Resolução CNS 510/2016):** É o instrumento ético-científico para participação na pesquisa aprovada pelo CEP/CONEP.
- **Termo da Página (LGPD):** É a interface operacional que colhe o consentimento imediato para o tratamento de dados e transferência internacional em tempo real.

#### 9. É preciso restringir ou avisar sobre o uso por menores?

**Sim.** Como o processamento envolve dados de saúde e transferência internacional, inclua no rodapé ou nas instruções uma frase simples: *"Serviço destinado a maiores de 18 anos"*. Isso reduz o risco de incidência das regras estritas do **Art. 14 da LGPD** (Tratamento de dados de crianças e adolescentes).

#### 10. A apuração da política da DeepSeek (Issue #197) altera essas respostas?

**Pode alterar parcialmente o nível de aviso no termo.**

- Se a consulta à API da DeepSeek retiver os dados por prazo determinado (ex.: 30 dias para moderação de segurança) e **não** utilizar os dados enviados via API para treinamento de modelos, o termo atual permanece válido.
- Se a política indicar que os dados enviados via API **são usados para treinamento de novos modelos**, será necessário adicionar uma frase curta no termo: *"A DeepSeek pode utilizar o texto enviado para aprimoramento dos seus sistemas."*

### 3. Matriz Sintética de Ações Recomendadas

| Issue / Módulo | Item | Ação Necessária |
| --- | --- | --- |
| **Issue #196** | Interface Chat Web | Atualizar o texto do termo no código (`spec.md`) com a minuta revisada deste parecer. |
| **Issue #196** | Sanitização (`minimizar.py`) | Manter o regex de telefone, CPF e e-mail, e assegurar o log sem PII. |
| **Issue #195** | Comitê de Ética (CEP) | Submeter a Emenda 01 ao CEP descrevendo a atualização da Seção 5 do TCLE e a inclusão do aviso no chat. |
| **Issue #197** | Análise da API DeepSeek | Verificar nos termos de uso da API (*API Terms of Service*) a cláusula de não-treinamento (*data retention / opt-out of model training*). |

---

## Como o grupo aplicou

- Os textos A, B e C entraram na spec `interface-chat-web` de
  `add-gerador-api-deepseek`, e a versão do termo passou de 1 para 2.
- Desvios:
  - **Formatação:** negrito e itálico saíram, porque a página mostra o texto
    puro e exibiria os asteriscos.
  - **Recusa:** "agências públicas" virou "agências de checagem", porque
    Lupa, Aos Fatos e Fato ou Fake são empresas privadas.
  - **Rodapé:** recebeu "Serviço para maiores de 18 anos", como pede a
    resposta 9.
- **Log do aceite:** o log registra "consentimento versão 2" com data e hora,
  o que equivale ao `consent_v1_granted` da resposta 5.
