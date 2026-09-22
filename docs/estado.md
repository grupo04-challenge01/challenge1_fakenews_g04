# Estado do projeto

Atualizado em **22/09/2026**.

## Os seis changes

| Change | Fase | Planejamento | Tasks |
| --- | --- | --- | --- |
| `add-engage-desinformacao-saude` | Engage | completo | **12 de 25** |
| `add-tratamento-datasets-ptbr` | Investigate | completo | **31 de 33** |
| `add-ampliacao-corpus-ptbr` | Investigate | completo | **55 de 55** ✅ |
| `add-selecao-modelos-arquitetura-rag` | Investigate | completo | **33 de 33** ✅ |
| `fix-resposta-sem-evidencia` | Investigate → Act | completo | **6 de 13** |
| `mvp-copiloto-verificacao` | Act | completo | 0 de 31 |

Todos passam `openspec validate --strict`.

## O que foi entregue em 20/09/2026

### Calendário derivado, e o Investigate com cinco dias

A proposta do challenge confirmou o cronograma. As datas derivadas mostram que
o **Investigate encerra em 25/09** e o **Act começa em 28/09** — ver
[Tasks pendentes](pendencias.md).

### Engage: de 4 para 12 de 25

Fecharam as oito tasks que não exigiam o grupo presente. As 13 restantes
exigem, sem exceção.

| Entregue | Serve a |
| --- | --- |
| [Casos da forense](engage/casos-forense.md) — seis casos, quatro tipos | bloco 2 |
| [Ficha de caso](engage/ficha-de-caso.md) — oito campos e checklist | bloco 2 |
| [Board do brainstorming](engage/board-brainstorming.md) — cinco quadros | bloco 3 |
| [Kit do workshop](engage/kit-matriz-confianca.md) — protocolo e cartões-semente | bloco 4 |

Dois achados na conferência de datasets, que estava dada como pronta:

1. **FakeHealth não tinha licença registrada.** Conferida: CC BY 4.0, no
   registro do Zenodo (`10.5281/zenodo.3606757`), não no GitHub, que não declara.
2. **O InSciOut não declara licença** no repositório dos autores. Entrou nas
   pendências junto do PUBHEALTH — são duas agora, não uma.

E um achado de taxonomia: as três funções de dataset nomeadas na task 6.2
(raciocínio, comparação fonte-manchete, banco de estímulos) **não bastam**. O
acervo de circulação não cabe em nenhuma, e virou a quarta.

## O que foi entregue em 19/09/2026

### Seleção de modelos e arquitetura RAG — de 12 para 27 tasks

| Entregue | Onde |
| --- | --- |
| Fronteira treino/recuperação operacional, com auditoria em cinco passos | decisão 12 do `design.md` |
| Rótulos de emoção propostos, ferramentas PT-BR com licença, teste cruzado | decisão 13 |
| Candidatos por papel com tamanho e licença; PUP da Gemma conferida | decisão 14 |
| Conjunto de aferição: 20 consultas reais, duas famílias, fora do covid | `prototipo/rag/consultas_afericao.json` |
| Aferidor de recall e calibração de limiar | `prototipo/rag/afericao.py` |
| Primeira aferição medida (braço léxico) e calibração do limiar | [Aferição da recuperação](investigate/afericao-recuperacao.md) |

Dois achados da aferição, ambos contra suposição do projeto:

1. **O limiar de `evidência insuficiente` não sai do score fundido**, e o motivo
   é estrutural, não de calibragem: o realce é relativo à própria consulta, e
   `como declarar imposto de renda atrasado` pontua 0,853, acima de 11 dos 20
   alvos reais. Sobre o BM25 bruto existe curva — 27,2 rejeita 100% do ruído e
   custa 40% dos positivos.
2. **Os oito positivos perdidos por esse limiar são todos `reformulada`.**
   Nenhum `verbatim` cai. O braço léxico só tem confiança calibrável quando o
   usuário cola a mensagem; quando ele reformula, o BM25 não distingue a própria
   ignorância de um acerto fraco. É a formulação precisa do que o híbrido tem de
   resolver, e vira previsão testável para a medição do braço denso.

Achado da decisão 13: a única ferramenta de emoção em PT-BR madura e de licença
limpa (LeIA, MIT) faz **só polaridade** — exatamente o uso que a decisão 7
proibiu. A via de emoção nomeada é prompt sobre o gerador local, não biblioteca.

