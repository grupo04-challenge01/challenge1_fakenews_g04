# Tasks: Teto da resposta garantido em código

TDD em toda task de código: teste falhando primeiro, depois a implementação.

## 1. Corte

- [x] 1.1 Teste e implementação de D1: ordem de corte, mínimo de uma frase nos
      blocos 3 e 4, blocos 1 e 2 intactos, `cortadas` no `Resposta`
- [x] 1.2 Teste e implementação de D3: corte que cria defeito de mito é desfeito
- [x] 1.3 Teste de que o corte roda depois da nova tentativa (D2)

## 2. Bancada

- [x] 2.1 `resumo` conta quantos casos tiveram corte
- [x] 2.2 Bancada real com o gerador padrão: nenhum defeito "camada visível"
      em caso cujo bloco 3 ou 4 tinha frase sobrando
- [x] 2.3 Suíte inteira verde e `openspec validate fix-teto-resposta --strict`
