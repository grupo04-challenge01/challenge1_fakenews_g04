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

Ainda em 13/10, a revisão do que falta para a apresentação de 16/10 achou
riscos que o portfólio sozinho não resolve:

- não havia versão definida para a demonstração. O branch
  `act-cobertura-alegacao-ampla` liga a cobertura ampla por padrão, e o
  change dele está bloqueado pelo caso jacaré;
- o chat lê textos da interface, da fronteira e da identidade de
  `openspec/changes/` em tempo de execução. Arquivar um change antes da
  apresentação muda esses caminhos;
- não havia roteiro de demo. O índice denso só carrega na primeira consulta,
  e a falha de carga do índice não derruba o servidor;
- os relatórios da bancada estão no `.gitignore` e só existem na máquina de
  quem rodou;
- o `README.md` tinha duas linhas, e o guia do chat cita latência e custo
  anteriores às rodadas de 09/10 em diante;
- a apresentação e a reflexão não tinham task.

Em 15/10 saíram as orientações da coordenação para a apresentação final de
16/10. Elas pedem quatro coisas, e a revisão contra o repositório achou
lacunas em três:

- **vídeo explicativo** de até 5 minutos no YouTube, com todos os integrantes,
  cobrindo contexto e problema, produto, IA, desafios e resultados. Não havia
  roteiro nem task;
- **entrega final versionada** com datasets, requisitos, EDA, Guiding
  Questions, organização e papéis, modelo de IA com relatório técnico,
  descrição final do produto, código e README com link do repositório.
  Faltavam no repositório a organização e os papéis, o relatório técnico (que
  existia só como HTML fora do git) e o link do próprio repositório no README;
- **estande** com o produto funcionando na mídia de destino, com pelo menos
  dois integrantes. A demo só tinha sido preparada para `127.0.0.1`;
- **apresentação para a banca** de no máximo 10 minutos, na ordem problema →
  solução → IA → demonstração → resultados. O conteúdo dos slides estava
  pensado para cerca de 15 minutos.

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
- A demonstração roda da `main`, marcada pela tag `showcase-demo`, e nenhum
  change é arquivado antes da apresentação (D5 e D6). A decisão vai para
  `docs/pendencias.md`.
- **NOVO** roteiro de demo, com preparação, aquecimento, casos e plano B (D7).
- **NOVO** tabela-resumo versionada da rodada da bancada usada na demo (D8).
- `README.md` reescrito como porta de entrada do repositório.
- `docs/interface/chat-web.md`: latência e custo das rodadas atuais.
- Limitações da avaliação completadas em `docs/pendencias.md`.
- **NOVO** slides da apresentação e texto de reflexão no portfólio.
- `mkdocs.yml`: entrada «Mapa da arquitetura» na nav do Showcase, apontando
  para `docs/mapa/arquitetura.html`, publicado por
  `add-arquitetura-diagramas` (D15).
- `docs/showcase/apresentacao.md` cortado para caber em 10 minutos, na ordem
  pedida pela coordenação (D12).
- **NOVO** `docs/showcase/organizacao.md`: como o grupo se organizou, fases,
  cadência e papéis de cada integrante (D10).
- **NOVO** `docs/act/relatorio-tecnico.md`: o relatório técnico consolidado,
  convertido do HTML v3 e com os números conferidos contra o portfólio (D11).
- **NOVO** `docs/showcase/roteiro-video.md`: roteiro do vídeo de até 5 minutos
  com a fala de cada integrante (D13).
- `README.md`: link do repositório, link do vídeo e tabela que mapeia cada
  item da entrega final ao artefato (D9).
- `docs/showcase/roteiro-demo.md`: preparação do estande na mídia de destino
  (D14).

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
- O merge de `act-cobertura-alegacao-ampla` na `main` fica suspenso até depois
  da apresentação.
- O deploy do site roda no merge para a `main` (`.github/workflows/deploy.yml`).

## Out of Scope

- Arquivar changes ou promover specs para `openspec/specs/`. Fica para depois
  da apresentação de 16/10 (D6).
- Corrigir código para a demo: timeout do cliente Ollama, veredito sem blocos
  de critério quando a saída do modelo não é JSON, `.env.example` e nome das
  agências na exibição. Pede um change `fix-*` próprio.
- Desbloquear `add-cobertura-alegacao-ampla`.
- Deploy público da demo. O estande usa a máquina do grupo, com
  `DONA_CHECA_HOST=0.0.0.0` quando a mídia for o celular na rede local; o
  servidor já suporta isso sem mudar código.
- Corrigir `NAO_LIGADO` em `bancada/pipeline.py`, que ainda lista a 1.6 como
  desligada. É código e pede change próprio.
