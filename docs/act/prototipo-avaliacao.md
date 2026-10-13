# Protótipo e avaliação

Como a Dona Checa funciona hoje e o que foi medido. Retrato de 13/10/2026,
`origin/main`. Para subir o chat, ver [Chat web](../interface/chat-web.md).

## O que ela faz

A pessoa cola a mensagem que recebeu, ou o link da notícia. A Dona Checa
responde com um veredito em um de quatro rótulos, sempre acompanhado do
critério e do trecho da checagem que o sustenta. Quando o acervo não cobre a
alegação, ela diz isso em vez de chutar.

Os quatro rótulos são `falso`, `verdadeiro`, `verdadeiro fora de contexto ou
exagerado` e `evidência insuficiente`. A guarda de `prototipo/verificacao/guarda.py` impede veredito
tirado só do conhecimento do modelo: sem trecho recuperado que cubra a
alegação, o rótulo é `evidência insuficiente`.

## O fluxo

O chat e a bancada rodam o mesmo fluxo (`bancada/pipeline.py`), em sete
etapas:

```text
fronteira -> leitura -> extracao -> decomposicao -> recuperacao -> guarda -> resposta
```

| Etapa | O que faz | Onde |
| --- | --- | --- |
| fronteira | separa pedido de conduta clínica e urgência; responde com redirecionamento | `prototipo/verificacao/fronteira.py` |
| leitura | abre o link, com bloqueio de rede interna; lê a página se o texto tem menos de 30 palavras | `prototipo/entrada/` |
| extracao | acha a alegação de saúde, e escolhe quando há várias | `prototipo/verificacao/extracao.py` |
| decomposicao | separa fato, evidência e opinião | `prototipo/verificacao/decomposicao.py` |
| recuperacao | busca híbrida no acervo, PT-BR antes de EN | `prototipo/rag/hibrida.py` |
| guarda | decide o rótulo e bloqueia veredito sem evidência | `prototipo/verificacao/guarda.py` |
| resposta | quatro blocos, até 120 palavras na camada visível, frase ancorada em trecho | `prototipo/resposta/` |

A resposta passa por quatro conferências em código antes de sair:

- a técnica nomeada pertence ao catálogo de sete rótulos (`catalogo.py`);
- a alegação falsa nunca abre a resposta sem marcação (`mito.py`);
- frase sem base no trecho recuperado sai (`conferencia.py` e `ancoragem.py`);
- acima de 120 palavras, frases do fim dos blocos são cortadas (`estrutura.py`).

## Modelos e acervo

| Papel | Escolha | Por quê |
| --- | --- | --- |
| Gerador, modo `uso` | `deepseek-v4-pro` via API | mediana de ~10 s contra ~102 s do local |
| Gerador, modo `piloto` e alternativa | Gemma 4 12B QAT local, via Ollama | nada sai da máquina |
| Embedding | `intfloat/multilingual-e5-base` | `e5-small` perde nas consultas reformuladas |
| Recuperação | BM25 + densa, fusão com α = 0,9 | melhor MRR em 20 consultas reais |

O índice tem **6.279 unidades e 23.655 fragmentos**: 5.089 unidades do
FactCenter (saúde) e 1.190 do FACTCK.BR. O FACTCK.BR entra só como fonte
auxiliar, não citável. A busca é exata, sem banco vetorial: na escala do
corpus, não compensa.

O acervo de checagens com texto integral vai de julho de 2013 a maio de 2021.
O índice de checagens recentes (Fact Check Tools API) aponta checagens mais
novas, sem citar o texto delas.

## O que foi medido

### Recuperação

Notebook `exploracao/avaliacao_modelo.ipynb`, 20 consultas reais de duas
famílias (`verbatim` e `reformulada`):

| Modo | R@1 | R@5 | MRR | Latência mediana |
| --- | --- | --- | --- | --- |
| léxica (BM25) | 0,60 | 0,85 | 0,725 | 26 ms |
| densa | 0,80 | 1,00 | 0,877 | 17 ms |
| **híbrida, α = 0,9** | **0,85** | **1,00** | **0,897** | 40 ms |

Sob leave-one-out, a híbrida mantém a vantagem: MRR 0,8975 contra 0,8767 da
densa. A afirmação defensável é «α = 0,9 com `e5-base`»; trocar o embedding
obriga a refazer a varredura.

### Bancada ponta a ponta

`python -m bancada rodar` roda o fluxo inteiro em 30 casos e compara cada
etapa com o esperado. Os casos cobrem link (10), fichas da forense (6), resposta
em quatro blocos, com um verdadeiro contra-intuitivo (4), fronteira e urgência
(3), conduta e ferimento (2), alegação em forma de pergunta (1), pauta sem
checagem ou fora do acervo (2) e extração com várias alegações ou só opinião
(2).

