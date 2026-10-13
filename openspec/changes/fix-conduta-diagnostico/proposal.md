# Proposal: Recusa por tipo de pedido e relato de sintoma sem checagem

**Fase do CBL:** Showcase. Change aberto em 13/10/2026, a partir do teste da
demo no modo uso com a DeepSeek. Corrige código do Act antes da tag
`showcase-demo` (decisão D5 de `add-portfolio-showcase`).

## Why

Três mensagens receberam o texto de conduta, que começa com "eu entendo a
dúvida sobre esse remédio", sem que nenhuma falasse de remédio:

1. **"o fulano tá doente?"** (com o nome de uma pessoa) A fronteira
   classificou a mensagem como conduta individual. Saiu só o texto de
   conduta, que fala de remédio.
2. **"estou com bolinhas no corpo"** Também saiu como conduta individual. Saiu
   o mesmo texto de remédio e, depois dele, uma checagem do próprio relato,
   com o veredito "Evidência insuficiente. Não encontramos estudos sobre
   bolinhas no corpo."
3. **"Com quantos anos tenho que tomar a vacina tetra-valente?"** Achada com
   a primeira versão deste change, que já trazia um texto único de conduta
   com "sinto muito que você esteja passando por isso". Para uma pergunta de
   calendário de vacina, o acolhimento não faz sentido, e a recusa de
   "receitar" também não: a resposta é informação pública.

As regras da fronteira não marcam nada nas três mensagens. Quem marca a
conduta é o modelo, e ele segue o prompt: a categoria `conduta_individual`
inclui "tomar ou não vacina", "interpretar exame" e "saber se tem uma
doença". O defeito está em três pontos:

- A categoria junta pedidos diferentes e tem uma única resposta padrão. Um
  texto só não serve ao mesmo tempo para quem pede para trocar de remédio,
  para quem conta que está passando mal e para quem pergunta a idade de uma
  vacina.
- Não há categoria para pergunta geral de saúde, que não é boato para checar
  nem pedido de decisão para um caso.
- A extração tratou o relato de um sintoma como alegação. Quem conta o que
  sente não está repassando uma informação, e um veredito sobre o relato não
  tem sentido.

## What Changes

- **MODIFICADO (spec)** `fronteira-orientacao-saude`: "Recusa de orientação
  clínica individual" cobre remédio, tratamento, vacina e exame, com texto
  que não cita "esse remédio" e abre com "entendo a sua dúvida".
- **NOVO (spec, prompt e código)** categoria `diagnostico` na fronteira:
  relato de sintoma ou pergunta se alguém tem uma doença. Resposta própria,
  que abre com "sinto muito que você esteja passando por isso" e indica a UPA
  ou o SAMU (192) se piorar.
- **NOVO (spec, prompt e código)** categoria `informacao_geral` na
  fronteira: pergunta geral de saúde, como idade de vacina. A resposta não
  dá o dado e indica a UBS e o Disque Saúde (136).
- **MODIFICADO (código)** só uma das três recusas aparece por mensagem, na
  ordem conduta, diagnóstico, pergunta geral. As três seguem o fluxo como a
  conduta já seguia.
- **MODIFICADO (prompt)** extração: relato de sintoma ou do estado de saúde de
  alguém não é alegação. Relato que traz uma afirmação ("Estou com dor de
  cabeça, chá de boldo resolve?") continua com a afirmação como alegação.
- **NOVO (dados)** quatro casos na bancada: `C3`, `C4`, `V1` e `V2`.

## Capabilities

### Modified Capabilities

- `fronteira-orientacao-saude`: "Recusa de orientação clínica individual"
  muda de texto; entram "Acolhimento em relato de sintoma e pedido de
  diagnóstico" e "Encaminhamento de pergunta geral de saúde".
- `verificacao-alegacao`: "Extração da alegação verificável" ganha o cenário
  de relato de sintoma.
- `interface-chat-web`: "Mensagem sem alegação de saúde" mostra a resposta
  da fronteira também para diagnóstico e pergunta geral.

As requirements modificadas também são modificadas por changes ainda não
arquivados: a recusa por `add-identidade-dona-checa`, a extração por
`fix-qualidade-gerador-remoto` e `fix-pergunta-e-conduta`, e a mensagem sem
alegação por `fix-pergunta-e-conduta`. Este change arquiva depois deles.

## Impact

- Mudam os prompts da fronteira e da extração: as gravações da bancada
  precisam ser refeitas, com uma rodada real (cerca de US$ 0,05).
- Vale para os dois geradores.
