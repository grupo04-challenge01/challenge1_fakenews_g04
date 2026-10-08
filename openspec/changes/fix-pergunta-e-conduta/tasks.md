# Tasks: Pergunta como alegação e conduta sem alegação

TDD em toda task de código: teste falhando primeiro, depois a implementação.

## 1. Extração

- [x] 1.1 Teste de que o prompt traz a regra de D1, com os exemplos positivo e
      negativo; frase nova no `SISTEMA` da extração

## 2. Conduta sem alegação

- [x] 2.1 Teste em `interface/tests/test_fluxo.py`: fronteira em conduta e
      extração sem alegação emitem `aviso` com o texto de conduta, sem
      `sem_alegacao`; implementação de D2
- [x] 2.2 Teste de página: o texto de conduta aparece como bolha da Dona Checa

## 3. Fronteira

- [x] 3.1 Testes do léxico `FERIMENTO` (D4): cada verbo vira risco imediato,
      e "corte de enxada se cura com…" não; implementação
- [x] 3.2 Teste de que o prompt da fronteira cita ferimento recente; frase nova

## 4. Bancada

- [x] 4.1 Casos `P1`, `C1` e `C2` em `bancada/casos.json` (D3)
- [ ] 4.2 Rodada real com o gerador padrão, que também regrava a bancada: P1,
      C1 e C2 passam, e a rodada cumpre D10 de `add-gerador-api-deepseek`
- [ ] 4.3 Suíte inteira verde e `openspec validate fix-pergunta-e-conduta --strict`