Falha **eliminatória** (rótulo errado, fronteira errada, mito sem marcação,
veredito implícito, erro) reprova a rodada. Falha de forma é tolerada até 3.

| Rodada | Gerador | Resultado | Mediana |
| --- | --- | --- | --- |
| 08/10, linha de base | Gemma 4 local | 26 de 27 | 102,4 s |
| 08/10, primeira com API | `deepseek-v4-pro` | 23 de 27 | 11,1 s |
| 08/10, com as correções de qualidade | `deepseek-v4-pro` | 27 de 27 | 9,9 s |
| 09/10, com pergunta e conduta | `deepseek-v4-pro` | 29 de 30 | 10,7 s |
| 09/10, rodada final do MVP | `deepseek-v4-pro` | **28 de 30**, sem eliminatória | 11,1 s |
| 13/10, rodada da demo | `deepseek-v4-pro` | **29 de 30**, sem eliminatória | 10,9 s |

Cada rodada com a API custa de US$ 0,05 a 0,12, conforme o horário. Ponta a
ponta com o servidor real, na rodada final do MVP: 22 de 22 no modo `uso` e
9 de 9 no modo `piloto`.

#### Rodada da demo

Rodada usada como referência na apresentação de 16/10 (decisão D8 de
`add-portfolio-showcase`). O JSON bruto fica fora do git
(`bancada/relatorios/20261013-104226.json`); os números abaixo saem dele.

| Medida | Valor |
| --- | --- |
| Rodada | 13/10/2026, 10:42, relatório `20261013-104226` |
| Código | branch `fix-robustez-demo`, commit `0e746719` (`main` de 13/10 com o `fix-robustez-demo`) |
| Gerador | `deepseek-v4-pro`, canal web, recuperação híbrida, k = 5, limiar 0,55 |
| Casos aprovados | **29 de 30**, sem falha eliminatória; critério de aceite cumprido |
| Falha | F06 (fígado e médico de Sorocaba): o bloco 2 não separa a opinião da mensagem, falha de forma |
| Acerto por etapa | fronteira 7/7, extração 36/36, recuperação 10/10, guarda 12/12, resposta 39/40, leitura 10/10 |
| Veredito com fonte | 10 de 10 respostas com evidência trazem link da checagem em todas as fontes |
| Conferência de sustentação | tirou frase sem base em 6 casos |
| Latência, verificação completa (19 casos) | mediana 13,8 s, p90 18,7 s, máximo 30,0 s |
| Latência, todos os casos | mediana 10,9 s |
| Tokens | 117 chamadas; entrada 169.689 (119.680 em cache), saída 13.155 |
| Custo da rodada | cerca de US$ 0,06 fora do pico e US$ 0,12 no pico |
| Custo médio por caso | cerca de US$ 0,002 fora do pico e US$ 0,004 no pico |

Custo calculado com os preços da DeepSeek consultados em 08/10/2026
(`add-gerador-api-deepseek`, proposta): US$ 0,66 a 1,32 por milhão de tokens
de entrada sem cache, 0,022 a 0,044 com cache e 1,98 a 3,96 de saída. Se o
código da tag `showcase-demo` mudar depois desta rodada, a rodada é refeita e
esta tabela trocada.

### Sondas por etapa

Com o Gemma local, três tentativas por caso:

| Sonda | Tentativas aprovadas |
| --- | --- |
| fronteira | 42 de 42 |
| classificação e guarda | 24 de 24 |
| extração e decomposição | 21 de 21 |
| resposta em quatro blocos | 21 de 21 |
| limiar de evidência | 20 de 20 alvos acima do limiar; menor alvo 0,5785 |

### Testes automatizados

861 testes passam e 2 ficam pulados, porque precisam do índice construído
localmente. Incluem testes de página com Playwright e axe-core.

### Com pessoas

O instrumento de coleta (`prototipo/avaliacao/`) mede discernimento,
transferência sem a ferramenta e tempo até a decisão fundamentada. O piloto
com 2 participantes (task 6.6) rodou em 08/10/2026. Agregado em
`datasets/relatorios_mvp_copiloto/relatorios_metricas.json`:

| Medida | Resultado |
| --- | --- |
| Discernimento | 4 de 4 |
| Transferência, sem a ferramenta | 4 de 4 |
| Transferência com critério declarado | 4 de 4 |
| Abriu a camada de detalhe | 6 de 6 |
| Tempo mediano até a decisão fundamentada | 137,5 s com a ferramenta; 80,5 s na transferência |

Com n = 2, o piloto valida o instrumento e o roteiro, **não sustenta conclusão
sobre efeito**. A métrica primária do projeto, ganho de discernimento, pede a
coleta com mais participantes.

## Limites

O que o protótipo não faz está em
[Tasks pendentes](../pendencias.md#limitacoes-conhecidas-do-prototipo).
