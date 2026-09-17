# Datasets e achados

Pacote coletado em 08/09/2026, tudo baixado da fonte primária e conferido. O
inventário completo, com contagens e licenças, está em `datasets/README.md` e
`datasets/FONTES.md`.

Esta página registra **o que a inspeção encontrou** — que é diferente do que o
inventário promete.

## O que temos

| Dataset | Idioma | Volume | Papel |
| --- | --- | --- | --- |
| FactCenter (recorte saúde) | PT | 4.063 checagens | corpus do RAG e itens falsos |
| FACTCK.BR | PT | 1.313 alegações | fonte auxiliar |
| FakeRecogna (saúde/ciência) | PT | 5.058 itens | banco de estímulos |
| PUBHEALTH | EN | 12.254 alegações | pool de exemplares few-shot |
| FakeHealth | EN | 22.959 avaliações de critério | critérios de qualidade |
| InSciOut | EN | 663 pares | definição de força da afirmação |
| Med-MMHL | EN | não baixado (4 GB) | teste de estresse, condicional |

## Achado 1: o problema de idioma é o inverso do que parecia

A pergunta inicial do grupo foi "como traduzimos os datasets em inglês, se
nossos usuários são brasileiros?". A inspeção mostra que **nenhum dos três
datasets em inglês chega ao usuário como texto**. Eles são instrumento:

| Dataset | Atravessa para PT-BR como |
| --- | --- |
| PUBHEALTH | substituição por casos brasileiros, não tradução |
| FakeHealth | rubrica adaptada e validada contra casos brasileiros |
| InSciOut | o conceito de força da afirmação; exemplos vêm daqui |

O que precisa cruzar a fronteira de idioma é **vocabulário de critério**, e isso
é adaptação validada, não tradução. Traduzir um exemplar de few-shot ensinaria o
modelo a escrever como tradução.

**O tratamento urgente é no corpus em português**, que é o único que chega ao
usuário como texto — e é o que está com problema.

## Achado 2: o corpus PT-BR está congelado em 2021

| Medida | Valor |
| --- | --- |
| Registros | 4.063 |
| Janela | 2013 a 2021 |
| Só 2020 | 2.188 (54%) |
| Mencionam covid | 2.274 (56%) |
| Mencionam `qdenga` | **0** |
| `mpox` / `oropouche` / `semaglutida` | **0 cada** |

Ou seja: as pautas brasileiras de saúde dos últimos anos têm cobertura zero.
Uma alegação sobre a vacina Qdenga cairia em `evidência insuficiente` — o que é
enganoso, porque existe checagem publicada; o nosso acervo é que não a contém.

Daí veio um requisito novo: o sistema tem de **distinguir lacuna de acervo de
ausência de checagem no mundo**.

## Achado 3: o campo de veredito não é um rótulo

O campo `rating` guarda uma lista serializada, com **285 valores distintos** e
seis vocabulários de agência conviventes:

```text
"['boato']"                    1.744 registros (43% do corpus)
"['FALSO']"                      705
"['fake']"                       371
"['FALSO', 'VERDADEIRO, MAS']"     3
```

Três consequências:

- **`boato` não gradua nada.** A agência de origem publica apenas rumor. Mapear
  `boato → falso` produz um corpus quase inteiramente falso.
- **Só 21 registros em 4.063** são `verdadeiro` ou `verdadeiro, mas`. O corpus
  não pode fornecer os itens verdadeiros que o teste com usuário precisa.
- **587 registros cobrem mais de uma alegação** — um deles com 101 rótulos. Um
  registro não equivale a uma alegação.

## Achado 4: os registros mistos são o material mais valioso

250 registros têm rótulos que divergem entre si:

```text
['FALSO', 'SUBESTIMADO', 'VERDADEIRO', 'VERDADEIRO']
['fato', 'nao e bem assim', 'fake']
```

O impulso é descartar o que não cabe num rótulo. Mas é exatamente isso que a
Big Idea pede para o sistema saber fazer: texto único em que parte é fato, parte
é exagero e parte é falso. Ficam reservados como conjunto de teste.

## Achado 5: dois defeitos de forma

**O arquivo do corpus é `;`-separado com newlines dentro do texto.** São 4.063
registros em 42.197 linhas físicas. Carregado no padrão do `read_csv`, produz
lixo silenciosamente.

**O FACTCK.BR perdeu todas as maiúsculas acentuadas.** Está gravado
`Sistema nico de Saúde` — o `Ú` foi deletado, não mal-codificado. Nove letras
acentuadas maiúsculas têm zero ocorrência no arquivo. A causa está no filtro de
caracteres do script de atualização, cuja lista de permitidos só inclui
acentuadas minúsculas. Como o produto cita trechos literais, isso apareceria na
tela do usuário.

## Correções que o portfólio precisa

| Onde | Correção |
| --- | --- |
| PUBHEALTH | A classe majoritária é `true` (~52% do treino), não "maioria falsa" |
| FakeHealth | São **20** perguntas em dois conjuntos distintos, não 10 |
| FactCenter | Todos os achados acima entram como caveats |

## O que ainda falta coletar

Dois pedaços não existem em nenhuma base baixada e são trabalho manual:

1. **Itens verdadeiros contra-intuitivos.** Agência de checagem só publica o que
   é suspeito, e o lado "verdadeiro" do FakeRecogna é notícia comum de portal
   grande — o participante acertaria pelo estilo do texto.
2. **Itens-armadilha** com evidência ambígua, construídos caso a caso.
