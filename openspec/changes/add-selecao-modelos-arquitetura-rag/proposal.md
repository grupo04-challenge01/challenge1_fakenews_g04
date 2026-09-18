# Proposal: Seleção de modelos e arquitetura de recuperação

**Fase do CBL:** Investigate (semanas 2–3). Sucede `add-tratamento-datasets-ptbr`,
que deixou explicitamente fora de escopo a "escolha de modelo, embeddings ou
infraestrutura de índice", e antecede as tasks 1.4 a 2.3 de
`mvp-copiloto-verificacao`.

## Why

A orientação recebida em 17/09/2026 foi de não treinar modelo do zero e partir de
um modelo pronto, com o MedGemma como candidato, mesclando fine-tuning ao RAG. A
primeira metade da orientação está correta e já é o que o MVP assume. A segunda
metade precisa ser registrada com precisão, porque três decisões diferentes
estavam sendo tratadas como uma só:

- **qual modelo**, para **qual dos três papéis** distintos que o MVP tem;
- **o que entra por recuperação e o que entra por peso treinado**;
- **que estatuto** a análise de sentimento tem na saída do sistema.

Nenhuma das três está registrada em change algum. Sem esse registro, as tasks 1.4
(recuperação com prioridade de idioma), 1.5 (limiar de `evidência insuficiente`) e
2.3 (guarda contra veredito paramétrico) de `mvp-copiloto-verificacao` não têm
critério de escolha, e o grupo entra na fase Act decidindo infraestrutura por
tentativa.

Há ainda um risco concreto de conformidade. Duas das leituras possíveis da
orientação — fine-tunar um modelo médico para emitir veredito, e usar polaridade
de sentimento como sinal de falsidade — colidem com restrições já fixadas em
`openspec/project.md` e em `mvp-copiloto-verificacao`. O change existe tanto para
escolher quanto para tornar essas colisões visíveis antes de custarem semanas.

## What Changes

Quatro capacidades novas, todas de pesquisa e decisão registrada — nenhuma é
módulo de código.

- **`selecao-modelo`** — decomposição do MVP em três papéis de modelo, critério de
  seleção por papel, decisão registrada com evidência, e registro de descarte do
  MedGemma com motivo.
- **`arquitetura-recuperacao`** — recuperação híbrida léxica + densa como linha de
  base obrigatória, dimensionamento do índice para a escala real do corpus, e
  procedência do limiar de `evidência insuficiente`.
- **`fronteira-treino-recuperacao`** — regra que separa o que pode ser aprendido em
  peso do que MUST vir de trecho recuperado, com auditoria.
- **`uso-analise-sentimento`** — estatuto da análise de sentimento e emoção:
  explicativa e descritiva, nunca evidenciária.

## Capabilities

### New Capabilities

- `selecao-modelo`: que modelo cumpre que papel, sob que critério, e o que foi
  descartado com que motivo.
- `arquitetura-recuperacao`: como a recuperação é construída, em complemento a
  `recuperacao-evidencia`, que define o que ela precisa entregar.
- `fronteira-treino-recuperacao`: onde o conhecimento mora, e o que isso proíbe.
- `uso-analise-sentimento`: onde sentimento e emoção podem aparecer na saída.

### Modified Capabilities

Nenhuma. `recuperacao-evidencia`, `verificacao-alegacao` e
`fronteira-orientacao-saude` de `mvp-copiloto-verificacao` continuam válidas;
este change fornece as decisões de construção que elas pressupõem.

## Out of Scope

- Índice de produção, pipeline de resposta e prompt do produto. São tasks de
  `mvp-copiloto-verificacao`, fase Act. A prova de conceito de recuperação das
  tasks 2.2 a 2.6 **está** em escopo e é o que torna mensuráveis as decisões 3,
  4 e 5 do `design.md` — `arquitetura-recuperacao` exige medição de recall nas
  duas configurações antes de aceitar qualquer simplificação, e medição exige
  algo que rode. A separação é de estatuto: o que sai daqui é evidência de
  decisão em `prototipo/`, não componente do MVP.
- Escolha do canal de entrega, que continua em aberto no `design.md` do MVP.
- Curadoria do catálogo de técnicas de manipulação (task 3.1 do MVP), ainda que
  este change restrinja o que pode entrar nele.
- Treino de classificador de veredito, vedado por `openspec/project.md`.
- Contratação de API paga ou provisionamento de infraestrutura.
- Avaliação de modelos multimodais e OCR, fora do escopo declarado do MVP.

## Impact

Entregáveis finais do challenge atingidos:

- **Portfólio de pesquisa** — o descarte fundamentado do MedGemma e a evidência
  de benchmark em português são resultado de pesquisa, não subproduto técnico.
- **Solução/protótipo com suporte de IA** — desbloqueia as tasks 1.4, 1.5, 1.6 e
  2.3 de `mvp-copiloto-verificacao`.
- **Estrutura de avaliação de confiança** — `uso-analise-sentimento` delimita o
  que pode virar dimensão da matriz e o que não pode.
- **Apresentação e reflexão** — a distinção entre "saúde clínica" e "saúde como
  domínio de desinformação" é material de reflexão sobre escolha de ferramenta.

Dependências e restrições:

- Depende de `add-tratamento-datasets-ptbr`: indexar antes de normalizar rótulos
  e reparar acentuação propaga o defeito para o índice.
- O ambiente de desenvolvimento conferido em 17/09/2026 não tem `torch`, `node`
  nem o CLI `openspec` instalados. Provisionamento é pré-requisito de qualquer
  task de Act.
- A escala do corpus (4.063 checagens) é pequena o bastante para tornar
  desnecessária parte da infraestrutura que a literatura de RAG pressupõe. Ver
  `design.md`, decisão 3.
