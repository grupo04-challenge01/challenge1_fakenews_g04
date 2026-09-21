# Tasks pendentes, por fase

**Levantado em 20/09/2026**, a partir dos `tasks.md` dos seis changes ativos.
Companheiro de [Estado do projeto](estado.md), que conta o que já foi entregue;
esta página conta o que falta.

## Resumo

| Fase | Change | Feitas | Pendentes |
| --- | --- | --- | --- |
| **Engage** | `add-engage-desinformacao-saude` | **12** | **13** |
| **Investigate** | `add-tratamento-datasets-ptbr` | 31 | **2** |
| **Investigate** | `add-ampliacao-corpus-ptbr` | 55 | **0** ✅ |
| **Investigate** | `add-selecao-modelos-arquitetura-rag` | 29 | **4** |
| **Investigate → Act** | `fix-resposta-sem-evidencia` | 6 | **7** |
| **Act** | `mvp-copiloto-verificacao` | 0 | **31** |
| **Showcase** | *nenhum change existe* | — | — |
| | **total** | **133** | **57** |

A distribuição engana se lida rápido. As 4 pendentes do RAG são **um comando**
na máquina certa; as 21 do Engage são **trabalho de grupo presencial** que nunca
foi feito; e as 31 do Act são a maior parte do produto.

## O que bloqueia o quê

Toda pendência cai em uma de cinco categorias. Saber qual muda quem precisa
fazer o quê.

| Bloqueio | Tasks | Quem resolve |
| --- | --- | --- |
| **Máquina** — precisa do ambiente com MPS | 4 | quem tem o Mac |
| **Trabalho de grupo** — sessão presencial, card sorting, forense | 11 | o grupo inteiro |
| **Decisão de grupo** — não é execução, é escolha | 4 | reunião |
| **Processo externo** — CEP, coleta de rede | 3 | prazo de terceiro |
| **Implementação** — código e prompt, destravados | 35 | quem estiver codando |

---

## Engage — 13 pendentes

**Change:** `add-engage-desinformacao-saude` · **Vigência declarada:** 07/09 a
11/09 · **Status:** 12 de 25, vencida há 9 dias.

Em 20/09 fecharam oito tasks — todo o bloco 1, todo o bloco 6, a validação do
bloco 7 e a decisão sobre o change de instrumento. **O que restou é, sem
exceção, trabalho que exige as pessoas presentes:** forense com um caso por pessoa e tempo cronometrado, sessão de
brainstorming com etapa privada, e card sorting dos sinais que cada integrante
usa na prática. Nada disso pode ser escrito por alguém no lugar do grupo.

### O que ficou pronto para a sessão

| Artefato | Serve a | Onde |
| --- | --- | --- |
| Seis casos selecionados, quatro tipos de manipulação | bloco 2 | [Casos da forense](engage/casos-forense.md) |
| Template da ficha, oito campos e checklist | bloco 2 | [Ficha de caso](engage/ficha-de-caso.md) |
| Board dos cinco quadros, com as três regras de condução | bloco 3 | [Board do brainstorming](engage/board-brainstorming.md) |
| Protocolo do card sorting e doze cartões-semente | bloco 4 | [Kit do workshop](engage/kit-matriz-confianca.md) |

### Bloco 2 — Investigação forense (4)

| # | Task | Bloqueio |
| --- | --- | --- |
| 2.1 | Distribuir os casos, um por pessoa no mínimo | grupo |
| 2.2 | Analisar cada caso com leitura lateral, **registrando o tempo gasto** | grupo |
| 2.3 | Preencher uma ficha por caso, com fontes rastreáveis | grupo |
| 2.4 | Consolidar os tempos medidos como evidência para o quadro Problema | grupo |

Os seis casos já estão escolhidos e classificados por tipo. O tempo medido da
2.2 não é burocracia: é a evidência que sustenta o quadro Problema, e sem ele o
argumento do projeto vira opinião.

### Bloco 3 — Sessão de brainstorming, ~90 min (3)