### Ampliação do corpus — change fechado, 55 de 55

Três bases novas baixadas, conferidas e integradas, e o acervo passou a ter
quatro níveis. Registro completo em
[Ampliação do corpus](investigate/ampliacao-corpus.md).

| Base | Licença | Escala medida | Nível |
| --- | --- | --- | --- |
| FakeRecogna 2.0 extrativa | MIT | 52.800 itens, 26.436 no recorte de saúde | texto transformado |
| WhaVax | CC BY 4.0 | 950 mensagens, 4 médicos, 84 empates isolados | anexo clínico |
| Telegram antivacina | CC BY-NC 4.0 | 3.998.633 posts, 119 canais | circulação |
| Fact Check Tools API | metadado ClaimReview | 861 checagens, 12 editores | índice de localização |

**A tabela que fecha a cobertura:** `oropouche` (122 posts) e `semaglutida` (56)
circularam e **não têm checagem publicada em português** — zero no acervo e zero
no índice. É o caso que prova que o terceiro estado de resposta precisa existir.

Três premissas do próprio change caíram na medição: a 2.0 não tem vocabulário de
veredito (rótulo binário); `Categoria` não é vocabulário compartilhado entre as
classes (5 na real, 69 na falsa); e a transformação de texto vaza a classe — **um
classificador que só conta caracteres acerta 80,5%**.

E três conferências bateram exatamente: 3.998.633 posts, 119 canais e 84
empates, todos idênticos ao declarado pelas fontes.

### Portão do índice de checagens recentes — bloco 1 fechado

A Fact Check Tools API foi sondada com chave própria e o resultado está
versionado em `datasets/derivados/sonda_factcheck_api.json`: **928 checagens em
`pt`, 525 posteriores a 2021, 11 editores** contra as seis agências do corpus.

A decisão é **manter** `indice-checagens-recentes`, e o que decidiu foi o caso
de borda: a **Qdenga tem 8 checagens no índice contra zero no corpus**, e mpox
tem 39. O índice começa onde o acervo termina.

Achado que delimita a promessa: `oropouche` e `semaglutida` continuam em zero
**no índice também**. Isso obriga um terceiro caso de teste de lacuna — pauta
ausente dos dois níveis — que a task 8.2 ainda não previa.

### Change de correção aberto — `fix-resposta-sem-evidencia`

O defeito de spec que a sonda T1 expôs em 18/09 virou change próprio.
`resposta-formativa` exigia nomear técnica do catálogo mesmo sob `evidência
insuficiente`, onde não há mensagem comprovadamente enganosa cuja técnica
nomear. Adotada a **forma própria** para o caso sem evidência, com três estados
distintos: evidência insuficiente, lacuna de acervo com ponteiro, e lacuna sem
ponteiro.


Tratamento dos datasets — o change que bloqueava as tasks 1.1 a 1.6 do MVP.
Pacote `tratamento/`, 53 testes, cinco artefatos reexecutáveis por
`python -m tratamento tudo`.

| Entregue | Onde |
| --- | --- |
| Contrato de leitura dos nove derivados, com formato medido | `tratamento/leitura.py` |
| Mapa de veredito versionado 1.0.0, 19 chaves canônicas | `tratamento/mapa_vereditos.json` |
| Verificador de integridade textual definitivo, por arquivo | `tratamento/integridade.py` |
| Declaração de cobertura e resposta de lacuna de acervo | `tratamento/frescor.py` |
| Rubrica PT-BR de seis critérios e pool de few-shot | `tratamento/criterios.py` |
| Reparo do `update_factckbr.py` (três defeitos) | `datasets/01_nucleo_metodologico/factckbr/` |
| Registro completo | [Tratamento dos datasets](investigate/tratamento-datasets.md) |

Quatro números do portfólio foram desmentidos pela medição e corrigidos nas
specs: 42.197 linhas físicas (são 48.392), 285 valores de veredito (são 285
strings, 26 grafias, 19 chaves), 250 registros mistos (são 245) e nove letras
perdidas no FACTCK.BR (são onze ausentes, sete com evidência de corrupção).

Três achados novos, nenhum previsto no change:

