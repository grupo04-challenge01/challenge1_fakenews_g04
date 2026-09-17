# Proposal: Tratamento dos datasets para uso em PT-BR

**Fase do CBL:** Investigate (semanas 2–3). Sucede
`add-engage-desinformacao-saude` e antecede qualquer task de `Act`.

## Why

O pacote de datasets foi coletado em 08/09/2026 e conferido na fonte, mas a
inspeção do corpus que sustentaria o RAG mostra que ele não está utilizável na
forma em que está. Medido em `derivados/factcenter_subset_saude.csv` (4.063
checagens de saúde em PT-BR):

- **Congelado em 2021**, com 54% dos registros em 2020 e 56% mencionando covid.
  Pautas brasileiras posteriores têm cobertura zero: `qdenga`, `mpox`,
  `oropouche`, `semaglutida` — nenhuma ocorrência. Os casos que o grupo está
  curando hoje cairiam em `evidência insuficiente`.
- **O campo `rating` não é um rótulo**: é uma lista Python serializada
  (`"['boato']"`, `"['FALSO', 'VERDADEIRO, MAS']"`), com 285 valores distintos e
  seis vocabulários de agência conviventes, mais variação de caixa.
- **43% do corpus é `['boato']`**, rótulo que não gradua nada, porque a agência
  de origem publica apenas rumor. Só 21 registros em 4.063 são `verdadeiro` ou
  `verdadeiro, mas`.
- **587 registros cobrem mais de uma alegação** (um deles com 101 rótulos) e 250
  têm rótulos divergentes entre si. Um registro não equivale a uma alegação.
- O arquivo é `;`-separado com newlines dentro de `text_news`: 4.063 registros
  em 42.197 linhas físicas. Carregado no default de `read_csv`, produz lixo.
- Em `derivados/factckbr_normalizado.csv`, **todas as maiúsculas acentuadas
  foram perdidas** — está gravado `Sistema nico de Saúde`. Causa raiz no
  `re_char()` de `01_nucleo_metodologico/factckbr/update_factckbr.py`, cuja
  allowlist inclui apenas acentuadas minúsculas.

A leitura inicial do problema de idioma era que os datasets em inglês precisavam
de tradução. A inspeção inverte isso: os três datasets em inglês são
**instrumento e definição**, não conteúdo entregue ao usuário. O tratamento
urgente é no corpus PT-BR.

## What Changes

Quatro capacidades novas, todas de pesquisa e curadoria — nenhuma é módulo de
produto.

- **`normalizacao-rotulos`** — contrato de leitura do corpus, parser do campo
  `rating`, mapa dos seis vocabulários de agência para os quatro rótulos de
  `verificacao-alegacao`, e política para registros multi-alegação.
- **`integridade-textual`** — reparo e verificação da acentuação, fidelidade do
  trecho citado ao texto da fonte, e correção do script de atualização a
  montante.
- **`frescor-corpus`** — medição da cobertura temporal e temática, e política
  para alegação cuja pauta é posterior ao corpus.
- **`adaptacao-criterios-en`** — adaptação dos critérios do FakeHealth e do
  vocabulário de `strength` do InSciOut para PT-BR, validada contra casos
  brasileiros, sem tradução de texto corrido.

## Capabilities

### New Capabilities

- `normalizacao-rotulos`: como o veredito das agências é lido, normalizado e
  reconciliado quando divergente ou múltiplo.
- `integridade-textual`: garantias sobre o texto em português que chega ao
  usuário como citação.
- `frescor-corpus`: cobertura temporal e temática do corpus, e comportamento
  exigido quando a pauta está fora dela.
- `adaptacao-criterios-en`: travessia dos instrumentos em inglês para PT-BR por
  adaptação validada, não por tradução.

### Modified Capabilities

Nenhuma. As capabilities de `add-engage-desinformacao-saude` e de
`mvp-copiloto-verificacao` continuam válidas; este change fornece as
pré-condições de dado que elas assumem.

## Out of Scope

- Treino de qualquer classificador. Os rótulos normalizados servem para
  recuperação, curadoria e estímulo, nunca como alvo de treino de veredito.
- Tradução de texto corrido de PUBHEALTH, FakeHealth ou InSciOut.
- Download do Med-MMHL (4,0 GB, quase todo imagem) — permanece condicional.
- Curadoria dos 20 a 30 casos e construção das armadilhas: são de
  `mvp-copiloto-verificacao`, capability `avaliacao-instrumento`.
- Escolha de modelo, embeddings ou infraestrutura de índice.

## Impact

Entregáveis finais do challenge atingidos:

- **Portfólio de pesquisa** — os caveats por dataset e os descartes com motivo
  são parte do portfólio; três correções factuais já identificadas entram nele.
- **Estrutura de avaliação de confiança** — `adaptacao-criterios-en` fornece o
  vocabulário de critério que a `matriz-confianca` precisa, e resolve o achado
  de que o FakeHealth tem 20 perguntas em dois conjuntos, não 10.
- **Solução/protótipo com suporte de IA** — sem este change, o RAG de
  `mvp-copiloto-verificacao` opera sobre corpus de 2021.

Dependências e restrições:

- Bloqueia as tasks 1.1 a 1.6 de `mvp-copiloto-verificacao` (corpus e
  recuperação): indexar antes de normalizar propaga o problema para o índice.
- A política de frescor pode reabrir a decisão de canal, se a atualização
  contínua exigir agendamento.
- O reparo do `update_factckbr.py` é a montante: código de terceiro, licença
  MIT, e usa API de `pandas` removida na versão 2.0.
