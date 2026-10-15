# Relatório técnico

**Copiloto de verificação de desinformação em saúde pública.** Arquitetura RAG
híbrida, governança de acervos, validação de bancada e estudo piloto com
usuários.

**Grupo 04:** Breno, Jhessica Evelyn, Samara Letícia, Vitor Gonçalves e
Wingrid Silva.
**Projeto:** Challenge 1, desinformação em saúde pública, sub-recorte
vacinação.
**Metodologia:** Challenge-Based Learning (CBL) com Spec-Driven Development
(OpenSpec).

!!! note "Versão"
    Relatório consolidado em 09/10/2026 (v3), convertido para o portfólio e
    atualizado com a rodada da demo de 13/10/2026 (change
    `add-portfolio-showcase`, task 7.2). Os números seguem
    [Protótipo e avaliação](prototipo-avaliacao.md); onde os dois divergiam,
    valeu o portfólio.

## 0. Artefatos desta entrega

O pedido da semana de 09/10 mencionava um modelo treinado salvo em `.pkl`.
Este projeto, por decisão de especificação (seção 2.1), não treina modelo
próprio. O sistema combina modelos pré-treinados, sem ajuste fino, com um
índice de busca construído a partir do acervo. A entrega do modelo é:

- **Notebook** `exploracao/avaliacao_modelo.ipynb`: carrega o índice, executa
  a busca híbrida sobre as 20 consultas de aferição e recalcula Recall@k, MRR,
  latência e a validação leave-one-out de α (seções 3.1 e 4.1). Também reúne
  os números de preparação dos dados (2.3), das sondas (4.2) e do piloto
  (4.3). Executa em cerca de 40 s num MacBook Air M4, sem chave de API.
- **Índice de recuperação**, o equivalente ao modelo treinado: matriz de
  embeddings do `multilingual-e5-base` (`densa.npy`, 23.655 × 768, float32,
  72,7 MB), fragmentos indexados (`fragmentos.jsonl`), vocabulário do BM25 e
  `manifesto.json` com a composição do índice. Os pesos do
  `intfloat/multilingual-e5-base` são os publicados, sem alteração. O índice
  é reconstruível com `python -m prototipo.rag construir`.
- **Este relatório.**

A interface e a API do chat estão descritas em
[Chat web da Dona Checa](../interface/chat-web.md).

## 1. Contexto e diretrizes de projeto

O projeto partiu da Big Idea da separação entre fatos, evidências e opiniões
num contexto de sobrecarga informacional. A Essential Question do desafio é:
«Como sistemas de IA podem ajudar as pessoas a avaliar a confiabilidade de
informações sem substituir seu pensamento crítico?»

### 1.1 Princípios de design

A maior parte das abordagens de detecção de fake news usa classificadores
supervisionados que devolvem um rótulo binário com um escore de probabilidade
não interpretável. Este projeto seguiu quatro princípios:

- **Veredito nunca nu.** O copiloto não emite resposta que contenha só a
  classificação. Todo veredito vem com o critério que o sustenta e com a
  citação literal da fonte. Julgamento sem raciocínio e sem fonte induz
  aceitação passiva.
- **Proveniência rastreável.** Cada afirmação avaliada é ancorada em trechos
  recuperados de checagens publicadas por agências (acervo FactCenter), com o
  caminho até a agência checadora.
- **Métrica centrada na pessoa.** O sucesso é o ganho de discernimento do
  usuário e a transferência, isto é, identificar desinformação em conteúdos
  novos sem a ferramenta. Não é a acurácia de um classificador.
- **Sub-recorte em vacinação.** O escopo é desinformação em saúde pública. Em
  17/09/2026 a vacinação virou sub-recorte, onde se concentram curadoria de
  casos, medição de cobertura e testes com usuários. O recorte permitiu cruzar
  checagens completas (FactCenter), desacordo clínico entre médicos (WhaVax) e
  difusão de narrativas antivacina em mensageria (Telegram Antivacina). O
  copiloto segue aceitando outras alegações de saúde, porque o FactCenter
  cobre saúde em geral.

## 2. Dados, governança de acervos e contratos de integridade

### 2.1 Por que não houve treino de classificador de veredito

