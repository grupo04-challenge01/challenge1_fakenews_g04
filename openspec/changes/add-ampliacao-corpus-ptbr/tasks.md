# Tasks — add-ampliacao-corpus-ptbr

Fase Investigate. Sucede `add-tratamento-datasets-ptbr`. Nenhum download começa
antes da task 0.1.

## 0. Pré-condição

- [ ] 0.1 Confirmar que `add-tratamento-datasets-ptbr` está aplicado, com o
      contrato de leitura e o verificador de integridade textual funcionando;
      verificar rodando o verificador sobre um derivado PT-BR existente e obter
      resultado registrado

## 1. Portão de medição do índice

Este bloco vem antes da aquisição de propósito: se o índice não se sustentar,
cai aqui, antes de qualquer trabalho de integração.

- [ ] 1.1 Obter chave da Fact Check Tools API e confirmar acesso ao
      `claims:search`, verificando retorno não vazio para uma consulta de
      controle com `languageCode=pt`
- [ ] 1.2 Medir o retorno para saúde em `pt`: contagem por ano e por agência
      sobre um conjunto de termos de pauta, verificando que a contagem está
      registrada em arquivo e não apenas em saída de terminal
- [ ] 1.3 Decidir manter ou descartar `indice-checagens-recentes` contra o
      limiar da Open Question do design; verificar que a decisão e o motivo
      estão registrados, e que o descarte, se houver, remove a capability da
      proposal e das specs

## 2. Aquisição e conferência de licença

- [ ] 2.1 Conferir a licença da FakeRecogna 2.0 na fonte primária dos autores,
      não no cartão do HuggingFace; verificar que a fonte conferida está citada
      e que divergência com o agregador, se houver, virou caveat
- [ ] 2.2 Conferir a licença do WhaVax no registro do Zenodo; verificar que o
      texto da licença está versionado junto da base
- [ ] 2.3 Baixar a variante **extrativa** da FakeRecogna 2.0 e gerar checksum;
      verificar que a contagem de itens bate com a declarada pela fonte, e
      registrar divergência se não bater
- [ ] 2.4 Baixar o WhaVax e gerar checksum; verificar que os campos de anotação
      por anotador estão presentes, e não apenas o rótulo agregado
- [ ] 2.5 Atualizar `.gitignore` para os brutos novos; verificar com
      `git status` que nenhum arquivo grande entra no índice do git

## 3. Medição de cobertura

- [ ] 3.1 Medir a janela real da FakeRecogna 2.0 sobre o arquivo baixado:
      mínimo, máximo e distribuição por ano; verificar que o resultado é
      reproduzível por reexecução do script
- [ ] 3.2 Rodar a busca de termos de pauta sobre a 2.0 (`qdenga`, `mpox`,
      `oropouche`, `semaglutida` e os demais do change anterior); verificar que
      a contagem por termo está registrada, inclusive os zeros
- [ ] 3.3 Medir a janela e a distribuição por ano do WhaVax; verificar que o
      período declarado pelos autores e o medido constam lado a lado

## 4. Substituição da FakeRecogna v1

- [ ] 4.1 Registrar que a amostra da v1 não sofreu curadoria nem tratamento —
      confirmado pelo grupo em 10/09/2026 — de modo que a única perda da
      substituição é a reprodutibilidade da seleção com semente; verificar por
      inspeção do registro em `FONTES.md`
- [ ] 4.2 Regerar `fakerecogna_subset_saude_ciencia.csv` a partir da 2.0 por
      script versionado; verificar a contagem do subset e o critério de filtro
      aplicado
- [ ] 4.3 Regerar a amostra estratificada de estímulos a partir do subset novo;
      verificar que o script e a semente estão versionados
- [ ] 4.4 Declarar a transformação de texto da 2.0 por classe, nomeando o método
      e identificando os itens transformados por consulta; verificar que a base
      não aparece em nenhuma lista de fonte de trecho citado
- [ ] 4.5 Remover a v1 e seus derivados do repositório; verificar por busca do
      nome da base que as ocorrências restantes são apenas as do registro de
      substituição
- [ ] 4.6 Registrar a substituição em `FONTES.md` com base removida, base nova,
      data e motivo, declarando a perda da seleção com semente da v1; verificar
      por inspeção do arquivo
