# Proposal: Ampliação do corpus PT-BR e índice de checagens recentes

## Why

**Fase do CBL:** Investigate (semanas 2–3). Sucede `add-tratamento-datasets-ptbr`
e não o substitui: normalizar antes de ampliar.

O corpus PT-BR do projeto termina em 2021. Estamos em setembro de 2026. O change
anterior tratou disso como defeito a ser *declarado* — a capability
`frescor-corpus` existe para o sistema dizer "o acervo não cobre esse período"
em vez de "evidência insuficiente". Isso é mitigação correta, e continua
necessária, mas mitigação não é cobertura: um copiloto de verificação de saúde
que responde lacuna para toda pauta de 2022 em diante falha justamente na
entrada que o teste com usuário e o Showcase vão produzir.

Existe material publicado que recua essa fronteira e não estava no pacote de
08/09/2026. Duas bases baixáveis e uma rota de índice:

- **FakeRecogna 2.0** — extensão da base que já usamos, do mesmo grupo, com
  52.800 itens (26.400 por classe) contra 11.903, e nove agências de checagem
  contra três. Licença **MIT**, contra licença não declarada da v1.
- **WhaVax** — 950 mensagens de WhatsApp sobre vacina anotadas por quatro
  profissionais médicos, com concordância medida (Fleiss κ = 0,621) e faixa de
  empate declarada (~8,8%). **CC BY 4.0**. Nenhuma base nossa tem veredito
  emitido por especialista clínico em português.
- **Telegram antivacina BR (2020–2025)** — 3.998.633 posts de 119 canais
  brasileiros, jan/2020 a jun/2025, em `.jsonl`. **CC BY-NC 4.0**, DOI
  `10.25824/redu/5JIVDT` (REDU/Unicamp). Único material do projeto que mostra
  **o que circulou, em que canal e quando**; nenhuma base de checagem fornece
  isso, porque agência publica o desmentido, não a difusão.
- **Google Fact Check Tools API** — única rota verificada até a data corrente.
  Devolve markup ClaimReview: alegação, veredito textual, agência, data e URL.
  **Não devolve o texto do artigo de checagem.**

### Correção de escopo — 17/09/2026

Até esta data o corpus de Telegram constava em Out of Scope como *"5,5 TB sem
rótulo de veracidade"*. A primeira metade é falsa: os 5,5 TB são a **mídia**, que
exige termo assinado; o **texto é um único `.jsonl` de 3,6 GB, aberto**,
conferido na API do Dataverse do REDU (`restricted: false`,
`fileAccessRequest: false`). A segunda metade é verdadeira e deixou de
desqualificar: o `project.md` já só admite rótulo binário como estímulo, e o que
falta ao acervo aqui é narrativa, não veredito.

A entrada desta base fechou o sub-recorte do projeto em **vacinação**
(`project.md`, nota de 17/09/2026).

## What Changes

- Substituição da FakeRecogna v1 pela 2.0, com regeração dos dois derivados
  versionados e atualização de `FONTES.md`, `README.md`, `SHA256SUMS` e
  `relatorio.json`. **BREAKING** para quem depende de
  `fakerecogna_amostra_estimulos_300.csv`: a amostra é refeita sobre a base nova,
  e a seleção com `random_state=42` sobre a v1 deixa de existir. A perda é apenas
  de reprodutibilidade da seleção — o grupo confirmou em 10/09/2026 que nenhum
  tratamento ou curadoria foi feito sobre os dados até aqui.
- A FakeRecogna 2.0 entra como **estímulo com texto transformado declarado**, não
  como base citável. Os itens verdadeiros são sumarizados na origem; a variante
  adotada é a extrativa, que preserva linguagem publicada em vez de texto gerado
  por modelo.
- Entrada do WhaVax em `01_nucleo_metodologico/`, não em `03_banco_estimulos/`.
  O critério é função, não formato: com anotação clínica e concordância medida,
  é referência metodológica, não estímulo bruto.
- Entrada do corpus de Telegram em camada nova, `04_acervo_circulacao/`, como
  **acervo de circulação**: texto íntegro, mas evidência sobre *difusão*, não
  sobre o fato. **Nenhum texto de post é versionado** — só derivados agregados
  (contagem por mês, por canal, frequência de termo) e o script que os gera.
- Índice de checagens recentes por `claims:search`, em nível de alegação,
  **sem raspagem** do texto das agências.
- **BREAKING** para `frescor-corpus`: a janela deixa de ser a constante
  `2013 a 2021` e passa a declaração de dois níveis, com data de corte.

Nenhuma janela temporal é afirmada por este change. A cobertura da FakeRecogna
2.0 e do índice **SHALL** ser medida antes de ser declarada — os números do
pacote anterior vieram de contagem, e estes também virão.

## Capabilities

### New Capabilities

- `anotacao-especialista-ptbr`: o que o projeto pode afirmar a partir de rótulo
  com anotador clínico em português, incluindo o tratamento normativo da faixa
  de empate entre anotadores.
- `procedencia-substituicao`: o que precisa ser verdade para trocar uma base do
  pacote por versão nova sem quebrar a auditoria da coleta.
- `indice-checagens-recentes`: localização e atribuição de checagem publicada
  fora da janela do acervo, sem citação de texto de terceiro.
