# Tasks — fix-resposta-sem-evidencia

Donos das tasks em aberto: nenhum — 13 de 13 feitas em 01/10/2026.

Divisão de 24/09/2026, por papel do artigo de MLOps (Kreuzberger et al.,
2023): R1 Breno, R2 Wingrid, R3 modelagem Vitor, R3 avaliação Jhessica,
R4+R6+R7 Samara. O nome em negrito no início de cada task em aberto é o dono
único dela. Task com dois donos é task sem dono.


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

- [x] 2.1 **Wingrid** Conferir a forma sem evidência contra o teto de 120 palavras de
      `acessibilidade-leitura`, medindo respostas reais em vez de estimar —
      conferido em `prototipo/relatorio_sonda_sem_evidencia.json` (decisão 4 do
      `design.md`, 28/09/2026): 12 de 12 respostas reais entre 65 e 85 palavras,
      todas abaixo do teto de 120 (folga mínima de 35 palavras); bloco 4 consome
      11 palavras com ponteiro e 6 sem
- [x] 2.2 **Wingrid** Conferir contra `recuperacao-evidencia` que nenhum bloco da forma sem
      evidência induz afirmação sem trecho de origem — conferido na sonda de 28/09
      (decisão 4) e conciliado na decisão 5 do `design.md` (01/10/2026): o check de
      guarda paramétrica passou nas 12 respostas reais; sob lacuna com ponteiro (E2),
      o bloco 2 atém-se à limitação do acervo interno e o veredito fica
      circunscrito ao ponteiro do bloco 4
- [x] 2.3 **Wingrid** Conferir contra `fronteira-orientacao-saude` que a forma sem evidência
      não vira porta de conduta clínica: sem evidência recuperada, pedido de
      conduta continua sendo recusado antes da verificação — conferido na decisão 5 do
      `design.md` (01/10/2026): os guardrails de conduta clínica e emergência atuam
      na entrada (pré-RAG) com recusa e bypass imediato para UBS/SAMU 192, nunca
      alcançando a geração; ademais, o bloco 3 veda prescrição alternativa
- [x] 2.4 **Samara** Levar o terceiro estado à task 8.2 de `add-ampliacao-corpus-ptbr`, que
      prevê três casos de teste de lacuna e precisa deste como o terceiro —
      já estava lá: caso `pauta_sem_correspondencia_em_nenhum_nivel`, exemplo
      `oropouche`, em `datasets/derivados/declaracao_cobertura_quatro_niveis.json`,
      e cenário «Alegação sem correspondência em nenhum nível» de `frescor-corpus`;
      remedido em 01/10 (`oropouche` e `semaglutida` em zero no FactCenter, no
      FACTCK.BR e no índice); decisão 6 do `design.md`, 01/10/2026

## 3. Verificação

- [x] 3.1 **Vitor** Sondar o gerador local nos três estados, no formato da sonda de 18/09
      — três tentativas por estado, resultado por tentativa, com `think: false`
      — decisão 4 do `design.md`, 28/09/2026
- [x] 3.2 **Vitor** Confirmar que a sonda T1 deixa de degenerar, que era o defeito que
      abriu este change — 0 de 12 respostas degeneraram; falha restante é outra
      (data de corte omitida), registrada na decisão 4
- [x] 3.3 **Wingrid** Teste que reprova resposta com técnica nomeada sob `evidência
      insuficiente` — implementado em `prototipo/resposta/catalogo.py`
      (`validar_sem_evidencia`) e aprovado em `prototipo/resposta/tests/test_catalogo.py`
      (5 testes cobrindo rótulos marcados, múltiplos rótulos, inventados e menção direta)
- [x] 3.4 `openspec validate fix-resposta-sem-evidencia --strict` limpo

