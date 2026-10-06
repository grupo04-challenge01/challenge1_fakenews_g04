# Instrumento de Coleta das Métricas de Resultado e de Guarda

**Projeto:** Copiloto de Verificação de Desinformação em Saúde
**Task de Referência:** 6.5 (R4 + R6 + R7 — Samara)
**Especificação Relacionada:** requirement *Métricas de resultado e de guarda*, em `spec.md` desta pasta
**Decisão de desenho:** decisão 27 do `design.md` do change
**Código:** `prototipo/avaliacao/` (esquema `registro_sessao.json`, cálculo em `metricas.py`)
**Data da Versão:** 06/10/2026 — instrumento 1.0.0

Este documento é o anexo 4 do dossiê de submissão ao comitê de ética
(`dossie-submissao-cep.md`). Diz o que se mede em cada sessão, como o
pesquisador observa e anota, e como cada número sai do que foi anotado.

---

## 1. O que se mede

A spec pede quatro métricas de resultado e quatro de guarda. A métrica primária
do projeto é ganho de discernimento do usuário, não acurácia do sistema.

| Métrica | Tipo | Como se observa | Campo no registro | Como se calcula |
| :--- | :---: | :--- | :--- | :--- |
| **Discernimento** | resultado | Julgamento do participante sobre cada mensagem, com a ferramenta | `julgamento` | acertos ÷ itens com ferramenta, **sem** os itens-armadilha |
| **Transferência** | resultado | Julgamento no bloco final, sem a ferramenta | `julgamento` no bloco `transferencia` | acertos ÷ itens de transferência, reportado à parte |
| Transferência com critério | resultado | Se o participante disse por que decidiu | `criterios_citados` | itens de transferência com ≥ 1 critério ÷ itens de transferência |
| **Tempo até decisão fundamentada** | resultado | Hora da entrega da mensagem e hora do julgamento | `inicio`, `decisao` | mediana, em segundos, dos itens com ≥ 1 critério citado, por bloco |
| **Consulta a fonte externa** | resultado | Busca fora da ferramenta (site, buscador, outra pessoa) | `consultou_fonte_externa` | itens com consulta ÷ itens, por bloco |
| Abertura da camada de detalhe | resultado | Toque em "Ver fontes e detalhes" | `abriu_detalhe` | itens com abertura ÷ itens com ferramenta |
| **Aceitação cega** | guarda | Reação à saída quando a IA errou | `rotulo_exibido`, `expressou_duvida`, consultas, `julgamento` | ver seção 4; nos itens-armadilha e em todo erro da IA, separados |
| **Falso positivo em conteúdo legítimo** | guarda | Mensagem verdadeira julgada não confiável | `julgamento` em caso verdadeiro | por participante (com e sem ferramenta) e pelo sistema (`rotulo_exibido`) |
| **Queda de confiança em fonte confiável** | guarda | Questionário da seção 3, no início e no fim | `confianca_fontes` | média do fim − média do início; queda quando negativa |
| **Abandono por atrito** | guarda | Desistência de item ou da sessão por dificuldade com a ferramenta | `abandono`, `abandono_sessao` | itens e sessões com motivo `atrito`, separados de outros motivos |

Toda taxa sai como fração (`n` de `de`), além do percentual. Com 2 participantes
no piloto e 20 a 30 na coleta, a fração diz mais que o percentual. Piloto e
coleta nunca entram no mesmo agregado.

O instrumento **não define limiar de aprovação** para nenhuma métrica: a spec
não fixa um, e o grupo decide o que é aceitável depois do piloto (task 6.6).

---

## 2. Onde cada coleta entra na sessão

Os blocos A a D são os do `guia-piloto.md`.

| Momento | O que se registra |
| :--- | :--- |
| Bloco A, depois do TCLE assinado | Questionário de confiança, aplicação inicial |
| Bloco B, a cada mensagem | Ficha de item com ferramenta (seção 5) |
| Bloco C, a cada mensagem | Ficha de item de transferência (seção 5) |
| Fim do bloco C, **antes** do debriefing | Questionário de confiança, aplicação final |
| Bloco D | Marcar `debriefing_realizado`; nenhuma métrica é coletada aqui |

