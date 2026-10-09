# Design: Notebook de execução e avaliação do modelo

## Context

Motivação em `proposal.md`. Medições de origem: `afericao_multilingual-e5-base.json`
e `varredura_alfa_multilingual-e5-base.json` (`prototipo/indice/`), relatórios de
`datasets/derivados/`, `prototipo/relatorio_sonda_*.json` e
`datasets/relatorios_mvp_copiloto/relatorios_metricas.json`.

## Goals / Non-Goals

**Goals:**

- Um avaliador com o índice local roda o notebook do início ao fim e obtém
  Recall@k, MRR, latência e a validação leave-one-out de alfa.
- O notebook mostra lado a lado o número recalculado e o número versionado.

**Non-Goals:**

- Reexecutar sondas do gerador ou a bancada ponta a ponta: exigem Ollama ou
  chave de API. O notebook lê os relatórios dessas execuções.
- Front-end, API ou interface (fora do pedido dos mentores).

## Decisions

### D1. Reaproveitar a CLI, não reimplementar

O notebook importa `carregar` de `prototipo.rag.__main__` e as funções de
`prototipo.rag.afericao`. Métrica calculada de outro jeito no notebook poderia
divergir da medida registrada sem ninguém notar.

### D2. Não gravar

`aferir` e `varrer-alfa` da CLI sobrescrevem os JSONs versionados. O notebook
chama as funções e guarda o resultado só em memória, para que a comparação
com o versionado continue possível.

### D3. Índice ausente

Os `.npy`, `.jsonl` e `vocabulario.json` não são versionados. Sem eles, a
célula de carga para com a instrução `python -m prototipo.rag construir`; as
seções que só leem relatórios versionados continuam executáveis.

## Risks / Trade-offs

- [Latência varia por máquina] → o notebook mostra a latência medida e avisa
  que a referência foi tomada num MacBook Air M4.
- [Índice local de outra versão] → `conferir_indice` já para a carga quando
  matriz e fragmentos divergem (decisão 16 de `mvp-copiloto-verificacao`).
