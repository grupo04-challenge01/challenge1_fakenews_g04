# Proposal: Arquitetura em diagramas

**Fase do CBL:** Showcase. Change aberto em 15/10/2026, semana 6.

## Why

Na devolutiva de 15/10/2026, o mentor da residência pediu que a apresentação
tenha menos texto e mais diagramas arquiteturais detalhados. Ele citou como
referência a página de arquitetura do projeto Dulce
(<https://dulce-work-schedule.github.io/especificacao/arquitetura.html>).

O portfólio descreve o protótipo em prosa. Em
`docs/act/prototipo-avaliacao.md` e `docs/act/relatorio-tecnico.md`, o fluxo,
a recuperação e a guarda aparecem como listas e parágrafos. Não há diagrama de
contexto, de contêineres, de sequência nem de implantação. O único bloco
`mermaid` do site, em `docs/engage/portfolio-engage.md`, não renderiza, porque
o `mkdocs.yml` não declara o fence `mermaid`.

Os slides 4, 5 e 7 de `docs/showcase/apresentacao.md` são listas de cinco a
seis itens. A banca é em 16/10/2026.

## What Changes

- `mkdocs.yml`: `pymdownx.superfences` com fence `mermaid`, para os diagramas
  renderizarem no site.
- `docs/arquitetura.md`, página nova: diagramas de contexto, contêineres,
  fluxo das sete etapas, sequência de `POST /verificar`, recuperação híbrida,
  guarda e resposta, pipeline de dados, avaliação, implantação e pacotes. Cada
  diagrama tem legenda curta e aponta para o código de onde saiu.
- `docs/showcase/apresentacao.md`: slides 4, 5 e 7 passam a ter um diagrama
  como conteúdo principal, com no máximo três frases de apoio.
- `mkdocs.yml`: página nova na nav.

## Impact

- Só documentação. Nenhum código do protótipo muda.
- O diagrama de implantação mostra o estado de 15/10 (servidor local). A
  hospedagem pública fica para um change próprio; quando ele entrar, o
  diagrama é atualizado nele.
