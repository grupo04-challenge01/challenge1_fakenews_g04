# Aferição da recuperação

**19/09/2026, completada em 22/09/2026.** Tasks 3.1 a 3.6 de
`add-selecao-modelos-arquitetura-rag`.

O índice de 18/09 funcionava mas não estava medido: os 35% de sobreposição entre
os braços eram sanidade, não aferição. Esta página traz a medição com documento
correto conhecido — e o resultado desmente três suposições do projeto.

!!! success "Medição completa em 22/09/2026"
    O braço denso, a fusão e a comparação entre modelos de embedding foram
    medidos. As tasks 3.1, 3.3 e 3.4 estão fechadas, e a 3.2 está registrada na
    decisão 15 do `design.md`. O achado que fechou a 3.1 não estava previsto:
    **o defeito era a calibração de `alfa`, não a arquitetura.**

## O instrumento

`prototipo/rag/consultas_afericao.json`, versão 1.0.0 — 20 consultas tiradas de
registros reais do corpus, **deliberadamente fora do recorte covid**, cada uma
com o documento correto conhecido pelo `registro_id`.

A decisão que faz a medição valer alguma coisa é a separação em duas famílias:

| Família | O que é | Por que existe |
| --- | --- | --- |
| `verbatim` (10) | a mensagem como circula; o usuário cola o que recebeu | medir só com isto favorece a busca léxica **por construção** |
| `reformulada` (10) | a pergunta nas palavras de quem pergunta, sem o termo raro que identifica o documento | medir só com isto favorece a densa |

A média das duas esconde a diferença. É justamente a diferença que interessa.

## Resultado do braço léxico (BM25)

| Família | recall@1 | recall@3 | recall@5 | recall@10 | MRR |
| --- | --- | --- | --- | --- | --- |
| `verbatim` | 0,80 | **1,00** | 1,00 | 1,00 | 0,90 |
| `reformulada` | 0,40 | 0,70 | 0,70 | **0,70** | 0,55 |
| global | 0,60 | 0,85 | 0,85 | 0,85 | 0,725 |

Latência de consulta: **187 ms** de mediana, 308 ms no pior caso, sobre 22.464
fragmentos.

O BM25 resolve o caso verbatim inteiro no top-3 — nenhuma consulta colada falha.
E perde **3 de 10** reformuladas mesmo abrindo para o top-10: `a14` (supremo e
vacinação de venezuelanos), `a16` (Lula e vacina de meningite) e `a20` (vacina
anual derruba imunidade). São três consultas em que o usuário não repetiu
nenhuma palavra rara do documento.

Isso não é defeito do BM25; é a definição dele. É também exatamente o buraco que
o braço denso existe para tapar, e a previsão que a medição pendente ia testar:
**se a densa não melhorar `reformulada`, a decisão 4 do `design.md` perde o
sustento e o híbrido vira custo sem retorno.**

!!! note "A previsão foi testada em 22/09 e confirmada — ver abaixo"
    A densa leva `reformulada` de 0,70 para 1,00 de recall@5 e recupera as três
    consultas perdidas. A decisão 4 sobreviveu, mas por pouco e com uma correção
    de calibração no caminho.

## Resultado do braço denso e da fusão (task 3.1)

Medido em 22/09/2026 sobre o mesmo conjunto, no mesmo índice, com
`intfloat/multilingual-e5-base`.

| configuração | recall@1 | recall@3 | recall@5 | recall@10 | MRR | latência mediana |
| --- | --- | --- | --- | --- | --- | --- |
| só léxica | 0,60 | 0,85 | 0,85 | 0,85 | 0,725 | 22 ms |
| só densa | 0,80 | **0,95** | 1,00 | 1,00 | 0,877 | **13 ms** |
| híbrida (score, α=0,9) | **0,85** | 0,90 | **1,00** | **1,00** | **0,897** | 38 ms |
| híbrida (RRF) | 0,85 | 0,85 | 0,85 | 0,85 | 0,850 | 44 ms |

Separado por família, é onde a diferença vive:

| configuração | `verbatim` recall@5 / MRR | `reformulada` recall@5 / MRR |
| --- | --- | --- |
| só léxica | 1,00 / 0,90 | 0,70 / 0,55 |
| só densa | 1,00 / 0,95 | 1,00 / 0,803 |
| híbrida (α=0,9) | 1,00 / 0,95 | **1,00 / 0,845** |

O braço denso recupera `a14`, `a16` e `a20` — as três que o BM25 perdia, e que
são exatamente as consultas em que o usuário não repetiu nenhum termo raro.
`reformulada` sai de 0,70 para 1,00 de recall@5. A previsão da medição parcial
se confirmou.

**RRF continua descartada como forma padrão**, e agora com medição além do
argumento: ela não recupera as três consultas perdidas, porque o score por
posição não deixa o braço denso puxar um documento que o léxico não viu.

## A calibração de `alfa` era o defeito (task 3.2)

