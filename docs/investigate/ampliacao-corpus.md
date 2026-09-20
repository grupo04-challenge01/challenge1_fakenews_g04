# Ampliação do corpus: três bases novas e quatro níveis de acervo

**19/09/2026.** Change `add-ampliacao-corpus-ptbr`, fase Investigate — **55 de
55 tasks**.

O acervo deixou de ser um corpus e passou a ser quatro coisas diferentes, cada
uma com uma janela própria e cada uma evidência de algo distinto. Esta página
registra o que entrou, o que foi medido e as três premissas do próprio change
que a medição derrubou.

## Os quatro níveis, e do que cada texto é evidência

| Nível | Base | Janela medida | Itens | Do que o texto é evidência | Citável |
| --- | --- | --- | --- | --- | --- |
| **1. Texto integral** | FactCenter | 2013-07 a 2021-05 | 4.063 | do que a agência publicou sobre a alegação | **sim** |
| **2. Texto transformado** | FakeRecogna 2.0 | 2002 a 2023 | 26.436 no recorte | de que o item foi coletado e rotulado — o texto real foi sumarizado | não |
| **3. Circulação** | Telegram antivacina | 2020-01 a 2025-06 | 3.998.633 | de que aquilo circulou, naquele canal, naquela data | não |
| **4. Índice de localização** | Fact Check Tools API | corte em 20/09/2026 | 861 | de que existe checagem publicada, por quem e quando | não |
| *anexo* | WhaVax | 2020-03 a 2023-11 | 950 | de como quatro médicos avaliaram, na data | não |

## A tabela que fecha a declaração de cobertura

Os quatro termos de pauta que o acervo de checagem não alcança, vistos nos três
instrumentos:

| Termo | Acervo (checagem) | Índice (API) | Circulação (Telegram) |
| --- | --- | --- | --- |
| `qdenga` | **0** | 8 | 166 |
| `mpox` | **0** | 39 | 1.259 |
| `oropouche` | **0** | **0** | 122 |
| `semaglutida` | **0** | **0** | 56 |
| `dengue` | 60 | 76 | 5.401 |
| `covid` | 2.280 | 306 | 129.542 |

**`oropouche` e `semaglutida` circularam e ninguém checou.** Zero no acervo,
zero no índice, presentes na circulação. É o caso que prova que o terceiro
estado de resposta — lacuna de acervo **sem** ponteiro — precisa existir, e é o
caso que a task 8.2 não previa quando foi escrita.

Vale o cuidado inverso também: a presença na circulação é conhecimento **do
projeto**, não afirmação ao usuário. Dizer «isso circulou em canal antivacina» é
procedência, não evidência, e veredito por proxy de canal é vedado.

## O que a medição desmentiu

### 1. A FakeRecogna 2.0 não tem vocabulário de veredito

A task 9.1 mandava «absorver os três vocabulários de agência novos da 2.0 no
mapa de rótulos». O número estava certo — são mesmo três agências novas (AFP
Checamos, E-farsas, UOL Confere) — mas o objeto não existe: o rótulo da 2.0 é
**binário** (`Label` 0/1) atribuído pela coleta, e as oito colunas não incluem
campo de veredito textual. Não há vocabulário a absorver.

O mapa de veredito versão 1.0.0 segue com as 19 chaves das seis agências do
FactCenter, e a 2.0 entra como banco de estímulos, nunca como fonte de veredito
graduado.

### 2. `Categoria` não é vocabulário compartilhado entre as classes

O plano era regerar o subset temático com o mesmo filtro da v1: categoria em
`saúde` ou `ciência`. Medido, o filtro é inválido:

- a classe **real** tem exatamente **cinco** categorias — um vocabulário
  controlado;
- a classe **falsa** tem **69**, das quais **64 não existem na classe real** —
  incluindo 6.870 itens de categoria **vazia**, nomes de editoria de agência
  (`nas redes`, `uol confere`, `falso`) e temas que a real nunca recebe
  (`pandemia`, `conspirações`, `tecnologia`).

Filtrar por categoria produziria um subset de 14.434 reais contra 1.603 falsas —
90% real por artefato de metadado — e perderia todo item falso de saúde
arquivado sob `pandemia` ou sob vazio.

O critério adotado é **termo de saúde sobre o texto**, aplicado igual às duas
classes, o mesmo método que produziu o subset do FactCenter. Resultado: 26.436
itens, 18.784 reais e 7.652 falsos.

### 3. A transformação de texto vaza a classe

A notícia real da 2.0 passou por sumarização extrativa na origem; a falsa veio
crua. O efeito é mensurável:

| Classe | Mediana | Máximo |
| --- | --- | --- |
| real (Label 0) | 684 caracteres | 1.493 |
| falsa (Label 1) | 294 caracteres | 12.904 |

