# Contexto do Projeto — Grupo 04 / Challenge 1

## O que é este repositório

Documentação spec-driven do Challenge 1 (Fake News / Desinformação) da residência
em IA, conduzido pelo grupo 04 sob a metodologia CBL
(Challenge Based Learning).

As specs aqui descrevem **artefatos de pesquisa e critérios de aceitação de
entregáveis**, não comportamento de software — pelo menos até o final da fase
Investigate. A partir da fase Act, capabilities de produto passam a ser
especificadas em changes próprios.

## Enquadramento do desafio

- **Big Idea:** em um mundo com excesso de informação, como distinguir fatos,
  evidências e opiniões.
- **Essential Question:** como sistemas de IA podem ajudar as pessoas a avaliar a
  confiabilidade de informações **sem substituir seu pensamento crítico**.
- **Competências nomeadas no enunciado:** investigar evidências, identificar
  vieses, construir critérios de confiança. As três precisam ter cobertura
  rastreável em capability; nenhuma é opcional.
- **Recorte adotado:** desinformação em saúde pública.
- **Sub-recorte:** **vacinação**. Decidido em 17/09/2026 — ver nota abaixo.
  Descartados como recorte: doença crônica, suplementos e produtos naturais.

### Nota de decisão — 17/09/2026: sub-recorte

O sub-recorte estava em aberto desde o Engage, bloqueando a curadoria dos casos
de `avaliacao-instrumento`. Foi fechado em **vacinação** ao avaliar a entrada do
corpus de Telegram antivacina (`add-ampliacao-corpus-ptbr`), que cobre
jan/2020 a jun/2025 em português.

O que pesou não foi o tamanho da base, e sim o fato de ela ser o único material
disponível ao projeto que mostra **o que circulou, em que canal e quando** —
insumo que nenhuma das bases de checagem fornece, porque agência publica o
desmentido, não a difusão. Vacinação é também o único dos três candidatos em que
o projeto passa a ter, ao mesmo tempo, checagem com texto integral
(FactCenter), veredito de especialista clínico (WhaVax) e circulação medida.

Os outros dois candidatos não estão proibidos como conteúdo: uma alegação sobre
suplemento continua verificável pelo protótipo. O que a decisão fixa é onde a
curadoria de casos, a medição de cobertura e o teste com usuário se concentram.

## Princípio arquitetural que restringe todas as soluções

A Essential Question exclui explicitamente a substituição do julgamento humano.
Em consequência, para qualquer capability proposta neste projeto:

- O sistema **pode** emitir veredito, nunca como saída única: todo veredito vem
  acompanhado do critério que o sustenta e é auditável até a fonte. Veredito nu —
  sem raciocínio nem proveniência — é que substitui julgamento.
- O sistema apresenta **evidência e proveniência**; o usuário precisa poder
  discordar do veredito com base no que lhe foi mostrado.
- Métrica primária de sucesso é ganho de discernimento do usuário, incluindo
  **transferência** (desempenho sem a ferramenta), não acurácia de classificador.
- Toda saída assistiva precisa ser auditável pelo usuário até a fonte.

Datasets de rótulo binário são admitidos apenas como banco de estímulos para
teste com usuários, nunca como alvo de treino de classificador de veredito.

### Nota de revisão — 10/09/2026

Até esta data o primeiro bullet dizia "o sistema **não emite veredito** de
verdadeiro/falso como saída principal". Essa regra era derivação nossa, não
texto do challenge.

A Big Idea fala em **apoiar a investigação** da confiabilidade, "fortalecendo o
pensamento crítico em vez de substituí-lo"; a Essential Question pergunta como a
IA ajuda a avaliar confiabilidade "sem substituir seu pensamento crítico".
Nenhuma das duas proíbe conclusão. A regra antiga confundia *não substituir o
julgamento do usuário* com *não oferecer um julgamento* — coisas diferentes.

Havia ainda contradição com a própria Big Idea, cujo problema declarado é
**excesso** de informação: segurar a conclusão adiciona atrito a um problema de
atrito.

O que a premissa exige de fato está preservado nos bullets de auditabilidade e
de transferência, que não foram alterados e que continuam sendo o teste real de
qualquer capability. Ver `changes/mvp-copiloto-verificacao/design.md`, decisão 1.

## Cronograma

| Semana | Fase | Datas | Foco |
| --- | --- | --- | --- |
| 1 | Engage | 07/09 a 11/09 | Entender o desafio |
| 2 | Investigate | 14/09 a 18/09 | Pesquisa e descoberta |
| 3 | Investigate | **21/09 a 25/09** | Pesquisa e descoberta |
| 4 | Act | 28/09 a 02/10 | Desenvolvimento |
| 5 | Act | 05/10 a 09/10 | Desenvolvimento |
| 6 | Showcase | 12/10 a 16/10 | Partilha de conhecimento |

Observação: 07/09 é feriado; a semana operacional do Engage começa em 08/09.

As datas por semana foram derivadas em 20/09/2026 da proposta do challenge, que
declara a vigência do Engage (07/09 a 11/09) e a fase de cada semana, mas não as
datas das demais. A proposta confirma o cronograma que já constava aqui; o que
foi acrescentado é o calendário explícito, porque «semanas 2–3» não deixava
óbvio que o Investigate encerra em **25/09** e o Act começa em **28/09**.

### Entregas declaradas por fase

A proposta detalha apenas a semana 1. Para o Engage, as atividades são
investigação forense, elaboração de guiding questions, workshop da confiança
(matriz) e exploração de datasets públicos — e a **entrega** declarada é
«processo investigativo + guiding questions». As guiding questions estão
prontas desde 11/09; o processo investigativo, não.

## Entregáveis finais do desafio

1. Portfólio de pesquisa
2. Estrutura de avaliação de confiança
3. Solução/protótipo com suporte de IA
4. Apresentação e reflexão

## Convenções deste repositório

- **Idioma:** texto em português. Palavras-chave normativas (`SHALL`, `MUST`,
  `MUST NOT`, `WHEN`, `THEN`, `AND`, `GIVEN`) permanecem em inglês para que
  `openspec validate --strict` funcione com a configuração padrão.
- **Capability = artefato entregável**, não módulo de código, enquanto o projeto
  estiver em fase de pesquisa.
- **Um change por fase do CBL.** Specs só são promovidas de `changes/` para
  `specs/` quando a fase correspondente é encerrada e o artefato existe de fato.
- `specs/` está vazio por design: no dia 1 não há nenhuma capability
  estabelecida como verdade corrente.

## Changes previstos

| Change | Fase | Estado |
| --- | --- | --- |
| `add-engage-desinformacao-saude` | Engage | ativo |
| `add-tratamento-datasets-ptbr` | Investigate | ativo |
| `add-ampliacao-corpus-ptbr` | Investigate | ativo |
| `add-selecao-modelos-arquitetura-rag` | Investigate | ativo |
| `fix-resposta-sem-evidencia` | Investigate → Act | proposto |
| `mvp-copiloto-verificacao` | Act | proposto |