O questionário final vem antes do debriefing de propósito: depois do gabarito,
a confiança medida seria a do debriefing, não a da sessão com a ferramenta.

---

## 3. Questionário de confiança em fontes oficiais

Lido em voz alta pelo pesquisador, igual nas duas aplicações. As fontes são as
da lista oficial do projeto (`prototipo/indice/fontes_oficiais.json`).

> "Vou falar o nome de três lugares de onde vêm informações de saúde. Para cada
> um, me diga quanto você confia no que ele fala sobre saúde, de 1 a 5:
> 1 é nada, 2 é pouco, 3 é mais ou menos, 4 é bastante, 5 é totalmente."

| Fonte | Início (1–5) | Fim (1–5) |
| :--- | :---: | :---: |
| Ministério da Saúde | | |
| Fiocruz | | |
| Anvisa | | |

Se o participante não conhece uma das fontes, o pesquisador explica em uma
frase ("a Anvisa é o órgão do governo que aprova remédios e vacinas") e repete
a pergunta.

---

## 4. Reação à saída e aceitação cega

O cenário *Item-armadilha em sessão de teste* pede que se registre se o
participante **aceitou, questionou ou consultou fonte externa**. O pesquisador
não classifica na hora; anota três fatos observáveis, e a classificação sai
deles, valendo o comportamento mais forte:

1. abriu a camada de detalhe **ou** consultou fonte fora da ferramenta → **consultou fonte**;
2. senão, expressou dúvida em voz alta ou por gesto claro ("será?", "isso está estranho") → **questionou**;
3. senão → **aceitou**.

Correspondência com a ficha do `guia-piloto.md`: "Desconfiou da resposta" e
"Apontou incoerência" são **questionou**; "Aceitou cegamente" é **aceitou**
quando o julgamento segue a IA.

**Erro da IA** é a ferramenta exibir um veredito de sentido oposto ao gabarito:
`falso` ou `fora de contexto` para caso verdadeiro, `verdadeiro` para caso
falso. `Evidência insuficiente` não é erro: a ferramenta se absteve.

**Aceitação cega** é, num item em que a IA errou: reação **aceitou** e
julgamento igual ao que a IA disse. Sai em duas taxas:

- nos itens-armadilha (task 6.2), que é a medida pedida pela spec;
- em todo item em que a IA errou, armadilha ou não, porque o sistema real pode
  errar fora das armadilhas.

Item-armadilha em que a ferramenta **não** exibiu erro não mede nada e fica
fora da taxa; a validação do registro avisa quando isso acontece.

---

## 5. Ficha de anotação por item

Uma linha por mensagem, na ordem em que foi apresentada. Em papel, a ficha tem
as colunas abaixo; depois da sessão, o pesquisador passa para o registro
eletrônico (seção 7).

### Bloco B — com a ferramenta

| Campo | Como anotar |
| :--- | :--- |
| Caso | Código do caso (os 8 primeiros caracteres bastam) |
| Início | Hora em que a mensagem foi entregue ao participante (hh:mm:ss) |
| Veredito exibido | O que a ferramenta mostrou: falso, verdadeiro, fora de contexto ou evidência insuficiente |
| Expressou dúvida? | Sim / Não |
| Abriu detalhes? | Sim / Não |
| Consultou fora? | Sim / Não (site, buscador, perguntou a alguém) |
| Decisão | Hora em que disse o julgamento (hh:mm:ss) |
| Julgamento | Confiável / Não confiável / Não sei |
| Por quê | Critérios que a pessoa disse ter usado (seção 6) |
| Abandonou? | Não / Sim por atrito (dificuldade com a ferramenta) / Sim por outro motivo, com uma frase |

Pergunta de julgamento, sempre igual:

> "Você confiaria nessa mensagem? Sim, não ou não sabe? E o que fez você pensar assim?"

### Bloco C — transferência, sem a ferramenta

