# Proposal: Limitações do MVP

**Fase do CBL:** Act. Change aberto em 09/10/2026, depois do teste de ponta a
ponta do MVP com a DeepSeek (PR #204).

## Why

O MVP passou no teste (uso 22/22, piloto 9/9, bancada 29/30), com três
limitações conhecidas:

1. **Afirmação sem base.** A ancoragem confere só termos verificáveis
   (números, meses, nomes) e declara o próprio limite: paráfrase passa, e
   frase que inverte o sentido do trecho com as mesmas palavras também. Nos
   testes, a resposta disse "o número de 50% se refere a casos raros de reação
   grave" (o trecho diz o contrário), "a vacina é segura para a maioria das
   pessoas" (nenhum trecho diz) e, sobre uma página da Wikipédia, que a
   mensagem "misturava opiniões alarmantes sobre a vacina". Isso fere a
   promessa central do projeto: veredito auditável até a fonte.
2. **Termo num bloco só.** O termo de consentimento tem cerca de 110 palavras
   num parágrafo, difícil para o público idoso.
3. **Teto estourado por pouco.** Respostas de 121 palavras passam quando os
   blocos 3 e 4 têm uma frase só, porque o corte de `fix-teto-resposta` não
   mexe no bloco 2.

## What Changes

- **NOVO (código e prompt)** `prototipo/resposta/conferencia.py`: uma chamada
  ao modelo confere cada frase da resposta; frase sem base sai (D1).
- **MODIFICADO (spec e página)** termo em seis parágrafos, com as mesmas
  palavras da versão 3 revisada (D2).
- **MODIFICADO (código)** corte de teto alcança o fim do bloco 2 depois dos
  blocos 3 e 4 (D3).

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `resposta-formativa`: novo requirement "Conferência de sustentação".
- `interface-chat-web`: "Consentimento antes do envio ao serviço externo"
  com o termo em parágrafos.
- `acessibilidade-leitura`: "Legibilidade da camada visível" com o corte no
  bloco 2.

Ordem de arquivamento: depois de `mvp-copiloto-verificacao`,
`add-interface-chat-web`, `add-gerador-api-deepseek`, `fix-teto-resposta` e
`fix-pergunta-e-conduta`.

## Impact

- Uma chamada a mais ao modelo por resposta completa: cerca de 3 a 5 s e
  menos de US$ 0,001.
- Respostas podem ficar mais curtas ou ser rebaixadas para a forma sem
  evidência quando a conferência tirar frases.
- As gravações da bancada precisam ser refeitas.