1. **A perda de caractere do FACTCK.BR é irreversível.** Está na fonte
   distribuída, não no nosso derivado. A task 3.5 pedia o impossível e foi
   reescrita como recoleta.
2. **Os derivados da FakeRecogna reprovam no mesmo portão, pela razão oposta** —
   texto lematizado na origem, não perda de caractere. O laudo passou a nomear
   a causa, para não acusar a base errada no portfólio.
3. **O proxy de validação da rubrica foi medido e reprovado.** Sob qualquer piso
   único ele removeria `alarme` e `linguagem`, os dois critérios mais relevantes
   para desinformação. As remoções se sustentam no argumento de unidade de
   análise; a validação empírica segue pendente de anotação humana.

## O que foi entregue em 18/09/2026

Primeiro código executável do projeto, em `prototipo/` — prova de conceito, não
componente do MVP.

| Entregue | Onde |
| --- | --- |
| Sonda do gerador local (Gemma 4 12B QAT), 1 de 3 aprovações | [Sonda do gerador](investigate/sonda-gerador.md) |
| Índice de recuperação: 5.090 unidades, 22.464 fragmentos | [Índice híbrido](investigate/indice-hibrido.md) |
| Busca léxica (BM25), densa exata e fusão das duas | `prototipo/rag/` |

Dois defeitos encontrados por medição, ambos invisíveis sem ela: o gerador não
sustenta a fronteira clínica por prompt, e a primeira versão da fusão estava
**anulando o braço denso** — somava um cosseno que varia 0,06 a um BM25 que
varia 0 a 35, e a ordem final saía inteira do léxico.

## Capabilities

### Engage

| Capability | Entrega |
| --- | --- |
| `pesquisa-investigativa` | protocolo da forense de casos, com ficha e medição de esforço |
| `matriz-confianca` | dimensões, sinais, limites e rubrica de três níveis |
| `guiding-questions` | backlog priorizado — **pronto** |

### Investigate

| Capability | Entrega |
| --- | --- |
| `normalizacao-rotulos` | contrato de leitura, parser de veredito, mapa por agência |
| `integridade-textual` | fidelidade do trecho citado e reparo de acentuação |
| `frescor-corpus` | cobertura declarada em quatro níveis e resposta para pauta fora dela |
| `adaptacao-criterios-en` | travessia dos instrumentos em inglês |
| `anotacao-especialista-ptbr` | o que se afirma a partir de rótulo clínico, e a faixa de empate |
| `procedencia-substituicao` | condições para trocar uma base sem quebrar a auditoria |
| `indice-checagens-recentes` | localizar checagem fora da janela, sem citar texto de terceiro |
| `acervo-circulacao` | o que se afirma a partir de conteúdo de usuário sem rótulo de veracidade |
| `selecao-modelo` | três papéis de modelo, critério por papel, descarte do MedGemma com motivo |
| `arquitetura-recuperacao` | híbrido como linha de base, índice à escala real, unidade com proveniência |
| `fronteira-treino-recuperacao` | o que mora em peso e o que MUST vir de trecho recuperado |
| `uso-analise-sentimento` | emoção é explicativa e descritiva, nunca evidenciária |

### Act

| Capability | Entrega |
| --- | --- |
| `verificacao-alegacao` | extração da alegação, quatro rótulos, decomposição fato/evidência/opinião |
| `recuperacao-evidencia` | RAG PT-BR antes de EN, tudo ancorado em trecho |
| `resposta-formativa` | quatro blocos, catálogo fechado de técnicas, revelação progressiva |
| `fronteira-orientacao-saude` | recusa de conduta clínica individual |
| `acessibilidade-leitura` | 120 palavras na camada visível, contraste, fonte, sem cadastro |
| `avaliacao-instrumento` | 20–30 casos, armadilhas, métricas de guarda, TCLE e CEP |

## Ordem de dependência

```text
Engage                Investigate                    Act
------                -----------                    ---
forense       -->     normalizacao-rotulos    -->    corpus e recuperacao
matriz        -->     adaptacao-criterios-en  -->    resposta-formativa
guiding q.    -->     frescor-corpus          -->    verificacao-alegacao
                      integridade-textual
```

O tratamento dos datasets **bloqueia** as tasks 1.1 a 1.6 do MVP. Indexar antes
de normalizar propaga o problema de rótulo para dentro do índice, onde ele fica
caro de tirar.