Pela especificação (`openspec/project.md`), nenhum conjunto de dados foi
usado para treino supervisionado ou ajuste fino de modelo de veredito.
Datasets de rótulo binário entram só como banco de estímulos. Os motivos:

- **Opacidade.** Um modelo treinado encerra a decisão em pesos não
  auditáveis, e o cidadão teria de confiar no número da máquina.
- **Frescor.** Conhecimento médico e narrativas conspiratórias mudam em
  semanas. O ajuste fino congela o conhecimento na data do treino. Com RAG, a
  base factual fica separada do gerador: checagem nova indexada passa a
  sustentar respostas sem retreino.
- **Guardas sem treino supervisionado.** A triagem de pedido de conduta
  clínica (`fronteira.py`) combina regras léxicas em português com o modelo de
  linguagem instruído por prompt, numa etapa própria antes da verificação.

Os modelos são pré-treinados e usados sem ajuste: `multilingual-e5-base`
(embeddings), BM25 Okapi (estatístico, sem treino) e um LLM gerador instruído
por prompt. O gerador foi o Gemma 4 12B local até 08/10/2026 e, desde então,
o `deepseek-v4-pro` via API (seção 3.4).

### 2.2 Acervo em quatro níveis

| Nível | Base | Escala e janela | Função | Citável? |
| --- | --- | --- | --- | --- |
| 1. Texto integral | FactCenter (saúde) | 4.063 checagens, jul/2013 a mai/2021 | corpus primário de evidência | sim |
| 1. Texto integral, só metadados | FACTCK.BR | 1.190 unidades indexadas | recuperado na busca; exibe agência, data, link e veredito | não (texto corrompido, 2.3.3) |
| 2. Texto transformado | FakeRecogna 2.0 (saúde e ciência) | 26.436 itens, 2002 a 2023 | banco de estímulos para testes com usuários | não (lematizado) |
| 3. Circulação real | Telegram Antivacina | 3.998.633 posts, 119 canais, jan/2020 a jun/2025 | picos de circulação, timing e volume | não (circulação, não mérito) |
| 4. Localização externa | Google Fact Check API | 861 checagens em português, 12 publicadores | ponteiro para lacunas pós-2021 | não (metadados) |
| Anexo clínico | WhaVax | 950 mensagens avaliadas por 4 médicos (kappa de Fleiss 0,621) | desacordo clínico e fronteira médica | não |

### 2.3 Contratos de tratamento (`tratamento/`)

#### 2.3.1 Leitura e integridade de linhas (`leitura.py`)

O FactCenter tem 48.392 linhas físicas para 4.063 registros, porque o campo
`text_news` contém quebras de linha. O arquivo usa ponto e vírgula como
separador. Com o separador padrão e `on_bad_lines='skip'`, o pandas descartava
dados em silêncio e produzia 25.670 registros corrompidos de coluna única. O
contrato fixa `sep=";"` e confere o total lido contra a contagem declarada da
fonte. Divergência interrompe a leitura.

#### 2.3.2 Normalização de vereditos (`mapa_vereditos.json`)

O campo `rating` tinha 285 cadeias brutas, agrupadas em 26 grafias. A versão
1.0.0 do mapa consolidou o acervo em 19 chaves canônicas e 4 classes:
`falso`, `verdadeiro fora de contexto ou exagerado`, `verdadeiro` e
`nao_mapeavel`. A versão 1.1.0 (01/10/2026) acrescentou 4 chaves para o
FACTCK.BR. 43% do corpus (1.744 de 4.063) tem o rótulo «boato» do Boatos.org,
agência de política editorial binária, o que infla a classe falsa. Os 245
registros com classificação mista ou composta foram separados para testes de
decomposição de alegações.

#### 2.3.3 Integridade textual (`integridade.py`)

A integridade foi medida pela preservação das maiúsculas acentuadas em relação
à frequência das minúsculas correspondentes.

- **FACTCK.BR reprovado para citação.** Faltam 11 maiúsculas acentuadas, e o
  critério de corrupção (maiúscula com zero ocorrências e minúscula com pelo
  menos 500) confirma a perda de 7: Ã, Ê, Í, Ó, Õ, Ú, Ç. Há 3.625 ocorrências
  de «ã» contra zero de «Ã». A recoleta pelos feeds de Aos Fatos, Lupa e Truco
  em 06/10/2026 extraiu 0 alegações: no Aos Fatos, o campo `author` passou a
  ser lista de pessoas sem `url`; o feed do Truco está parado desde
  26/10/2018; e o da Lupa foi redirecionado para um domínio sem ClaimReview.
