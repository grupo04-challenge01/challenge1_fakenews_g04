# Pacote de Datasets — Challenge 1: Fake News e Desinformação em Saúde

Coleta feita em 08/09/2026, seguindo a organização do *Portfólio de Pesquisa e Arquitetura do Sistema*.
Tudo abaixo foi baixado da fonte primária, verificado e contado (nada veio de cache ou de segunda mão).

## Estrutura

```
datasets-desinformacao/
├── 01_nucleo_metodologico/     # cadeia de raciocínio, few-shot, RAG
│   ├── pubhealth/              # train/dev/test já limpos (CSV)
│   ├── fakehealth/             # reviews/ content/ engagements/ (JSON originais)
│   ├── factcenter/             # central_de_fatos.csv (bruto, sep=";")
│   └── factckbr/               # FACTCKBR.tsv + script de update RSS
├── 02_comparacao_exagero/
│   └── scientific_exaggeration/  # insciout train/test (JSONL + CSV)
├── 03_banco_estimulos/
│   ├── fakerecogna2/           # fakerecogna_extrativo.csv (2.0, substitui a v1)
│   └── med_mmhl/               # só docs + script (dados não baixados, ver abaixo)
├── derivados/                  # tabelas já prontas para uso no projeto
└── relatorio.json              # contagens e distribuições de rótulo de tudo
```

## 1. Núcleo metodológico

### PUBHEALTH — 12.254 alegações (inglês)
Fonte: release original dos autores (Kotonya & Toni), a mesma que o `bigbio/pubhealth` do HuggingFace baixa por trás.
Peguei o TSV original em vez do loader do HF **de propósito**: o script do HF mapeia rótulos por índice, que é
exatamente o ponto frágil apontado no portfólio. No TSV os rótulos vêm como texto (`true/false/mixture/unproven`),
então o problema some.

| split | bruto | após limpeza | true | false | mixture | unproven |
|---|---|---|---|---|---|---|
| train | 9.832 | 9.804 | 5.078 | 3.001 | 1.434 | 291 |
| dev | 1.233 | 1.222 | 635 | 381 | 165 | 41 |
| test | 1.238 | 1.228 | 599 | 385 | 200 | 44 |

A limpeza removeu as linhas com o rótulo `invalid` (não documentado) e as sem `claim` ou `explanation`.

**Correção para o portfólio:** o texto diz que as classes são desbalanceadas "maioria falsa". Na verdade a
classe majoritária é `true` (~52% do treino). O desbalanceamento real está em `unproven` (~3%), que é raro
como o portfólio já aponta. Vale ajustar essa frase antes da entrega.

Colunas: `claim_id, claim, date_published, explanation, fact_checkers, main_text, sources, label, subjects`.

### FakeHealth — 2.296 notícias (1.690 HealthStory + 606 HealthRelease)
Baixado do repositório dos autores (EnyanDai/FakeHealth). Conferi contra o ZIP do Zenodo
(DOI 10.5281/zenodo.3606757): é o mesmo snapshot, então mantive só a versão do repositório e citamos o DOI.

- `reviews/` — o que interessa: 22.959 avaliações de critério, com `question`, `answer` e `explanation` por especialista.
- `content/` — texto das notícias originais (`story_reviews_*.json`, `release_reviews_*.json`).
- `engagements/` — IDs de tweets (só serve se formos medir difusão; a API do X inviabiliza na prática).

Respostas: 11.730 *Satisfactory*, 9.934 *Not Satisfactory*, 1.294 *Not Applicable*.

**Achado:** são **20** perguntas únicas, não 10. HealthStory e HealthRelease usam conjuntos de 10 critérios
diferentes (o de release é adaptado para comunicado institucional). Isso importa na Matriz de Confiança:
ou escolhemos um dos dois conjuntos, ou fazemos o mapeamento entre eles à mão.

### FactCenter / Central de Fatos — 11.647 checagens (português)
Achei o link de dados, que não está no artigo do JIDM: **Zenodo DOI 10.5281/zenodo.5191798**, licença CC BY 4.0.
Arquivo de 55 MB, separador `;`, com `text_news` integral.

