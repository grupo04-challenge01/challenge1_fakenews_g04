# Tasks pendentes, por fase

**Levantado em 20/09/2026**, a partir dos `tasks.md` dos seis changes ativos.
Companheiro de [Estado do projeto](estado.md), que conta o que já foi entregue;
esta página conta o que falta.

## Resumo

| Fase | Change | Feitas | Pendentes |
| --- | --- | --- | --- |
| **Engage** | `add-engage-desinformacao-saude` | 4 | **21** |
| **Investigate** | `add-tratamento-datasets-ptbr` | 31 | **2** |
| **Investigate** | `add-ampliacao-corpus-ptbr` | 55 | **0** ✅ |
| **Investigate** | `add-selecao-modelos-arquitetura-rag` | 29 | **4** |
| **Investigate → Act** | `fix-resposta-sem-evidencia` | 6 | **7** |
| **Act** | `mvp-copiloto-verificacao` | 0 | **31** |
| **Showcase** | *nenhum change existe* | — | — |
| | **total** | **125** | **65** |

A distribuição engana se lida rápido. As 4 pendentes do RAG são **um comando**
na máquina certa; as 21 do Engage são **trabalho de grupo presencial** que nunca
foi feito; e as 31 do Act são a maior parte do produto.

## O que bloqueia o quê

Toda pendência cai em uma de cinco categorias. Saber qual muda quem precisa
fazer o quê.

| Bloqueio | Tasks | Quem resolve |
| --- | --- | --- |
| **Máquina** — precisa do ambiente com MPS | 4 | quem tem o Mac |
| **Trabalho de grupo** — sessão presencial, card sorting, forense | 15 | o grupo inteiro |
| **Decisão de grupo** — não é execução, é escolha | 5 | reunião |
| **Processo externo** — CEP, coleta de rede | 3 | prazo de terceiro |
| **Implementação** — código e prompt, destravados | 38 | quem estiver codando |

---

## Engage — 21 pendentes

**Change:** `add-engage-desinformacao-saude` · **Vigência declarada:** 08/09 a
11/09 · **Status real:** vencida e incompleta.

Esta é a dívida mais antiga do projeto e a menos visível, porque o Investigate
avançou por cima dela. As guiding questions ficaram prontas (bloco 5); o resto
não.

### Bloco 1 — Preparação (3)

| # | Task | Bloqueio |
| --- | --- | --- |
| 1.1 | Selecionar 4 a 6 casos brasileiros, cobrindo ao menos 3 tipos de manipulação | grupo |
| 1.2 | Criar o template da ficha de caso conforme `pesquisa-investigativa` | implementação |
| 1.3 | Preparar o board com os cinco quadros: Problema, Público, Específicas, Solução, Sucesso | grupo |

> **Nota.** A seleção de casos da 1.1 agora tem material que não existia em
> setembro: 20 casos reais já curados em `prototipo/rag/consultas_afericao.json`,
> fora do recorte covid e com o documento de checagem conhecido para cada um.
> Serve de ponto de partida, não de substituto — a forense exige caso analisado
> por pessoa.

### Bloco 2 — Investigação forense (4)

| # | Task | Bloqueio |
| --- | --- | --- |
| 2.1 | Distribuir os casos, um por pessoa no mínimo | grupo |
| 2.2 | Analisar cada caso com leitura lateral, **registrando o tempo gasto** | grupo |
| 2.3 | Preencher uma ficha por caso, com fontes rastreáveis | grupo |
| 2.4 | Consolidar os tempos medidos como evidência para o quadro Problema | grupo |

O tempo medido da 2.2 não é burocracia: é a evidência que sustenta o quadro
Problema, e sem ele o argumento do projeto vira opinião.

### Bloco 3 — Sessão de brainstorming, ~90 min (3)

| # | Task | Bloqueio |
| --- | --- | --- |
| 3.1 | Rodar Problema, Público e Sucesso em modo privado antes de abrir a discussão | grupo |
| 3.2 | Preencher o quadro Solução **apenas como hipóteses**, sem decidir | grupo |
| 3.3 | Plotar guiding questions na matriz impacto × incerteza | grupo |

### Bloco 4 — Matriz de confiança (4)

| # | Task | Bloqueio |
| --- | --- | --- |
| 4.1 | Card sorting dos sinais que cada integrante usa na prática | grupo |
| 4.2 | Consolidar em dimensões, cada uma com sinal observável, papel da IA e limite | grupo |
| 4.3 | Escrever a rubrica de três níveis por dimensão | implementação |
| 4.4 | Testar a matriz contra os casos da forense e remover o que não discrimina | grupo |

> **Atalho disponível.** A rubrica de seis critérios adaptada do FakeHealth já
> existe, com três níveis cada, em
> `datasets/derivados/rubrica_criterios_ptbr.json`. Ela **não é** a matriz de
> confiança — é o instrumento de qualidade de cobertura —, mas o formato de
> rubrica está resolvido e a 4.3 pode reusá-lo.

### Bloco 6 — Exploração de datasets (3)

| # | Task | Situação |
| --- | --- | --- |
| 6.1 | Verificar disponibilidade e licença de cada dataset candidato, com link conferido | **aparentemente satisfeita** |
| 6.2 | Classificar cada dataset por função: raciocínio, comparação fonte-manchete, banco de estímulos | **aparentemente satisfeita** |
| 6.3 | Registrar caveats por dataset, incluindo descartados com motivo | **aparentemente satisfeita** |

As três parecem cumpridas pelo trabalho de 19/09: `datasets/FONTES.md` traz
licença conferida na fonte primária de cada base, a estrutura de diretórios
(`01_nucleo_metodologico`, `02_comparacao_exagero`, `03_banco_estimulos`,
`04_acervo_circulacao`) é a classificação por função, e os caveats estão em
`datasets/README.md` e em
[Tratamento dos datasets](investigate/tratamento-datasets.md).

**Não foram marcadas de propósito.** O trabalho foi feito sob outros changes, e
marcar task de um change a partir de entrega de outro é o tipo de atalho que a
metodologia existe para impedir. Cabe ao grupo conferir e marcar — ou registrar
o que ainda falta.

### Bloco 7 — Fechamento (4)

| # | Task | Bloqueio |
| --- | --- | --- |
| 7.1 | Consolidar o portfólio de pesquisa (fichas + método + datasets) | depende dos blocos 1 a 4 |
| 7.2 | Consolidar a matriz de confiança versão 1 | depende do bloco 4 |
| 7.3 | `openspec validate add-engage-desinformacao-saude --strict` | **já passa limpo** |
| 7.4 | Abrir `add-instrumento-avaliacao-ptbr` para a fase Investigate | decisão de grupo |

> **A 7.4 é uma lacuna de estrutura.** O change `add-instrumento-avaliacao-ptbr`
> **nunca foi aberto**, e a fase Investigate está encerrando sem ele. Ou ele é
> aberto agora, ou o grupo registra por escrito que a capability
> `avaliacao-instrumento` de `mvp-copiloto-verificacao` o absorveu.

---

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

## Duas lacunas de estrutura

1. **`add-instrumento-avaliacao-ptbr` nunca foi aberto** (task 7.4 do Engage).
   Abrir ou registrar a absorção por `avaliacao-instrumento`.
2. **Não existe change de Showcase.** Abrir antes da semana 6.
