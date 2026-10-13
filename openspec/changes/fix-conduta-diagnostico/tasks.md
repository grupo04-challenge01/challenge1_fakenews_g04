# Tasks: Conduta que cobre diagnóstico e relato de sintoma sem checagem

TDD em toda task de código: teste falhando primeiro, depois a implementação.

## 1. Texto de conduta

- [x] 1.1 Teste de que as respostas de `conduta_individual`, web e WhatsApp,
      não citam "esse remédio" e citam diagnóstico; textos novos de D1 no
      delta da spec
- [x] 1.2 Teste de página: o texto de conduta continua aparecendo como bolha
      da Dona Checa

## 2. Extração

- [x] 2.1 Teste de que o prompt traz a regra de D2, com os exemplos positivo e
      negativo; frase nova no `SISTEMA` da extração

## 3. Bancada

- [x] 3.1 Casos `C3` e `C4` em `bancada/casos.json` (D3)
- [x] 3.2 Rodada real com o gerador padrão, que também regrava a bancada: C3 e
      C4 passam, e a rodada cumpre D10 de `add-gerador-api-deepseek`
- [x] 3.3 Suíte inteira verde e `openspec validate fix-conduta-diagnostico --strict`
