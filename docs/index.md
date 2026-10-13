# Challenge 1 — Desinformação em Saúde

Portfólio de pesquisa do **grupo 04**, residência em IA do
Instituto Eldorado.

A proposta original do challenge, de onde saem a Big Idea, a Essential Question
e o cronograma das seis semanas, está em [CBL_Challenge1.pdf](CBL_Challenge1.pdf).


## O que estamos construindo

Um copiloto de verificação de informação de saúde: a pessoa manda a mensagem
que recebeu, e o sistema responde com o veredito **e** com o critério que
permitiu chegar nele — de modo que ela consiga avaliar a próxima mensagem
sozinha.

O que medimos como sucesso não é a acurácia do sistema. É a **transferência**:
o acerto da pessoa depois, sem a ferramenta.

!!! success "Situação em 13/10/2026"
    O protótipo funciona de ponta a ponta. A **Dona Checa** recebe texto ou
    link pelo chat web e responde em cerca de 11 segundos. Na bancada de 30
    casos, passa em 28, sem nenhuma falha eliminatória. Estamos na semana 6,
    o Showcase.

## Por onde começar

| Se você quer... | Vá para |
| --- | --- |
| Entender o enunciado do desafio | [O desafio](visao-geral.md) |
| Entender como o grupo trabalha | [Metodologia](metodologia.md) |
| Ver as perguntas que vamos investigar | [Guiding Questions](engage/guiding-questions.md) |
| Saber quais dados temos e o que há de errado com eles | [Datasets e achados](engage/datasets.md) |
| Ver como o protótipo funciona e o que foi medido | [Protótipo e avaliação](act/prototipo-avaliacao.md) |
| Subir o chat da Dona Checa | [Chat web](interface/chat-web.md) |
| Saber o que está pronto e o que falta | [Estado do projeto](estado.md) e [Tasks pendentes](pendencias.md) |

## Onde as coisas moram no repositório

```text
docs/          este site (portfólio)
openspec/      especificações: o que cada fase entrega e sob que critério
datasets/      pacote de dados coletados, derivados e relatório de contagens
tratamento/    leitura, vereditos, integridade e frescor dos datasets
prototipo/     o copiloto: entrada, verificação, recuperação, resposta, avaliação
interface/     chat web da Dona Checa (FastAPI)
bancada/       teste ponta a ponta em 30 casos, com gravações
exploracao/    notebooks de análise exploratória e de avaliação
```

!!! note "Nada entra sem spec"
    O projeto opera sob Spec-Driven Development. Código, dataset ou documento
    só entra no repositório se houver um *change* ativo que o cubra. Ver
    [Metodologia](metodologia.md).