| # | Task | Bloqueio |
| --- | --- | --- |
| 3.1 | Rodar Problema, Público e Sucesso em modo privado antes de abrir | grupo |
| 3.2 | Preencher o quadro Solução **apenas como hipóteses**, sem decidir | grupo |
| 3.3 | Plotar guiding questions na matriz impacto × incerteza | grupo |

### Bloco 4 — Matriz de confiança (4)

| # | Task | Bloqueio |
| --- | --- | --- |
| 4.1 | Card sorting dos sinais que cada integrante usa na prática | grupo |
| 4.2 | Consolidar em dimensões, com sinal observável, papel da IA e **limite** | grupo |
| 4.3 | Escrever a rubrica de três níveis por dimensão | depende de 4.2 |
| 4.4 | Testar a matriz contra os casos da forense e remover o que não discrimina | **depende do bloco 2** |

**Este bloco subiu de prioridade.** Deixou de ser dívida histórica: a spec de
`adaptacao-criterios-en` exige rubrica «compatível com `matriz-confianca`», e
essa compatibilidade nunca foi verificada, porque a matriz não existe. A task
8.1 do Act depende dela também.

A 4.4 amarra o bloco 4 ao bloco 2 — sem fichas preenchidas, a validação da
matriz não tem contra o que rodar. **A forense vem antes.**

### Bloco 7 — Fechamento (2)

| # | Task | Bloqueio |
| --- | --- | --- |
| 7.1 | Consolidar o portfólio de pesquisa (fichas + método + datasets) | depende dos blocos 2 a 4 |
| 7.2 | Consolidar a matriz de confiança versão 1 | depende do bloco 4 |

A parte «datasets» da 7.1 já está pronta — é o que o bloco 6 entregou. Falta a
parte «fichas + método», que sai da forense.

> **A 7.4 foi resolvida em 20/09/2026.** O change
> `add-instrumento-avaliacao-ptbr` **não será aberto**: a capability
> `avaliacao-instrumento` de `mvp-copiloto-verificacao` já cobre o escopo nos
> seus quatro requirements, e o material de estímulo já veio do Investigate.
> Escopo preservado, rastreamento realocado. Motivo registrado no `design.md`
> do change do Engage.

## Investigate — 6 pendentes

### `add-tratamento-datasets-ptbr` — 2 de 33

| # | Task | Bloqueio |
| --- | --- | --- |
| 3.5 | Recoletar o FACTCK.BR pelos três feeds com o script reparado, registrando a perda histórica como irreversível | processo externo (coleta de rede) |
| 5.4 | Validar a rubrica contra casos brasileiros e remover o que não discrimina | trabalho de grupo (anotação humana) |

**Sobre a 3.5.** O texto original pedia o impossível — regerar o derivado «a
partir da fonte, com a correção» — quando a corrupção já está no `FACTCKBR.tsv`
distribuído (`Ã` = 0 contra `ã` = 3.625 na própria fonte). A task foi reescrita
para o que é executável: recoletar pelos feeds do Aos Fatos, Agência Pública e
Lupa com o `update_factckbr.py` já corrigido. Traz só artigos recentes, não
recompõe as 1.313 alegações históricas.

**Sobre a 5.4.** O instrumento está entregue: seis critérios com rubrica de três
níveis, e as cinco remoções com motivo por escrito. O que falta é a validação
empírica, que exige anotação humana dos casos — e o proxy automático que
tentamos foi **medido e reprovado**: sob qualquer piso único ele removeria
`alarme` e `linguagem`, os dois critérios mais relevantes para desinformação.

### `add-selecao-modelos-arquitetura-rag` — 4 de 33

As quatro dependem da **mesma matriz densa**, e fecham juntas.

| # | Task |
| --- | --- |
| 3.1 | Medir recall das três configurações — só léxica, só densa, híbrida |
| 3.2 | Registrar o resultado como evidência da decisão 4, **inclusive se contrariar a decisão** |
| 3.3 | Comparar ao menos dois modelos de embedding sob o mesmo conjunto |
| 3.4 | Medir a latência de consulta de cada modelo, separando custo de indexação de custo de consulta |

