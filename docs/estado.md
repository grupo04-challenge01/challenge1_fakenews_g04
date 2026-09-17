# Estado do projeto

Atualizado em **10/09/2026**.

## Os três changes

| Change | Fase | Planejamento | Tasks |
| --- | --- | --- | --- |
| `add-engage-desinformacao-saude` | Engage | completo | 4 de 25 |
| `add-tratamento-datasets-ptbr` | Investigate | completo | 0 de 33 |
| `mvp-copiloto-verificacao` | Act | completo | 0 de 31 |

Todos passam `openspec validate --strict`.

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
| `frescor-corpus` | cobertura declarada e resposta para pauta fora dela |
| `adaptacao-criterios-en` | travessia dos instrumentos em inglês |

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

## Pendências conhecidas

### Lacuna de escopo

**"Identificar vieses" não tem cobertura.** É uma das três competências nomeadas
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
| Limiar de `evidência insuficiente` | `mvp-copiloto-verificacao` | calibragem |
| Qual conjunto de critérios do FakeHealth | `add-tratamento-datasets-ptbr` | `matriz-confianca` |
| Origem dos itens verdadeiros | `add-tratamento-datasets-ptbr` | teste com usuário |
| Sub-recorte dentro de saúde | `openspec/project.md` | curadoria dos casos |

## Próximo trabalho na fila

1. Forense de casos e matriz de confiança — resto do Engage.
2. Registro de licença e caveat por dataset (tasks 6.1 a 6.3 do Engage).
3. Decisão sobre "identificar vieses".
4. Tratamento dos datasets, que destrava o MVP.