O índice de 18/09/2026 não viola isso, e a forma como não viola importa: ele
guarda o veredito **com a grafia original da agência** e uma chave normalizada
só por caixa e acento. Nenhum rótulo foi mapeado para os quatro de
`verificacao-alegacao` — esse mapa é a task 2.3 do tratamento de datasets, e
atribuí-lo por semelhança de string é vedado em texto expresso. O índice está
pronto para receber o mapa quando ele existir, sem reindexar.

## Pendências conhecidas

A lista completa de tasks pendentes, separada por fase do CBL, está em
[Tasks pendentes](pendencias.md).

### Lacuna de escopo

**"Identificar vieses" tem cobertura parcial desde 17/09/2026.** A capability
`acervo-circulacao` endereça procedência e alcance com dado medido, que é uma
face do problema. As outras duas seguem descobertas — conflito de interesse da
fonte e viés de confirmação de quem lê. O texto abaixo permanece como registro
do diagnóstico original.

**"Identificar vieses" não tinha cobertura.** É uma das três competências nomeadas
na Essential Question, e nenhuma das quatorze capabilities a endereça. O
catálogo de técnicas trata de técnica retórica do texto (`cura milagrosa`,
`manchete exagerada`), o que é diferente de viés: quem publicou e o que ganha
com isso, conflito de interesse da fonte, e o viés de confirmação de quem lê.

Decisão pendente do grupo: virar requisito, ou sair como *Out of Scope* com
justificativa escrita.

### Questões em aberto registradas

| Questão | Onde está registrada | Bloqueia |
| --- | --- | --- |
| Canal de entrega (WhatsApp vs. web) | `mvp-copiloto-verificacao` | arquitetura, e a GQ sobre momento da jornada |
| Composição do catálogo de técnicas | `mvp-copiloto-verificacao` | `resposta-formativa` |
| Limiar de `evidência insuficiente` | `mvp-copiloto-verificacao` | **medido em 19/09: não sai do score fundido, por motivo estrutural; sobre BM25 bruto, 27,2 rejeita todo o ruído e custa 40% dos positivos** |
| Estrutura de quatro blocos sob `evidência insuficiente` | `add-selecao-modelos-arquitetura-rag`, decisão 10 | task 3.2 do MVP; precisa de change de correção |
| ~~Necessidade de reranker~~ | **resolvido em 22/09/2026: não compensa.** Só 2 das 20 consultas caem fora do top-3 (posições 4 e 5); as outras 18 estão no top-2 | — |
| ~~Qual conjunto de critérios do FakeHealth~~ | **resolvido em 19/09/2026: HealthStory como base** | — |
| Destino de `enganoso` (218) e `impreciso` (64) no mapa de veredito | `tratamento/mapa_vereditos.json` | confirmação do grupo |
| Validação empírica da rubrica de seis critérios | `add-tratamento-datasets-ptbr`, task 5.4 | `avaliacao-instrumento` |
| Origem dos itens verdadeiros | `add-tratamento-datasets-ptbr` | teste com usuário |
| ~~Sub-recorte dentro de saúde~~ | **resolvido em 17/09/2026: vacinação** | — |
| ~~Local ou API para geração~~ | **resolvido em 17/09/2026: local, Gemma 4 12B QAT** | — |
| ~~Provisionamento do ambiente~~ | **resolvido em 18/09/2026: Python 3.14.6, torch com MPS** | — |

## Próximo trabalho na fila

1. ~~Aferição do braço denso e do híbrido~~ (tasks 3.1 a 3.4) — **feita em
   22/09/2026**, e ela fechou o change em 33 de 33. A híbrida em α=0,9 dá
   recall@5 de 1,00 e MRR de 0,897. O defeito não era a arquitetura: era o
   `ALFA_PADRAO` de 0,5, fixado sem medição. Ver decisão 15 do `design.md`.
2. **Decidir o destino de `enganoso` e `impreciso`** no mapa de veredito — 218 e
   64 ocorrências, marcadas como «a confirmar pelo grupo».
5. ~~Tratamento dos datasets~~ — **feito em 19/09/2026.** O mapa de vocabulário
   que o índice esperava existe, versionado, e o índice pode recebê-lo sem
   reindexar.
6. Forense de casos e matriz de confiança — resto do Engage.
7. Decisão sobre "identificar vieses".
