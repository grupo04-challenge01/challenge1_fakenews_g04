# Tasks — fix-resposta-sem-evidencia

Change de correção. Bloqueia a task 3.2 de `mvp-copiloto-verificacao`.

## 1. Decisão e registro

- [x] 1.1 Escolher entre forma própria e catálogo condicional, com o motivo
      registrado — **saída A**, decisão 1 do `design.md`, 19/09/2026
- [x] 1.2 Reescrever o requirement da estrutura de quatro blocos com as duas
      formas declaradas e a proibição de trocá-las
- [x] 1.3 Condicionar a obrigação do catálogo de técnicas à forma com evidência,
      tratando técnica nomeada sem evidência como defeito
- [x] 1.4 Especificar a lacuna de acervo como resposta distinta, com o ponteiro
      no bloco 4 e a vedação de afirmar ausência de checagem no mundo
- [x] 1.5 Registrar o terceiro estado — pauta ausente do acervo **e** do índice —
      medido em 19/09 (`oropouche` e `semaglutida` em zero nos dois níveis)

## 2. Conciliação com as capabilities vizinhas

- [ ] 2.1 Conferir a forma sem evidência contra o teto de 120 palavras de
      `acessibilidade-leitura`, medindo respostas reais em vez de estimar
- [ ] 2.2 Conferir contra `recuperacao-evidencia` que nenhum bloco da forma sem
      evidência induz afirmação sem trecho de origem
- [ ] 2.3 Conferir contra `fronteira-orientacao-saude` que a forma sem evidência
      não vira porta de conduta clínica: sem evidência recuperada, pedido de
      conduta continua sendo recusado antes da verificação
- [ ] 2.4 Levar o terceiro estado à task 8.2 de `add-ampliacao-corpus-ptbr`, que
      prevê três casos de teste de lacuna e precisa deste como o terceiro

## 3. Verificação

- [ ] 3.1 Sondar o gerador local nos três estados, no formato da sonda de 18/09
      — três tentativas por estado, resultado por tentativa, com `think: false`
- [ ] 3.2 Confirmar que a sonda T1 deixa de degenerar, que era o defeito que
      abriu este change
- [ ] 3.3 Teste que reprova resposta com técnica nomeada sob `evidência
      insuficiente`
- [x] 3.4 `openspec validate fix-resposta-sem-evidencia --strict` limpo
