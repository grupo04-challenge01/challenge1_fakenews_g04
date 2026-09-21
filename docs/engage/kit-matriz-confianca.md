# Kit do workshop da confiança

Material de preparação para o bloco 4 do change `add-engage-desinformacao-saude`.

!!! warning "Isto não é a matriz"
    Este documento **não cumpre** nenhuma das tasks 4.1 a 4.4. Card sorting é
    trabalho das pessoas: o insumo são os sinais que **cada integrante usa na
    prática**, e ninguém pode escrevê-los por elas. O que está aqui é o
    material da sessão, para que os 90 minutos sejam gastos decidindo e não
    preparando.

## O que a capability exige do resultado

Quatro exigências, e a terceira é a que costuma ser violada sem querer:

1. **Cada dimensão tem quatro elementos:** nome, sinal observável, papel que a
   IA pode cumprir, e **limite explícito** do que a dimensão não determina.
   Dimensão sem limite declarado MUST NOT entrar na matriz.
2. **Rubrica de três níveis por dimensão** — sinal forte, sinal fraco, sinal
   ausente —, escrita com precisão suficiente para que dois avaliadores cheguem
   à mesma classificação no mesmo caso.
3. **Nenhum score agregado.** Sem nota única, sem selo, sem soma ponderada. A
   saída é um conjunto de evidências lado a lado. O motivo está na spec:
   score único não é auditável, porque esconde qual dimensão pesou, e não ensina
   critério nenhum, porque não sobra nada de observável para a próxima mensagem.
4. **Cada dimensão discrimina pelo menos um caso da forense.** A que não
   discriminar nenhum sai da versão 1, com o motivo registrado.

A exigência 4 amarra o bloco 4 ao bloco 2: **sem as fichas da forense
preenchidas, a validação da matriz não tem contra o que rodar.**

---

## Protocolo da sessão (~60 min do bloco de 90)

### Etapa 1 — Card sorting individual (15 min, em silêncio)

Cada pessoa escreve, **sem consultar ninguém**, os sinais que usa na prática
quando desconfia de uma mensagem de saúde. Um sinal por cartão.

A instrução exata importa: *«o que te fez desconfiar, da última vez que você
desconfiou»* — não *«o que indica desinformação»*. A primeira pergunta colhe
prática; a segunda colhe teoria lida em algum lugar.

### Etapa 2 — Agrupamento aberto (20 min)

Os cartões vão para a mesa sem dono. Agrupar por afinidade, sem nomear os
grupos ainda. Nomear cedo fecha o agrupamento antes da hora.

### Etapa 3 — Nomear dimensões e declarar limites (20 min)

Cada grupo vira uma dimensão candidata. Para cada uma, preencher os quatro
elementos. **O limite é obrigatório e é a parte difícil** — é o campo que
impede a matriz de virar detector.

### Etapa 4 — Rubrica (fora da sessão, task 4.3)

Três níveis por dimensão. Teste de qualidade: duas pessoas classificam o mesmo
caso separadamente; divergência significa que a rubrica precisa de texto mais
preciso, não de discussão.

---

## Cartões-semente

Use apenas se a etapa 1 travar. **Não distribua antes** — eles enviesam o que
as pessoas escreveriam sozinhas.

Todos saem de sinais observados nos seis casos selecionados para a forense ou
de material já medido no projeto.

| Sinal | De onde veio |
| --- | --- |
| Atribui a fala a «um médico» / «um dermatologista» sem nome | casos 01 e 06 |
| Autoridade de segunda mão («o marido da Simone, médico») | caso 06 |
| Cita instituição real mas o estudo não existe | caso 02 |
| Antecipa-se à objeção («o estudo ainda não foi divulgado») | caso 02 |
| Número redondo e extremo, sem fonte (50%) | caso 01 |
| Data da mídia não bate com a data da alegação | caso 03 |
| Corte de vídeo remove a palavra que muda o sentido | casos 03 e 05 |
| Documento real citado afirma menos do que a mensagem diz | caso 04 |
| Atribui motivação conspiratória a autoridade pública | casos 01 e 06 |
| Pede repasse urgente | formato de corrente, caso 06 |
| Não há link, só texto | correntes em geral |
| Tom sóbrio e pseudo-técnico | formato dominante do acervo de circulação |

O último merece atenção na discussão: ele é **inverso** dos demais. O corpus de
circulação mostra que boa parte da desinformação antivacina circula em tom
calmo e técnico — logo, «tom exaltado» como sinal de falsidade erra justamente
onde mais importa.

---

## Três armadilhas conhecidas

**1. A matriz não é um detector.** Toda dimensão vai ter a tentação de virar
«indicador de falsidade». O campo de limite existe para impedir isso. Exemplo
que a própria spec dá: na dimensão de linguagem e enquadramento, o limite
registrado precisa dizer que **texto sensacionalista pode ser verdadeiro**, e o
papel da IA é marcar o trecho, não apontar falsidade.

**2. Polaridade emocional não entra como dimensão evidenciária.** Já está
decidido e medido — decisão 7 de `add-selecao-modelos-arquitetura-rag`. Emoção
entra como **técnica nomeada ao usuário**, conteúdo formativo, nunca como
indício de falsidade. Um classificador que aprenda «texto emocionado → falso»
viola `verificacao-alegacao` por construção.

**3. Não confundir com a rubrica de critérios que já existe.** A rubrica de seis
critérios em `datasets/derivados/rubrica_criterios_ptbr.json` avalia **qualidade
de cobertura jornalística** (adaptada do FakeHealth). A matriz de confiança
avalia **confiabilidade de uma mensagem recebida**. São instrumentos
diferentes, com objetos diferentes.

O formato da rubrica de três níveis daquele arquivo pode ser reusado na task
4.3 — e **precisa** ser reconferido contra a matriz quando ela existir, porque a
spec de `adaptacao-criterios-en` exige que a rubrica seja «compatível com a
capability `matriz-confianca`», e essa compatibilidade nunca foi verificada,
justamente porque a matriz não existe.

---

## Saída esperada

| Artefato | Task | Onde |
| --- | --- | --- |
| Cartões agrupados, com dono anônimo | 4.1 | foto do board + transcrição |
| Dimensões com nome, sinal, papel da IA e limite | 4.2 | `docs/engage/matriz-confianca.md` |
| Rubrica de três níveis por dimensão | 4.3 | mesmo arquivo |
| Registro do que foi removido por não discriminar | 4.4 | mesmo arquivo |
| Matriz de confiança versão 1 consolidada | 7.2 | mesmo arquivo |
