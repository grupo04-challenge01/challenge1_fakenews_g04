# Design: Conduta que cobre diagnóstico e relato de sintoma sem checagem

## Context

Motivação em `proposal.md`. Teste no modo uso em 13/10/2026:

| Mensagem | Regras | Fronteira | Fim |
| --- | --- | --- | --- |
| "o vitor ta doente?" | nenhuma | `conduta` | `aviso` com o texto de conduta (remédio) |
| "estou com bolinhas no corpo" | nenhuma | `conduta` | texto de conduta (remédio) e resposta "Evidência insuficiente" |

O prompt `SISTEMA` de `prototipo/verificacao/fronteira.py` define
`conduta_individual` como pedido de "parar, começar, trocar ou dosar remédio
ou tratamento, tomar ou não vacina, interpretar exame, saber se tem uma
doença". A spec e o texto da resposta só cobrem o remédio.

## Goals / Non-Goals

**Goals:**

- O texto de conduta faz sentido para pedido de remédio, de diagnóstico e de
  interpretação de exame.
- Relato de sintoma recebe só o texto de conduta, sem veredito.

**Non-Goals:**

- Criar uma resposta padrão por subtipo de conduta. Exigiria mudar o prompt
  da fronteira, a spec e `fronteira.responder`, a três dias da demo.
- Mudar as categorias da fronteira ou o léxico `CONDUTA`.
- Tratar sintoma de pele como urgência. O léxico `SINTOMA` fica como está.

## Decisions

### D1. Texto único de conduta, sem citar remédio

O requirement passa a dizer "conduta pessoal ou diagnóstico", e os textos
ficam assim:

- Web: abre com "sinto muito que você esteja passando por isso" e "queria
  poder ajudar mais", diz que a Dona Checa não receita,
  não dá diagnóstico e não indica tratamento, e diz que só quem examina a
  pessoa sabe o que ela tem. Mantém o aviso sobre mudar remédio por conta
  própria e fecha com a UBS: "eles vão saber te ajudar".
- WhatsApp: mesma mudança, no formato do canal.

As obrigações do cenário atual continuam: nenhum parecer, a declaração de que
só confere informação, o aviso de risco, a UBS e "meu bem" no máximo uma vez.
A frase "não posso indicar nem mudar tratamento", que o teste de página
procura, fica no texto.

A primeira versão abria com "entendo a sua preocupação" e soou ríspida no
teste do grupo em 13/10/2026, para quem conta que está passando mal. O
acolhimento ("sinto muito", "queria poder ajudar mais") entra antes da
recusa. "Passando por isso" serve também para quem pergunta de remédio ou de
outra pessoa.

### D2. Relato de sintoma não é alegação

A regra do prompt da extração ganha uma frase depois da regra da pergunta:

> Relato de sintoma ou do estado de saúde de alguém ("Estou com bolinhas no
> corpo", "Meu vizinho está doente?") não é alegação. Se o relato trouxer uma
> afirmação ("Estou com dor de cabeça, chá de boldo resolve?"), a alegação é
> a afirmação ("Chá de boldo resolve dor de cabeça.").

Sem alegação, o fluxo para na extração. Com a fronteira em conduta, a página
já mostra o texto de conduta no lugar de `sem_alegacao` (D2 de
`fix-pergunta-e-conduta`). Nenhum código de fluxo muda.

A regra fica no prompt, sem conferência em código. Diferente da pergunta (D5
de `fix-pergunta-e-conduta`), relato não tem marca de superfície confiável
como o "?".

### D3. Casos novos na bancada

- `C3`: "Estou com bolinhas no corpo", esperado fronteira
  `conduta_individual` e `verificavel: false`.
- `C4`: "Estou com dor de cabeça, chá de boldo resolve?", esperado
  verificável, alegação contendo "boldo". Sem expectativa de fronteira: a
  mensagem pode sair como checagem ou como conduta, e as duas servem, porque
  com conduta a página mostra o texto de conduta junto com a checagem.

## Risks / Trade-offs

- [A extração deixa de checar uma afirmação dita junto com um relato] → o
  exemplo positivo fica no prompt, e o caso `C4` cobre esse risco.
- [O texto genérico perde o acolhimento específico da dúvida sobre remédio]
  → o aviso sobre mudar remédio por conta própria continua no texto.
- [Regravar a bancada] → uma rodada real; os critérios de D10 de
  `add-gerador-api-deepseek` valem para ela.

## Resultado

- **Bancada real** de 13/10/2026 (`20261013-151311.json`, `deepseek-v4-pro`):
  30/32, sem falha eliminatória. Cumpre D10 de `add-gerador-api-deepseek`,
  com 2 das 3 falhas permitidas. C3 e C4 passaram. As falhas foram de forma,
  fora deste change: F06, com o bloco 2 sem separar a opinião, e R2, que saiu
  na forma sem evidência. As gravações dessa rodada são as da bancada offline.
- **Bancada offline** com as gravações novas: mesmo resultado, 30/32.
