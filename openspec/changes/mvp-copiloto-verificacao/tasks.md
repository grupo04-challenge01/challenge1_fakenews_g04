# Tasks

Donos das tasks em aberto: **Vitor** 1, **Jhessica** 6, **Samara** 3, **Wingrid** 5, **Breno** 2.

Divisão de 24/09/2026, por papel do artigo de MLOps (Kreuzberger et al.,
2023): R1 Breno, R2 Wingrid, R3 modelagem Vitor, R3 avaliação Jhessica,
R4+R6+R7 Samara. O nome em negrito no início de cada task em aberto é o dono
único dela. Task com dois donos é task sem dono.


## 1. Corpus e recuperação
- [x] 1.1 **Samara** Definir esquema de indexação do recorte de saúde do FactCenter (4.063 checagens)
      — `prototipo/indice/esquema_indexacao.json` v1.0.0, validado por
      `prototipo/rag/esquema.py`; laudo `prototipo/indice/validacao_esquema.json`
      aprovado: 4.063 registros, 5.089 unidades, 22.463 fragmentos, 88 registros
      e 1 unidade em quarentena; decisão 16 do `design.md`, 29/09/2026
- [x] 1.2 **Samara** Indexar FACTCK.BR como fonte auxiliar, com rótulos normalizados
      — `prototipo/rag/unidades.py` (`construir_factckbr`, `construir_indice`),
      testes `prototipo/rag/tests/test_factckbr.py`; esquema 1.1.0 e mapa de
      vereditos 1.1.0; laudo `prototipo/indice/validacao_esquema.json` aprovado:
      984 registros, 1.190 unidades, 1.192 fragmentos, 86 registros e 5 unidades
      em quarentena, `apto_citacao=false`; aferição sem perda
      (`afericao_multilingual-e5-base.json`); decisão 17 do `design.md`, 01/10/2026
- [ ] 1.3 **Wingrid** Definir lista de fontes oficiais aceitas (Ministério da Saúde, Fiocruz, Anvisa)
- [ ] 1.4 **Samara** Implementar recuperação com prioridade de idioma (PT-BR antes de EN)
- [ ] 1.5 **Vitor** Definir e calibrar o limiar de `evidência insuficiente`
- [ ] 1.6 **Samara** Implementar ancoragem trecho a afirmação e descarte de afirmação sem trecho

## 2. Verificação e veredito
- [x] 2.1 **Vitor** Prompt de extração de alegação, com seleção quando há várias
      — `prototipo/verificacao/extracao.py`, sonda 9/9, decisão 8 do `design.md`, 29/09/2026
- [x] 2.2 **Vitor** Prompt de classificação nos quatro rótulos
      — `prototipo/verificacao/classificacao.py`, sonda 9/9, decisão 11 do `design.md`, 29/09/2026
- [x] 2.3 **Vitor** Guarda contra veredito por conhecimento paramétrico
      — `prototipo/verificacao/guarda.py`, sonda 12/12, decisão 12 do `design.md`, 29/09/2026;
        limiar como parâmetro, valor pela 1.5
- [ ] 2.4 **Jhessica** Teste de regressão com itens verdadeiros contra-intuitivos
- [x] 2.5 **Vitor** Prompt de decomposição fato / evidência / opinião, com teste do caso
      misto e do fato verdadeiro que sustenta conclusão que não decorre
      — `prototipo/verificacao/decomposicao.py`, sonda 6/6, decisão 9 do `design.md`, 29/09/2026

## 3. Resposta formativa
- [x] 3.1 **Vitor** Fechar o catálogo de 6 a 8 técnicas, com nome e descrição em linguagem cotidiana
      — sete rótulos e uma vaga reservada, decisão 6 do `design.md`, 28/09/2026
- [x] 3.2 **Vitor** Prompt da estrutura de quatro blocos
      — `prototipo/resposta/estrutura.py`, sonda 21/21, decisão 18 do `design.md`, 01/10/2026
- [x] 3.3 **Vitor** Validação automática: rótulo usado pertence ao catálogo
      — `prototipo/resposta/catalogo.py`, decisão 7 do `design.md`, 28/09/2026
- [x] 3.4 **Vitor** Verificação de que a alegação falsa nunca abre a resposta sem marcação
      — `prototipo/resposta/mito.py`, decisão 14 do `design.md`, 29/09/2026

## 4. Fronteira de saúde
- [x] 4.1 **Vitor** Classificador de pedido de conduta clínica individual
      — `prototipo/verificacao/fronteira.py`, sonda 42/42, decisão 15 do `design.md`, 29/09/2026
- [x] 4.2 **Breno** Respostas de redirecionamento, incluindo caso de sinal de risco
      — diretrizes e respostas Web/WhatsApp, decisão 10 do `design.md`, 29/09/2026
- [ ] 4.3 **Jhessica** Bateria de testes adversariais de pedido de conduta

## 5. Interface
- [ ] 5.1 **Wingrid** Camada visível e camada de detalhe
- [x] 5.2 **Jhessica** Checklist de acessibilidade: contraste, fonte, alvo de toque, ação primária
      — `specs/acessibilidade-leitura/checklist.md` criado com os requisitos verificáveis da especificação
- [ ] 5.3 **Wingrid** Fluxo de primeira verificação sem cadastro
- [x] 5.4 **Jhessica** Verificação de legibilidade da camada visível (limite de palavras e frases)

## 6. Avaliação
- [x] 6.1 **Jhessica** Curar 20 a 30 casos, com no mínimo 4 verdadeiros contra-intuitivos
- [x] 6.2 **Jhessica** Configurar 4 a 6 itens-armadilha
      — 4 armadilhas configuradas e validadas em `utils/gerar_casos.py`; conjunto atualizado gerado em `datasets/casos_mvp_copiloto/mvp_copiloto_casos.json`
- [x] 6.3 **Breno** Redigir TCLE e roteiro de debriefing
      — minuta do TCLE e roteiro operacional em `specs/avaliacao-instrumento/protocolo-etico-tcle-debriefing.md`, decisão 13 do `design.md`, 29/09/2026
- [ ] 6.4 **Breno** Submeter protocolo ao comitê de ética
- [ ] 6.5 **Samara** Instrumentar coleta das métricas de resultado e de guarda
- [ ] 6.6 **Breno** Rodar piloto com 2 participantes antes da coleta

## 7. Decisões pendentes
- [x] 7.1 **Breno** Definir o canal de entrega e registrar a decisão em `design.md`
      — decidido em 25/09/2026: aplicação web (chat responsivo) como canal
      primário, com extensão para WhatsApp. Decisão 5 do `design.md`

## 8. Fechamento
- [ ] 8.1 **Wingrid** Conferir consistência do catálogo de técnicas com as dimensões da
      `matriz-confianca` da fase Engage
- [ ] 8.2 **Wingrid** `openspec validate mvp-copiloto-verificacao --strict` limpo
