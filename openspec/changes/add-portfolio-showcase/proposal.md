# Proposal: Portfólio atualizado para o Showcase

**Fase do CBL:** Showcase. Change aberto em 13/10/2026, semana 6.

## Why

O portfólio de pesquisa é o site publicado a partir de `docs/` no GitHub
Pages, e é um dos quatro entregáveis finais. Em 13/10/2026 ele estava parado
em 01/10:

- `docs/estado.md` e `docs/pendencias.md` contavam 6 changes e 23 tasks
  pendentes, quando a `main` já tinha 15 changes e só 2 tasks abertas;
- nenhuma página explicava o protótipo como ele ficou nem reunia os números
  da avaliação;
- `docs/visao-geral.md` ainda dizia que o sub-recorte estava em aberto e que
  «identificar vieses» não tinha cobertura;
- `mkdocs.yml` apontava o `repo_url` para um fork, não para a organização.

O Showcase não tinha change, e a metodologia pede um por fase.

## What Changes

- `docs/estado.md`: resumo do estado em 13/10, tabela dos 16 changes e
  entregas de 02/10 a 13/10. O registro até 01/10 vira a seção «Histórico».
- `docs/pendencias.md`: reescrita com as tasks abertas, o bloqueio de
  `add-cobertura-alegacao-ampla`, a ordem de arquivamento, as decisões em
  aberto e as limitações conhecidas do protótipo.
- **NOVO** `docs/act/prototipo-avaliacao.md`: fluxo, modelos, índice e os
  números de recuperação, bancada, sondas, testes e piloto.
- `docs/index.md` e `docs/visao-geral.md`: situação atual, sub-recorte,
  calendário com datas e cobertura parcial de vieses.
- `mkdocs.yml`: página nova na nav e `repo_url` da organização.
- `openspec/project.md`: tabela de changes atualizada.
- `mvp-copiloto-verificacao`, task 6.6: marcada com a evidência do piloto de
  08/10/2026, confirmado pelo grupo em 13/10/2026.

## Capabilities

### New Capabilities

- `portfolio-showcase`: o portfólio publicado reflete o estado do repositório
  na data declarada, com números rastreáveis até o arquivo de origem e
  limitações declaradas.

### Modified Capabilities

Nenhuma.

## Impact

- **Entregável final atingido:** portfólio de pesquisa. Indiretamente,
  apresentação e reflexão, que passam a ter onde buscar os números.
- Nenhum código de `prototipo/`, `interface/`, `bancada/` ou `tratamento/`
  muda.
- O deploy do site roda no merge para a `main` (`.github/workflows/deploy.yml`).

## Out of Scope

- A apresentação e a reflexão em si. Entram neste change em tasks próprias,
  quando o grupo definir o formato.
- Arquivar changes ou promover specs para `openspec/specs/`.
- Desbloquear `add-cobertura-alegacao-ampla`.
- Corrigir `NAO_LIGADO` em `bancada/pipeline.py`, que ainda lista a 1.6 como
  desligada. É código e pede change próprio.