**Bloqueio: máquina.** A indexação densa roda a ~0,8 fragmentos/s em CPU e não
fecha em sessão; no ambiente com MPS levou 13 minutos. O conjunto de aferição,
o aferidor e a calibração já existem e estão versionados.

```bash
python -m prototipo.rag construir     # se a matriz não existir
python -m prototipo.rag aferir        # fecha 3.1, 3.2 e 3.4
python -m prototipo.rag aferir --modelo intfloat/multilingual-e5-small   # 3.3
```

O braço léxico já está medido: recall@3 de **1,00** em `verbatim` e **0,70** em
`reformulada`. A previsão a testar é direta — **se a densa não melhorar
`reformulada`, a decisão 4 perde o sustento e o híbrido vira custo sem
retorno**. A task 3.2 obriga a registrar isso se acontecer.

---

## Investigate → Act — 7 pendentes

### `fix-resposta-sem-evidencia` — 7 de 13

Change de correção aberto em 19/09. Planejamento completo, specs escritas sob a
saída A (forma própria para o caso sem evidência).

**Bloqueia a task 3.2 do MVP.**

| # | Task | Bloqueio |
| --- | --- | --- |
| 2.1 | Conferir a forma sem evidência contra o teto de 120 palavras de `acessibilidade-leitura`, **medindo respostas reais** | implementação |
| 2.2 | Conferir contra `recuperacao-evidencia` que nenhum bloco induz afirmação sem trecho | implementação |
| 2.3 | Conferir contra `fronteira-orientacao-saude` que a forma sem evidência não vira porta de conduta clínica | implementação |
| 2.4 | Levar o terceiro estado à task 8.2 de `add-ampliacao-corpus-ptbr` | **já resolvido** na declaração de quatro níveis; confirmar |
| 3.1 | Sondar o gerador local nos três estados, formato da sonda de 18/09 | precisa de Ollama + Gemma 4 |
| 3.2 | Confirmar que a sonda T1 deixa de degenerar — o defeito que abriu o change | idem |
| 3.3 | Teste que reprova resposta com técnica nomeada sob `evidência insuficiente` | implementação |

As 3.1 e 3.2 precisam da máquina com Ollama e o Gemma 4 12B QAT instalados.

---

## Act — 31 pendentes

**Change:** `mvp-copiloto-verificacao` · **Cronograma declarado:** semanas 4–5 ·
**Executadas até agora: nenhuma.**

Esta é a fase inteira do produto. O bloco 1 estava bloqueado pelo tratamento dos
datasets — **e não está mais**.

### Bloco 1 — Corpus e recuperação (6) — **destravado em 19/09**

| # | Task | O que já existe |
| --- | --- | --- |
| 1.1 | Esquema de indexação do recorte de saúde do FactCenter | `prototipo/rag/unidades.py` — 5.090 unidades, 22.464 fragmentos |
| 1.2 | Indexar FACTCK.BR como fonte auxiliar, com rótulos normalizados | **atenção:** reprovado para citação; só contagem de rótulo |
| 1.3 | Lista de fontes oficiais aceitas (Ministério da Saúde, Fiocruz, Anvisa) | nada |
| 1.4 | Recuperação com prioridade de idioma (PT-BR antes de EN) | híbrida PT-BR pronta |
| 1.5 | Definir e calibrar o limiar de `evidência insuficiente` | **medido:** não sai do score fundido; sobre BM25 bruto, 27,2 rejeita todo o ruído e custa 40% dos positivos |
| 1.6 | Ancoragem trecho a afirmação e descarte de afirmação sem trecho | procedimento de auditoria em 5 passos na decisão 12; `tratamento.integridade.trecho_e_fiel` |

### Bloco 2 — Verificação e veredito (5)

