# Design — Resposta quando não há evidência recuperada

## Decisão 1: saída A, forma própria — 19/09/2026

A `proposal.md` deixou duas saídas. Adotada a **A**, forma própria para o caso
sem evidência, com a B registrada como descartada.

O argumento que decidiu não é de elegância de spec. É que os dois casos fazem
perguntas diferentes ao leitor:

| Caso | A pergunta do bloco 3 | O que o leitor faz com a resposta |
| --- | --- | --- |
| há evidência | por que **aquela mensagem** engana | aprende a reconhecer o sinal |
| não há evidência | o que **você** pode conferir | sai daqui com um próximo passo |

A saída B mantinha o rótulo da primeira pergunta sobre o conteúdo da segunda. O
bloco 3 ficaria com o título "por que engana" e o corpo vazio — que é
exatamente a degeneração que a sonda T1 produziu em 18/09, com o modelo
repetindo "evidência insuficiente" dentro do bloco.

A B também não tinha onde pôr o ponteiro da lacuna de acervo. Os quatro blocos
originais não têm lugar para "a Lupa checou isso em 03/2025, aqui está", e essa
informação é o produto inteiro naquele caso.

## Decisão 2: o ponteiro fica na camada visível

`resposta-formativa` manda fonte, trecho e detalhe metodológico para a camada de
detalhe, acessível por ação explícita. O ponteiro da lacuna de acervo é
exceção declarada.

Motivo: nos outros casos o usuário recebe uma resposta e a fonte serve para
conferir. Aqui ele **não** recebe resposta — o ponteiro é a resposta. Mandá-lo
para a segunda camada devolve à pessoa exatamente o problema com que ela chegou,
com um clique a mais.

O custo é orçamento de palavras: `acessibilidade-leitura` fixa 120 palavras na
camada visível, e agora o ponteiro compete por elas. Por isso o requirement
manda reduzir os blocos 2 e 3 antes de tocar no 4.

## Decisão 3: três respostas, não duas

A medição de 19/09 mostrou que `oropouche` e `semaglutida` têm zero ocorrência
**no acervo e no índice** da Fact Check Tools API. Isso obriga um terceiro
estado, que nenhuma das duas saídas previa:

| Estado | Condição | Bloco 4 |
| --- | --- | --- |
| `evidência insuficiente` | pauta dentro da janela, nada recuperado | o que conferir |
| lacuna de acervo **com** ponteiro | pauta fora da janela, índice devolve checagem | agência, data, veredito da agência, link |
| lacuna de acervo **sem** ponteiro | pauta fora da janela, índice também vazio | declara que não há checagem localizada em português |

O terceiro é o mais delicado: é onde é mais tentador dizer "não existe checagem
sobre isso", que é afirmação sobre o mundo que o sistema não pode fazer. O
requirement veda isso em texto expresso.

## Riscos

| Risco | Efeito | Mitigação |
| --- | --- | --- |
| Duas formas viram duas implementações que divergem | a forma sem evidência envelhece e ninguém percebe | o gerador escolhe a forma pelo estado da recuperação, não por prompt separado; o teste cobre os três estados |
| O ponteiro estoura o teto de 120 palavras | a camada visível fica ilegível no caso que mais precisa de clareza | ordem de redução declarada no requirement: blocos 2 e 3 encolhem, o 4 não |
| Checagem do índice em português de Portugal atribuída como brasileira | erro de proveniência na cara do usuário | a origem do editor entra no ponteiro; ver decisão 11 de `add-ampliacao-corpus-ptbr` |

## Questões em aberto

- Se a forma sem evidência deve nomear a técnica quando o usuário **pedir**
  explicitamente a análise da mensagem sem veredito. Hoje a spec veda nomear
  técnica sem evidência; o caso do pedido explícito não foi examinado.
- Quantas palavras sobram para os blocos 2 e 3 depois do ponteiro, o que só se
  sabe medindo respostas reais.
