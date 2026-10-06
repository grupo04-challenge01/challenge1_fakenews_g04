# Design — Resposta quando não há evidência recuperada

## Decisão 1: saída A, forma própria — 19/09/2026

A `proposal.md` deixou duas saídas. Adotada a **A**, forma própria para o caso
sem evidência, com a B registrada como descartada.

O argumento que decidiu não é de elegância de spec. É que os dois casos fazem
perguntas diferentes ao leitor:

| Caso | A pergunta do bloco 3 | O que o leitor faz com a resposta |
| --- | --- | --- |
| há evidência | por que **aquela mensagem** engana | aprende a reconhecer o sinal |
| não há evidência | o que **você** pode conferir | sai daqui com um próximo passo |

A saída B mantinha o rótulo da primeira pergunta sobre o conteúdo da segunda. O
bloco 3 ficaria com o título "por que engana" e o corpo vazio — que é
exatamente a degeneração que a sonda T1 produziu em 18/09, com o modelo
repetindo "evidência insuficiente" dentro do bloco.

A B também não tinha onde pôr o ponteiro da lacuna de acervo. Os quatro blocos
originais não têm lugar para "a Lupa checou isso em 03/2025, aqui está", e essa
informação é o produto inteiro naquele caso.

## Decisão 2: o ponteiro fica na camada visível

`resposta-formativa` manda fonte, trecho e detalhe metodológico para a camada de
detalhe, acessível por ação explícita. O ponteiro da lacuna de acervo é
exceção declarada.

Motivo: nos outros casos o usuário recebe uma resposta e a fonte serve para
conferir. Aqui ele **não** recebe resposta — o ponteiro é a resposta. Mandá-lo
para a segunda camada devolve à pessoa exatamente o problema com que ela chegou,
com um clique a mais.

O custo é orçamento de palavras: `acessibilidade-leitura` fixa 120 palavras na
camada visível, e agora o ponteiro compete por elas. Por isso o requirement
manda reduzir os blocos 2 e 3 antes de tocar no 4.

## Decisão 3: três respostas, não duas

A medição de 19/09 mostrou que `oropouche` e `semaglutida` têm zero ocorrência
**no acervo e no índice** da Fact Check Tools API. Isso obriga um terceiro
estado, que nenhuma das duas saídas previa:

| Estado | Condição | Bloco 4 |
| --- | --- | --- |
| `evidência insuficiente` | pauta dentro da janela, nada recuperado | o que conferir |
| lacuna de acervo **com** ponteiro | pauta fora da janela, índice devolve checagem | agência, data, veredito da agência, link |
| lacuna de acervo **sem** ponteiro | pauta fora da janela, índice também vazio | declara que não há checagem localizada em português |

O terceiro é o mais delicado: é onde é mais tentador dizer "não existe checagem
sobre isso", que é afirmação sobre o mundo que o sistema não pode fazer. O
requirement veda isso em texto expresso.

## Decisão 4: sonda dos três estados — 28/09/2026

Tasks 3.1 e 3.2. Arranjo em `prototipo/sonda_sem_evidencia.py`, resultado por
tentativa em `prototipo/relatorio_sonda_sem_evidencia.json`. Formato da sonda de
18/09: Gemma 4 12B QAT, `think: false`, temperatura 0,2, três tentativas por
estado. O estado da recuperação é injetado à mão, porque o roteamento por janela
do acervo ainda não está ligado ao gerador. Um prompt só, com as duas formas; a
forma é escolhida pelo estado que chega na mensagem, como manda o risco 1.

| Sonda | Estado | Passou |
| --- | --- | --- |
| E1 | `evidência insuficiente` — chá de goiabeira cura dengue | 3/3 |
| E2 | lacuna com ponteiro — vacina da dengue "transgênica", Aos Fatos 02/02/2024 | 0/3 |
| E3 | lacuna sem ponteiro — oropouche, zero no acervo e no índice | 0/3 |
| T1 | reprise literal da T1 de 18/09, mesma mensagem e mesmo trecho | 0/3 |

**O defeito que abriu o change não se repete.** Nas 12 respostas, o bloco 3
trouxe um passo que a pessoa pode dar sozinha. Nenhuma repetiu "evidência
insuficiente" dentro do bloco, e nenhuma nomeou técnica do catálogo. Na T1, que
em 18/09 degenerou, as três tentativas ficaram na forma sem evidência, com os
quatro blocos em ordem. A task 3.2 está confirmada.

**As falhas de E2, E3 e T1 têm uma causa só.** Nas 9 respostas de lacuna de
acervo, o bloco 1 abre com "lacuna de acervo" mas omite a data de corte, que o
requirement "Lacuna de acervo distinguida na resposta" exige. O prompt pede a
data em texto expresso, e o modelo a ignora 9 vezes em 9. Não é variação de
amostra; é instrução que não pega. A data de corte é metadado do acervo, não
conteúdo gerado. Recomendação para a task 3.2 de `mvp-copiloto-verificacao`: o
sistema compõe a frase de corte do bloco 1 por modelo fixo, sem depender do
gerador. É a mesma lição da fronteira clínica na decisão 10 de
`add-selecao-modelos-arquitetura-rag`: o que a spec exige literalmente não deve
depender de o prompt pegar.