**Um classificador que não lê nenhuma palavra, só conta caracteres, acerta
80,5%** nesta base balanceada, contra 50% de linha de base. Nenhuma acurácia
medida sobre ela sustenta afirmação sobre detecção de desinformação — o que
reforça, com número, a regra que o projeto já tinha por princípio.

## O que bateu exatamente com a fonte

Nem tudo desmentiu. Três conferências fecharam sem divergência:

| Conferência | Declarado | Medido |
| --- | --- | --- |
| Posts do acervo de circulação | 3.998.633 | **3.998.633** |
| Canais | 119 | **119** |
| Empates 2-2 no WhaVax | 84 (8,8%) | **84 (8,8%)** |
| Itens da FakeRecogna 2.0 | 52.800 | **52.800** |
| `is_vaccine_related` positivos | 407.723 (10,2%) | **407.723** |

## As lacunas declaradas pelos autores, medidas

A task 3.6 exigia medir as lacunas, não copiá-las do artigo. Duas foram
verificadas e uma não se confirmou como descrita:

**Reações antes de 30/12/2021.** Os autores declaram ausência; medido, **1,7%**
dos 695.257 posts do período têm reação. Não é zero porque mensagem antiga pode
receber reação depois que o recurso passou a existir. A limitação vale; a forma
exata dela é essa.

**Meses com queda abrupta por canal apagado.** Medida sobre o arquivo inteiro,
apareceu **uma** queda (junho/2025, −78,5%), e ela se explica pelo fim da
coleta, não por canal apagado. O artefato que os autores descrevem não se
manifesta na série agregada — o que não o nega, só diz que ele é por canal e
não por mês.

## A faixa de empate do WhaVax, que quase se perdeu

Os autores adotaram estratégia conservadora: os 84 empates 2-2 foram rotulados
como não-desinformação. Se o pacote publicasse só o rótulo agregado, essa faixa
seria irrecuperável.

O pacote publica o voto por anotador (`av1_desinfo` a `av4_desinfo`), então ela
foi isolada. São **84 mensagens em que quatro médicos olharam e não
concordaram** — o material mais valioso da base para este projeto, porque é a
evidência de onde a fronteira passa.

| Votos de desinformação | Mensagens |
| --- | --- |
| 0 (consenso não) | 442 |
| 1 | 138 |
| **2 (empate)** | **84** |
| 3 | 82 |
| 4 (consenso sim) | 204 |

## Uma tensão de spec que o grupo precisa resolver

As tasks 8.5 e 8.6 se cruzam. A 8.5 manda verificar que correspondência apenas
na circulação **não resolve** nenhuma das três respostas de lacuna. A 8.6 manda
tirar da declaração o nível que **não muda nenhuma resposta** do sistema.

Aplicadas juntas, a circulação sai da declaração por construção — e o texto
transformado também, pelo mesmo motivo. Sobram dois níveis que mudam resposta:
o texto integral e o índice.

Duas leituras possíveis, e a escolha é do grupo:

1. a declaração de cobertura passa a ter **dois níveis** e três anexos de
   pesquisa e avaliação — mais honesta sobre o que o usuário vê;
2. o critério da 8.6 é afrouxado para «muda ao menos uma **decisão de
   projeto**» — o que preserva os quatro níveis, já que a circulação foi o que
   fechou o sub-recorte em vacinação.

O registro está em `datasets/derivados/declaracao_cobertura_quatro_niveis.json`,
seção `cada_nivel_muda_uma_resposta`.

## Privacidade, licença e o que não é versionado

| Base | Licença | Bruto versionado? |
| --- | --- | --- |
| FakeRecogna 2.0 | **MIT** | não (42 MB) |
| WhaVax | **CC BY 4.0** | não — texto de mensagem e remetente pseudonimizado |
| Telegram | **CC BY-NC 4.0** | não (3,608 GB) |

A cláusula não comercial do acervo de circulação **propaga** a todo derivado, e
está no cabeçalho de cada arquivo gerado. Nenhum texto de post e nenhum
`user_id` foi versionado, nem como exemplo em documentação — conferido por busca
no repositório.

Os 5,5 TB de mídia do acervo de circulação têm acesso restrito por acordo
assinado e **não foram baixados**.

## Reexecução

```bash
python datasets/scripts/sondar_factcheck_api.py       # portão de medição
python datasets/scripts/coletar_indice_checagens.py   # índice, 9 campos
python datasets/scripts/regerar_fakerecogna2.py       # subset e amostra
python datasets/scripts/medir_telegram.py             # 4M posts em streaming
```

A chave da API vem de `GOOGLE_FACTCHECK_API_KEY`, fora do git.