Por agência: boatos 5.523 · lupa 2.574 · aos fatos 1.679 · fato-ou-fake 917 · Estadão Verifica 593 · Comprova 361.

Colunas: `url, source_name, title, subtitle, publication_date, text_news, image_link, video_link, authors, categories, tags, obtained_at, rating`.

### FACTCK.BR — 1.313 alegações (português)
Clonado de `thiagorainmaker77/FACTCK.BR` (mirror do original `jghm-f/FACTCK.BR`, mesmo conteúdo). Licença MIT
para a estrutura — o texto das checagens continua sendo das agências, como o portfólio já registra.

Rótulos: falso 943 · verdadeiro 120 · exagerado 91 · distorcido 54 · sem contexto 42 · impossível provar 20 · outros.
Só 3 agências, contra 6 do FactCenter — confirma o papel de fonte auxiliar.

## 2. Comparação: detecção de exagero

### Scientific Exaggeration (InSciOut) — 663 pares
| split | pares | same | exaggerates | downplays |
|---|---|---|---|---|
| test (rotulado, o do artigo) | 563 | 345 | 122 | 96 |
| train | 100 | 61 | 22 | 17 |

Campos: `press_release_conclusion`, `press_release_strength`, `abstract_conclusion`, `abstract_strength`, `exaggeration_label`.
Os pares vêm com o *strength* (força da afirmação) dos dois lados, que é justamente a definição operacional
que precisamos para o prompt do RAG. Deixei fora o `unlabelled_pet.jsonl` (18 MB, serve só para treinar PET).

## 3. Banco de estímulos

### FakeRecogna — 11.903 itens (português)
`Classe 0` = falso (boatos.org, e-farsas, AFP Checamos) · `Classe 1` = verdadeiro (UOL, G1). Perfeitamente
balanceado, 5.951 de cada — o que por si só já denuncia curadoria artificial.

Categorias: saúde 4.456 · política 3.951 · entretenimento 1.409 · brasil 904 · ciência 602.

O viés de sumarização apontado no portfólio se confirma na inspeção: as notícias verdadeiras vêm de portais
grandes e estão encurtadas. Como aqui o uso é só amostragem de estímulo para a interface, não treino, isso
não invalida o uso — mas os itens verdadeiros precisam de revisão manual antes de ir para o teste com usuário,
senão o participante pode acertar pelo estilo do texto.

### Med-MMHL — **não baixado**
Os dados não estão no GitHub: ficam num Dropbox de **4,0 GB** (o volume é quase todo imagem). Como o uso
previsto é teste de estresse condicional, deixei em `03_banco_estimulos/med_mmhl/baixar_med_mmhl.sh` o comando
pronto, mais o apêndice do artigo e a licença (CC BY-NC 4.0 — não comercial, compatível com o uso acadêmico).

## Derivados (`derivados/`)

| Arquivo | O que é |
|---|---|
| `pubhealth_pool_fewshot.csv` | Casos com explicação > 300 caracteres e fontes preenchidas, 15 por classe — pool para escolher os exemplos do prompt |
| `fakehealth_criterios_long.csv` | 22.959 linhas: um critério por linha, com pergunta, resposta e explicação do especialista |
| `fakehealth_matriz_10_criterios.csv` | Cada pergunta com nº de ocorrências e nº de *Not Satisfactory* — base para calibrar a Matriz de Confiança |
| `fakehealth_reviews_indice.csv` | Índice enxuto das 2.296 reviews (id, rating, veículo, links) |
| `factcenter_subset_saude.csv` | **4.063** checagens PT-BR filtradas por termos de saúde/ciência — é este o corpus para o RAG e para os itens falsos do dataset local |
| `factckbr_normalizado.csv` | FACTCK.BR com coluna `rotulo_norm` (rótulos em minúsculas, resolve o "Falso"/"falso" duplicado) |
| `exagero_pares_abstract_vs_release.csv` | Os 663 pares InSciOut num CSV único |
| `fakerecogna2_subset_saude_ciencia.csv` | 26.436 itens (7.652 falsos, 18.784 reais) da 2.0, por **termo de saúde no texto** — o filtro por categoria da v1 não vale na 2.0 |
| `fakerecogna2_amostra_estimulos_300.csv` | Amostra estratificada de 300 itens (`random_state=42`) sobre o subset da 2.0 |
| `fakerecogna2_transformacao.json` | Declaração da transformação de texto por classe e o vazamento medido (80,5% só pelo comprimento) |
| `whavax_agregados.json` | 950 mensagens anotadas por quatro médicos, com a faixa de 84 empates isolada |
| `telegram_agregados.json` | 3.998.633 posts de 119 canais, só contagens — sem texto e sem autor |
| `sonda_factcheck_api.json` | 928 checagens em `pt` pela Fact Check Tools API, 525 posteriores a 2021 |

