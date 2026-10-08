# Revisão do termo de consentimento (LGPD)

Documento para a revisão jurídica ou do encarregado de dados (DPO). Reúne o
que a revisão precisa saber sobre o envio de mensagens da Dona Checa a um
serviço de inteligência artificial estrangeiro. Faz parte da task 5.1 do
change `add-gerador-api-deepseek` (issue #196).

O grupo não tem formação jurídica. As seções 6 e 8 trazem a leitura que o
grupo fez da LGPD para desenhar o fluxo. Não são parecer, e é exatamente o que
pedimos que seja revisto.

**Resultado:** [parecer de 08/10/2026](parecer-termo-lgpd.md). Os textos da
seção 4 abaixo são a versão 1, enviada para revisão. A versão em uso é a 3:
a do parecer, mais o aviso sobre treino e retenção da DeepSeek (issue #197).

## 1. O serviço

A Dona Checa é um chat web de checagem de mensagens de saúde, pensado para
pessoas idosas que recebem desinformação pelo WhatsApp. A pessoa cola a
mensagem que recebeu, ou o link de uma notícia. O sistema procura checagens já
publicadas por agências (Lupa, Aos Fatos, Fato ou Fake e outras) e responde
dizendo o que essas checagens dizem, com as fontes.

O serviço roda em dois modos:

- **Uso:** demonstração e uso comum.
- **Piloto:** sessões da pesquisa com participantes, cobertas pelo TCLE e pelo
  protocolo do CEP.

## 2. O que mudou

Até 08/10/2026, o modelo de linguagem que escreve a resposta rodava num
computador do projeto, e nada saía dele. Cada resposta levava cerca de 100
segundos, tempo demais para o público.

O grupo passou a usar a API da DeepSeek, empresa de inteligência artificial
da China. A resposta caiu para cerca de 10 segundos. Em troca, o texto da
mensagem passa a sair do servidor do projeto e ir para a DeepSeek.

## 3. Caminho dos dados

1. A pessoa abre a página. Antes de poder escrever, vê o termo da seção 4 e
   escolhe "Aceito" ou "Não aceito".
2. Com o aceite, a pessoa cola a mensagem e envia. A página manda ao servidor
   do projeto o texto e a versão do termo aceita.
3. O servidor confere a versão do termo. Sem ela, recusa o pedido e nada é
   enviado à DeepSeek.
4. O servidor troca telefone, CPF e e-mail do texto por marcadores
   (`[telefone]`, `[cpf]`, `[email]`).
5. O servidor manda à DeepSeek o texto já trocado, as instruções do sistema e
   trechos das checagens públicas encontradas.
6. A DeepSeek devolve o texto da resposta, que o servidor mostra na página.

| Dado | Vai para a DeepSeek? |
| --- | --- |
| Texto da mensagem colada | Sim, sem telefone, CPF e e-mail |
| Nome escrito pela pessoa dentro da mensagem | **Sim**: não há como removê-lo automaticamente sem apagar nomes de remédios e cidades |
| Texto de página de notícia, quando a pessoa manda um link | Sim. É conteúdo público |
| Nome, telefone, IP ou qualquer identificador da pessoa | Não. O pedido parte do servidor do projeto, e a DeepSeek vê o endereço do servidor |
| Trechos de checagens das agências | Sim. É conteúdo público |

**O que fica no servidor do projeto:** nada do conteúdo. Não há banco de dados,
arquivo nem sessão. A conversa existe só na página aberta e some ao recarregar.
O registro técnico (log) guarda só eventos sem conteúdo, por exemplo
"consentimento versão 1", "consentimento recusado; gerador local" ou o tipo de
um erro.

## 4. O que a pessoa vê

Texto do termo, mostrado antes do campo de mensagem:

> Antes de começar, meu bem: para te responder, eu mando o texto da sua
> mensagem para a DeepSeek, uma empresa de inteligência artificial da China.
> Ela recebe só o texto, sem seu nome e sem seu telefone, e pode guardar esse
> texto pelas regras dela. Aqui do nosso lado nada fica guardado: fechou a
> página, a conversa some. Por isso, não escreva dados seus, como nome,
> telefone, CPF ou doença que você tem. Quem responde por este serviço é o
> grupo 04 da Residência em IA, pelo contato **CONTATO_DO_GRUPO**. Você aceita
> que sua mensagem vá para a DeepSeek?

Botões: **Aceito** e **Não aceito**. Nenhum vem marcado, e o campo de mensagem
fica bloqueado até a escolha.

O tom informal ("meu bem") é da personagem Dona Checa, pensada para o público
idoso.

Resposta a quem não aceita, quando não há alternativa local:

> Tudo bem, meu bem. Sem esse aceite eu não consigo checar por aqui. Você pode
> procurar a checagem no site de uma agência, como a Lupa, o Aos Fatos ou o
> Fato ou Fake.

Resposta a quem não aceita, quando o servidor tem o modelo local disponível:

> Tudo bem, meu bem. Vou checar aqui no computador do projeto, sem mandar sua
> mensagem para fora. Só que demora mais, uns dois minutos.

Aviso fixo no rodapé, durante toda a conversa:

> Para te responder, eu mando sua mensagem para um serviço de inteligência
> artificial de fora do Brasil. Não coloque seu nome, telefone ou dados de
> saúde seus na mensagem.

## 5. Como o aceite funciona

- O termo tem versão (hoje, `1`). A página manda a versão aceita junto com
  cada mensagem, e o servidor confere antes de chamar a DeepSeek. Se o texto
  do termo mudar, a versão muda, e quem aceitou a anterior precisa aceitar de
  novo.
- O aceite vale só para a página aberta. Ao recarregar, o termo aparece de
  novo. Para desistir, basta fechar a página ou não aceitar.
- O servidor não guarda quem aceitou: guardar exigiria identificar a pessoa, e
  o serviço foi desenhado para não guardar nada dela. O log registra só que
  houve um aceite da versão 1, sem identidade.

## 6. Fundamentos que o grupo usou

Leitura do grupo, para revisão:

- **Dado sensível (art. 5º, II):** a mensagem pode trazer dado de saúde da
  própria pessoa, por exemplo "tenho diabetes, esse chá cura?".
- **Consentimento para dado sensível (art. 11, I):** de forma específica e
  destacada, para finalidade específica. Por isso o termo aparece sozinho,
  antes de tudo, e não junto de outros avisos.
- **Transferência internacional (art. 33, VIII):** a China não tem decisão de
  adequação da ANPD. O grupo usou o consentimento específico e em destaque,
  com informação prévia sobre o caráter internacional da operação.
- **Necessidade (art. 6º, III):** telefone, CPF e e-mail saem antes do envio.
- **Informação ao titular (art. 9º):** o termo diz para onde vai o texto, quem
  recebe e quem responde pelo serviço.
- **Prova do consentimento (art. 8º, § 2º):** ver o ponto 2 da seção 8.

## 7. Piloto da pesquisa

No modo piloto, o modelo local continua sendo o padrão. Para usar a DeepSeek
nas sessões, o grupo atualizou a seção 5 do TCLE com a frase sobre o envio à
DeepSeek e mudou de "Nulo" para "Baixo" o risco de vazamento no dossiê do CEP.
A mudança foi submetida como emenda 01 ao protocolo (issue #195) e aprovada
em 08/10/2026, com o risco classificado como "Moderado" (registro simulado
para fins acadêmicos). No piloto, o termo da página aparece também, além do TCLE
assinado.

## 8. Pontos de atenção que o grupo já identificou

1. **Promessa sobre o nome.** O termo diz que a DeepSeek recebe o texto "sem
   seu nome e sem seu telefone". Isso vale para o que o sistema envia por
   conta própria. Se a pessoa escrever o nome dentro da mensagem, ele vai junto
   (seção 3). O telefone escrito na mensagem é removido; o nome, não.
2. **Prova do aceite.** Sem guardar identidade, o projeto só consegue mostrar
   que o servidor recusa pedido sem aceite e que o log registra aceites da
   versão 1. Não consegue provar o aceite de uma pessoa específica.
3. **Quem é o controlador.** O termo nomeia o "grupo 04 da Residência em IA",
   que não é pessoa jurídica.
4. **Consentimento livre.** Sem a alternativa local ligada, quem não aceita
   não consegue usar o serviço.
5. **O que a DeepSeek faz com os dados.** Ainda não verificado: por quanto
   tempo guarda o que recebe pela API, se usa esse conteúdo para treinar
   modelos e onde os dados ficam. O termo diz só que ela "pode guardar esse
   texto pelas regras dela". Levantamento em andamento (issue #197).
6. **Contrato com a DeepSeek.** O uso é pelos termos padrão da API, sem
   contrato próprio nem cláusulas-padrão de transferência internacional.
7. **Idade.** A página não pergunta a idade. O público pensado é idoso, mas
   nada impede o uso por menores.

## 9. Perguntas para a revisão

1. O texto do termo (seção 4) atende ao consentimento específico e em
   destaque dos arts. 11, I, e 33, VIII? O que precisa mudar?
2. O tom informal da personagem compromete a validade do consentimento?
3. A frase "sem seu nome e sem seu telefone" deve sair ou ser reescrita,
   dado o ponto 1 da seção 8?
4. Quem deve figurar como controlador e qual contato deve aparecer no lugar de
   `CONTATO_DO_GRUPO`?
5. A forma de registro do aceite (seção 5) é suficiente para um projeto
   acadêmico? Se não, o que seria o mínimo, sem guardar o conteúdo das
   mensagens?
6. A alternativa local para quem recusa deve ser obrigatória para que o
   consentimento seja livre?
7. O consentimento basta como base para a transferência internacional, ou é
   preciso usar outro mecanismo, como as cláusulas-padrão contratuais da
   ANPD?
8. No piloto, o TCLE assinado com a emenda 01 dispensa o termo da página, ou
   os dois devem continuar?
9. É preciso restringir ou avisar sobre o uso por menores de idade?
10. A política de dados da DeepSeek, quando levantada (issue #197), muda
    alguma das respostas acima?

## 10. Onde está cada coisa no repositório

| O quê | Arquivo |
| --- | --- |
| Textos do termo, da recusa e do rodapé, e regras do aceite | `openspec/changes/add-gerador-api-deepseek/specs/interface-chat-web/spec.md` |
| Decisões D6 (piloto), D8 (termo) e D9 (minimização) | `openspec/changes/add-gerador-api-deepseek/design.md` |
| Regra de minimização | `prototipo/entrada/minimizar.py` |
| Conferência do aceite no servidor | `interface/app.py` |
| TCLE e dossiê do CEP | `openspec/changes/mvp-copiloto-verificacao/specs/avaliacao-instrumento/` |
