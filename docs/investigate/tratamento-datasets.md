# Tratamento dos datasets para uso em PT-BR

**19/09/2026.** Change `add-tratamento-datasets-ptbr`, fase Investigate.

Este é o trabalho que estava bloqueando o MVP: indexar antes de normalizar
propaga o problema de rótulo para dentro do índice, onde ele fica caro de tirar.
O pacote de datasets foi coletado em 08/09 e conferido na fonte, mas não estava
utilizável na forma em que estava. Aqui está o que foi construído, o que foi
medido e o que a medição desmentiu.

Tudo o que aparece como número nesta página sai de artefato gerado, não de texto
escrito à mão. Para reexecutar:

```bash
python -m tratamento tudo      # regera os cinco artefatos
python -m pytest tratamento    # 53 testes
```

---

## 1. Contrato de leitura

O corpus é `;`-separado com newlines dentro de `text_news`. Lido no padrão do
`read_csv` ele **não** produz lixo silenciosamente, como o portfólio afirmava —
produz coisa pior, dependendo de como se chama:

| Como se lê | O que acontece |
| --- | --- |
| `read_csv(p)` | `ParserError: ',' expected after '"'` — falha ruidosa |
| `read_csv(p, on_bad_lines="skip")` | **25.670 registros de uma coluna só**, em silêncio |
| `read_csv(p, sep=";")` | 4.063 registros, 13 colunas |

O arquivo tem 48.392 linhas físicas para 4.063 registros — o portfólio dizia
42.197, número que nenhuma forma de contar reproduz.

O contrato vive em `tratamento/leitura.py` e cobre os nove derivados, cada um
com o formato **medido**: separador, contagem declarada, colunas e em quais
delas há newline interno. Contagem divergente interrompe a leitura, e nenhum
derivado é gerado a partir dela.

Dois arquivos desmentem o próprio nome:

- `factcenter_subset_saude.csv` é o único separado por `;`;
- `fakehealth_matriz_10_criterios.csv` tem **20** perguntas, não 10.

E um desmente o próprio conteúdo: `pubhealth_pool_fewshot.csv` vem com aspas
escapadas em excesso na origem (`"""""""texto"""`), que precisam sair antes de
qualquer uso do texto.

---

## 2. O campo de veredito não é um rótulo

O portfólio dizia "285 valores distintos". O número está certo e descreve a
coisa errada: 285 é a contagem de **strings serializadas distintas** no campo
`rating`. O vocabulário de veredito é bem menor:

| Medida | Valor |
| --- | --- |
| Strings brutas distintas em `rating` | 285 |
| Grafias distintas de veredito | **26** |
| Chaves canônicas (dobrando caixa e acento) | **19** |
| Agências | 6 |

As 19 chaves estão mapeadas em `tratamento/mapa_vereditos.json`, versão 1.0.0,
cada uma com agência, grafias, ocorrências e — onde a decisão não é óbvia — a
nota do que se perde no mapeamento. Valor fora do mapa **interrompe o
processamento**: não recebe rótulo por semelhança de string.

### Como o corpus se distribui sob o mapa

| Rótulo consolidado | Registros |
| --- | --- |
| `falso` | 3.419 |
| `verdadeiro fora de contexto ou exagerado` | 363 |
| `verdadeiro` | 21 |
| `nao_mapeavel` | 15 |
| misto (sem consolidado) | 245 |

Três anotações que mudam o que se pode afirmar com esses números:

**`boato` são 43% do corpus e não gradua nada.** A agência de origem publica
apenas rumor: `boato` é o único valor que ela emite, em 1.744 de 1.744
registros. Equiparar a `falso` infla a classe `falso` e apaga a informação de
que a gradação nunca existiu naquela fonte.

**Quatro chaves ficaram em `nao_mapeavel`, de propósito.** `contraditório` é
relacional (a afirmação contradiz outra do mesmo autor); `ainda é cedo para
dizer` é temporal; `de olho` é marcação de acompanhamento. E `insustentável`
ficou fora pelo motivo mais delicado: parece `evidência insuficiente`, mas
aquele rótulo é estado da **recuperação do sistema**, e importar um veredito de
agência para dentro dele faria o sistema atribuir a si mesmo uma lacuna que é
do mundo.