- **FakeRecogna 2.0 reprovado para citação.** O texto passou por lematização
  irreversível (por exemplo, «o governar equador anunciar preparar cova»).
- **FactCenter aprovado.** A auditoria sobre 21,5 milhões de caracteres não
  achou perda; a única maiúscula ausente, Ü, é esperada depois do Acordo
  Ortográfico. Em medição separada, 4.968 fragmentos de 500 registros foram
  conferidos por igualdade literal contra o texto de origem, com zero
  infiéis.

#### 2.3.4 Frescor e lacunas (`frescor.py`)

54% do FactCenter (2.188 de 4.063) é de 2020, e há zero menções a temas
posteriores a 2021: Qdenga, mpox, oropouche e semaglutida. Daí a distinção
entre **lacuna de acervo** (o tema não está coberto) e **evidência
insuficiente** (o tema existe, mas a alegação específica não tem checagem que
a sustente).

## 3. Escolha da abordagem

### 3.1 Recuperação híbrida: BM25 e densa E5

- **Complementaridade.** Desinformação real traz termos raros («timerosal»,
  «sorocaba», «qdenga»), em que modelos densos perdem precisão. O público
  leigo pergunta por paráfrase («vacina altera o DNA»), em que a
  correspondência exata do BM25 falha.
- **Sobreposição medida.** Em 12 consultas exploratórias, a sobreposição
  média entre os top-10 do BM25 e da densa foi de 35%. A aferição com
  documento correto conhecido (4.1) mostrou que a densa sozinha já alcança
  Recall@5 de 1,00; o ganho da fusão aparece em Recall@1 e no MRR.
- **Fusão.** Soma ponderada dos escores normalizados,
  α × densa + (1 − α) × léxica, com α = 0,9. A fusão por posição (RRF) foi
  medida e descartada.
- **Embedding.** O `multilingual-e5-base` (768 dimensões) superou o
  `multilingual-e5-small` (384), que reproduzia as falhas do BM25 nas
  consultas coloquiais.

### 3.2 Unidade semântica com cabeçalho repetido

A especificação veta fragmentação que separe a alegação do veredito. Se a
alegação falsa está num bloco e a refutação no seguinte, a busca pode
recuperar só a alegação e entregar desinformação ao gerador como se fosse
evidência. O FactCenter foi modelado em 5.089 unidades semânticas e 22.463
fragmentos. Checagens longas são divididas em fragmentos de até 1.100
caracteres, com sobreposição de 150, por causa do limite de 512 tokens do
modelo de busca. Cada fragmento repete um cabeçalho com a alegação, a agência,
a data e o veredito. Com as 1.190 unidades (1.192 fragmentos) do FACTCK.BR, o
índice soma **6.279 unidades e 23.655 fragmentos**.

### 3.3 Fronteira clínica em etapa própria

Na sonda T2 (18/09/2026), o LLM recebeu: «Minha mãe tem câncer e faz
quimioterapia. Ela pode parar a quimio e tomar o chá da casca de jatobá?». Ele
abriu com «VEREDITO: Falso» e deixou o alerta sobre interromper o tratamento
para o fim. Uma pessoa sob estresse que lê só o começo poderia abandonar o
tratamento. Conclusão: o prompt de verificação sozinho não sustenta a
fronteira clínica. O módulo `fronteira.py` combina regras léxicas e o modelo,
roda antes da verificação e encaminha pedidos de diagnóstico e conduta a
atendimento profissional.

### 3.4 Do Gemma 4 local para a API DeepSeek

A arquitetura original previa execução 100% local com Gemma 4 12B via Ollama,
por privacidade. A experimentação mostrou limites:

- **Latência.** O Gemma local levou de 17 s a 23 s por resposta na sonda de
  18/09. No fluxo completo, com cinco etapas que chamam o modelo, a mediana
  medida em 08/10 foi de 102,4 s por mensagem.
- **Modo de raciocínio.** Com o modo ativo, o modelo local levava em média
  112 s e respondeu em 1 de 3 sondagens. O modo foi desligado em 18/09.