- [ ] 4.7 Atualizar `SHA256SUMS`, `README.md` e `relatorio.json`; verificar que
      os checksums conferem contra os arquivos presentes
- [ ] 4.8 Baixar a pendência de licença da FakeRecogna em `FONTES.md`; verificar
      que a seção de pendências lista apenas o PUBHEALTH

## 5. Integração do WhaVax

- [ ] 5.1 Acomodar o WhaVax em `01_nucleo_metodologico/whavax/` com licença e
      citação; verificar que a estrutura segue a das demais bases do núcleo
- [ ] 5.2 Registrar a proveniência da anotação — número de anotadores,
      qualificação, regra de agregação e concordância medida; verificar que
      consta no pacote, e não apenas por referência ao artigo
- [ ] 5.3 Isolar a faixa de empate como classe própria, recuperável por consulta;
      verificar que a contagem de empates bate com a declarada pelos autores
- [ ] 5.4 Registrar o uso vedado (treino de classificador de veredito) e os usos
      permitidos; verificar por inspeção do README da base
- [ ] 5.5 Registrar o caveat de viés de amostra declarado pelos autores e o
      período de validade do rótulo; verificar por inspeção

## 6. Construção do índice

Executar apenas se a task 1.3 decidiu manter a capability.

- [ ] 6.1 Escrever o coletor com paginação e os nove campos do ClaimReview;
      verificar que nenhum campo de texto de artigo é gravado
- [ ] 6.2 Gerar o snapshot com data de corte e parâmetros de consulta
      registrados; verificar que a reexecução produz snapshot com data distinta
      e mesmos parâmetros
- [ ] 6.3 Preservar a grafia original do veredito da agência e marcar como
      derivação qualquer mapeamento para o vocabulário interno; verificar que o
      veredito original permanece recuperável no arquivo
- [ ] 6.4 Documentar as agências alcançadas e a contagem por ano; verificar que
      a lista é a medida, não a esperada

## 7. Declaração de cobertura em dois níveis

- [ ] 7.1 Reescrever a declaração de cobertura separando acervo com texto
      integral e índice de localização; verificar que cada base do acervo tem
      janela medida e que o índice tem data de corte
- [ ] 7.2 Especificar as três respostas de lacuna com um caso de teste cada:
      pauta com checagem só no índice, pauta sem correspondência, pauta
      posterior a ambas as datas de corte; verificar que nenhuma colapsa em
      `evidência insuficiente`
- [ ] 7.3 Verificar que nenhum item do índice está referenciado como fonte de
      trecho citado, por busca nos artefatos que alimentam citação
- [ ] 7.4 Verificar que a FakeRecogna 2.0 conta para a janela temporal mas não
      para o nível citável, e que nenhum texto transformado alcança citação nem
      é oferecido como estímulo sem a transformação declarada

## 8. Reconciliação com `add-tratamento-datasets-ptbr`

- [ ] 8.1 Absorver os três vocabulários de agência novos da 2.0 no mapa de
      rótulos daquele change; verificar que os nove vocabulários têm destino
      definido e que nenhum cai em rótulo padrão silencioso
- [ ] 8.2 Atualizar as tasks 4.1 a 4.4 daquele change, que este desloca;
      verificar que o texto atualizado não afirma a janela 2013–2021 como
      corrente
- [ ] 8.3 Revisar a task 2.8 daquele change (carência de itens `verdadeiro`)
      contra o balanço da 2.0; verificar que o caveat reflete a base nova
- [ ] 8.4 Estender o verificador de `integridade-textual` daquele change para
      distinguir perda de caractere de texto transformado na origem; verificar
      que ele reprova a 2.0 como fonte de citação sem reprová-la como estímulo

## 9. Fechamento

- [ ] 9.1 Confirmar que nenhum derivado remanescente aponta para base removida e
      que nenhuma referência órfã sobreviveu, por busca nos quatro arquivos de
      metadado
- [ ] 9.2 Promover `frescor-corpus` para `openspec/specs/` via `/opsx:sync` a
      partir de `add-tratamento-datasets-ptbr`; verificar que
      `openspec validate --strict` deixa de emitir o aviso de
      `target spec does not exist`
- [ ] 9.3 `openspec validate add-ampliacao-corpus-ptbr --strict` limpo
