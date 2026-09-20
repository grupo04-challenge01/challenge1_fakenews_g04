# Estado do projeto

Atualizado em **19/09/2026**.

## Os cinco changes

| Change | Fase | Planejamento | Tasks |
| --- | --- | --- | --- |
| `add-engage-desinformacao-saude` | Engage | completo | 4 de 25 |
| `add-tratamento-datasets-ptbr` | Investigate | completo | **31 de 33** |
| `add-ampliacao-corpus-ptbr` | Investigate | completo | 0 de 55 |
| `add-selecao-modelos-arquitetura-rag` | Investigate | completo | **12 de 33** |
| `mvp-copiloto-verificacao` | Act | completo | 0 de 31 |

Todos passam `openspec validate --strict`.

## O que foi entregue em 19/09/2026

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
| Limiar de `evidência insuficiente` | `mvp-copiloto-verificacao` | calibragem — **medido em 18/09: não sai de similaridade bruta** |
| Estrutura de quatro blocos sob `evidência insuficiente` | `add-selecao-modelos-arquitetura-rag`, decisão 10 | task 3.2 do MVP; precisa de change de correção |
| Necessidade de reranker | `add-selecao-modelos-arquitetura-rag` | depende da aferição da task 3.1 |
| ~~Qual conjunto de critérios do FakeHealth~~ | **resolvido em 19/09/2026: HealthStory como base** | — |
| Destino de `enganoso` (218) e `impreciso` (64) no mapa de veredito | `tratamento/mapa_vereditos.json` | confirmação do grupo |
| Validação empírica da rubrica de seis critérios | `add-tratamento-datasets-ptbr`, task 5.4 | `avaliacao-instrumento` |
| Origem dos itens verdadeiros | `add-tratamento-datasets-ptbr` | teste com usuário |
| ~~Sub-recorte dentro de saúde~~ | **resolvido em 17/09/2026: vacinação** | — |
| ~~Local ou API para geração~~ | **resolvido em 17/09/2026: local, Gemma 4 12B QAT** | — |
| ~~Provisionamento do ambiente~~ | **resolvido em 18/09/2026: Python 3.14.6, torch com MPS** | — |

## Próximo trabalho na fila

1. **Conjunto de 20 consultas de aferição** com o documento correto conhecido
   (task 2.6). Sem ele, o índice funciona mas não está medido — a comparação de
   35% de sobreposição entre os braços é sanidade, não aferição.
2. **Medir recall das três configurações** — só léxica, só densa, híbrida — e
   registrar o resultado mesmo se ele contrariar a decisão de usar híbrido
   (tasks 3.1 e 3.2).
3. **Calibrar o limiar de `evidência insuficiente`** sobre o score fundido,
   incluindo o caso Qdenga, de pauta ausente do corpus (task 3.5).
4. **Change de correção** para a estrutura de quatro blocos sob `evidência
   insuficiente`, defeito de spec exposto pela sonda (task 2.1b).
5. ~~Tratamento dos datasets~~ — **feito em 19/09/2026.** O mapa de vocabulário
   que o índice esperava existe, versionado, e o índice pode recebê-lo sem
   reindexar.
6. Forense de casos e matriz de confiança — resto do Engage.
7. Decisão sobre "identificar vieses".
