# Aferição da recuperação

**19/09/2026.** Tasks 3.1 a 3.6 de `add-selecao-modelos-arquitetura-rag`.

O índice de 18/09 funcionava mas não estava medido: os 35% de sobreposição entre
os braços eram sanidade, não aferição. Esta página traz a primeira medição com
documento correto conhecido — e o resultado desmente duas suposições do projeto.

!!! warning "Medição parcial"
    O braço denso desta máquina ainda estava indexando quando esta página foi
    escrita. O que está medido é o **braço léxico** e a **calibração do limiar**
    sobre ele. A comparação entre as três configurações (task 3.1) e entre dois
    modelos de embedding (task 3.3) fica pendente da matriz densa. O aferidor
    está pronto: `python -m prototipo.rag aferir`.

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
o braço denso existe para tapar, e a previsão que a medição pendente vai testar:
**se a densa não melhorar `reformulada`, a decisão 4 do `design.md` perde o
sustento e o híbrido vira custo sem retorno.**

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
```

O resultado é gravado em `prototipo/indice/afericao_<modelo>.json`. A medição do
braço léxico desta página está em `prototipo/indice/afericao_lexica.json`.

## Limites desta medição

- **20 consultas é pouco** para diferença de poucos pontos percentuais. A
  medição sustenta afirmação sobre diferença grande — recall@3 de 1,00 contra
  0,70 entre famílias — e não sobre empate técnico.
- O recorte não-covid do corpus é **dominado pela agência `boatos`** (11 das
  20 consultas). A medição não sustenta comparação entre agências.
- As consultas `reformulada` foram escritas por quem conhece o documento
  correto. Isso é um viés conhecido e otimista: um usuário real erraria mais.
- O braço denso e a comparação entre modelos de embedding **não** estão
  medidos nesta página.
