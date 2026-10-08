# Design: Teto da resposta garantido em código

## Context

Motivação em `proposal.md`. Dados das rodadas no `design.md` de
`add-gerador-api-deepseek` (D10 e tabelas de 08/10/2026).

## Goals / Non-Goals

**Goals:**

- Camada visível nunca acima de 120 palavras quando os blocos 3 e 4 têm
  frases sobrando.
- Nenhum corte cria defeito eliminatório.

**Non-Goals:**

- Garantir 20 palavras por frase.
- Cortar blocos 1 e 2, que carregam veredito e evidência ancorada.

## Decisions

### D1. Onde cortar

Ordem: última frase do bloco 4, depois última do bloco 3, alternando a partir
do bloco que tiver mais frases, até caber ou até os dois terem uma frase só.
Frases separadas pelo mesmo `_frases` que conta o limite de 20 palavras.

### D2. Quando cortar

Depois da escolha entre a primeira saída e a nova tentativa (D5 de
`fix-qualidade-gerador-remoto`), antes de calcular os defeitos finais. Assim
o modelo tem a chance de escrever curto, e o corte só pega o que sobrar.

### D3. Corte que piora

Os defeitos são recalculados depois do corte. Se surgir defeito de mito ou de
veredito insinuado que não existia, vale a resposta sem corte. O `Resposta`
registra `cortadas`, as frases tiradas, para o rastro e a bancada.

## Risks / Trade-offs

- [Corte tira a dica mais útil] → a última frase costuma ser complemento; o
  rastro guarda o que saiu, e a bancada mostra quantas vezes cortou.
- [Blocos 1 e 2 longos demais] → o corte não alcança; o defeito de tamanho
  continua registrado e conta como falha não eliminatória.