**Os registros mistos são material, não sujeira.** 245 registros têm vereditos
que caem em rótulos diferentes — o portfólio dizia 250, número anterior ao mapa.
Eles não recebem consolidado e ficam reservados como caso de teste da
decomposição fato/evidência/opinião de `verificacao-alegacao`. Onze registros
trazem mais de vinte vereditos, um deles 101: são compilados periódicos de
agência, e saem do banco de estímulos porque não são mensagem que alguém
receberia.

### Duas decisões de mapeamento que o grupo precisa confirmar

| Chave | Ocorrências | Destino | Por quê olhar |
| --- | --- | --- | --- |
| `enganoso` | 218 | `verdadeiro fora de contexto ou exagerado` | segunda maior massa do mapa; erro aqui desloca boa parte do corpus |
| `impreciso` | 64 | `verdadeiro fora de contexto ou exagerado` | `impreciso` e `exagerado` são etiquetas distintas na mesma agência |

---

## 3. Integridade textual

O verificador definitivo está em `tratamento/integridade.py`, e roda por arquivo.
O critério **não** é ausência total de uma letra, porque a leitura literal
reprova corpus íntegro: `factcenter_subset_saude.csv` tem zero `Ü` em 21,5
milhões de caracteres porque o trema foi abolido em 1990, e o `ü` minúsculo
aparece 57 vezes. O critério é **maiúscula com zero ocorrências e minúscula
correspondente frequente**.

| Arquivo | Aprovado | Causa |
| --- | --- | --- |
| `factcenter_subset_saude.csv` | sim | — |
| `factckbr_normalizado.csv` | **não** | perda seletiva de caractere |
| `fakerecogna_subset_saude_ciencia.csv` | **não** | texto transformado na origem |
| `fakerecogna_amostra_estimulos_300.csv` | **não** | texto transformado na origem |

### Achado: reprovar não basta, o laudo precisa dizer por quê

Os dois derivados da FakeRecogna reprovam no mesmo portão que o FACTCK.BR, e
**pela razão oposta**. O FACTCK.BR perdeu caractere: o texto conserva a caixa e
só as maiúsculas acentuadas sumiram. A FakeRecogna entrega a coluna `Noticia`
lematizada e sem caixa na origem — `o governar equador anunciar preparar cova`.
O efeito no portão é o mesmo (nenhum dos dois serve de trecho citado), mas a
acusação não é, e registrar "perda de caractere" contra a FakeRecogna seria erro
de portfólio. O laudo agora distingue os dois casos.

### Correção de número: são onze letras, não nove

O portfólio dizia que nove maiúsculas acentuadas têm zero ocorrência no
FACTCK.BR. Medido: **onze** estão ausentes (`À Â Ã Ê Í Ó Ô Õ Ú Ü Ç`), das quais
**sete** sustentam acusação de corrupção pelo critério acima — `Ã` contra 3.625
`ã`, `Ç` contra 2.312 `ç`, `Í` contra 1.521, `Ê` contra 1.024, `Ú` contra 973,
`Õ` contra 700, `Ó` contra 622. As outras quatro têm minúscula rara demais para
concluir.

### Fidelidade do trecho citado

Todo fragmento que o índice exibe é conferido contra o texto de origem por
igualdade literal — sem dobrar acento, sem colapsar espaço, porque isso é
exatamente a normalização silenciosa que a capability proíbe. Medido sobre 500
registros: **4.968 fragmentos, zero infiéis**.

### O que não dá para reparar

A task pedia regerar o derivado do FACTCK.BR a partir da fonte, com a correção.
**Não é possível**, e o motivo importa: a corrupção já está no `FACTCKBR.tsv`
distribuído. Contado no arquivo de origem, `Ã` = 0 contra `ã` = 3.625, os mesmos
números do derivado. Nenhuma reexecução recupera caractere que não está lá, e
inferir a acentuação por ortografia seria adivinhar em texto que vira citação.

