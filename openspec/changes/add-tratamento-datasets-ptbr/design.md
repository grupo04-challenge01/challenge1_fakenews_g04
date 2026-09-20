# Design — Tratamento dos datasets para uso em PT-BR

## Decisão 1: o problema de idioma é o inverso do que parecia

A leitura inicial era que os datasets em inglês precisavam de tradução para
servir a usuários brasileiros. A inspeção mostra o contrário: os três datasets em
inglês nunca chegam ao usuário como texto.

| Dataset | Papel real | Atravessa como |
| --- | --- | --- |
| PUBHEALTH | pool de exemplares few-shot | substituição por casos PT-BR |
| FakeHealth | critérios de qualidade de cobertura | rubrica adaptada e validada |
| InSciOut | definição operacional de força da afirmação | conceito, com exemplos locais |

O que precisa cruzar a fronteira de idioma é **vocabulário de critério**, e isso
é adaptação validada contra casos brasileiros, não tradução. O tratamento urgente
está no corpus em português, que é o único que chega ao usuário como texto.

**Consequência.** Nenhuma task deste change traduz texto corrido. A tradução do
pool de few-shot foi considerada e descartada: o exemplar ensina o modelo a
redigir a explicação, e um exemplar traduzido ensina a escrever como tradução.

## Decisão 2: normalizar rótulo não é achatar rótulo

Há duas maneiras de lidar com os 285 valores distintos do campo de veredito. A
primeira é mapear tudo para os quatro rótulos e seguir. A segunda é mapear e
**preservar o original ao lado**.

Adotada a segunda. Motivo: `boato` responde por 43% dos registros e não gradua
nada — a agência de origem publica apenas rumor. Achatar `boato` em `falso`
produz um corpus quase inteiramente falso e apaga a informação de que a
gradação nunca existiu naquela fonte. O mapa fica versionado e o valor original
rastreável até a agência.

**Alternativa descartada.** Inferir rótulo por semelhança de string
(`ENGANOSO` ≈ `Enganoso` ≈ `enganoso` é seguro; `impreciso` ≈ `exagerado` não é).
Qualquer valor fora do mapa interrompe o processamento em vez de receber palpite.

## Decisão 3: os registros mistos são material, não sujeira

587 registros cobrem mais de uma alegação e 250 têm vereditos divergentes entre
si — `['FALSO', 'SUBESTIMADO', 'VERDADEIRO', 'VERDADEIRO']`,
`['fato', 'nao e bem assim', 'fake']`.

O impulso é descartá-los por não caberem em um rótulo. Eles são exatamente o caso
que o requirement de decomposição fato, evidência e opinião de
`verificacao-alegacao` precisa como teste: texto único em que parte é verdadeira,
parte é exagerada e parte é falsa. Ficam reservados como conjunto de teste.

Os compilados muito longos são outra história: um registro traz 101 vereditos.
Esses saem do banco de estímulos, porque um compilado periódico de agência não é
uma mensagem que alguém receberia.

## Decisão 4: frescor é requisito de produto, não manutenção

O corpus termina em 2021 e 54% dele é de 2020. Isso não é dívida de manutenção a
resolver depois: muda o que o produto pode dizer hoje. `qdenga`, `mpox`,
`oropouche` e `semaglutida` têm zero ocorrência, e são justamente as pautas
brasileiras de saúde dos últimos anos.

Por isso a política de frescor é spec, não task: o sistema tem de **distinguir
lacuna de acervo de ausência de checagem no mundo**. Responder
`evidência insuficiente` para Qdenga é enganoso — existe checagem publicada,
o acervo é que não a contém.

**Alternativa descartada.** Ampliar o corpus até cobrir o presente antes de
qualquer outra coisa. Descartada porque a coleta contínua depende de decisão de
canal e de agendamento, ainda em aberto, e porque o comportamento correto diante
da lacuna é necessário mesmo com corpus atualizado — sempre haverá pauta mais
nova que o último ciclo de atualização.

## Riscos registrados

| Risco | Efeito | Mitigação |
| --- | --- | --- |
| Indexar antes de normalizar | Problema de rótulo propaga para o índice e reaparece na saída | Este change bloqueia as tasks 1.1 a 1.6 de `mvp-copiloto-verificacao` |
| Reparo de acentuação incompleto | Texto corrompido citado ao usuário em contexto de saúde | Verificação por classe de caractere, por arquivo, antes da aprovação |
| Mapa de rótulo tratado como definitivo | Atualização introduz veredito novo e recebe palpite | Valor fora do mapa interrompe o processamento |
| Corpus dominado por covid | O produto parece funcionar em teste e falha na pauta real | Casos de teste escolhidos fora do recorte covid, deliberadamente |
| Critérios do FakeHealth adotados como universais | Rubrica que não discrimina caso brasileiro | Validação contra o corpus PT-BR, com remoção do que não discrimina |

## Questões em aberto

1. ~~Qual dos dois conjuntos de critérios do FakeHealth adotar~~ — **resolvido
   em 19/09/2026: `HealthStory` como base**, com as duas perguntas próprias de
   `HealthRelease` mapeadas para dentro dele. O que chega ao usuário deste
   projeto é mensagem que circulou, não comunicado institucional. A pergunta
   sobre financiador entra como nível do critério de conflito de interesse; a de
   linguagem sensacionalista é preservada inteira, por endereçar direto o
   catálogo de técnicas de `resposta-formativa`. Cinco perguntas saíram da
   rubrica, com motivo por escrito.
2. Se os registros multi-alegação entram no índice do RAG separados por alegação
   ou se ficam fora do índice e só no conjunto de teste.
3. Qual a periodicidade aceitável de atualização, o que depende da decisão de
   canal ainda aberta em `mvp-copiloto-verificacao`.
4. De onde vêm os itens de veredito `verdadeiro`, já que o corpus tem 21 em
   4.063 e nenhuma base coletada os fornece.
