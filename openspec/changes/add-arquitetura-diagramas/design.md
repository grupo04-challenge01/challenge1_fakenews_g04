# Design: Arquitetura em diagramas

## Context

Motivação em `proposal.md`. Os fatos dos diagramas saem do código da branch
`showcase-entrega-final` em 15/10/2026: `interface/`, `bancada/pipeline.py`,
`prototipo/` e `prototipo/indice/manifesto.json`.

## Goals / Non-Goals

**Goals:**

- Quem abre a página entende a arquitetura pelos diagramas, sem ler prosa.
- Todo componente, número e limiar do diagrama existe no código citado.

**Non-Goals:**

- Mudar código ou comportamento do protótipo.
- Hospedar o chat em produção (change próprio).

## Decisions

### D1. Mermaid no Markdown, não imagem exportada

O diagrama fica no próprio `.md`, versionado e revisável em diff. O
mkdocs-material renderiza Mermaid nativamente com `pymdownx.superfences`, que
o CI já instala junto com `mkdocs-material`.

Alternativa descartada: imagens PNG, como no exemplo do Dulce. Imagem
desatualiza sem aparecer no diff.

### D2. Fluxograma estilizado, não a sintaxe `C4Context`

Os níveis de contexto e contêineres seguem o modelo C4, mas desenhados como
`flowchart` com `subgraph` e `classDef`. A sintaxe C4 do Mermaid é
experimental e posiciona mal os elementos.

### D3. Cada diagrama cita a origem

Abaixo de cada diagrama, uma linha com os arquivos de onde ele saiu. Mesmo
critério do portfólio: número sem origem não entra.

### D4. Slides apontam para os diagramas

Os slides 4, 5 e 7 reaproveitam os diagramas da página nova, para que slide e
portfólio não divirjam.
