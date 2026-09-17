# Tasks

## 1. Corpus e recuperação
- [ ] 1.1 Definir esquema de indexação do recorte de saúde do FactCenter (4.063 checagens)
- [ ] 1.2 Indexar FACTCK.BR como fonte auxiliar, com rótulos normalizados
- [ ] 1.3 Definir lista de fontes oficiais aceitas (Ministério da Saúde, Fiocruz, Anvisa)
- [ ] 1.4 Implementar recuperação com prioridade de idioma (PT-BR antes de EN)
- [ ] 1.5 Definir e calibrar o limiar de `evidência insuficiente`
- [ ] 1.6 Implementar ancoragem trecho a afirmação e descarte de afirmação sem trecho

## 2. Verificação e veredito
- [ ] 2.1 Prompt de extração de alegação, com seleção quando há várias
- [ ] 2.2 Prompt de classificação nos quatro rótulos
- [ ] 2.3 Guarda contra veredito por conhecimento paramétrico
- [ ] 2.4 Teste de regressão com itens verdadeiros contra-intuitivos
- [ ] 2.5 Prompt de decomposição fato / evidência / opinião, com teste do caso
      misto e do fato verdadeiro que sustenta conclusão que não decorre

## 3. Resposta formativa
- [ ] 3.1 Fechar o catálogo de 6 a 8 técnicas, com nome e descrição em linguagem cotidiana
- [ ] 3.2 Prompt da estrutura de quatro blocos
- [ ] 3.3 Validação automática: rótulo usado pertence ao catálogo
- [ ] 3.4 Verificação de que a alegação falsa nunca abre a resposta sem marcação

## 4. Fronteira de saúde
- [ ] 4.1 Classificador de pedido de conduta clínica individual
- [ ] 4.2 Respostas de redirecionamento, incluindo caso de sinal de risco
- [ ] 4.3 Bateria de testes adversariais de pedido de conduta

## 5. Interface
- [ ] 5.1 Camada visível e camada de detalhe
- [ ] 5.2 Checklist de acessibilidade: contraste, fonte, alvo de toque, ação primária
- [ ] 5.3 Fluxo de primeira verificação sem cadastro
- [ ] 5.4 Verificação de legibilidade da camada visível (limite de palavras e frases)

## 6. Avaliação
- [ ] 6.1 Curar 20 a 30 casos, com no mínimo 4 verdadeiros contra-intuitivos
- [ ] 6.2 Configurar 4 a 6 itens-armadilha
- [ ] 6.3 Redigir TCLE e roteiro de debriefing
- [ ] 6.4 Submeter protocolo ao comitê de ética
- [ ] 6.5 Instrumentar coleta das métricas de resultado e de guarda
- [ ] 6.6 Rodar piloto com 2 participantes antes da coleta

## 7. Decisões pendentes
- [ ] 7.1 Definir o canal de entrega e registrar a decisão em `design.md`

## 8. Fechamento
- [ ] 8.1 Conferir consistência do catálogo de técnicas com as dimensões da
      `matriz-confianca` da fase Engage
- [ ] 8.2 `openspec validate mvp-copiloto-verificacao --strict` limpo
