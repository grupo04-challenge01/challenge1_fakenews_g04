# Proposal: Engage — Desinformação em Saúde Pública

## Why

O Challenge 1 foi entregue ao grupo como enunciado aberto: uma Big Idea, uma
Essential Question e um roadmap de seis semanas. Nada disso é acionável sem
que o grupo defina o que vai investigar, com que método, e como saberá que
investigou bem.

Há um risco concreto de partir direto para a solução. A leitura literal do tema
("fake news" + "IA") sugere um classificador de veracidade, e existem datasets
públicos abundantes que empurram nessa direção. Mas o que a Essential Question
descarta é a substituição do pensamento crítico, e o que substitui pensamento
crítico é o **veredito nu**: conclusão sem raciocínio e sem proveniência, que o
usuário só pode aceitar ou recusar. É nele que o classificador de veracidade
desemboca. Sem uma decisão registrada agora, o viés dos dados disponíveis decide
o projeto pelo grupo.

Este change existe para fixar, antes de qualquer desenvolvimento, três coisas:
o recorte do problema, o método de investigação, e os critérios que tornam os
artefatos da fase Engage aceitáveis.

## What Changes

Introduz três capabilities de pesquisa, todas entregáveis até 11/09:

- **`pesquisa-investigativa`** — protocolo de análise forense de casos de
  desinformação em saúde, com ficha padronizada e medição de esforço.
- **`matriz-confianca`** — estrutura de avaliação de confiança: dimensões,
  sinais observáveis, limites e rubrica. É o primeiro dos entregáveis finais
  do desafio a ganhar forma.
- **`guiding-questions`** — backlog priorizado de perguntas norteadoras que
  define o escopo das semanas 2–3.

Fixa também duas decisões de escopo que restringem todos os changes futuros:

- Recorte temático em **saúde pública**.
- Condição sobre o veredito: permitido, nunca como saída única. Todo veredito
  vem acompanhado do critério que o sustenta e é auditável até a fonte
  (ver `openspec/project.md`).

## Impact

- **Specs afetadas:** nenhuma. `openspec/specs/` está vazio; as três
  capabilities são novas.
- **Entregáveis do desafio atingidos:** portfólio de pesquisa (parcial),
  estrutura de avaliação de confiança (versão 1).
- **Restrição herdada por changes futuros:** auditabilidade até a fonte e
  transferência como métrica primária restringem o desenho do produto. Aplicada
  em `mvp-copiloto-verificacao` — os nomes `add-copiloto-leitura-lateral` e
  `add-rag-evidencia-primaria`, previstos aqui, foram substituídos por esse
  change único.
- **Risco de reversão:** se a fase Investigate demonstrar que o andaime
  cognitivo não produz ganho mensurável de discernimento, a restrição de
  produto será reaberta em um change de revisão, não silenciosamente
  abandonada.

## Out of Scope

Fora deste change, por serem prematuros no dia 1:

- Arquitetura do protótipo, escolha de modelo, pipeline de RAG.
- Sub-recorte definitivo dentro de saúde (vacinação, crônicas, suplementos).
- Construção do instrumento de avaliação em PT-BR — ~~vai para
  `add-instrumento-avaliacao-ptbr`, na fase Investigate~~. **Revisto em
  20/09/2026:** o change não será aberto; a responsabilidade fica com a
  capability `avaliacao-instrumento` de `mvp-copiloto-verificacao`, que já
  cobre o escopo inteiro. Ver a nota de decisão no `design.md`.
- Qualquer treino de modelo.
