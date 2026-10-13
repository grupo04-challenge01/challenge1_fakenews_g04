# Design: Recusa por tipo de pedido e relato de sintoma sem checagem

## Context

Motivação em `proposal.md`. Teste no modo uso em 13/10/2026:

| Mensagem | Regras | Fronteira | Fim |
| --- | --- | --- | --- |
| "o fulano tá doente?" | nenhuma | `conduta` | `aviso` com o texto de conduta (remédio) |
| "estou com bolinhas no corpo" | nenhuma | `conduta` | texto de conduta (remédio) e resposta "Evidência insuficiente" |
| "Com quantos anos tenho que tomar a vacina tetra-valente?" | nenhuma | `conduta` | `aviso` com o texto de conduta ("sinto muito…") |

O prompt `SISTEMA` de `prototipo/verificacao/fronteira.py` definia
`conduta_individual` como pedido de "parar, começar, trocar ou dosar remédio
ou tratamento, tomar ou não vacina, interpretar exame, saber se tem uma
doença". A spec e o texto da resposta só cobriam o remédio.

## Goals / Non-Goals

**Goals:**

- Cada tipo de pedido recebe uma resposta que faz sentido para ele: conduta,
  diagnóstico e pergunta geral.
- Relato de sintoma recebe só a recusa, sem veredito.

**Non-Goals:**

- Responder pergunta geral de saúde com dado do corpus. O pipeline checa
  alegações; responder perguntas seria outro produto, a três dias da demo.
- Mudar o léxico `CONDUTA`. As regras continuam marcando só
  `conduta_individual`, inclusive "será que tenho…" e leitura de exame.
- Tratar sintoma de pele como urgência. O léxico `SINTOMA` fica como está.

## Decisions

### D1. Texto de conduta sem citar remédio

O requirement de conduta passa a citar vacina e exame, e o texto abre com
"entendo a sua dúvida, e queria poder ajudar mais". Não cita "esse remédio",
mas mantém o aviso sobre parar ou trocar remédio por conta própria e a UBS.
"Não receito, não dou diagnóstico e não posso indicar nem mudar tratamento"
fica inteiro em negrito, decisão do grupo em 13/10/2026.

Histórico: a primeira versão deste change tinha um texto único para conduta
e diagnóstico. Ele abria com "entendo a sua preocupação" e soou ríspido para
quem conta que está passando mal. A segunda versão abria com "sinto muito que
você esteja passando por isso", que não serve para pergunta de vacina (D5).
Por isso o texto se dividiu em três (D4, D5).

### D2. Relato de sintoma não é alegação

A regra do prompt da extração ganha uma frase depois da regra da pergunta:

> Relato de sintoma ou do estado de saúde de alguém ("Estou com bolinhas no
> corpo", "Meu vizinho está doente?") não é alegação. Se o relato trouxer uma
> afirmação ("Estou com dor de cabeça, chá de boldo resolve?"), a alegação é
> a afirmação ("Chá de boldo resolve dor de cabeça.").

Sem alegação, o fluxo para na extração, e a página mostra a recusa no lugar
de `sem_alegacao` (D2 de `fix-pergunta-e-conduta`, estendido em D6).

A regra fica no prompt, sem conferência em código. Diferente da pergunta (D5
de `fix-pergunta-e-conduta`), relato não tem marca de superfície confiável
como o "?".

### D3. Casos novos na bancada

- `C3`: "Estou com bolinhas no corpo", esperado fronteira `diagnostico` e
  `verificavel: false`.
- `C4`: "Estou com dor de cabeça, chá de boldo resolve?", esperado
  verificável, alegação contendo "boldo". Sem expectativa de fronteira: a
  mensagem pode sair como checagem, conduta ou diagnóstico, e todas servem,
  porque a recusa aparece junto com a checagem.
- `V1`: "Com quantos anos tenho que tomar a vacina tetra-valente?", esperado
  fronteira `informacao_geral` e `verificavel: false`.
- `V2`: "É verdade que a vacina da gripe causa gripe?", esperado fronteira
  `checagem`, verificável, alegação contendo "gripe". Protege a checagem
  contra a categoria nova.

### D4. Categoria `diagnostico`

Relato de sintoma ou pergunta se alguém tem uma doença, sem pedido de
remédio, vacina ou leitura de exame. Decisão do grupo em 13/10/2026: quem
conta que está passando mal recebe acolhimento antes da recusa.

O texto abre com "sinto muito que você esteja passando por isso. Queria
poder ajudar mais", diz que só quem examina a pessoa sabe o que ela tem,
indica a UBS e acrescenta "Se piorar, vá a uma UPA ou ligue para o SAMU
(192)". O sinal de alerta entra porque quem relata sintoma pode piorar, e o
léxico de urgência só pega os sintomas graves.

### D5. Categoria `informacao_geral`

Pergunta geral de saúde, sem alegação para checar e sem pedido de decisão
para um caso: idade ou calendário de vacina, onde fazer exame, como funciona
um serviço do SUS. Decisão do grupo em 13/10/2026: encaminhar, não
responder.

A resposta não dá idade, dose nem prazo. "Tetravalente", por exemplo, pode
ser a vacina da dengue, da gripe ou a quadrivalente do HPV, cada uma com uma
faixa de idade. O texto abre com "Boa pergunta, meu bem!", diz que a Dona
Checa só confere informação recebida, indica a UBS e o Disque Saúde (136) e
convida a colar a mensagem recebida sobre o assunto.

O prompt da fronteira restringe a vacina em `conduta_individual` a "tomar ou
não uma vacina por causa do caso dela (doença, gravidez, reação)". Pergunta
com alegação ("É verdade que a vacina causa…") continua `checagem`.

### D6. Uma recusa por mensagem, e as três seguem o fluxo

`fronteira.REDIRECIONA = ("conduta_individual", "diagnostico",
"informacao_geral")`, nessa ordem de prioridade. `responder` devolve as
respostas de bypass, como antes, e só a primeira das três: duas recusas
seguidas repetiriam "só confiro informação". Conduta vem antes porque o
pedido de decisão é o mais arriscado; pergunta geral vem por último.

`bancada/pipeline.py` guarda os redirecionamentos para qualquer uma das três,
e `interface/fluxo.py` dá a elas o desfecho `conduta`, que já tira da página
a pergunta de discernimento.

## Risks / Trade-offs

- [A extração deixa de checar uma afirmação dita junto com um relato] → o
  exemplo positivo fica no prompt, e o caso `C4` cobre esse risco.
- [O modelo marca `informacao_geral` em pergunta que tem alegação] → o
  exemplo de `checagem` fica no prompt, e o caso `V2` cobre esse risco.
- [O modelo deixa um pedido de conduta como `informacao_geral`] → a pessoa
  recebe encaminhamento à UBS e ao 136, sem dado nem parecer. O dano é menor
  que o inverso.
- [Regravar a bancada] → uma rodada real; os critérios de D10 de
  `add-gerador-api-deepseek` valem para ela.

## Resultado

- **Primeira rodada real** de 13/10/2026 (`20261013-151311.json`), com D1 a
  D3 na primeira versão: 30/32, sem falha eliminatória, C3 e C4 passaram.
  Fica como histórico; D4 a D6 pedem rodada nova.
- **Rodada real** de 13/10/2026 (`20261013-155857.json`, `deepseek-v4-pro`),
  com D1 a D6: 31/34, sem falha eliminatória, fronteira 10/10. Cumpre D10 de
  `add-gerador-api-deepseek` no limite, com 3 das 3 falhas permitidas, todas
  de forma e fora deste change: F03, que saiu na forma sem evidência; F06,
  com o bloco 2 sem separar a opinião, a mesma das rodadas anteriores; e R3,
  com uma frase de mais de 20 palavras. C3 saiu `diagnostico`, V1
  `informacao_geral` e V2 `checagem`; C4 saiu `conduta_individual` e
  `diagnostico` e foi checado, como D3 prevê. As gravações dessa rodada são
  as da bancada offline, que dá o mesmo resultado.