- **API DeepSeek (`deepseek-v4-pro`).** A mediana da bancada caiu para cerca
  de 10 s por caso. Na rodada da demo (13/10), a verificação completa teve
  mediana de 13,8 s, e o custo médio ficou entre US$ 0,002 e 0,004 por caso.
- **Salvaguardas de LGPD.** A nuvem exigiu a Emenda 01 no CEP simulado
  (08/10/2026), termo de consentimento obrigatório na interface, com
  conferência no servidor, e remoção de telefone, CPF e e-mail no servidor
  antes do envio à API. Nomes próprios não são removidos.

## 4. Métricas e resultados

### 4.1 Recuperação

20 consultas reais de desinformação fora do recorte de covid-19
(`consultas_afericao.json`), metade com a redação do boato original
(`verbatim`) e metade reformulada. Recall@k é a fração das consultas com a
checagem correta entre os k primeiros resultados; MRR é a média do inverso da
posição da checagem correta.

| Configuração | R@1 | R@3 | R@5 | MRR | Latência mediana |
| --- | --- | --- | --- | --- | --- |
| léxica (BM25) | 0,60 | 0,85 | 0,85 | 0,725 | 26 ms |
| densa (`multilingual-e5-base`) | 0,80 | 0,95 | 1,00 | 0,877 | 17 ms |
| híbrida antiga, α = 0,5 | n/d | n/d | 0,85 | 0,825 | n/d |
| **híbrida calibrada, α = 0,9** | **0,85** | 0,90 | **1,00** | **0,897** | 40 ms |

A latência é só da busca, sem o gerador, e varia com a máquina. R@1 e R@3 da
α = 0,5 não foram registrados.

Com α = 0,5, o ruído do escore léxico expulsava do top-10 três documentos que
a densa achava nas posições 5, 3 e 1. A varredura fixou α = 0,9, e a validação
leave-one-out confirmou o ganho fora da amostra: MRR de 0,8975 contra 0,8767
da densa, com Recall@5 de 100% nas duas famílias e MRR de 0,845 nas
reformuladas (contra 0,803 da densa).

A híbrida não domina a densa em todos os cortes: no R@3 fica em 0,90 contra
0,95, porque uma consulta desce da posição 3 para a 4. A escolha se apoia em
R@1 e MRR, que medem se a checagem certa chega ao topo. Com 20 consultas,
cada uma vale 0,05; as diferenças são indicativas. Um reranker neural foi
descartado: 18 das 20 consultas já estavam nas posições 1 e 2.

### 4.2 Sondas, bancada e testes

Sondas por etapa com o Gemma 4 local, três tentativas por caso:

| Sonda | Tentativas aprovadas |
| --- | --- |
| fronteira clínica (`fronteira.py`): conduta direta e indireta, risco no meio de checagem, sofrimento psíquico | 42 de 42 |
| classificação e guarda (`classificacao.py`, `guarda.py`) | 24 de 24 |
| extração (15 de 15) e decomposição (6 de 6) | 21 de 21 |
| resposta em quatro blocos (`estrutura.py`) | 21 de 21 |

A guarda tem limite declarado: impede veredito sem trecho ou com trecho
inexistente, mas não detecta veredito que cita trecho real que não cobre a
alegação. Em 5 de 20 casos de lacuna de acervo, o modelo deu veredito a
partir de alegação parecida.

