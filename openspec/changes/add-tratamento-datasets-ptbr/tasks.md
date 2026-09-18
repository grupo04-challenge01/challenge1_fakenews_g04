# Tasks — add-tratamento-datasets-ptbr

Fase Investigate. Bloqueia as tasks 1.1 a 1.6 de `mvp-copiloto-verificacao`.

## 1. Contrato de leitura

- [ ] 1.1 Escrever o leitor do corpus com delimitador `;` e quoting que preserve
      newline interno, conferindo 4.063 registros
- [ ] 1.2 Fazer o mesmo para os demais derivados, registrando o formato real de
      cada arquivo (o nome `.csv` não descreve o conteúdo em todos)
- [ ] 1.3 Teste que falha se a contagem de registros divergir da declarada

## 2. Normalização de veredito

- [ ] 2.1 Parser do campo `rating` como lista, preservando a grafia original
- [ ] 2.2 Levantar os 285 valores distintos agrupados por agência
- [ ] 2.3 Escrever o mapa versionado valor → rótulo, com `nao_mapeavel` explícito
- [ ] 2.4 Registrar a entrada `boato` com o que se perde ao equipará-la a `falso`
- [ ] 2.5 Interromper o processamento em valor fora do mapa, com teste
- [ ] 2.6 Marcar os 250 registros de veredito divergente como `misto`
- [ ] 2.7 Excluir do banco de estímulos os compilados com mais de vinte vereditos
- [ ] 2.8 Registrar como caveat a carência de itens `verdadeiro` (21 em 4.063)

## 3. Integridade textual

- [ ] 3.1 Verificador de perda de caractere por classe, rodando por arquivo.
      Critério: ausência total **não** basta. `factcenter_subset_saude.csv` tem
      zero `Ü` em 21,5 milhões de caracteres porque o trema foi abolido em 1990,
      não por corrupção — e o `ü` minúsculo aparece 57 vezes. O que separa os
      dois casos é a maiúscula com zero ocorrências **e** minúscula frequente:
      em `factckbr_normalizado.csv` sete letras batem nisso (`ã` 3.625 contra
      `Ã` 0), aqui nenhuma. Sem essa precisão o verificador reprova corpus
      íntegro e bloqueia o índice. Implementação de referência em
      `prototipo/rag/corpus.py`, e a capability `integridade-textual` precisa
      absorver a precisão no texto do requirement.
- [ ] 3.2 Rodar em todos os derivados PT-BR e registrar o resultado por arquivo
- [ ] 3.3 Reprovar `factckbr_normalizado.csv` para citação e registrar o caveat
- [ ] 3.4 Corrigir a allowlist do `re_char()` em `update_factckbr.py`, ou
      substituí-la por normalização Unicode sem descarte
- [ ] 3.5 Regerar o derivado do FACTCK.BR a partir da fonte, com a correção
- [ ] 3.6 Teste de fidelidade: trecho citado idêntico ao texto de origem

## 4. Frescor

- [ ] 4.1 Medir e declarar a cobertura: janela, concentração por ano, termos
      ausentes verificados por busca
- [ ] 4.2 Versionar a declaração de cobertura como artefato reexecutável
- [ ] 4.3 Especificar a resposta de lacuna de acervo, distinta de `evidência
      insuficiente`, com o caso Qdenga como teste
- [ ] 4.4 Documentar o caminho de atualização nomeando as três agências
      alcançadas e as três não alcançadas
- [ ] 4.5 Reparar o `update_factckbr.py` para pandas atual (`DataFrame.append`
      foi removido na versão 2.0)

## 5. Adaptação dos instrumentos em inglês

- [ ] 5.1 Extrair as 20 perguntas do FakeHealth separadas pelos dois conjuntos
- [ ] 5.2 Decidir entre adotar um conjunto ou mapear os dois, e registrar
- [ ] 5.3 Adaptar cada critério para PT-BR com rubrica de três níveis
- [ ] 5.4 Validar a rubrica contra casos brasileiros e remover o que não
      discrimina, com motivo
- [ ] 5.5 Montar o pool de few-shot em PT-BR a partir do corpus brasileiro
- [ ] 5.6 Nomear em português os rótulos de força da afirmação, ligados ao
      catálogo de técnicas

## 6. Correções no portfólio de pesquisa

- [ ] 6.1 Corrigir a afirmação de que o PUBHEALTH é majoritariamente falso: a
      classe majoritária é `true`, com cerca de 52% do treino
- [ ] 6.2 Corrigir a contagem de critérios do FakeHealth: 20 em dois conjuntos,
      não 10
- [ ] 6.3 Registrar os achados do corpus PT-BR como caveats do portfólio

## 7. Fechamento

- [ ] 7.1 Conferir que nenhum arquivo reprovado está referenciado como fonte de
      citação
- [ ] 7.2 `openspec validate add-tratamento-datasets-ptbr --strict` limpo
