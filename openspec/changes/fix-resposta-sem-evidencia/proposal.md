# Proposal: Resposta quando não há evidência recuperada

**Fase do CBL:** Investigate, transbordando para Act. Change de correção aberto
pela task 2.1b de `add-selecao-modelos-arquitetura-rag`, em 19/09/2026.

## Why

A sonda T1 do gerador, em 18/09/2026, expôs um defeito **da spec**, não do
modelo. `resposta-formativa` exige os quatro blocos em toda resposta de
verificação e exige que o bloco 3 nomeie ao menos uma técnica do catálogo
fechado. Quando o veredito é `evidência insuficiente`, as duas exigências ficam
incoerentes: não há mensagem comprovadamente enganosa cuja técnica nomear, e
nomear uma assim mesmo afirma sobre a mensagem exatamente o que o veredito
acabou de dizer que não se sabe.

O modelo fez o que uma spec incoerente induz: degenerou, repetindo "evidência
insuficiente" dentro do bloco 3. Qualquer gerador colocado no lugar faria o
mesmo, porque a instrução pede uma coisa impossível.

O custo de não corrigir é maior do que parece. `evidência insuficiente` não é
caso raro de borda: a medição de 18/09 mostrou que o limiar não sai de
similaridade bruta, e a declaração de cobertura de 19/09 mostrou que o acervo
termina em 2021, com zero ocorrência de `qdenga`, `mpox`, `oropouche` e
`semaglutida`. Pauta fora do acervo será comum, e é justamente o caso em que a
resposta precisa ser mais cuidadosa, não menos.

A correção MUST entrar antes da task 3.2 de `mvp-copiloto-verificacao`, que é
quem implementa a estrutura de resposta.

## What Changes

- **MODIFICADO** `resposta-formativa`: a estrutura de quatro blocos passa a ter
  forma declarada para o caso `evidência insuficiente`, e a obrigatoriedade do
  catálogo de técnicas no bloco 3 passa a ser condicionada ao veredito.
- **MODIFICADO** `resposta-formativa`: acréscimo da distinção entre `evidência
  insuficiente` e **lacuna de acervo**, que a capability `frescor-corpus`
  estabeleceu em 19/09/2026 e que a estrutura de resposta ainda não reflete.
  São duas respostas diferentes e hoje colapsam na mesma.

Não há capability nova. O change corrige uma que já existe.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `resposta-formativa`: estrutura da resposta e obrigatoriedade do catálogo
  quando não há evidência recuperada que sustente afirmação sobre a mensagem.

## Questão a decidir pelo grupo

O `design.md` da sonda deixou duas saídas, e elas não são equivalentes:

| Saída | O que faz | Custo |
| --- | --- | --- |
| **A. Forma própria** para `evidência insuficiente` | a resposta passa a ter uma estrutura declarada e diferente nesse caso, com blocos próprios | mais superfície de spec e de implementação; duas formas para testar |
| **B. Catálogo condicional** | os quatro blocos continuam, e só a obrigação de nomear técnica cai quando não há evidência | mudança mínima; risco de o bloco 3 ficar vazio de conteúdo e virar ruído |

**Recomendação: A**, por um motivo que a medição sustenta. O bloco 3 pergunta
"por que aquela mensagem engana"; sob `evidência insuficiente` a pergunta certa
é outra — "o que você poderia conferir por conta própria". São perguntas
diferentes, e a saída B mantém o rótulo de uma sobre o conteúdo da outra. Além
disso, a saída A é a única que acomoda a distinção entre evidência insuficiente
e lacuna de acervo, que precisa apontar **onde procurar**, algo que não cabe em
nenhum dos quatro blocos atuais.

A decisão é do grupo e MUST ser registrada antes de as specs delta serem
escritas.

## Impact

- Bloqueia a task 3.2 de `mvp-copiloto-verificacao` (implementação da estrutura
  de resposta) até ser decidida.
- Consome parte do orçamento de 6 a 8 rótulos do catálogo, se a saída A criar
  rótulos próprios — o que interage com a proposta de rótulos de emoção da
  decisão 13 de `add-selecao-modelos-arquitetura-rag`.
- Interage com `acessibilidade-leitura`: a camada visível tem teto de 120
  palavras, e qualquer forma nova precisa caber nele.
- Não afeta o índice nem o corpus. É correção de forma de resposta.