A primeira execução mediu `alfa` em 0,5, o valor que estava fixado desde 18/09
**sem nenhuma medição por trás**, e concluiu que a híbrida perdia da densa pura.
A conclusão estava errada, e o que perdia era o 0,5.

| α | recall@5 | MRR | perdidos |
| --- | --- | --- | --- |
| 0,00 (só léxica) | 0,85 | 0,725 | `a14`, `a16`, `a20` |
| 0,50 (padrão antigo) | 0,85 | 0,825 | `a14`, `a16`, `a20` |
| 0,80 | 0,90 | 0,850 | — |
| **0,90 (padrão novo)** | **1,00** | **0,897** | — |
| 0,98 | 1,00 | 0,902 | — |
| 1,00 (só densa) | 1,00 | 0,877 | — |

Em α=0,5 o ruído léxico empurrava para fora do top-10 os três documentos que o
braço denso achava nas posições 5, 3 e 1. Metade de peso para um braço que
resolve 7 de 10 reformuladas é peso demais.

### Duas guardas antes de fixar o novo padrão

Trocar uma constante porque um número subiu em 20 consultas é como o 0,5 entrou
no código. As duas verificações abaixo são o que separa uma coisa da outra, e
**ambas viraram código** em `afericao.varrer_alfa`.

**Forma da curva.** Cinco valores de α, de 0,90 a 0,98, ficam dentro de 0,01 do
topo com recall@5 máximo. É platô, não pico: um erro de ±0,08 na calibração não
muda o resultado. Um ótimo isolado entre vizinhos piores seria indistinguível de
sorte.

**Leave-one-out.** Escolher α e avaliar no mesmo conjunto superestima sempre. Com
α escolhido em 19 consultas e avaliado na vigésima, vinte vezes:

| | MRR fora da amostra |
| --- | --- |
| híbrida com α escolhido em 19 consultas | **0,8975** |
| densa pura (α=1,0) | 0,8767 |

Só dois valores de α foram escolhidos ao longo das vinte rodadas, 0,9 e 0,98. O
ganho sobrevive a não ver a consulta em que é medido.

## Comparação entre modelos de embedding (task 3.3)

| | `e5-base` | `e5-small` |
| --- | --- | --- |
| dimensão | 768 | 384 |
| matriz em disco | 65,8 MB | **32,9 MB** |
| indexação de 22.464 fragmentos | 883,4 s | **227,4 s** |
| consulta densa, mediana | 13 ms | **9 ms** |
| densa, `verbatim` recall@5 / MRR | 1,00 / 0,95 | 1,00 / **1,00** |
| densa, `reformulada` recall@5 / MRR | **1,00 / 0,803** | 0,80 / 0,725 |

O `e5-small` é melhor em tudo que é custo e melhor em `verbatim`, onde acerta
todos os alvos em primeiro lugar. Perde onde importa: em `reformulada` ele deixa
`a14` e `a16` para trás, **as mesmas que o braço léxico perde**. Um braço denso
que falha junto com o léxico não está cumprindo a função dele.

**O melhor α não se transfere entre modelos.** No `e5-small` o ótimo é α=1,00 e a
híbrida *perde* sob leave-one-out — 0,8500 contra 0,8625 —, com a escolha de α
oscilando entre 0,74 e 1,00. A leitura que a medição sustenta é «0,9 com
`e5-base`», não «híbrida supera densa»: o braço léxico corrige na margem, e só
tem margem para corrigir quando o braço denso já é bom. Trocar o modelo obriga a
revarrer.

## Custo, separando indexação de consulta (task 3.4)

| | `e5-base` | `e5-small` |
| --- | --- | --- |
| índice léxico | 2,1 s | 2,1 s |
| indexação densa | 883,4 s | 227,4 s |
| consulta só léxica | 22 ms | 20 ms |
| consulta só densa | 13 ms | 9 ms |
| consulta híbrida | 38 ms | 32 ms |

A indexação é lote único e reaproveitável: a matriz não depende do conjunto de
aferição, então medir de novo não repaga os 883 s. A consulta compete com os 17
a 23 segundos do gerador, e nesse orçamento os 38 ms da híbrida são ruído.

!!! warning "A latência léxica de 19/09 estava contaminada"
    A medição parcial registrou 187 ms de mediana para o braço léxico. A de
    22/09 registra 22 ms, com o mesmo código e o mesmo índice. A diferença é
    contenção: em 19/09 a indexação densa rodava na mesma máquina enquanto a
    aferição léxica era medida. **O número de 187 ms não deve ser citado**; ele
    mede a máquina ocupada, não o índice.

## Calibração do limiar de `evidência insuficiente` (task 3.5)

Oito consultas sem alvo no acervo, versionadas no mesmo arquivo: cinco de pauta
medida com zero ocorrência (`qdenga`, `mpox`, `oropouche`, `semaglutida`) e três
fora do domínio de saúde, como piso de ruído.

### O score normalizado não serve, e o motivo é estrutural

