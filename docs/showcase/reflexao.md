# Reflexão

!!! warning "Rascunho para o grupo"
    Este texto reúne os fatos do repositório que sustentam a reflexão. A
    reflexão é do grupo: reescrevam na voz de vocês, cortem o que não
    reconhecem e acrescentem o que viveram e o repositório não registra. A
    task 5.2 de `add-portfolio-showcase` só é marcada depois disso.

## O que mudou no nosso entendimento

Começamos o desafio com uma regra que nós mesmos inventamos: o sistema não
daria veredito. A Essential Question pede que a IA ajude a avaliar a
confiabilidade «sem substituir o pensamento crítico», e lemos isso como «sem
concluir».

Em 10/09 relemos o enunciado e vimos que ele não proíbe conclusão. Nossa
regra confundia não substituir o julgamento da pessoa com não oferecer
julgamento nenhum. Ela também ia contra a Big Idea: se o problema é excesso de
informação, segurar a conclusão só acrescenta atrito.

A regra nova é mais exigente, não menos: veredito permitido, nunca nu. Todo
veredito vem com o critério que o sustenta e com a fonte, e a pessoa precisa
poder discordar com base no que viu. Boa parte do que construímos depois
(guarda, ancoragem, conferência de sustentação, verificação de mito) existe
para cumprir essa frase.

*Para o grupo:* como foi chegar a essa revisão? Quem levantou a dúvida, e o
que convenceu o resto?

## O caso jacaré: preferir a regra a passar no teste

«Vacina de covid transforma pessoas em jacaré» recebe «evidência
insuficiente». Para quem pergunta, a resposta parece fraca, porque a dúvida
sai maior do que entrou. Tentamos resolver aceitando veredito quando a
alegação nova implica uma já checada: se a vacina transformasse alguém em
jacaré, ela alteraria o DNA, e essa alegação as agências desmentiram.

Os dois modelos negaram a implicação em todas as variantes que testamos. Em
13/10 o grupo decidiu manter a regra conservadora e não mudar a spec para o
caso passar. A lição que tiramos daqui: num sistema que dá veredito, um
«não sei» honesto custa menos do que um «falso» sem base.

*Para o grupo:* houve quem defendesse afrouxar a regra? O que pesou na
decisão?

## O que a avaliação pode e não pode dizer

A métrica primária do projeto é ganho de discernimento, não acurácia. O
piloto com duas pessoas deu 4 de 4 em discernimento e em transferência, mas
com n = 2 e sem linha de base isso valida o instrumento, não o efeito. O
item-armadilha, que mediria confiança cega na ferramenta, não foi exercido:
a ferramenta acertou nas duas sessões, e a aceitação cega ficou em 0 de 0.

A bancada de 30 casos mede o sistema, não a pessoa: 29 de 30 na rodada da
demo. É o número mais sólido que temos, e é justamente o que o projeto disse
que não seria a medida de sucesso. Fica a tensão para a próxima etapa: a
coleta com 20 a 30 pessoas, com a armadilha decidida.

Detalhe em [limitações da avaliação](../pendencias.md#limitacoes-da-avaliacao).

## Como trabalhamos

Trabalhamos com Spec-Driven Development: nada entrava no repositório sem um
change com proposta, design, specs e tasks. Isso nos obrigou a escrever o
porquê antes do como, e deixou rastro de cada decisão, inclusive das
revertidas.

O custo também apareceu. Na semana da apresentação, uma correção mudou o nome
das agências na resposta e quebrou a ancoragem de dois casos da bancada; só a
rodada real mostrou. E a ordem de arquivamento dos changes virou um problema
próprio, porque o protótipo lê textos das specs em tempo de execução.

*Para o grupo:* o que vocês fariam diferente no processo? Onde o SDD ajudou e
onde atrapalhou?

## O que levamos

*Para o grupo:* uma ou duas frases de cada pessoa sobre o que aprendeu. O
repositório não tem como registrar isso.