## O que ainda falta para a fase Investigate

O portfólio pede 20 a 30 casos curados, e nenhum dataset aqui resolve dois pedaços disso:

1. **Itens verdadeiros contra-intuitivos** não existem em nenhuma base baixada. Agência de checagem só publica o
   que é suspeito, e o lado "verdadeiro" do FakeRecogna é notícia comum. Isso é coleta manual mesmo — Fiocruz,
   Ministério da Saúde, divulgação científica.
2. **Armadilhas de IA** (4 a 6 itens com evidência ambígua) são construção nossa, item a item, sobre casos reais.

O `factcenter_subset_saude.csv` é o ponto de partida natural para os itens falsos: 4.063 casos com texto
integral da checagem, o que dá para escolher por plausibilidade cultural em vez de por sorteio.

## Caveats do tratamento (19/09/2026)

Registrados pelo change `add-tratamento-datasets-ptbr`. Todos reexecutáveis por
`python -m tratamento tudo`; detalhe em `docs/investigate/tratamento-datasets.md`.

| Base | Caveat |
| --- | --- |
| FactCenter | 43% do corpus é `boato`, rótulo que não gradua; a classe `falso` está inflada por construção |
| FactCenter | 21 registros consolidam em `verdadeiro` em 4.063 — **não** é fonte de itens verdadeiros |
| FactCenter | janela 2013-07-08 a 2021-05-19, 54% em 2020; `qdenga`, `mpox`, `oropouche` e `semaglutida` com zero ocorrência |
| FactCenter | 245 registros mistos e 11 compilados, fora do banco de estímulos |
| FactCenter | 48.392 linhas físicas para 4.063 registros; separador `;` |
| FACTCK.BR | **reprovado para citação.** Onze maiúsculas acentuadas ausentes, sete com evidência de corrupção. A perda está na fonte distribuída e é irreversível |
| FakeRecogna | **reprovada para citação** por texto transformado na origem (coluna `Noticia` lematizada e sem caixa), não por corrupção |
| PUBHEALTH | classe majoritária é `true` (~52% do treino), não "maioria falsa"; o derivado tem aspas escapadas em excesso na origem |
| FakeHealth | 20 perguntas em dois conjuntos de 10. O nome `fakehealth_matriz_10_criterios.csv` está errado e foi mantido por estabilidade de referência |

### Derivados gerados pelo tratamento

| Arquivo | O que é |
| --- | --- |
| `factcenter_vereditos_normalizados.csv` | cada registro com chaves, rótulos, `misto` e exclusão |
| `relatorio_vereditos.json` | contagens por agência, grafia e chave |
| `relatorio_integridade.json` | laudo por arquivo, com causa provável |
| `declaracao_cobertura.json` | janela, ano a ano, termos de pauta, caminho de atualização |
| `rubrica_criterios_ptbr.json` | rubrica de seis critérios, removidos com motivo, força da afirmação |
| `fewshot_ptbr_pool.csv` | 15 exemplares PT-BR, 5 por rótulo, semente 42 |
