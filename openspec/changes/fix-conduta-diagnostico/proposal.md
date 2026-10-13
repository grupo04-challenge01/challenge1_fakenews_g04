# Proposal: Conduta que cobre diagnóstico e relato de sintoma sem checagem

**Fase do CBL:** Showcase. Change aberto em 13/10/2026, a partir do teste da
demo no modo uso com a DeepSeek. Corrige código do Act antes da tag
`showcase-demo` (decisão D5 de `add-portfolio-showcase`).

## Why

Duas mensagens receberam o texto de conduta, que começa com "eu entendo a
dúvida sobre esse remédio", sem que nenhuma das duas falasse de remédio:

1. **"o vitor ta doente?"** A fronteira classificou a mensagem como conduta
   individual. Saiu só o texto de conduta, que fala de remédio.
2. **"estou com bolinhas no corpo"** Também saiu como conduta individual. Saiu
   o mesmo texto de remédio e, depois dele, uma checagem do próprio relato,
   com o veredito "Evidência insuficiente. Não encontramos estudos sobre
   bolinhas no corpo."

As regras da fronteira não marcam nada nas duas mensagens. Quem marca a
conduta é o modelo, e ele segue o prompt: a categoria `conduta_individual`
inclui "saber se tem uma doença" e "interpretar exame". A classificação está
certa. O defeito está em dois pontos:

- A categoria tem uma única resposta padrão, e o texto dessa resposta só fala
  de remédio. O requirement "Recusa de orientação clínica individual" também
  só cita medicamento e tratamento, embora o prompt cubra diagnóstico e exame.
- A extração tratou o relato de um sintoma como alegação. Quem conta o que
  sente não está repassando uma informação, e um veredito sobre o relato não
  tem sentido.

## What Changes

- **MODIFICADO (spec)** `fronteira-orientacao-saude`: o requirement "Recusa
  de orientação clínica individual" passa a cobrir pedido de diagnóstico e de
  interpretação de exame. As respostas padrão, web e WhatsApp, deixam de citar
  "esse remédio" e passam a valer para os três casos.
- **MODIFICADO (prompt)** extração: relato de sintoma ou do estado de saúde de
  alguém não é alegação. Relato que traz uma afirmação ("Estou com dor de
  cabeça, chá de boldo resolve?") continua com a afirmação como alegação.
- **NOVO (dados)** dois casos na bancada: `C3` ("Estou com bolinhas no
  corpo", conduta sem checagem) e `C4` (relato com afirmação, checado).

## Capabilities

### Modified Capabilities

- `fronteira-orientacao-saude`: "Recusa de orientação clínica individual"
  cobre diagnóstico e exame, com texto novo.
- `verificacao-alegacao`: "Extração da alegação verificável" ganha o cenário
  de relato de sintoma.

As duas requirements também são modificadas por changes ainda não
arquivados: a recusa por `add-identidade-dona-checa`, e a extração por
`fix-qualidade-gerador-remoto` e `fix-pergunta-e-conduta`. Este change
arquiva depois deles.

## Impact

- Muda o prompt da extração: as gravações da bancada precisam ser refeitas,
  com uma rodada real (cerca de US$ 0,05).
- Nenhum código de fluxo muda. Sem alegação, o fluxo já para na extração e
  mostra o texto de conduta (D2 de `fix-pergunta-e-conduta`).
- Vale para os dois geradores.
