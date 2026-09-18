# Índice híbrido — como o protótipo acha a checagem certa

**Data:** 18/09/2026 · **Fase:** Investigate · **Change:** `add-selecao-modelos-arquitetura-rag`

A [sonda do gerador](sonda-gerador.md) mediu o modelo que **escreve** a resposta,
com o trecho de evidência colado à mão porque o índice ainda não existia. Esta
página é a outra metade: o índice existe, e é ele quem decide a qualidade do
produto. Se a checagem certa não é recuperada, nenhum gerador a inventa sem
violar a regra de que todo veredito vem acompanhado da fonte que o sustenta.

## O que foi construído

| | |
| --- | --- |
| Registros lidos do corpus | 4.063 |
| Unidades de indexação | 5.090 |
| Fragmentos indexados | 22.464 |
| Registros em quarentena | 88 |
| Modelo de embedding | `intfloat/multilingual-e5-base`, 768 dimensões |
| Busca | exata, em memória, sem banco vetorial |
| Custo de indexação | 13,2 min (denso) + 2,1 s (léxico) |
| Custo de consulta | 26 a 33 ms no modo híbrido |

Tudo isso é reconstituível a partir do corpus com um comando, e o
`prototipo/indice/manifesto.json` versionado é a declaração auditável do que foi
indexado.

## Uma unidade não é um pedaço de texto de tamanho fixo

O tutorial padrão de RAG manda picar o documento em blocos de tamanho fixo. Aqui
isso seria um defeito, e a spec o proíbe por escrito: **fragmentação que separe
a alegação do seu veredito não pode ser usada**.

A razão é direta. Se a alegação "chá de jatobá cura câncer" cai num bloco e o
"é falso" da agência cai no bloco seguinte, a busca pode recuperar o primeiro
sozinho — e aí o sistema entrega ao gerador um texto que afirma a mentira, sem
o que a desmente.

A unidade adotada é a alegação com seu veredito e sua justificativa, carregando
agência, data e endereço. Checagem longa ainda precisa ser fragmentada, porque o
modelo de embedding lê no máximo 512 tokens por vez, mas **cada fragmento repete
o cabeçalho** com a alegação e o veredito. O pedaço nunca viaja sozinho.

Vale a ressalva que a spec faz questão de registrar: o índice guardar o texto
integral **não** autoriza mostrá-lo ao usuário. A resposta cita trecho curto e
parafraseia. Indexar não é reproduzir.

## O problema que deu mais trabalho: um registro, várias alegações

587 dos 4.063 registros trazem mais de um veredito. São as checagens de
entrevista e de debate, em que a agência avalia quatro ou cinco falas na mesma
página, cada uma com seu selo.

O corpus não diz onde uma alegação termina e a outra começa. Os selos eram
elementos visuais da página e não sobreviveram à raspagem — sobrou uma lista de
vereditos e um texto corrido. Alinhar os dois por ordem, na fé, é o caminho
óbvio e é exatamente o que a spec proíbe: nenhuma unidade pode receber veredito
de alegação diferente da sua. Um deslocamento de uma posição faz o sistema
afirmar que a agência chamou de falso algo que ela chamou de verdadeiro.

O que existe de concreto é um marcador de formato, e só na Lupa: cada alegação
aparece como linha inteira entre aspas. A regra adotada aceita a segmentação
**apenas quando o número de trechos entre aspas bate com o número de vereditos
declarados**. Bater não prova que o alinhamento está certo, mas é a evidência
disponível, e a checagem falha alto: uma alegação a mais ou a menos derruba o
registro para a via conservadora.

| Situação | Registros | O que acontece |
| --- | --- | --- |
| Um veredito só | 3.476 | vira uma unidade; o título é a alegação |
| Segmentação confere | 221 | uma unidade por alegação, veredito alinhado |
| Não confere, vereditos todos iguais | 278 | uma unidade, marcada como grossa |
| Não confere, vereditos divergentes | 88 | quarentena |

A terceira linha é um desvio assumido, não um acerto: a unidade cobre mais de
uma alegação. O que a torna aceitável é que, com todos os vereditos iguais, não
há veredito alheio a atribuir. Ela sai marcada, para que a citação saia sempre
do fragmento recuperado e nunca da unidade inteira.

Os 88 da quarentena são os casos em que o registro mistura verdadeiro com falso.
Eles ficam fora do índice e viram conjunto de teste — é o mesmo conjunto que o
tratamento de datasets já reservava para estudar a decomposição entre fato,
evidência e opinião.

## Por que dois tipos de busca, e não um

O índice tem dois braços:

- **Léxico (BM25).** Conta palavra. Acha `timerosal` porque a palavra
  `timerosal` está lá.
- **Denso (embeddings).** Compara sentido. Acha "vacina modifica o código
  genético" quando se pergunta por "vacina altera o DNA", sem nenhuma palavra em
  comum além de "vacina".

A ordem natural de construção seria fazer o denso primeiro e acrescentar o
léxico se precisar. O projeto inverteu essa ordem por decisão de spec, e o
domínio explica: checagem de saúde é densa em nome próprio — `qdenga`,
`oropouche`, `semaglutida`, `timerosal`, número de lote, dosagem. São exatamente
os termos pelos quais uma alegação é identificada, e são os que o denso trata
pior.