O que **foi** feito é a correção a montante, para a coleta futura:

- `re_char()` não filtra mais por allowlist (que continha só as acentuadas
  minúsculas): agora descarta apenas caracteres de controle;
- `text_pre_proc()` lê o JSON-LD com `json.loads`, não com `ast.literal_eval`,
  que quebra em `true`/`false`/`null`;
- `update_dataset()` usa `pd.concat`, no lugar de `DataFrame.append`, removido
  no pandas 2.0.

Seis testes cobrem as três correções.

---

## 4. Frescor: a lacuna de acervo não é evidência insuficiente

Cobertura medida sobre o arquivo, reexecutável por `python -m tratamento frescor`:

| Medida | Valor |
| --- | --- |
| Janela | 2013-07-08 a 2021-05-19 |
| Concentração | 2.188 registros em 2020 (54%) |
| `covid` | 2.280 |
| `vacina` | 811 |
| `dengue` | 60 |
| `cloroquina` | 293 |
| `qdenga` · `mpox` · `oropouche` · `semaglutida` | **0 cada** |

O zero de `qdenga` só vale como evidência porque foi medido junto de termos que
dão diferente de zero, com busca por palavra inteira — `mpox` não pode casar
dentro de outra palavra.

Daí sai a distinção que o produto precisa fazer:

| Situação | Resposta | O que a pessoa faz com isso |
| --- | --- | --- |
| Pauta dentro da janela, sem correspondência | `evidência insuficiente` | não há o que procurar |
| Pauta posterior à janela | **`lacuna de acervo`** | procurar na agência; o link vai junto |

Responder `evidência insuficiente` sobre a Qdenga é enganoso: existe checagem
publicada, o nosso acervo é que não a contém. `tratamento/frescor.py` classifica
a pauta **antes** da recuperação e devolve a mensagem com a data de corte e para
onde ir.

### Caminho de atualização

O `update_factckbr.py` alcança três feeds — Aos Fatos, Agência Pública (Truco) e
Lupa — contra as **seis** agências do corpus. Não alcança `boatos`,
`fato-ou-fake` e `COMPROVA`, que juntas respondem por 2.364 dos 4.063 registros.
E o feed devolve só os artigos recentes de cada agência: serve a incremento, não
a recomposição do acervo.

---

## 5. Instrumentos em inglês: adaptação, não tradução

O FakeHealth tem 20 perguntas em dois conjuntos de 10, não 10. Oito são o mesmo
conceito nos dois; duas são próprias de cada.

**Adotado `HealthStory` como base**, com as duas de `HealthRelease` mapeadas
para dentro dele. O que chega ao usuário deste projeto é mensagem que circulou,
não comunicado institucional. A pergunta sobre financiador é conflito de
interesse visto pelo outro lado e entra como nível da rubrica; a de linguagem
sensacionalista é preservada por endereçar direto o catálogo de técnicas.

A rubrica final tem **seis critérios**, cada um com três níveis em português, em
`datasets/derivados/rubrica_criterios_ptbr.json`. Cinco perguntas saíram, com
motivo registrado: `custo`, `disponibilidade`, `alternativas`, `novidade` e
`release` foram escritas para avaliar jornalismo sobre tecnologia médica e não
têm objeto quando a unidade analisada é a mensagem que circulou.

### Achado: o proxy de validação foi medido e reprovado

A primeira tentativa de validar a rubrica foi contar cobertura de vocabulário
por critério e remover o que ficasse abaixo de um piso. A medição derrubou o
método:

| Critério | Proporção sobre a alegação | Decisão real |
| --- | --- | --- |
| `conflito_de_interesse` | 0,193 | mantido |
| `beneficio` | 0,141 | mantido |
| `evidencia` | 0,107 | mantido |
| `dano` | 0,100 | mantido |
| `novidade` | 0,063 | **removido** |
| `custo` | 0,051 | **removido** |
| `alarme` | 0,039 | **mantido** |
| `linguagem` | 0,029 | **mantido** |