| # | Task | Nota |
| --- | --- | --- |
| 2.1 | Prompt de extração de alegação, com seleção quando há várias | — |
| 2.2 | Prompt de classificação nos quatro rótulos | o mapa de veredito versionado já existe |
| 2.3 | Guarda contra veredito por conhecimento paramétrico | a sonda de 18/09 já mediu o comportamento base |
| 2.4 | Teste de regressão com itens verdadeiros contra-intuitivos | **sem material:** 21 itens `verdadeiro` em 4.063, e a FakeRecogna 2.0 não resolve |
| 2.5 | Prompt de decomposição fato / evidência / opinião | 245 registros `misto` reservados como conjunto de teste |

### Bloco 3 — Resposta formativa (4)

| # | Task | Nota |
| --- | --- | --- |
| 3.1 | Fechar o catálogo de 6 a 8 técnicas | dois rótulos de emoção propostos com motivo na decisão 13 do RAG |
| 3.2 | Prompt da estrutura de quatro blocos | **bloqueado** por `fix-resposta-sem-evidencia` |
| 3.3 | Validação automática: rótulo usado pertence ao catálogo | a sonda alertou: pertinência não é adequação |
| 3.4 | Verificar que a alegação falsa nunca abre a resposta sem marcação | — |

### Bloco 4 — Fronteira de saúde (3)

| # | Task | Nota |
| --- | --- | --- |
| 4.1 | Classificador de pedido de conduta clínica individual | **obrigatório**, não opcional: a sonda T2 mostrou que prompt não sustenta a fronteira |
| 4.2 | Respostas de redirecionamento, incluindo caso de sinal de risco | — |
| 4.3 | Bateria de testes adversariais de pedido de conduta | — |

A 4.1 é o **único candidato a fine-tuning** hoje, e as quatro condições que o
autorizam estão na decisão 12 do RAG. Falta a condição 2: conjunto de avaliação
versionado.

### Bloco 5 — Interface (4)

| # | Task |
| --- | --- |
| 5.1 | Camada visível e camada de detalhe |
| 5.2 | Checklist de acessibilidade: contraste, fonte, alvo de toque, ação primária |
| 5.3 | Fluxo de primeira verificação sem cadastro |
| 5.4 | Verificação de legibilidade da camada visível |

Todo o bloco depende da **decisão de canal** (task 7.1), ainda aberta.

### Bloco 6 — Avaliação (6)

| # | Task | Bloqueio |
| --- | --- | --- |
| 6.1 | Curar 20 a 30 casos, com no mínimo 4 verdadeiros contra-intuitivos | grupo — e os verdadeiros são trabalho manual |
| 6.2 | Configurar 4 a 6 itens-armadilha | grupo |
| 6.3 | Redigir TCLE e roteiro de debriefing | implementação |
| 6.4 | **Submeter protocolo ao comitê de ética** | **processo externo, com prazo próprio** |
| 6.5 | Instrumentar coleta das métricas de resultado e de guarda | implementação |
| 6.6 | Rodar piloto com 2 participantes antes da coleta | depende de 6.4 |

> **A 6.4 é a pendência de maior risco de cronograma do projeto.** Submissão ao
> CEP tem prazo que não depende do grupo, e as 6.6, o teste com usuário e a
> métrica primária de sucesso dependem dela. Se houver uma coisa a começar
> nesta semana, é essa.

O material de estímulo para a 6.1 e a 6.2 melhorou muito em 19/09: 950
mensagens do WhaVax com veredito de quatro médicos, **84 delas empatadas** — que
são casos difíceis já identificados —, mais 300 itens da FakeRecogna 2.0 e os
245 registros `misto` do corpus.

### Blocos 7 e 8 — Decisões e fechamento (3)

| # | Task | Bloqueio |
| --- | --- | --- |
| 7.1 | Definir o canal de entrega (WhatsApp vs. web) e registrar em `design.md` | **decisão de grupo** |
| 8.1 | Conferir consistência do catálogo de técnicas com as dimensões da matriz de confiança | depende do Engage bloco 4 |
| 8.2 | `openspec validate mvp-copiloto-verificacao --strict` | **já passa limpo** |

