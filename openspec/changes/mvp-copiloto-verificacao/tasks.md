# Tasks

Donos das tasks em aberto: **Vitor** 10, **Jhessica** 6, **Samara** 5, **Wingrid** 5, **Breno** 5.

Divisão de 24/09/2026, por papel do artigo de MLOps (Kreuzberger et al.,
2023): R1 Breno, R2 Wingrid, R3 modelagem Vitor, R3 avaliação Jhessica,
R4+R6+R7 Samara. O nome em negrito no início de cada task em aberto é o dono
único dela. Task com dois donos é task sem dono.


## 1. Corpus e recuperação
- [ ] 1.1 **Samara** Definir esquema de indexação do recorte de saúde do FactCenter (4.063 checagens)
- [ ] 1.2 **Samara** Indexar FACTCK.BR como fonte auxiliar, com rótulos normalizados
- [ ] 1.3 **Wingrid** Definir lista de fontes oficiais aceitas (Ministério da Saúde, Fiocruz, Anvisa)
- [ ] 1.4 **Samara** Implementar recuperação com prioridade de idioma (PT-BR antes de EN)
- [ ] 1.5 **Vitor** Definir e calibrar o limiar de `evidência insuficiente`
- [ ] 1.6 **Samara** Implementar ancoragem trecho a afirmação e descarte de afirmação sem trecho

## 2. Verificação e veredito
- [ ] 2.1 **Vitor** Prompt de extração de alegação, com seleção quando há várias
- [ ] 2.2 **Vitor** Prompt de classificação nos quatro rótulos
- [ ] 2.3 **Vitor** Guarda contra veredito por conhecimento paramétrico
- [ ] 2.4 **Jhessica** Teste de regressão com itens verdadeiros contra-intuitivos
- [ ] 2.5 **Vitor** Prompt de decomposição fato / evidência / opinião, com teste do caso
      misto e do fato verdadeiro que sustenta conclusão que não decorre

## 3. Resposta formativa
- [ ] 3.1 **Vitor** Fechar o catálogo de 6 a 8 técnicas, com nome e descrição em linguagem cotidiana
- [ ] 3.2 **Vitor** Prompt da estrutura de quatro blocos
- [ ] 3.3 **Vitor** Validação automática: rótulo usado pertence ao catálogo
- [ ] 3.4 **Vitor** Verificação de que a alegação falsa nunca abre a resposta sem marcação

## 4. Fronteira de saúde
- [ ] 4.1 **Vitor** Classificador de pedido de conduta clínica individual
- [ ] 4.2 **Breno** Respostas de redirecionamento, incluindo caso de sinal de risco
- [ ] 4.3 **Jhessica** Bateria de testes adversariais de pedido de conduta

## 5. Interface
- [ ] 5.1 **Wingrid** Camada visível e camada de detalhe
- [ ] 5.2 **Jhessica** Checklist de acessibilidade: contraste, fonte, alvo de toque, ação primária
- [ ] 5.3 **Wingrid** Fluxo de primeira verificação sem cadastro
- [ ] 5.4 **Jhessica** Verificação de legibilidade da camada visível (limite de palavras e frases)

## 6. Avaliação
- [ ] 6.1 **Jhessica** Curar 20 a 30 casos, com no mínimo 4 verdadeiros contra-intuitivos
- [ ] 6.2 **Jhessica** Configurar 4 a 6 itens-armadilha
- [ ] 6.3 **Breno** Redigir TCLE e roteiro de debriefing
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
