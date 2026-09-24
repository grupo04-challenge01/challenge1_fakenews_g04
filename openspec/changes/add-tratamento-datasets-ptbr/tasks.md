# Tasks — add-tratamento-datasets-ptbr

Donos das tasks em aberto: **Samara** 1 (3.5), **Jhessica** 1 (5.4).

Divisão de 24/09/2026, por papel do artigo de MLOps (Kreuzberger et al.,
2023): R1 Breno, R2 Wingrid, R3 modelagem Vitor, R3 avaliação Jhessica,
R4+R6+R7 Samara. O nome em negrito no início de cada task em aberto é o dono
único dela. Task com dois donos é task sem dono.


Fase Investigate. Bloqueia as tasks 1.1 a 1.6 de `mvp-copiloto-verificacao`.

## 1. Contrato de leitura

- [x] 1.1 Escrever o leitor do corpus com delimitador `;` e quoting que preserve
      newline interno, conferindo 4.063 registros
- [x] 1.2 Fazer o mesmo para os demais derivados, registrando o formato real de
      cada arquivo (o nome `.csv` não descreve o conteúdo em todos)
- [x] 1.3 Teste que falha se a contagem de registros divergir da declarada

## 2. Normalização de veredito

- [x] 2.1 Parser do campo `rating` como lista, preservando a grafia original
- [x] 2.2 Levantar os 285 valores distintos agrupados por agência
- [x] 2.3 Escrever o mapa versionado valor → rótulo, com `nao_mapeavel` explícito
- [x] 2.4 Registrar a entrada `boato` com o que se perde ao equipará-la a `falso`
- [x] 2.5 Interromper o processamento em valor fora do mapa, com teste
- [x] 2.6 Marcar os 250 registros de veredito divergente como `misto`
- [x] 2.7 Excluir do banco de estímulos os compilados com mais de vinte vereditos
- [x] 2.8 Registrar como caveat a carência de itens `verdadeiro` (21 em 4.063)

## 3. Integridade textual

- [x] 3.1 Verificador de perda de caractere por classe, rodando por arquivo.
      Critério: ausência total **não** basta. `factcenter_subset_saude.csv` tem
      zero `Ü` em 21,5 milhões de caracteres porque o trema foi abolido em 1990,
      não por corrupção — e o `ü` minúsculo aparece 57 vezes. O que separa os
      dois casos é a maiúscula com zero ocorrências **e** minúscula frequente:
      em `factckbr_normalizado.csv` sete letras batem nisso (`ã` 3.625 contra
      `Ã` 0), aqui nenhuma. Sem essa precisão o verificador reprova corpus
      íntegro e bloqueia o índice. Implementação de referência em
      `prototipo/rag/corpus.py`, e a capability `integridade-textual` precisa
      absorver a precisão no texto do requirement.
- [x] 3.2 Rodar em todos os derivados PT-BR e registrar o resultado por arquivo
- [x] 3.3 Reprovar `factckbr_normalizado.csv` para citação e registrar o caveat
- [x] 3.4 Corrigir a allowlist do `re_char()` em `update_factckbr.py`, ou
      substituí-la por normalização Unicode sem descarte
- [ ] 3.5 **Samara** Recoletar o FACTCK.BR pelos três feeds com o script reparado, e
      registrar a perda histórica como irreversível. **Reescrita em 19/09/2026.**
      O texto anterior — "regerar o derivado a partir da fonte, com a correção"
      — pedia o impossível: a perda de caractere já está no `FACTCKBR.tsv`
      distribuído (`Ã` = 0 contra `ã` = 3.625 **na própria fonte**), e nenhuma
      reexecução recupera o que não está no arquivo. O reparo da task 3.4 vale
      para coleta futura; o acervo de 1.313 alegações permanece reprovado para
      citação
- [x] 3.6 Teste de fidelidade: trecho citado idêntico ao texto de origem

## 4. Frescor

- [x] 4.1 Medir e declarar a cobertura: janela, concentração por ano, termos
      ausentes verificados por busca
- [x] 4.2 Versionar a declaração de cobertura como artefato reexecutável
- [x] 4.3 Especificar a resposta de lacuna de acervo, distinta de `evidência
      insuficiente`, com o caso Qdenga como teste
- [x] 4.4 Documentar o caminho de atualização nomeando as três agências
      alcançadas e as três não alcançadas
- [x] 4.5 Reparar o `update_factckbr.py` para pandas atual (`DataFrame.append`
      foi removido na versão 2.0)

## 5. Adaptação dos instrumentos em inglês

- [x] 5.1 Extrair as 20 perguntas do FakeHealth separadas pelos dois conjuntos
- [x] 5.2 Decidir entre adotar um conjunto ou mapear os dois, e registrar
- [x] 5.3 Adaptar cada critério para PT-BR com rubrica de três níveis
- [ ] 5.4 **Jhessica** Validar a rubrica contra casos brasileiros e remover o que não
      discrimina, com motivo. **Parcial em 19/09/2026:** as cinco remoções estão
      feitas e com motivo registrado, por argumento de unidade de análise. O
      proxy de cobertura de vocabulário foi tentado, medido e **reprovado** — sob
      qualquer piso único ele removeria `alarme` (0,039) e `linguagem` (0,029) e
      manteria `novidade` (0,063) e `custo` (0,051). A validação empírica da
      rubrica depende de anotação humana dos casos, que é de
      `avaliacao-instrumento` em `mvp-copiloto-verificacao`
- [x] 5.5 Montar o pool de few-shot em PT-BR a partir do corpus brasileiro
- [x] 5.6 Nomear em português os rótulos de força da afirmação, ligados ao
      catálogo de técnicas

## 6. Correções no portfólio de pesquisa

- [x] 6.1 Corrigir a afirmação de que o PUBHEALTH é majoritariamente falso: a
      classe majoritária é `true`, com cerca de 52% do treino
- [x] 6.2 Corrigir a contagem de critérios do FakeHealth: 20 em dois conjuntos,
      não 10
- [x] 6.3 Registrar os achados do corpus PT-BR como caveats do portfólio

## 7. Fechamento

- [x] 7.1 Conferir que nenhum arquivo reprovado está referenciado como fonte de
      citação
- [x] 7.2 `openspec validate add-tratamento-datasets-ptbr --strict` limpo