---

## Showcase — nenhum change existe

**Cronograma declarado:** semana 6. **Nenhum change cobre esta fase.**

A metodologia do projeto diz «um change por fase do CBL». Engage, Investigate e
Act têm os seus; Showcase não. Os entregáveis finais do desafio incluem
**apresentação e reflexão**, e hoje nenhuma task no repositório os cobre.

Precisa ser aberto antes da semana 6, e a proposta natural é que ele cubra:

- consolidação do portfólio de pesquisa como entregável apresentável;
- a apresentação em si, e o que dela é evidência medida contra o que é
  narrativa;
- a reflexão sobre o que o grupo aprendeu, que o CBL trata como entregável e
  não como epílogo.

---

## Onde estamos no cronograma

Datas derivadas da proposta do challenge em 20/09/2026 — ver
`openspec/project.md`.

| Semana | Fase | Datas | Situação |
| --- | --- | --- | --- |
| 1 | Engage | 07/09 a 11/09 | **vencida há 9 dias**, 12 de 25 tasks |
| 2 | Investigate | 14/09 a 18/09 | encerrada |
| **3** | **Investigate** | **21/09 a 25/09** | **começa amanhã — é a última** |
| 4 | Act | 28/09 a 02/10 | não começou |
| 5 | Act | 05/10 a 09/10 | não começou |
| 6 | Showcase | 12/10 a 16/10 | sem change |

**Hoje é domingo, 20/09.** O Investigate tem **cinco dias úteis** e encerra na
sexta, 25/09. O Act começa na segunda seguinte, 28/09.

### O que isso muda na leitura

**O Investigate não está atrasado.** Está em 115 de 121, com 6 pendentes, e as
4 do RAG são um comando na máquina com MPS. Fechar a fase no prazo é
plausível — depende de rodar a aferição densa esta semana.

**O Engage está.** Nove dias vencido. Em 20/09 fecharam sete tasks, todas as que
não exigiam o grupo presente — restam 14, e **as 14 exigem**. Pela própria
proposta, a entrega do Engage é «processo investigativo + guiding questions»: as
guiding questions estão prontas desde 11/09, e o processo investigativo agora
tem casos, ficha e protocolo prontos, faltando ser **executado**.

### O caminho crítico é o comitê de ética

A cadeia é esta, e ela não tem folga:

```text
6.4 submeter ao CEP  →  6.6 piloto com 2 participantes  →  teste com usuário
                                                        →  métrica primária
```

O Act encerra em **09/10** e o Showcase é de **12 a 16/10**. Da data de hoje até
o fim do Act são **19 dias**. Toda a avaliação com usuário — que é de onde sai a
métrica primária de sucesso do projeto, ganho de discernimento — está depois da
aprovação do CEP nessa cadeia.

O grupo sabe o prazo real do CEP da instituição; eu não. Mas a estrutura da
dependência é essa, e a janela é essa. **Se houver uma única coisa a iniciar
nesta segunda, é a submissão** — ela é a única pendência cujo prazo não depende
de ninguém do grupo.

### Sugestão de ordem para a semana 3

1. **Segunda:** submissão ao CEP (6.4) e aferição densa na máquina com MPS
   (3.1 a 3.4 do RAG, fecha o change).
2. **Segunda ou terça:** forense — bloco 2 do Engage. Vem **antes** do workshop,
   porque a task 4.4 valida a matriz contra os casos analisados. Casos, ficha e
   protocolo já estão prontos; falta cronometrar e preencher.
3. **Meio da semana:** workshop da confiança — bloco 4. É pré-requisito da
   rubrica já entregue e da task 8.1 do Act. Kit pronto em
   [Kit do workshop](engage/kit-matriz-confianca.md).