Os mesmos campos, **sem** veredito exibido, dúvida sobre a saída e abertura de
detalhes. A pergunta de julgamento é a mesma.

---

## 6. Codificação dos critérios citados

O que o participante diz em "por quê" é anotado com os rótulos do catálogo de
técnicas (`prototipo/resposta/catalogo_tecnicas.json`), que são também o que a
ferramenta ensina. Assim a transferência mede se a técnica ensinada voltou sem
a ferramenta (decisão 2 do `design.md`).

| Rótulo | O participante diz algo como |
| :--- | :--- |
| cura milagrosa | "promete curar tudo", "fácil demais" |
| manchete exagerada | "o estudo existe, mas não diz isso", "aumentaram o que a pesquisa falou" |
| fora de contexto | "isso é de outra época / outro lugar", "cortaram o vídeo" |
| fonte sem nome | "não diz quem falou", "'um médico' qualquer", "alguém que ouviu de alguém" |
| estudo inventado | "cita a universidade, mas esse estudo não existe", "a instituição nunca disse isso" |
| urgência fabricada | "manda compartilhar logo", "antes que apaguem" |
| medo de dano oculto | "diz que a vacina / o remédio esconde um perigo grave", "sem mostrar de onde tirou" |
| fonte oficial | "vem do Ministério / Fiocruz / Anvisa", "conferi no site oficial" |
| outro: *texto* | qualquer outro motivo, nas palavras da pessoa |

Decisão sem nenhum critério ("achei que sim") conta para discernimento e
transferência, mas não para o tempo até decisão **fundamentada**.

---

## 7. Do papel ao número

1. Antes da sessão: `python -m prototipo.avaliacao modelo --participante P-01 --tipo piloto --com <casos> --transf <casos>`
   grava o esqueleto em `prototipo/avaliacao/sessoes/P-01.json`, já com os
   casos na ordem e o hash do conjunto de casos.
2. Depois da sessão: o pesquisador passa a ficha para o arquivo (horas em
   formato `2026-10-20T14:05:10-03:00`).
3. `python -m prototipo.avaliacao validar` recusa registro incompleto ou
   incoerente: caso inexistente ou repetido, saída da ferramenta registrada na
   transferência, item-armadilha fora do bloco B, decisão antes do início,
   sessão sem TCLE ou sem debriefing. Invariantes S1 a S9 em
   `registro_sessao.json`.
4. `python -m prototipo.avaliacao metricas` calcula tudo e grava
   `prototipo/avaliacao/relatorio_metricas.json`, com o hash do conjunto de
   casos usado. Registro inválido fica fora do cálculo e aparece listado.

---

## 8. Proteção dos dados

- O registro identifica o participante só pelo código `P-xx` e pela faixa
  etária (18–39, 40–59, 60+). Nome, telefone e qualquer dado identificável
  ficam fora; o esquema recusa código fora do formato.
- Os registros de sessão ficam em `prototipo/avaliacao/sessoes/`, que **não é
  versionada** (`.gitignore`). Só o relatório agregado entra no repositório.
- O cálculo roda localmente; nenhum dado da sessão passa por API externa.

---

## 9. Condições para a medida valer

O instrumento mede o que acontece; não garante que a sessão foi montada para
medir. Três condições dependem dos casos e da ferramenta:

1. **Item-armadilha precisa exibir erro.** O conjunto de casos marca os itens
   com `armadilha`, mas a aceitação cega só é medida se a ferramenta de fato
   mostrar o veredito errado nesses itens. Se o sistema real acertar, o item
   não conta (seção 4). A saída errada precisa ser preparada antes da sessão.
2. **Os ids dos casos mudam a cada geração.** `utils/gerar_casos.py` usa
   `uuid4`; regerar o arquivo troca todos os ids. O registro guarda o hash do
   arquivo usado, e a validação recusa registro feito com outra versão.
3. **Falso positivo em conteúdo legítimo depende de casos verdadeiros.** Com
   poucos verdadeiros por sessão, essa taxa terá denominador pequeno; a sessão
   precisa incluir ao menos um caso verdadeiro em cada bloco para medi-la.
