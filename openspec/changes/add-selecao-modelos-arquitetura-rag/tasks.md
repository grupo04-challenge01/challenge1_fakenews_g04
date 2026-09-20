# Tasks

## 1. Registro da decisão de modelo
- [x] 1.1 Redigir a tabela de três papéis (recuperação, geração, classificação
      auxiliar) com o critério de seleção de cada um
- [x] 1.2 Registrar o descarte do MedGemma citando model card oficial e a
      colisão com a task 2.3 de `mvp-copiloto-verificacao`
- [x] 1.3 Levantar candidatos de recuperação com desempenho medido em benchmark
      de português, com tamanho, licença e score anotados
- [x] 1.4 Levantar candidatos de geração, separando via local de via API
- [x] 1.5 Registrar a licença de cada modelo adotado, pelo nome, com a restrição
      encontrada
- [x] 1.6 Fechar a decisão local vs. API para o papel de geração e registrar em
      `design.md` como nota de decisão — local, Gemma 4 12B QAT q4_0, decisão 8
- [x] 1.7 Conferir a Prohibited Use Policy da Gemma 3 contra
      `fronteira-orientacao-saude`, caso a contingência do Gemma 3 seja acionada

## 2. Prova de conceito de recuperação
- [x] 2.1 Provisionar ambiente (fixar versão de Python, instalar dependências de
      embedding e de busca léxica) e registrar o que foi fixado — Python 3.14.6,
      `requirements-rag.txt` + `requirements-rag.lock.txt`, MPS ativo
- [x] 2.1b Abrir change de correção em `mvp-copiloto-verificacao` para o defeito
      da estrutura de quatro blocos sob `evidência insuficiente` (decisão 10)
      — aberto em 19/09/2026 como `fix-resposta-sem-evidencia`, com a proposal
      escrita. As specs delta ficam pendentes da decisão do grupo entre forma
      própria e catálogo condicional, registrada na proposal
- [x] 2.1c Registrar `think: false` como obrigatório em toda chamada ao gerador
      — medido: 3/3 respostas em 17 s vs 1/3 em 112 s com raciocínio ligado
- [x] 2.1d Documentar a sonda e os resultados no portfólio
      (`docs/investigate/sonda-gerador.md`, na nav do mkdocs)
- [x] 2.2 Construir as unidades de indexação a partir de
      `derivados/factcenter_subset_saude.csv`, preservando agência, data e URL
      — `prototipo/rag/unidades.py`; 4.063 registros → 5.090 unidades e 22.464
      fragmentos, 88 em quarentena; decisão 11 de `design.md`
- [x] 2.2b Levar a precisão do portão de acentuação (`Ü` ausente por ortografia,
      não por corrupção) à task 3.1 de `add-tratamento-datasets-ptbr`
- [x] 2.3 Implementar busca léxica sobre as unidades — `prototipo/rag/lexica.py`,
      BM25 Okapi sobre os fragmentos, índice em 2,1 s
- [x] 2.4 Implementar busca densa exata em memória, sem banco vetorial
      — `prototipo/rag/densa.py`, `multilingual-e5-base`, matriz 22.464 × 768
      em memória, produto escalar exato
- [x] 2.5 Implementar a fusão das duas listas — `prototipo/rag/hibrida.py`;
      combinação convexa de scores realçados contra o fundo da consulta, com RRF
      disponível para a comparação da task 3.1. Primeira versão anulava o braço
      denso; defeito medido e corrigido, decisão 11 de `design.md`
- [x] 2.6 Montar conjunto de 20 consultas de aferição a partir de casos reais do
      corpus, com o documento correto conhecido para cada uma

## 3. Medição e calibração
- [ ] 3.1 Medir recall das três configurações — só léxica, só densa, híbrida —
      sobre as 20 consultas de aferição
- [ ] 3.2 Registrar o resultado como evidência da decisão 4 de `design.md`,
      inclusive se ele contrariar a decisão
- [ ] 3.3 Comparar ao menos dois modelos de embedding sob o mesmo conjunto de
      aferição
- [ ] 3.4 Medir a latência de consulta de cada modelo comparado, separando custo
      de indexação de custo de consulta
- [ ] 3.5 Calibrar o limiar de `evidência insuficiente` sobre o score fundido,
      incluindo casos de pauta ausente do corpus
- [ ] 3.6 Documentar o conjunto de aferição e a calibração de forma reproduzível

## 4. Fronteira entre treino e recuperação
- [x] 4.1 Redigir a regra de fronteira em linguagem operacional, com os dois
      casos vedados nomeados
- [x] 4.2 Redigir o procedimento de auditoria de afirmação sem trecho de origem
- [x] 4.3 Registrar a sequência adotada (linha de base sem treino antes de
      qualquer fine-tuning) com o critério que autoriza o primeiro treino

## 5. Análise de sentimento
- [x] 5.1 Registrar o resultado da pesquisa: por que polaridade não entra no
      veredito, com os três motivos e as referências
- [x] 5.2 Propor os rótulos de emoção nomeada candidatos ao catálogo de técnicas,
      para consumo da task 3.1 de `mvp-copiloto-verificacao`, respeitando o
      orçamento de 6 a 8 rótulos já ocupado por técnicas não emocionais
- [x] 5.3 Levantar ferramentas de análise de emoção em PT-BR, com licença
- [x] 5.4 Redigir o teste dos dois casos cruzados: alegação verdadeira com carga
      emocional alta e alegação falsa em tom neutro

## 6. Fechamento
- [x] 6.1 Conferir que nenhuma decisão deste change contradiz
      `recuperacao-evidencia`, `verificacao-alegacao` ou
      `fronteira-orientacao-saude` — ver decisão 9 de `design.md`
- [x] 6.2 Registrar o change na tabela "Changes previstos" de
      `openspec/project.md`
- [x] 6.3 `openspec validate add-selecao-modelos-arquitetura-rag --strict` limpo
