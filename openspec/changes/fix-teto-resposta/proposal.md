# Proposal: Teto da resposta garantido em código

**Fase do CBL:** Act. Change aberto em 08/10/2026, por decisão do grupo na
revisão do critério de aceite de `add-gerador-api-deepseek` (D10).

## Why

`acessibilidade-leitura` exige no máximo 120 palavras na camada visível. Hoje
só o prompt e uma nova tentativa (`fix-qualidade-gerador-remoto`, D5 e D7)
cuidam disso. Nas rodadas de 08/10 com `deepseek-v4-pro`, respostas de 121 a
126 palavras apareceram em quase toda rodada, cada vez num caso diferente. É
variação do modelo na beira do limite. Enquanto o teto depender do modelo, a
falha volta.

Parte do teto dá para garantir sem o modelo: os blocos 3 ("por que engana" ou
equivalente) e 4 ("o que observar") são dicas sem âncora em trecho. Cortar a
última frase deles não muda veredito nem evidência. O limite de 20 palavras
por frase não dá para garantir sem reescrever a frase, o que só o modelo faz;
ele continua como métrica de forma.

## What Changes

- **MODIFICADO (código)** `prototipo/resposta/estrutura.py`: depois da nova
  tentativa, se a camada visível passar de 120 palavras, o código tira frases
  do fim do bloco 4 e depois do bloco 3, deixando pelo menos uma frase em
  cada, até caber.
- Blocos 1 e 2, bordão, títulos e aviso de leitura parcial nunca são cortados.
- Corte que criar defeito eliminatório (por exemplo, tirar a afirmação correta
  depois da última menção ao mito) é desfeito: vale a resposta sem corte, com
  o defeito de tamanho registrado.

## Capabilities

### Modified Capabilities

- `acessibilidade-leitura`: "Legibilidade da camada visível" ganha o corte
  determinístico e o cenário correspondente.

A capacidade vive em `mvp-copiloto-verificacao`, ainda não arquivado. Ordem de
arquivamento: `mvp-copiloto-verificacao`, `add-entrada-por-link`, depois este.

## Impact

- Respostas longas perdem a última dica. A resposta fica mais curta, e a
  pessoa idosa lê menos.
- Muda o texto entregue, não as chamadas ao modelo: nenhuma regravação da
  bancada.
- Vale para os dois geradores.
