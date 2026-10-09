# Design: Limitações do MVP

## Context

Motivação em `proposal.md`. A ancoragem (`prototipo/resposta/ancoragem.py`)
continua como primeira barreira, barata e determinística. A conferência de D1
pega o que ela declara não pegar.

## Goals / Non-Goals

**Goals:**

- Nenhuma frase dos blocos 1 e 2 sem base nos trechos chega à pessoa.
- Termo legível sem mudar o texto revisado.
- Teto de 120 palavras garantido também quando os blocos 3 e 4 são curtos.

**Non-Goals:**

- Conferir o bloco 4 ("o que observar"), que é conselho geral, não afirmação.
- Trocar a ancoragem léxica.

## Decisions

### D1. Conferência de sustentação

`conferencia.conferir(resposta, trechos, mensagem, chat)` faz uma chamada com
os trechos citados (`T1`…), a mensagem e as frases numeradas dos blocos 1, 2
e 3. O prompt pede, em JSON, a lista das frases sem base:

- blocos 1 e 2: a frase precisa estar dita ou implicada diretamente por um
  trecho; conhecimento do modelo não vale;
- bloco 3: a frase precisa descrever algo que está na mensagem; o rótulo da
  técnica ("Técnica: …"), posto pelo código, não é conferido.

O código tira as frases apontadas e registra cada uma em
`Resposta.sem_base`. A abertura do bloco 1, escrita pelo código ("Falso."), e
a frase sobre opinião não são conferidas. Se o bloco 1 ou o 2 ficar sem frase
do modelo, a resposta é rebaixada, pelo mesmo caminho da ancoragem. Se o
bloco 3 ficar vazio, a primeira frase é mantida e o defeito "frase sem base"
fica registrado.

A conferência roda no pipeline (`bancada/pipeline.py`), dentro da etapa de
resposta, logo depois de `estrutura.responder`: montar, nova tentativa, corte
de teto, conferência. Assim os testes de `estrutura` ficam como estão, a
página não ganha etapa nova de andamento, e o rebaixamento reaproveita
`estrutura.responder` com o veredito rebaixado (`estrutura.rebaixar`). O corte
antes da conferência não atrapalha: a conferência só tira frases. Ela roda uma
vez por resposta, e só na forma com evidência. Falha da
chamada (`ErroGerador`, `ValueError`) deixa a resposta como está e registra
"conferência não rodou".

### D2. Termo em parágrafos

O texto da versão 3 é separado em seis parágrafos, um por assunto: o envio, a
minimização, o que a DeepSeek faz, o que fica do nosso lado, quem mantém e a
pergunta. As palavras não mudam, e a versão continua 3. O servidor passa a
manter as quebras de parágrafo, e a página monta um `<p>` por parágrafo dentro
do grupo do termo.

### D3. Corte no bloco 2

Depois de esgotar os blocos 3 e 4, `_cortar` tira frases do fim do bloco 2,
mantendo pelo menos uma. A frase sobre opinião, quando existir, fica. A regra
de desfazer o corte que cria defeito eliminatório continua.

### D4. Ajuste do juiz depois da primeira bancada

Bancada `20261009-163535`: 24/30, sem eliminatória, mas com seis falhas de
forma criadas pela conferência. O juiz tirou:

- a frase do modelo sobre a opinião da mensagem no bloco 2 (F01, F04, F06,
  R2), conferida contra os trechos, que nunca falam disso. Ela passa a ser
  conferida como frase sobre a mensagem;
- paráfrase do trecho (R1) e interpretação que decorre da mensagem (X2, R3).
  O prompt passa a aceitar resumo do trecho e interpretação da mensagem, e
  deixa de mandar marcar "na dúvida".

No X2, o juiz rebaixou certo: os trechos eram sobre boldo e **covid**, e a
alegação, sobre boldo e hepatite. A guarda tinha dado "falso" com evidência de
outra alegação, e a conferência barrou.

## Risks / Trade-offs

- [O juiz também erra e tira frase boa] → a frase tirada fica no rastro, e a
  bancada mostra quantas; se o rebaixamento crescer, revisar o prompt.
- [Latência] → medida na bancada; o critério de mediana de D10 de
  `add-gerador-api-deepseek` continua valendo.