| Distribuição | mínimo | mediana | máximo |
| --- | --- | --- | --- |
| score do alvo (positivas) | 0,658 | 0,814 | 0,917 |
| score do topo (sem alvo) | 0,632 | 0,716 | **0,853** |

As faixas se sobrepõem em quase toda a extensão. O caso que explica por quê:

> `como declarar imposto de renda atrasado` → **0,853**, acima de 11 dos 20
> alvos reais. O topo recuperado foi uma checagem sobre aposentadoria de
> ministro do STF.

A causa não é o BM25, é a **normalização**. A fusão realça cada braço contra o
fundo da própria consulta — mede o quanto o topo se destaca daquilo que aquele
braço devolveria para qualquer coisa. Para uma consulta fora do domínio, o fundo
é baixíssimo, então qualquer casamento acidental se destaca muito. O realce é
**relativo por construção** e, por isso, incomparável entre consultas.

**Consequência para a task 3.5.** A task manda calibrar o limiar "sobre o score
fundido". O objeto está errado: sobre o score fundido não existe limiar que
separe, e nenhuma escolha de corte melhora isso, porque a grandeza não é
comparável entre consultas. O limiar tem de sair do **score bruto** do braço, ou
de outro sinal.

### Sobre o score bruto há uma curva, e ela tem uma forma útil

| Limiar BM25 bruto | Positivos mantidos | Ruído rejeitado |
| --- | --- | --- |
| 10 | 100% | 0% |
| 15 | 95% | 38% |
| 20 | 80% | 88% |
| 25 | 60% | 88% |
| **27,2** | **60%** | **100%** |
| 35 | 30% | 100% |

O menor limiar que rejeita todo o ruído é **27,2**, e ele custa 40% dos
positivos. Mas o custo não é distribuído ao acaso:

> **Os oito positivos que caem abaixo de 27,2 são, todos, da família
> `reformulada`. Nenhuma consulta `verbatim` cai.**

Ou seja: sozinho, o braço léxico tem confiança calibrável **apenas** quando o
usuário cola a mensagem. Quando ele reformula, o BM25 não sabe distinguir a
própria ignorância de um acerto fraco. Essa é a formulação precisa do problema
que o híbrido precisa resolver, e ela é testável assim que a matriz densa
existir.

### O que já funciona hoje

A resposta de **lacuna de acervo** de `frescor-corpus` não depende de score
nenhum: ela decide pela janela declarada do acervo e pelos termos de pauta
medidos com zero ocorrência. Das oito consultas sem alvo, cinco são capturadas
por esse mecanismo antes de qualquer recuperação rodar — incluindo as quatro de
pauta posterior a 2021.

É o único mecanismo medido que separa lacuna de evidência insuficiente hoje, e é
mais um argumento para a forma própria de resposta adotada em
`fix-resposta-sem-evidencia`.

## Reexecução

```bash
python -m prototipo.rag construir          # unidades, léxico e denso
python -m prototipo.rag aferir             # as três configurações + calibração
python -m prototipo.rag varrer-alfa        # a curva de alfa + leave-one-out

# o segundo modelo da task 3.3, matriz própria, mesmo conjunto
python -m prototipo.rag aferir      --modelo intfloat/multilingual-e5-small
python -m prototipo.rag varrer-alfa --modelo intfloat/multilingual-e5-small
```

`aferir` grava `prototipo/indice/afericao_<modelo>.json` e `varrer-alfa` grava
`prototipo/indice/varredura_alfa_<modelo>.json`. Os quatro arquivos estão
versionados. A matriz densa só é reconstruída se faltar, então reexecutar a
medição não repaga o custo de indexação. A medição parcial de 19/09 do braço
léxico continua em `prototipo/indice/afericao_lexica.json`, com a ressalva de
latência acima.

## Limites desta medição

- **20 consultas é pouco** para diferença de poucos pontos percentuais. A
  medição sustenta afirmação sobre diferença grande — recall@3 de 1,00 contra
  0,70 entre famílias — e não sobre empate técnico.
- O recorte não-covid do corpus é **dominado pela agência `boatos`** (11 das
  20 consultas). A medição não sustenta comparação entre agências.
- As consultas `reformulada` foram escritas por quem conhece o documento
  correto. Isso é um viés conhecido e otimista: um usuário real erraria mais.
- **A vantagem da híbrida sobre a densa pura é de uma consulta.** A diferença
  de MRR em `reformulada`, 0,845 contra 0,803 sobre 10 consultas, equivale a um
  alvo subindo da posição 2 para a 1. O que é robusto é que α=0,5 perde três
  documentos que α≥0,8 recupera; o que é frágil é a margem sobre a densa pura.
  O leave-one-out sustenta a margem, não a amplia.
- **O α foi escolhido e validado no mesmo conjunto de 20 consultas.** Não há
  conjunto reservado. O leave-one-out é o substituto honesto disponível, e não
  é a mesma coisa que um conjunto novo.
- A comparação de modelos usa **dois** modelos da mesma família `e5`. Ela mede
  efeito de tamanho, não de família nem de objetivo de treino.