- `acervo-circulacao`: o que o projeto pode e não pode afirmar a partir de
  conteúdo de usuário sem rótulo de veracidade — incluindo rótulo derivado por
  modelo, pseudonimização e a proibição de veredito por proxy de canal.

### Modified Capabilities

- `frescor-corpus`: a cobertura deixa de ser janela única e fixa e passa a
  declaração de **quatro** níveis — acervo com texto integral, que serve para
  citação; acervo com texto transformado, que serve como estímulo; acervo de
  circulação, que atesta difusão e não o fato; e índice de localização, que só
  localiza. A política de lacuna é preservada e reescrita para distinguir três
  casos, não dois.

## Impact

Entregáveis finais do desafio atingidos:

- **Portfólio de pesquisa** — a substituição da v1 e o motivo entram como
  registro de proveniência; a medição de cobertura vira caveat datado.
- **Estrutura de avaliação de confiança** — a faixa de empate do WhaVax é o
  primeiro material do projeto onde especialistas humanos discordaram sobre um
  caso real de saúde, e é insumo direto da `matriz-confianca`.
- **Solução/protótipo com suporte de IA** — o índice muda o pior caso da
  resposta de lacuna: de "não sei" para "não tenho o texto, mas existe checagem
  publicada, e é esta".
- **Estrutura de avaliação de confiança**, segunda contribuição — o acervo de
  circulação é o que permite à `matriz-confianca` tratar *procedência e alcance*
  com dado medido em vez de suposição, e é o primeiro material do projeto que
  toca a competência "identificar vieses", hoje sem cobertura (`docs/estado.md`).
- **Sub-recorte fechado em vacinação**, destravando a curadoria de casos de
  `avaliacao-instrumento`.

Dependências e restrições:

- **Depende de `add-tratamento-datasets-ptbr`.** A 2.0 traz nove vocabulários de
  agência contra os seis já inventariados; ampliar antes de normalizar escreve o
  parser contra alvo móvel.
- **Pré-condição de arquivamento:** `frescor-corpus` só existe como delta em
  change não aplicado. `openspec validate --strict` passa, mas o archive recusa
  `MODIFIED` contra spec inexistente. A capability precisa ser promovida para
  `openspec/specs/` via `/opsx:sync` antes de este change ser arquivado.
- Desloca as tasks 4.1 a 4.4 e 2.8 de `add-tratamento-datasets-ptbr`.
- Resolve uma das duas pendências de licença de `FONTES.md`. A do PUBHEALTH
  permanece aberta.
- O índice depende de serviço de terceiro e de chave de API. Se a medição
  inicial mostrar retorno raso para saúde em `pt`, a capability é descartada com
  motivo registrado, em vez de virar entregável oco.

## Out of Scope

- **Raspagem do texto integral das checagens.** O texto é das agências. A
  Central de Fatos é redistribuível por vir sob CC BY; uma raspagem nossa não
  seria. O repositório é público e já carrega uma pendência de licença.
- **Mídia** do corpus de Telegram (1.440.498 itens, os 5,5 TB): exige termo
  assinado e é multimodal. Só o `.jsonl` de texto entra.
- **Derivado com texto de post individual.** A licença permitiria; a ética não.
  Os posts são de pessoas reais, pseudonimizadas mas não anônimas. Versionamos
  agregados, nunca o texto.
- Med-MMHL e MM Health: teste de estresse multimodal permanece condicional.

### Bases avaliadas e recusadas em 17/09/2026

- **FakeCovid** (Shahi & Nandini, arXiv:2006.11343), via o espelho
  `thedevastator/fakecovid-fact-checked-news-dataset` no Kaggle. Medido sobre o
  CSV dos autores: 7.623 linhas, **481 em português**, janela 2020/01/24 a
  2020/07/01. Cruzando `article_source` contra `derivados/factcenter_subset_saude.csv`,
  **330 das 481 (69%) já estão no pacote** — e a comparação é só contra o subset
  de saúde, 4.063 de 11.647 checagens, de modo que a sobreposição real é maior.
  Não recua fronteira alguma: o FactCenter já tem 2.188 itens de 2020. Somam-se
  dois impedimentos: o Kaggle declara **CC0** enquanto o original é **CC BY-NC 4.0**,
  o erro de proveniência que `procedencia-substituicao` existe para barrar; e
  `content_text` é o corpo raspado do artigo da agência, vedado acima.
- **`fabioselau/fakes-news-portuguese`** no Kaggle. Licença **"Unknown"** no
  próprio metadado, versão única de 12/09/2022, sem artigo, sem URL de origem
  por item e sem método descrito — é o TCC do autor. Reprova em
  `procedencia-substituicao` antes do download, porque não há fonte primária a
  conferir. O desbalanceamento (20k falsas contra 2k verdadeiras) agravaria,
  ainda por cima, a carência de itens `verdadeiro` da task 2.8 de
  `add-tratamento-datasets-ptbr`.
- Treino de qualquer classificador. Vale integralmente para a anotação clínica
  do WhaVax, que é referência de calibração, nunca alvo.
- Curadoria dos 20 a 30 casos e construção das armadilhas: são de
  `mvp-copiloto-verificacao`, capability `avaliacao-instrumento`.
- Agendamento ou serviço de atualização contínua. O índice é snapshot com data
  de corte declarada e script reexecutável.