A medição sustentou a decisão. Em 12 consultas, a sobreposição média entre o
top-10 de cada braço foi de **35%** — as listas são complementares, não
redundantes. No top-5 do híbrido, 14 das 60 vagas foram ocupadas por unidades que
só o léxico encontrou e 6 por unidades que só o denso encontrou: **um terço do
top-5 se perderia ao desligar qualquer um dos dois**. Em `hidroxicloroquina
previne covid-19` a interseção foi zero — os dois braços acharam conjuntos
inteiramente diferentes.

## O defeito que só a medição mostrou

A primeira versão da fusão somava os dois scores direto. Ela rodava, devolvia
resultado plausível, e estava **desligando o braço denso**.

| Consulta | cosseno mediano | cosseno máximo | BM25 máximo |
| --- | --- | --- | --- |
| `chá da casca do jatobá cura câncer` | 0,787 | 0,893 | 35,1 |
| `hidroxicloroquina previne covid-19` | 0,816 | 0,903 | 11,3 |
| `como faço bolo de cenoura` | 0,762 | 0,826 | 13,2 |

O cosseno do modelo denso não é centrado. Ele devolve cerca de 0,79 para
qualquer par de textos, e o topo raramente passa de 0,90 — todo o sinal vive numa
faixa de 0,06, muito longe do zero. Somado a um BM25 que varia de 0 a 35, ele
vira praticamente uma constante: contribui o mesmo para todo candidato, e a
ordem final sai inteira do braço léxico.

O sintoma apareceu em `hidroxicloroquina previne covid-19`: o braço denso achou
a checagem certa, o léxico achou `dexametasona` e `própolis`, e a fusão premiou
o léxico. O híbrido estava de pé na forma e desligado no efeito.

A correção foi normalizar cada braço contra o **fundo da própria consulta**: a
mediana sobre os 22.464 fragmentos é o que aquele braço devolve para qualquer
coisa, e a distância até o percentil 99 é a escala em que ele realmente separa.
Depois da correção, a checagem que só o denso achava voltou ao top-3 do híbrido.

É a mesma lição da sonda do gerador, em outro lugar: **a primeira versão de uma
medição costuma confirmar o que se esperava.** Lá, uma checagem frouxa declarou
3 de 3 aprovações e virou 1 de 3 quando endurecida. Aqui, um híbrido que somava
dois números e parecia funcionar usava um deles só.

## O que o índice ainda não resolve

Perguntar `Qdenga causa a própria dengue` devolve checagens sobre dengue e zika,
com score alto, e nenhuma sobre Qdenga. O corpus termina em 2021 e a vacina é
posterior — o sistema não tem o que responder, mas o score não avisa isso.

Pior: `como faço bolo de cenoura`, que não tem nada a ver com o corpus, alcança
cosseno máximo de 0,826 contra 0,893 de uma consulta perfeitamente atendida. A
normalização contra o fundo reduz a distorção, não a elimina.

Isso é o problema do limiar de `evidência insuficiente`, e a medição já diz uma
coisa útil sobre ele: **ele não vai sair de similaridade bruta**. Calibrá-lo é a
próxima etapa, e o caso Qdenga é o teste de lacuna de acervo — a resposta certa
ali não é "não sei", é "meu acervo vai até 2021 e essa pauta é mais nova".

## Reproduzir

```bash
python -m prototipo.rag construir
python -m prototipo.rag buscar "chá da casca do jatobá cura câncer"
python -m prototipo.rag buscar "timerosal na vacina causa autismo" --modo lexica
python -m prototipo.rag buscar "vacina altera o DNA" --modo densa --k 5
```

Antes de construir qualquer unidade, dois portões rodam sobre o corpus: a
contagem de registros tem de bater com a declarada (4.063), e o arquivo passa
por verificação de perda de acentuação. Corpus que falha em qualquer um dos dois
não gera índice — indexar um corpus defeituoso propaga o defeito para tudo que
vem depois.

O portão de acentuação rendeu uma correção de método. O critério original era
"letra acentuada com zero ocorrência no arquivo é sinal de corrupção", e ele
reprovaria este corpus por causa do `Ü`, ausente em 21,5 milhões de caracteres.
Só que o trema foi abolido do português em 1990 e o corpus cobre 2013 a 2021 — a
ausência é da língua, não do arquivo. O que de fato distingue corrupção é a
maiúscula zerada **com** a minúscula frequente: no arquivo do FACTCK.BR, que foi
reprovado de verdade, `ã` aparece 3.625 vezes e `Ã` nenhuma.

## Próximos passos

1. Montar 20 consultas de aferição a partir de casos reais, com o documento
   correto conhecido para cada uma.
2. Medir recall das três configurações — só léxica, só densa, híbrida — e
   registrar o resultado mesmo se ele contrariar a decisão de usar híbrido.
3. Comparar ao menos dois modelos de embedding sob o mesmo conjunto.
4. Calibrar o limiar de `evidência insuficiente` sobre o score fundido,
   incluindo os casos de pauta ausente.
