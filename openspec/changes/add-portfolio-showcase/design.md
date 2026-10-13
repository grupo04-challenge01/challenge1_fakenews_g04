# Design: Portfólio atualizado para o Showcase

## Context

Motivação em `proposal.md`. Fontes dos números: `tasks.md` de cada change em
`origin/main`, `openspec validate --all --strict`, `pytest`, os `design.md`
dos changes do Act (rodadas da bancada), `exploracao/avaliacao_modelo.ipynb`,
`prototipo/relatorio_sonda_*.json`, `prototipo/indice/manifesto.json` e
`datasets/relatorios_mvp_copiloto/relatorios_metricas.json`.

## Goals / Non-Goals

**Goals:**

- Quem abre o site sabe em um minuto o que existe, o que falta e o que foi
  medido.
- Todo número do site aponta para o arquivo de onde saiu.

**Non-Goals:**

- Reexecutar a bancada ou as sondas. O site cita rodadas já registradas.
- Reescrever as páginas das fases Engage e Investigate, que seguem corretas.

## Decisions

### D1. Histórico preservado, não apagado

O texto de `estado.md` até 01/10 vira a seção «Histórico», com os títulos
rebaixados um nível. Ele registra achados que não estão em outro lugar, como o
caso 05 reclassificado e o `ALFA_PADRAO` de 0,5.

Alternativa descartada: apagar e deixar a história no `git log`. Quem lê o
site não lê o `git log`.

### D2. Uma página para o protótipo, separada do guia do chat

`docs/interface/chat-web.md` ensina a subir o chat. A página nova explica o
que o protótipo faz e o que foi medido. Misturar as duas deixaria o guia
operacional longo demais para quem só quer subir o servidor.

### D3. Limitações e simulação declaradas no site

O site declara que o protocolo do CEP e a emenda 01 são simulados, como o
próprio dossiê declara, e lista o que o protótipo não faz. A métrica primária
é ganho de discernimento, e o piloto tem n = 2. Apresentar o resultado sem
esses limites seria veredito nu sobre o próprio projeto.

### D4. Piloto confirmado pelo grupo

As duas sessões de 08/10/2026 contam como o piloto da task 6.6 do MVP, por
confirmação do grupo em 13/10/2026. O site registra o resultado com a ressalva
de n = 2, que o notebook de avaliação já fazia.

## Risks / Trade-offs

- [O site envelhece de novo até 16/10] → a data de atualização fica no topo de
  `estado.md` e `pendencias.md`.
- [Número citado diverge da fonte] → cada número no site cita o arquivo ou a
  rodada de origem.
