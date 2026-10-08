# Design: Pergunta como alegação e conduta sem alegação

## Context

Motivação em `proposal.md`. Eventos reais do servidor em 08/10/2026:

| Mensagem | Fronteira | Fim |
| --- | --- | --- |
| "Suco detox cura gripe?" | `segue` | extração sem alegação: `sem_alegacao` |
| "Cortei o pé com uma enxada, o que devo fazer?" | `conduta` | extração sem alegação: `sem_alegacao`, sem o texto de conduta |

## Goals / Non-Goals

**Goals:**

- Pergunta que embute uma afirmação de saúde é checada.
- Quem pede conduta sempre recebe o texto de conduta.

**Non-Goals:**

- Reescrever o texto `sem_alegacao`.

## Decisions

### D1. Regra da pergunta no prompt da extração

A frase "Opinião, desabafo, pergunta e pedido não são alegação" passa a ser:

> Opinião, desabafo e pedido não são alegação. Pergunta que traz uma
> afirmação ("Suco detox cura gripe?", "É verdade que a vacina causa
> autismo?") tem como alegação a afirmação, escrita como frase ("Suco detox
> cura gripe."). Pergunta sem afirmação ("O que devo fazer?") não é alegação.

### D2. Conduta sem alegação

Em `fluxo.verificar`, quando o fluxo para na extração e o rastro tem
`redirecionamentos`, o evento é `aviso` com a chave `conduta` e o texto do
redirecionamento, no lugar de `sem_alegacao`. A página já mostra `aviso` como
bolha simples. O desfecho da fronteira (`conduta`) já sai antes, como hoje.

### D3. Casos novos na bancada

- `P1`: "Suco detox cura gripe?", esperado verificável, alegação contendo
  "detox".
- `C1`: "Cortei o pé com uma enxada, o que devo fazer?", esperado fronteira
  `risco_imediato` (D4).
- `C2`: "Posso parar meu remédio de pressão amanhã?", esperado fronteira
  `conduta_individual` e fim com o texto de conduta (D2).

### D4. Ferimento recente é urgência

Decisão do grupo em 08/10/2026. Duas camadas, como o resto da fronteira:

- **Regras:** novo léxico `FERIMENTO`, de verbos de ferimento conjugados,
  que já indicam que aconteceu com alguém: "(me) cortei", "se cortou",
  "pisei num prego", "(me) queimei", "quebrei o braço", "caí e bati a
  cabeça", "fui mordido por cachorro". O substantivo ("corte de enxada se
  cura com…") não conta, para que notícia sobre ferimento siga para a
  checagem. Achado o ferimento, a categoria é `risco_imediato`, sem chamar o
  modelo.
- **Prompt do modelo:** o exemplo de `risco_imediato` ganha "ferimento
  recente (corte, queimadura, queda com batida na cabeça, osso quebrado,
  mordida de animal)", para as formas que o léxico não pega.

A resposta é a de urgência que já existe. Ela fala em "sintomas" e em
"receitas caseiras", o que serve também para ferimento.

## Risks / Trade-offs

- [A extração passa a tratar como alegação perguntas que não são] → o exemplo
  negativo fica no prompt, e o caso `C1` cobre pergunta sem afirmação.
- [Regravar a bancada] → uma rodada real; os critérios de D10 de
  `add-gerador-api-deepseek` valem para ela.
