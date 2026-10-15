# Roteiro do vídeo

Vídeo explicativo de até 5 minutos, publicado no YouTube, com os cinco
integrantes. Change `add-portfolio-showcase`, decisão D13, tasks 7.4 e 7.5.
Parte do rascunho do Breno de 15/10, reescrito para soar como conversa e
conferido contra o portfólio. Os números seguem a mesma regra dos slides: só os
que estão na [rodada da demo](../act/prototipo-avaliacao.md#rodada-da-demo) ou
nas páginas do portfólio.

| # | Tópico da coordenação | Quem fala | Tempo | Acumulado |
| --- | --- | --- | --- | --- |
| 1 | Contexto e problema | Wingrid | 0:55 | 0:55 |
| 2 | Produto e solução | Vitor | 1:00 | 1:55 |
| 3 | Aplicação e técnicas de IA | Samara | 1:00 | 2:55 |
| 4 | Principais desafios | Jhessica | 0:55 | 3:50 |
| 5 | Resultados e conclusão | Breno | 1:00 | 4:50 |

Folga de 10 s para as transições. Cada fala tem entre 115 e 135 palavras, o
que cabe em um minuto falado sem pressa.

!!! tip "Como gravar a fala"
    O texto é um guia, não um teleprompter. Leia duas vezes, depois grave
    falando com as suas palavras, como se explicasse para alguém da família.
    O que não pode mudar são os números e os nomes: esses estão conferidos.

## 1. Contexto e problema — Wingrid (0:55)

**Tela:** Wingrid na câmera. Em «vacina da febre amarela», print do
[caso 01](../forense/caso-01-febre-amarela.md); em «suco de inhame», do
[caso 02](../forense/caso-02-inhame.md). No fim, a tela inicial da Dona Checa
(`figma-dona-checa/png/desktop/01-inicial.png`).

> Oi! A gente é o grupo 04, e este é o nosso projeto: a Dona Checa.
>
> Sabe aquela mensagem que chega no grupo da família dizendo que a vacina da
> febre amarela mata metade de quem toma? Ou que suco de inhame cura a
> dengue? Quem recebe tem poucos segundos para decidir se acredita e se
> repassa.
>
> A gente quis saber quanto custa checar isso direito. Pegamos seis casos
> reais e cronometramos: na mediana, 22 minutos por mensagem. O pior levou
> 43. Ninguém faz isso no dia a dia.
>
> E quando existe uma ferramenta, ela costuma dar só um selo: «falso».
> Sem motivo, sem fonte. E a pessoa não aprende nada para o próximo boato.
>
> Então a nossa pergunta foi: como a IA pode ajudar a pessoa a avaliar uma
> informação, sem pensar no lugar dela?

## 2. Produto e solução — Vitor (1:00)

**Tela:** gravação do chat: termo aceito, caso 1 do
[roteiro da demo](roteiro-demo.md#casos) colado, andamento ao vivo, resposta
em quatro blocos e «Ver fontes e detalhes» aberto. No fim, o caso 4, com
«evidência insuficiente». Sem gravação, usar as telas `03`, `04` e `10` de
`figma-dona-checa/png/desktop/`.

> A Dona Checa é um chat. Você cola a mensagem ou o link que recebeu, sem
> criar conta.
>
> Antes, ela pede o seu consentimento, porque o texto vai para um modelo de
> linguagem externo. E o servidor tira e-mail, CPF e telefone antes de
> mandar.
>
> Aí ela responde em quatro blocos curtos: o veredito, o que se sabe sobre o
> assunto, por que aquela mensagem engana e o que observar da próxima vez.
>
> A nossa regra é: veredito nunca nu. Se ela diz «falso», mostra o critério
> e o link da checagem de uma agência brasileira, como a Lupa ou o Aos Fatos.
> Você abre, confere e pode até discordar.
>
> E quando não existe checagem sobre aquilo, ela diz «evidência
> insuficiente», em vez de chutar.

## 3. Aplicação e técnicas de IA — Samara (1:00)

**Tela:** o [mapa da arquitetura](../mapa/arquitetura.html), fluxo guiado
«Na linha da verificação», avançando com `→` a cada estação citada.

> Por trás do chat, tem uma linha com sete etapas.
>
> A primeira é uma fronteira de saúde. Se alguém escreve «minha mãe está com
> dor no peito agora», a Dona Checa não checa nada: manda ligar para o SAMU.
>
> Depois, um modelo de linguagem acha a alegação de saúde na mensagem e
> separa o que é fato do que é opinião.
>
> Aí vem a busca, um RAG híbrido. Juntamos a busca por palavras, o BM25, que
> acha nomes exatos de vacina e remédio, com a busca por significado, o
> modelo multilingual-e5, que entende o jeito como as pessoas escrevem. Tudo
> sobre mais de seis mil checagens de agências brasileiras.
>
> E tem uma guarda: se nenhuma checagem cobre a alegação, o modelo nem dá
> veredito. A gente não treinou classificador nenhum.

## 4. Principais desafios — Jhessica (0:55)

**Tela:** um trecho do FACTCK.BR sem acentos e o exemplo lematizado da
[página de tratamento](../investigate/tratamento-datasets.md); depois, o card
«Gerador» do mapa, com 102,4 s contra 10,9 s.

> Tivemos três desafios grandes.
>
> O primeiro foram os dados. Bases públicas conhecidas vieram estragadas: uma
> perdeu as maiúsculas com acento, outra veio com as palavras reduzidas, tipo
> «o governar equador anunciar preparar cova». Não dá para citar isso.
> Auditamos tudo, e só uma base ficou boa para citar.
>
> O segundo foi segurança. Num teste, perguntamos se uma mãe com câncer podia
> trocar a quimioterapia por um chá. O modelo abriu com «falso» e só no final
> falou em médico. Por isso a fronteira de saúde virou a primeira etapa.
>
> O terceiro foi o tempo. Rodando local, cada mensagem levava uns 100
> segundos. Passamos para a API da DeepSeek, com termo de consentimento, e
> caiu para uns 11.

## 5. Resultados e conclusão — Breno (1:00)

**Tela:** mapa, faixa 07, card «Rodada da demo» aberto; depois, o grupo
todo, com o link do repositório e do portfólio.

> E funciona? Medimos de três jeitos.
>
> Na busca: em 20 consultas reais, a checagem certa apareceu entre as cinco
> primeiras em todas.
>
> No fluxo completo: montamos 30 casos de teste, com o esperado em cada
> etapa. Na última rodada, 29 passaram, e todas as respostas com veredito
> trouxeram o link da checagem. Cada verificação leva uns 14 segundos,
> contra aqueles 22 minutos, e custa menos de meio centavo de dólar.
>
> E com pessoas: num piloto com duas pessoas, as duas acertaram tudo,
> inclusive depois, sem a ferramenta. Com duas pessoas, isso valida o método;
> ainda não prova o efeito. O próximo passo é testar com 20 a 30.
>
> A Dona Checa não pensa por você. Ela mostra o critério e a fonte, para
> você decidir. Valeu!

## Gravação e publicação

- Cada integrante grava a própria fala, de preferência na horizontal, em
  lugar silencioso e com o rosto iluminado de frente.
- As telas de cada trecho entram por cima da fala, na edição. Quem edita
  junta na ordem da tabela.
- Legendas: gerar no YouTube e corrigir os termos técnicos (BM25, e5,
  DeepSeek, SAMU).
- Conferir a duração final: até 5:00.
- Publicar no YouTube como «Não listado» ou «Público», conforme a
  coordenação pedir.
- Colocar o link no `README.md` e nesta página (task 7.6).

**Link do vídeo:** pendente.
