# Proposal: Notebook de execução e avaliação do modelo

**Fase do CBL:** Act. Change aberto em 09/10/2026 para o entregável da semana
pedido pelos mentores (prazo 09/10, 23h59).

## Why

O entregável pede um notebook que carregue, execute e avalie o modelo, com as
métricas de desempenho, e o modelo salvo. O projeto não treina modelo
(`openspec/project.md`, revisão de 10/09/2026): o artefato equivalente é o
índice de recuperação (`prototipo/indice/`), montado sobre modelos
pré-treinados sem ajuste. As medições existem, mas espalhadas em JSONs de
aferição, relatórios de tratamento e relatórios de sonda, e a aferição só roda
pela CLI. Falta um ponto único que um avaliador execute e leia.

## What Changes

- **NOVO** `exploracao/avaliacao_modelo.ipynb`: carrega o índice pelo mesmo
  `carregar()` da CLI, reexecuta `aferir_tudo` e `varrer_alfa` sobre as 20
  consultas, compara com as medições versionadas, mostra uma busca de exemplo
  e reúne as métricas de preparação de dados, das sondas e do piloto.
- **NOVO** `requirements-notebook.txt`: `nbformat`, `nbclient`, `ipykernel` e
  `matplotlib`, por cima de `requirements-rag.txt`.
- Nenhum código de `prototipo/` ou `tratamento/` muda. O notebook só chama
  funções existentes e lê arquivos versionados; não grava nada no repositório.

## Capabilities

### New Capabilities

- `avaliacao-modelo`: execução reprodutível da avaliação do mecanismo de
  recuperação e consolidação das métricas para entrega.