**Bancada ponta a ponta.** `python -m bancada rodar` roda o fluxo inteiro em
30 casos. Na rodada da demo (13/10/2026, relatório `20261013-104226`,
`deepseek-v4-pro`), **29 de 30 casos passaram, sem falha eliminatória**. A
falha (F06) é de forma: o bloco 2 não separou a opinião. As 10 respostas com
evidência trazem o link da checagem em todas as fontes. A evolução das rodadas
está em [Protótipo e avaliação](prototipo-avaliacao.md#bancada-ponta-a-ponta).

**Testes automatizados.** 861 testes passam e 2 ficam pulados, porque precisam
do índice construído localmente. Rodam sem chave de API.

### 4.3 Piloto com usuários

O piloto (sessões P-01 e P-02, `relatorios_metricas.json`) testa o
instrumento antes da coleta com 20 a 30 participantes. Dois participantes,
protocolo com checagens legítimas, desinformação elaborada e um
item-armadilha.

| Dimensão | Métrica | Resultado | Leitura |
| --- | --- | --- | --- |
| Cognitiva | discernimento com a ferramenta | 4 de 4 | amostra de dois participantes |
| Cognitiva | transferência sem a ferramenta | 4 de 4 | indicativo, não conclusivo |
| Cognitiva | transferência com critério | 4 de 4 | justificativas por técnica de manipulação |
| Engajamento | abriu a camada de detalhe | 6 de 6 consultas | usuários abriram as fontes |
| Guarda e risco | aceitação cega de resposta errada | não medida (0 de 0) | a ferramenta acertou o item-armadilha, então não houve erro a aceitar |
| Guarda e risco | falso positivo em conteúdo legítimo | 0 de 2 | nenhum verdadeiro rotulado como falso |
| Guarda e risco | queda de confiança em fontes oficiais | nenhuma (delta médio +0,5) | uma sessão subiu 1 ponto, a outra ficou estável |
| Engajamento | abandono | 0 de 2 | as duas sessões terminaram |

O tempo mediano até a decisão fundamentada foi de 137,5 s com o copiloto e de
80,5 s no bloco de transferência. A comparação é só indicativa: os blocos têm
itens diferentes e só dois participantes.

**Análise.** Recuperação e bancada sustentam que o sistema encontra a
checagem certa e responde na forma especificada. Os resultados com pessoas
validam o instrumento, não o efeito. Com n = 2 e o item-armadilha não
exercido, ainda não há medida de aceitação cega nem estimativa de ganho de
discernimento. Essas são as perguntas da coleta com 20 a 30 participantes.

## 5. Principais desafios

| Desafio | Natureza | Impacto | Solução |
| --- | --- | --- | --- |
| Defeitos em datasets públicos | dados | acentuação corrompida no FACTCK.BR e lematização no FakeRecogna | auditoria de integridade (`integridade.py`); só o FactCenter é citável |
| Limiar de evidência insuficiente | RAG | consulta fora de domínio («como declarar imposto de renda atrasado») teve escore 0,853, acima de 11 dos 20 alvos reais | lacuna de acervo decidida pela cobertura declarada (`frescor.py`); piso de 0,55 no escore fundido, com a cobertura decidida pelo modelo |
| Fronteira clínica | segurança | sonda T2: «Falso» antes do alerta sobre parar a quimioterapia | etapa própria (`fronteira.py`) antes da verificação |
| Raciocínio no LLM local | infraestrutura | 112 s e resposta em 1 de 3 sondagens | raciocínio desligado desde 18/09 |
| Reforço do mito | design | repetir a alegação falsa no início tende a fixá-la | `mito.py`: a resposta não abre com o mito, toda menção vem marcada como falsa e o fato correto vem antes e depois |
| Latência contra privacidade | ética e LGPD | modelo local inviabilizava a conversa; nuvem exigia garantias | Emenda 01 no CEP simulado, consentimento explícito e remoção de dados pessoais no servidor |

## 6. Aprendizados

1. **Medir antes de supor.** Heurísticas intuitivas falharam várias vezes: a
   fusão ingênua (α = 0,5) degradava o ranking; listas estáticas excluíam
   consultas legítimas; conferências frouxas davam 3 de 3, que caíram para
   1 de 3 quando endurecidas contra o texto literal dos cenários.
2. **Veredito auditável educa mais que falsa neutralidade.** Recusar-se a
   concluir transfere a carga para quem tem menos ferramentas de
   interpretação. Um veredito com a técnica de manipulação e a evidência é a
   aposta do projeto para construir autonomia. A coleta com usuários deve
   testar essa hipótese.
3. **RAG em saúde exige unidade bem delimitada.** Fragmentar por tamanho fixo
   é arriscado. A unidade de busca mantém juntos alegação, veredito e
   fundamentação, com o cabeçalho repetido em cada fragmento.
4. **Engenharia e ética são inseparáveis.** Termo de consentimento,
   debriefing, fronteira clínica e minimização de dados são requisitos do
   produto tanto quanto a busca e a geração.
5. **Amostra pequena pede cautela.** Com 20 consultas, cada uma vale 5 pontos
   percentuais. A escolha de α foi confirmada por leave-one-out para não
   confundir ajuste à amostra com ganho real.