Falha isolada: uma frase acima de 25 palavras em E2.

**Orçamento de palavras, medido.** As respostas tiveram de 65 a 85 palavras,
todas abaixo do teto de 120. O ponteiro do bloco 4 custou 11 palavras. A forma
sem ponteiro fecha o bloco 4 em 6. Sobram ao menos 35 palavras de folga, o que
responde à segunda questão em aberto abaixo e alimenta a task 2.1.

**Correção de método, registrada.** A primeira avaliação reprovou T1 e E2
também por "afirmação paramétrica". Era falso positivo: o regex pegava o bloco
1 repetindo a alegação procurada ("foi procurado se a vacina Qdenga causa a
própria dengue"). O check passou a olhar só os blocos 2 e 3, e as respostas
gravadas foram reavaliadas sem nova chamada ao modelo (`--reavaliar`). Antes de
confiar nos checks, testei-os contra uma resposta sintética correta, que passa,
e contra a resposta degenerada de 18/09, que reprova em 10 checks.

**Nota de ambiente.** Nesta máquina, com RTX 2060 de 6 GB, o `llama-server` do
Ollama 0.34.4 cai ao iniciar CUDA (`shared object initialization failed`). A
sonda rodou só em CPU (`--cpu`, `num_gpu: 0`), com 58 a 157 s por resposta,
contra 17 s em 18/09. Isso muda a latência, não a resposta esperada.

## Decisão 5: conciliação arquitetural das tasks 2.2 e 2.3 — 01/10/2026

Tasks 2.2 e 2.3. R2 Wingrid.

**Task 2.2 — Ancoragem e guarda paramétrica contra `recuperacao-evidencia`:**
1. Conferido contra os dados da sonda de 28/09 (`prototipo/relatorio_sonda_sem_evidencia.json`): o check de guarda paramétrica passou nas 12 respostas reais produzidas pelo modelo (`gemma4:12b-it-qat`). Os blocos 2 e 3 não fazem afirmação factual ou médica sobre o tema a partir do conhecimento do modelo.
2. Resolução da questão aberta de E2: sob lacuna de acervo com ponteiro, o bloco 2 atém-se estritamente à limitação do acervo interno consultado (explicando que a ausência no acervo não equivale a desmentido), enquanto qualquer veredito externo e sustentação factual ficam exclusivamente circunscritos e atribuídos ao ponteiro oficial do bloco 4 (agência, data, veredito da agência e link). O bloco 2 não emite juízo sobre a veracidade da alegação.
3. O bloco 3 oferece passos práticos de verificação que a pessoa pode fazer por conta própria, sem induzir julgamento fático sem trecho ancorado.

**Task 2.3 — Fronteira clínica contra `fronteira-orientacao-saude`:**
1. A recusa de conduta clínica e o encaminhamento de urgência médica (SAMU 192 / UBS) são aplicados por guardrails na entrada da requisição (pré-RAG). Se o usuário pedir prescrição, alteração de medicação ou relatar emergência, a requisição é interceptada imediatamente com resposta padrão acolhedora do SUS, sem passar pelo pipeline de verificação.
2. A forma sem evidência só é acionada para alegações informativas em que não houve recuperação. O bloco 3 veda prescrição alternativa e limita-se a canais oficiais de informação pública (como portais do Ministério da Saúde e Anvisa) ou recomendação de procurar profissionais habilitados, cumprindo integralmente o requirement "Veredito sem prescrição alternativa".

## Decisão 6: o terceiro estado já é o segundo caso de teste da 8.2 — 01/10/2026

Task 2.4. R4 Samara.

A task pedia levar o terceiro estado da decisão 3 — pauta ausente do acervo
**e** do índice — à task 8.2 de `add-ampliacao-corpus-ptbr`, que prevê três
casos de teste de lacuna. A conferência mostra que ele já está lá. A 8.2 foi
fechada em 20/09 com os três casos em
`datasets/derivados/declaracao_cobertura_quatro_niveis.json`
(`tres_respostas_de_lacuna`), e o segundo deles é este estado, com `oropouche`
como exemplo medido. Nada precisa ser acrescentado àquele change.

**Correspondência entre os dois changes.**

| Estado (decisão 3 deste change) | Situação de `frescor-corpus` (`add-ampliacao-corpus-ptbr`) | Caso de teste da 8.2 |
| --- | --- | --- |
| `evidência insuficiente` | nenhuma: a pauta está dentro da janela, não é lacuna | — |
| lacuna de acervo **com** ponteiro | 1. checagem localizada | `pauta_com_checagem_so_no_indice` — `qdenga` |
| lacuna de acervo **sem** ponteiro (o terceiro estado) | 2. sem correspondência no acervo consultado | `pauta_sem_correspondencia_em_nenhum_nivel` — `oropouche` |
| lacuna de acervo **sem** ponteiro, com a data de corte do índice | 3. fora da janela declarada | `pauta_posterior_as_duas_datas_de_corte` |

O terceiro estado deste change cobre duas situações de `frescor-corpus`: a pauta
que o índice não tem, e a pauta posterior à data de corte do índice. Nas duas,
o bloco 4 fica sem ponteiro. O que as separa é a data de corte que a resposta
nomeia, e isso já está no cenário «Alegação sem correspondência em nenhum
nível» daquela spec.

**As duas specs dizem a mesma coisa sobre o terceiro estado.** O cenário «Pauta
ausente do acervo e do índice» de `resposta-formativa`, aqui, e o cenário
«Alegação sem correspondência em nenhum nível» de `frescor-corpus` exigem
juntos: lacuna de acervo, e não `evidência insuficiente`; declaração de que não
há checagem localizada em português; e a vedação de apresentar a ausência de
ponteiro como ausência de checagem no mundo. Nenhum dos dois contradiz o outro,
e o caso de teste da 8.2 registra a resposta com as mesmas três exigências.

**Remedição em 01/10/2026: o terceiro estado continua valendo.** Os dois exemplos
da decisão 3 foram contados de novo, por busca sem caixa no texto inteiro de
cada registro:

| Termo | FactCenter (4.063) | FACTCK.BR (1.313 linhas) | índice gravado (861, 20/09) | sondagem da API (19/09) |
| --- | --- | --- | --- | --- |
| `oropouche` | 0 | 0 | 0 | 0 |
| `semaglutida` | 0 | 0 | 0 | 0 |
| `qdenga` | 0 | 0 | **0** | 8 |

O FACTCK.BR entrou no índice de recuperação em 01/10 (task 1.2 de
`mvp-copiloto-verificacao`) e não muda o quadro: `oropouche` e `semaglutida`
seguem ausentes de todos os níveis, e a resposta certa para as duas continua
sendo lacuna de acervo sem ponteiro.

**Achado: o exemplo de lacuna com ponteiro não está no índice gravado.** O
segundo estado usa a Qdenga como exemplo, aqui (cenário «Pauta posterior ao
acervo com checagem localizada») e na 8.2. As 8 checagens vêm de
`datasets/derivados/sonda_factcheck_api.json`, a sondagem de 19/09. O índice
que o sistema consultaria, `datasets/derivados/indice_checagens_recentes.json`,
gerado em 20/09, registra `qdenga: 0` em `por_termo`, e a palavra não aparece em
nenhuma das 861 checagens. O índice tem checagens sobre a vacina da dengue (por
exemplo «A vacina da dengue é transgênica, altera o DNA e causa câncer», AFP
Checamos, 15/02/2024), mas nenhuma usa o nome comercial. Isso não muda a 2.4,
que trata do terceiro estado. Muda o caso de teste do segundo: contra o índice
gravado, uma alegação que diga «Qdenga» cairia em lacuna **sem** ponteiro.
Registrado em Questões em aberto.

## Riscos

| Risco | Efeito | Mitigação |
| --- | --- | --- |
| Duas formas viram duas implementações que divergem | a forma sem evidência envelhece e ninguém percebe | o gerador escolhe a forma pelo estado da recuperação, não por prompt separado; o teste cobre os três estados |
| O ponteiro estoura o teto de 120 palavras | a camada visível fica ilegível no caso que mais precisa de clareza | ordem de redução declarada no requirement: blocos 2 e 3 encolhem, o 4 não |
| Checagem do índice em português de Portugal atribuída como brasileira | erro de proveniência na cara do usuário | a origem do editor entra no ponteiro; ver decisão 11 de `add-ampliacao-corpus-ptbr` |

## Questões em aberto

- **Aberta em 01/10 (decisão 6):** o caso de teste da lacuna com ponteiro não se
  sustenta no índice gravado. A sondagem de 19/09 contou 8 checagens para
  `qdenga`; o índice de 20/09 tem 0. Falta decidir entre regerar o índice com o
  termo, trocar o exemplo por uma pauta que o índice tem (vacina da dengue,
  2024) ou fazer a busca do índice casar a alegação por assunto, e não só pelo
  nome. É de `indice-checagens-recentes`, de `add-ampliacao-corpus-ptbr`.
- Se a forma sem evidência deve nomear a técnica quando o usuário **pedir**
  explicitamente a análise da mensagem sem veredito. Hoje a spec veda nomear
  técnica sem evidência; o caso do pedido explícito não foi examinado.
- Quantas palavras sobram para os blocos 2 e 3 depois do ponteiro, o que só se
  sabe medindo respostas reais. **Medido em 28/09 (decisão 4):** de 65 a 85
  palavras no total, com o ponteiro custando 11. A task 2.1 confere o teto.
- **Aberta em 28/09 pela sonda E2 e resolvida em 01/10 (decisão 5, task 2.2):** o
  que o bloco 2 diz quando há ponteiro. O bloco 2 atém-se à ausência no acervo
  interno consultado; o veredito da checagem externa fica circunscrito ao ponteiro
  do bloco 4, sem conflito de premissas.

