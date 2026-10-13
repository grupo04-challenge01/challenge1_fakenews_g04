# Tasks: Recusa por tipo de pedido e relato de sintoma sem checagem

TDD em toda task de código: teste falhando primeiro, depois a implementação.

## 1. Textos da fronteira

- [x] 1.1 Teste de que a resposta de `conduta_individual`, web e WhatsApp, não
      cita "esse remédio" e traz a recusa inteira em negrito; texto de D1 no
      delta da spec
- [x] 1.2 Teste de página: o texto de conduta continua aparecendo como bolha
      da Dona Checa

## 2. Extração

- [x] 2.1 Teste de que o prompt traz a regra de D2, com os exemplos positivo e
      negativo; frase nova no `SISTEMA` da extração

## 3. Categorias novas

- [x] 3.1 Testes das respostas de `diagnostico` (D4) e `informacao_geral`
      (D5), lidas da spec; requirements novos no delta
- [x] 3.2 Teste de que o prompt da fronteira traz as duas categorias, com os
      exemplos; `CATEGORIAS` e `SISTEMA` novos
- [x] 3.3 Testes de D6: uma recusa só, na ordem; redirecionamento no pipeline
      e desfecho `conduta` no fluxo para as três; implementação

## 4. Bancada

- [x] 4.1 Casos `C3`, `C4`, `V1` e `V2` em `bancada/casos.json` (D3)
- [x] 4.2 Rodada real com `--gerador deepseek`, que também regrava a bancada:
      C3, C4, V1 e V2 passam, e a rodada cumpre D10 de
      `add-gerador-api-deepseek`
- [x] 4.3 Suíte inteira verde e `openspec validate fix-conduta-diagnostico --strict`
- [x] 4.4 Teste e implementação de D7: vacina fora do léxico de conduta; caso
      `V3` em `bancada/casos.json`
- [ ] 4.5 Rodada real do caso `V3` com `--gerador deepseek`, que grava o caso:
      fronteira `informacao_geral`