4. **Quando der:** as cinco decisões abaixo, que são reunião e não execução.
5. **Antes de 28/09:** abrir o change de Showcase, que é a lacuna de estrutura
   que sobrou.

## A ordem das fases foi invertida, e isso tem custo

O CBL prevê Engage (07/09 a 11/09) antes de Investigate (semanas 2–3). O que
existe é o contrário: **Engage em 4 de 25, Investigate em 115 de 121**.

**Por que aconteceu.** As 21 pendentes do Engage são quase todas trabalho de
grupo presencial — forense com um caso por pessoa, sessão de brainstorming de
90 minutos, card sorting da matriz. Nada disso se faz individualmente. O que
avançou foi o que dava para avançar sozinho.

**O que custou.** A ordem de dependência declarada em [Estado do
projeto](estado.md) tem três cadeias, e elas não foram afetadas igualmente:

| Cadeia | Respeitada? | Consequência |
| --- | --- | --- |
| `guiding q.` → `frescor-corpus` | **sim** | o bloco 5 do Engage estava pronto |
| `forense` → `normalizacao-rotulos` | não, sem dano | a normalização de rótulo não precisava das fichas de caso |
| `matriz` → `adaptacao-criterios-en` | **não, com dívida** | ver abaixo |

### A dívida da terceira cadeia

A spec de `adaptacao-criterios-en` exige, em texto expresso, que a rubrica seja
**«de três níveis compatível com a capability `matriz-confianca`»**.

A rubrica de seis critérios foi entregue com três níveis cada. A compatibilidade
com `matriz-confianca` **não foi verificada contra nada**, porque a matriz não
existe — o bloco 4 do Engage está em 0 de 4.

A task 5.3 está marcada corretamente: ela pede a adaptação, e a adaptação foi
feita. Mas o requirement da capability só se cumpre quando a matriz existir e a
compatibilidade for conferida. **Quando o bloco 4 do Engage fechar, a rubrica
precisa ser reconferida contra a matriz**, e pode exigir ajuste.

A mesma dependência alcança a task 8.1 do Act, que manda conferir a consistência
do catálogo de técnicas com as dimensões da matriz.

### O que isso implica para a ordem de trabalho

O bloco 4 do Engage — card sorting, dimensões, rubrica, teste contra os casos —
deixou de ser dívida histórica e passou a ser **pré-requisito de duas coisas já
construídas**. Ele sobe na fila, junto com a submissão ao comitê de ética.

## Decisões que travam execução

Cinco, e nenhuma é trabalho — são escolhas. Cada uma destrava tasks.

| # | Decisão | Destrava |
| --- | --- | --- |
| 1 | **Canal de entrega** (WhatsApp vs. web) | bloco 5 inteiro do MVP, 4 tasks |
| 2 | **Destino de `enganoso` (218) e `impreciso` (64)** no mapa de veredito | fecha o mapa versão 1.1 |
| 3 | **Composição do catálogo de 6 a 8 técnicas** | tasks 3.1 e 3.3 do MVP |
| 4 | **Declaração de cobertura: dois níveis ou quatro?** | fecha a tensão entre as tasks 8.5 e 8.6 |
| 5 | **«Identificar vieses» é requisito ou *Out of Scope*?** | cobertura de competência nomeada no enunciado |

Sobre a 5: a competência tem cobertura **parcial** desde 17/09. `acervo-circulacao`
endereça procedência e alcance; o critério `conflito_de_interesse` da rubrica
endereça quem publicou e o que ganha com isso. Falta o **viés de confirmação de
quem lê** — e essa é a face que mais se aproxima da métrica primária do projeto,
que é ganho de discernimento do usuário.

## Uma lacuna de estrutura

**Não existe change de Showcase.** Abrir antes da semana 6 (12 a 16/10).

A outra lacuna — `add-instrumento-avaliacao-ptbr` — **foi fechada em
20/09/2026**: o change não será aberto, e a capability `avaliacao-instrumento`
de `mvp-copiloto-verificacao` responde pelo escopo.