Sob qualquer piso único, o proxy removeria `alarme` e `linguagem` — os dois
critérios que mais diretamente endereçam desinformação — e manteria `custo` e
`novidade`. A causa é identificável: estilo (caixa alta, exclamação, pedido de
repasse) não sobrevive à reescrita do título pela agência, enquanto `novo` e
`reais` são palavras comuns que casam por acaso.

Houve ainda um erro de objeto antes desse: medir sobre `text_news` mede a
**análise escrita pela agência**, não a mensagem que circulou. Lá `custo`
aparece em 36% dos registros e `novidade` em 49% — números que não dizem nada
sobre o caso. A medição correta é sobre título e subtítulo.

**Consequência honesta:** as remoções se sustentam no argumento de unidade de
análise, não no número, e a validação empírica da rubrica segue **pendente** de
anotação humana dos casos, que é de `avaliacao-instrumento`. Um teste trava essa
conclusão, para que ninguém a reabra por engano confiando no proxy.

### Pool de few-shot em português

15 exemplares, 5 por rótulo, tirados do corpus brasileiro com semente 42 —
nenhum traduzido do PUBHEALTH, como a capability exige. Entram só registros de
alegação única, com rótulo consolidado, fora do rótulo `nao_mapeavel` e com pelo
menos 400 caracteres de texto. Os 5 exemplares `verdadeiro` esgotam quase um
quarto dos 21 disponíveis no corpus — a carência continua sendo o gargalo.

### Força da afirmação, em português

Escala do InSciOut (0 a 3) atravessa como definição operacional:

| Nível | Nome adotado |
| --- | --- |
| 0 | sem afirmação de relação |
| 1 | associação observada |
| 2 | relação condicional |
| 3 | relação causal afirmada |

E a comparação entre a força do estudo e a da manchete liga ao catálogo de
técnicas: `exaggerates` → **afirma mais que o estudo**, técnica `manchete
exagerada`. Os pares em inglês não são exibidos ao usuário.

---

## 6. Caveats que entram no portfólio

| Base | Caveat |
| --- | --- |
| FactCenter | 43% do corpus é `boato`, rótulo que não gradua; a classe `falso` está inflada por construção |
| FactCenter | 21 registros `verdadeiro` em 4.063. O corpus **não** é fonte de itens verdadeiros, e amostrar isso dele é recusado em código |
| FactCenter | janela 2013–2021, 54% em 2020; pautas posteriores a 2021 têm cobertura zero |
| FactCenter | 245 registros mistos e 11 compilados, todos fora do banco de estímulos |
| FACTCK.BR | reprovado para citação; a perda de caractere está na fonte e é irreversível |
| FakeRecogna | reprovada para citação por texto transformado na origem, não por corrupção; serve a contagem e a estímulo declarado |
| PUBHEALTH | classe majoritária é `true` (~52% do treino), não "maioria falsa" |
| FakeHealth | 20 perguntas em dois conjuntos, não 10; o nome do derivado diz 10 e está errado |
| InSciOut | instrumento, não conteúdo: nenhum texto em inglês é exibido |

---

## 7. Artefatos gerados

| Arquivo | O que é |
| --- | --- |
| `datasets/derivados/factcenter_vereditos_normalizados.csv` | cada registro com chaves, rótulos, `misto` e exclusão |
| `datasets/derivados/relatorio_vereditos.json` | contagens por agência, grafia e chave |
| `datasets/derivados/relatorio_integridade.json` | laudo por arquivo, com causa provável |
| `datasets/derivados/declaracao_cobertura.json` | janela, ano a ano, termos de pauta, caminho de atualização |
| `datasets/derivados/rubrica_criterios_ptbr.json` | rubrica, removidos com motivo, força da afirmação, validação |
| `datasets/derivados/fewshot_ptbr_pool.csv` | 15 exemplares PT-BR, semente 42 |
| `tratamento/mapa_vereditos.json` | mapa versionado 1.0.0, 19 chaves |
