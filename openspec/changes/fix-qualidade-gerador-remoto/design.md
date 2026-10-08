# Design: Qualidade com gerador remoto

## Context

Motivação em `proposal.md`. Falhas detalhadas no `design.md` de
`add-gerador-api-deepseek` (tabelas das rodadas de 08/10/2026).

## Goals / Non-Goals

**Goals:**

- R2, R3 e X2 passam com `deepseek-v4-pro` sem mudar o que conta como defeito
  de mito.
- Defeito de forma da resposta tem uma chance de correção antes de sair.
- Nenhum caso que passa com o Gemma deixa de passar.

**Non-Goals:**

- Reconhecer paráfrase do mito sem negação explícita.
- Mudar o limite de 20 palavras por frase ou o teto de 120 palavras.
- Ajustar prompts por gerador.

## Decisions

### D1. Formas novas de marcação, com teste negativo

As formas novas negam a existência de evidência, como "não há estudo", que já
conta como marcação. Cada forma entra com um teste positivo (frase das
gravações de 08/10) e um negativo que precisa continuar defeito:

| Frase | Esperado |
| --- | --- |
| "Nenhum estudo mostra que chá de boldo cura hepatite" | marcada |
| "A checagem não encontrou nenhum estudo que mostre que a casca do jatobá cura o câncer" | marcada |
| "A checagem não achou prova de que a casca do jatobá trate câncer" | marcada |
| "A mensagem promete curar câncer com algo simples e caseiro, sem estudo que mostre isso" | marcada |
| "O estudo que ligava vacina a autismo foi retratado" | marcada (D7) |
| "A mensagem tira de contexto uma entrevista para afirmar que a vacina mata em 50% dos casos" | marcada (D7) |
| "A mensagem retrata a vacina como perigosa: vacina causa autismo" | não marcada |
| "Num contexto de medo, a vacina mata em 50% dos casos" | não marcada |
| "Um estudo mostra que chá de boldo cura hepatite" | não marcada |
| "A mensagem promete curar dengue em 24 horas" | não marcada |
| "Não encontrou ninguém que discorde: boldo cura hepatite" | não marcada |

### D2. Nova tentativa na decomposição

`decompor` passa a seguir `estrutura.responder`: se `defeitos(bruto)` não for
vazio, pede de novo com os defeitos listados ao fim do pedido. A segunda saída
com defeito levanta `ValueError`, como hoje. Uma tentativa só, para não somar
latência sem limite.

### D3. Ajuste do prompt da decomposição

Duas frases novas no `SISTEMA`:

- "Pergunta ou exclamação de quem mandou a mensagem ('Isso é verdade?',
  'Absurdo!') não é fato, opinião nem conclusão: deixe de fora."
- "O salto explica o que falta entre fato e conclusão. Não diga se algo é
  verdadeiro ou falso nele."

### D5. Nova tentativa da resposta também por defeito de forma

Hoje `estrutura.responder` só pede de novo quando a ancoragem falha. Defeitos
de forma (camada visível acima de 120 palavras, frase acima de 20, mito sem
marcação) só ficam registrados, e a resposta sai com eles. Nas três rodadas
com `deepseek-v4-pro`, foram a maior parte das falhas. A resposta passa a ter
uma nova tentativa quando sair com qualquer defeito registrado, com os
defeitos listados no aviso. `responder` chama `_montar` duas vezes no máximo;
o `bruto` guarda as duas saídas, separadas por "--- refeita por defeito da
resposta ---". A
tentativa é uma só no total: se a ancoragem já gastou a nova tentativa, os
defeitos de forma ficam registrados, como hoje. Se a segunda saída tiver mais
defeitos que a primeira, vale a primeira.

### D6. Teto de alegações e nova tentativa na extração

Na segunda rodada de conferência do critério (relatório
`20261008-154557.json`), o L01 terminou em erro: da página de um blog, o
`deepseek-v4-pro` listou 22 alegações, inclusive de política, e a saída foi
cortada no limite de 1200 tokens, no meio de uma string. O `flash` falhou do
mesmo jeito na primeira rodada. A verificação só usa a alegação de saúde de
maior risco; listar todas é custo e risco de corte.

- O prompt da extração passa a pedir no máximo 8 alegações, as de saúde
  primeiro, na ordem em que aparecem na mensagem.
- Saída com defeito, inclusive JSON cortado, tem uma nova tentativa com o
  defeito informado, como na decomposição (D2).
- `ChatDeepSeek` registra no log quando a API devolve `finish_reason`
  `length`, sem o texto.

O limite de 1200 tokens não sobe: subir só adia o corte e aumenta a espera.

### D7. Alvo de tamanho com folga e marcas de desmentido

Decisão do grupo em 08/10/2026, depois das rodadas `155424` e `155808`.

- O bordão e os títulos somam 26 palavras fixas. O prompt pedia 90 palavras
  para "a resposta inteira", e o modelo escrevia 95 a 100 nos blocos: 121 a
  126 no total, teto 120. O prompt passa a pedir no máximo 80 palavras nos
  quatro blocos, 106 no total, com 14 de folga. O teto de 120 não muda.
- O aviso da nova tentativa diz quantas palavras a camada visível teve e
  quantas cortar dos blocos (o excesso mais 10), em vez de só repetir o teto.
- "retratado/retratada" e "fora de contexto"/"tira(m) de contexto" contam como
  marcação, ao lado de "desmentido" e "engana". "retrata" (verbo "mostrar")
  e "contexto" sozinho não contam.

### D4. Gravações

Mudar o `SISTEMA` muda a chave das gravações da decomposição, e a bancada
offline passa a falhar com "chamada ao modelo sem gravação". A regravação usa
o gerador que estiver como padrão quando o change for aplicado.

## Risks / Trade-offs

- [Afrouxar a régua para o modelo passar] → só negação explícita de evidência,
  com testes negativos (D1). Decisão do grupo registrada em 08/10/2026.
- [Nova tentativa esconde prompt ruim] → o `bruto` da resposta guarda as duas
  saídas, e a decomposição registra `refeita_por` com os defeitos da
  primeira; os dois vão para o rastro da bancada.
