# Tasks — add-ampliacao-corpus-ptbr

Fase Investigate. Sucede `add-tratamento-datasets-ptbr`. Nenhum download começa
antes da task 0.1.

Emendado em 17/09/2026 para incluir o acervo de circulação (corpus de Telegram
antivacina). Blocos 6 a 10 foram renumerados.

**Total: 55 tasks.**

## 0. Pré-condição

- [x] 0.1 Confirmar que `add-tratamento-datasets-ptbr` está aplicado, com o
      contrato de leitura e o verificador de integridade textual funcionando;
      verificar rodando o verificador sobre um derivado PT-BR existente e obter
      resultado registrado

## 1. Portão de medição do índice

Este bloco vem antes da aquisição de propósito: se o índice não se sustentar,
cai aqui, antes de qualquer trabalho de integração.

- [x] 1.1 Obter chave da Fact Check Tools API e confirmar acesso ao
      `claims:search`, verificando retorno não vazio para uma consulta de
      controle com `languageCode=pt`
- [x] 1.2 Medir o retorno para saúde em `pt`: contagem por ano e por agência
      sobre um conjunto de termos de pauta, verificando que a contagem está
      registrada em arquivo e não apenas em saída de terminal
- [x] 1.3 Decidir manter ou descartar `indice-checagens-recentes` contra o
      limiar da Open Question do design; verificar que a decisão e o motivo
      estão registrados, e que o descarte, se houver, remove a capability da
      proposal e das specs — **mantida** em 19/09/2026, decisão 11 do
      `design.md`: 928 checagens, 525 posteriores a 2021, e a Qdenga tem 8 no
      índice contra zero no corpus

## 2. Aquisição e conferência de licença

- [x] 2.1 Conferir a licença da FakeRecogna 2.0 na fonte primária dos autores,
      não no cartão do HuggingFace; verificar que a fonte conferida está citada
      e que divergência com o agregador, se houver, virou caveat — feito em
      19/09/2026, decisão 12 do `design.md`. Ressalva registrada: `recogna-nlp`
      no HuggingFace **é** a organização dos autores, não agregador; a
      divergência real é entre o repositório da v1, sem licença, e o cartão da
      2.0, com MIT
- [x] 2.2 Conferir a licença do WhaVax no registro do Zenodo; verificar que o
      texto da licença está versionado junto da base — Zenodo `18190030`,
      CC BY 4.0, e o texto integral versionado em
      `01_nucleo_metodologico/whavax/LICENSE-CC-BY-4.0.txt`
- [x] 2.3 Baixar a variante **extrativa** da FakeRecogna 2.0 e gerar checksum;
      verificar que a contagem de itens bate com a declarada pela fonte, e
      registrar divergência se não bater
- [x] 2.4 Baixar o WhaVax e gerar checksum; verificar que os campos de anotação
      por anotador estão presentes, e não apenas o rótulo agregado
- [x] 2.5 Conferir a licença do corpus de Telegram no depósito do REDU, não no
      arXiv; verificar que o registro declara CC BY-NC 4.0 e que a condição de
      acesso do `.jsonl` de texto é aberta, distinta da da mídia — feito em
      19/09/2026, DOI `10.25824/redu/5JIVDT`: CC BY-NC 4.0 confirmada, `.jsonl`
      de 3,4 GB com acesso público, 5,5 TB de mídia com acesso restrito por
      acordo assinado. Decisão 13 do `design.md`
- [x] 2.6 Baixar apenas `telegram-vaccine-info-disorder-dataset-2020-2025.jsonl`
      (3,6 GB) e o `readme.pdf` do depósito, e gerar checksum; verificar que
      nenhum arquivo de mídia foi baixado e que a contagem de linhas bate com os
      3.998.633 posts declarados, registrando divergência se não bater
- [x] 2.7 Atualizar `.gitignore` para os brutos novos, incluindo o `.jsonl` de
      3,6 GB; verificar com `git status` que nenhum arquivo grande entra no
      índice do git

## 3. Medição de cobertura

- [x] 3.1 Medir a janela real da FakeRecogna 2.0 sobre o arquivo baixado:
      mínimo, máximo e distribuição por ano; verificar que o resultado é
      reproduzível por reexecução do script
- [x] 3.2 Rodar a busca de termos de pauta sobre a 2.0 (`qdenga`, `mpox`,
      `oropouche`, `semaglutida` e os demais do change anterior); verificar que
      a contagem por termo está registrada, inclusive os zeros
- [x] 3.3 Medir a janela e a distribuição por ano do WhaVax; verificar que o
      período declarado pelos autores e o medido constam lado a lado
- [x] 3.4 Medir o corpus de Telegram por leitura em streaming: janela real,
      distribuição por mês, contagem de canais distintos e proporção de
      `is_vaccine_related`; verificar que a medição roda sem carregar o arquivo
      inteiro em memória e que o resultado é reproduzível por reexecução
- [x] 3.5 Rodar sobre o corpus de Telegram a mesma busca de termos de pauta das
      tasks 3.2 (`qdenga`, `mpox`, `oropouche`, `semaglutida` e demais);
      verificar que a contagem por termo está registrada, inclusive os zeros, e
      que os termos de 2022 em diante são comparados contra o zero do acervo
      antigo
- [x] 3.6 Medir as lacunas declaradas pelos autores sobre o arquivo baixado —
      reações ausentes antes de 30/12/2021 e meses com queda abrupta por canal
      apagado; verificar que a lista de lacunas é a medida, não a copiada do
      artigo

## 4. Substituição da FakeRecogna v1

- [x] 4.1 Registrar que a amostra da v1 não sofreu curadoria nem tratamento —
      confirmado pelo grupo em 10/09/2026 — de modo que a única perda da
      substituição é a reprodutibilidade da seleção com semente; verificar por
      inspeção do registro em `FONTES.md`
- [x] 4.2 Regerar `fakerecogna_subset_saude_ciencia.csv` a partir da 2.0 por
      script versionado; verificar a contagem do subset e o critério de filtro
      aplicado
- [x] 4.3 Regerar a amostra estratificada de estímulos a partir do subset novo;
      verificar que o script e a semente estão versionados
- [x] 4.4 Declarar a transformação de texto da 2.0 por classe, nomeando o método
      e identificando os itens transformados por consulta; verificar que a base
      não aparece em nenhuma lista de fonte de trecho citado
- [x] 4.5 Remover a v1 e seus derivados do repositório; verificar por busca do
      nome da base que as ocorrências restantes são apenas as do registro de
      substituição
- [x] 4.6 Registrar a substituição em `FONTES.md` com base removida, base nova,
      data e motivo, declarando a perda da seleção com semente da v1; verificar
      por inspeção do arquivo
- [x] 4.7 Atualizar `SHA256SUMS`, `README.md` e `relatorio.json`; verificar que
      os checksums conferem contra os arquivos presentes
- [x] 4.8 Baixar a pendência de licença da FakeRecogna em `FONTES.md`; verificar
      que a seção de pendências lista apenas o PUBHEALTH

## 5. Integração do WhaVax

- [x] 5.1 Acomodar o WhaVax em `01_nucleo_metodologico/whavax/` com licença e
      citação; verificar que a estrutura segue a das demais bases do núcleo
- [x] 5.2 Registrar a proveniência da anotação — número de anotadores,
      qualificação, regra de agregação e concordância medida; verificar que
      consta no pacote, e não apenas por referência ao artigo
- [x] 5.3 Isolar a faixa de empate como classe própria, recuperável por consulta;
      verificar que a contagem de empates bate com a declarada pelos autores —
      **salva em 19/09/2026:** o pacote publica o voto por anotador (`av1_desinfo`
      a `av4_desinfo`), então o empate é recuperável. Medidos **84 empates 2-2**,
      exatamente o declarado pelos autores
- [x] 5.4 Registrar o uso vedado (treino de classificador de veredito) e os usos
      permitidos; verificar por inspeção do README da base
- [x] 5.5 Registrar o caveat de viés de amostra declarado pelos autores e o
      período de validade do rótulo; verificar por inspeção

## 6. Integração do acervo de circulação

- [x] 6.1 Criar a camada `04_acervo_circulacao/telegram_antivacina_br/` com a
      licença CC BY-NC 4.0, o `readme.pdf` do depósito e a citação com DOI;
      verificar que a estrutura segue a das demais camadas do pacote
- [x] 6.2 Registrar a proveniência do rótulo `is_vaccine_related` — modelo
      Sabiá-3, método por prompt, F1 de 0,90 sobre 600 posts anotados;
      verificar que consta no README da base como rótulo derivado, e não como
      classificação verificada
- [x] 6.3 Registrar o critério de seleção dos 119 canais e o viés de amostra que
      ele produz, com a vedação explícita de leitura de prevalência; verificar
      por inspeção do README da base
- [x] 6.4 Gerar os derivados agregados por script versionado — contagem por mês,
      por canal e frequência de termo de pauta; verificar por inspeção do
      arquivo gerado que nenhuma coluna contém texto de post nem identificador
      de autor
- [x] 6.5 Verificar por busca no repositório que nenhum texto de post individual
      e nenhum `user_id` foi versionado, inclusive em amostras de exemplo
      dentro de documentação
- [x] 6.6 Registrar o uso vedado (fonte de citação sobre o mérito, veredito por
      proxy de canal, estimativa de prevalência, re-identificação) e os usos
      permitidos; verificar por inspeção do README da base
- [x] 6.7 Propagar a cláusula não comercial e a atribuição a cada derivado
      gerado; verificar que ambas constam no cabeçalho do derivado ou no README
      que o acompanha

## 7. Construção do índice

Executar apenas se a task 1.3 decidiu manter a capability.

- [x] 7.1 Escrever o coletor com paginação e os nove campos do ClaimReview;
      verificar que nenhum campo de texto de artigo é gravado
- [x] 7.2 Gerar o snapshot com data de corte e parâmetros de consulta
      registrados; verificar que a reexecução produz snapshot com data distinta
      e mesmos parâmetros
- [x] 7.3 Preservar a grafia original do veredito da agência e marcar como
      derivação qualquer mapeamento para o vocabulário interno; verificar que o
      veredito original permanece recuperável no arquivo
- [x] 7.4 Documentar as agências alcançadas e a contagem por ano; verificar que
      a lista é a medida, não a esperada

## 8. Declaração de cobertura em quatro níveis

- [x] 8.1 Reescrever a declaração de cobertura separando os quatro níveis —
      texto integral, texto transformado, circulação e índice de localização;
      verificar que cada base do acervo tem janela medida, que o índice tem data
      de corte e que consta, por base, do que o texto é evidência
- [x] 8.2 Especificar as três respostas de lacuna com um caso de teste cada:
      pauta com checagem só no índice, pauta sem correspondência, pauta
      posterior a ambas as datas de corte; verificar que nenhuma colapsa em
      `evidência insuficiente`
- [x] 8.3 Verificar que nenhum item do índice nem do acervo de circulação está
      referenciado como fonte de
      trecho citado, por busca nos artefatos que alimentam citação
- [x] 8.4 Verificar que a FakeRecogna 2.0 conta para a janela temporal mas não
      para o nível citável, e que nenhum texto transformado alcança citação nem
      é oferecido como estímulo sem a transformação declarada

- [x] 8.5 Verificar que o acervo de circulação conta para a janela temporal e
      não para o nível citável, e que correspondência apenas nele não resolve
      nenhuma das três respostas de lacuna
- [x] 8.6 Verificar que cada um dos quatro níveis muda ao menos uma resposta do
      sistema, com o caso que a demonstra; nível que não mudar nenhuma sai da
      declaração, com o motivo registrado

## 9. Reconciliação com `add-tratamento-datasets-ptbr`

- [x] 9.1 **Reescrita, premissa derrubada em 19/09/2026 e executada na forma
      correta:** a 2.0 entra como banco de estímulos com rótulo binário, jamais
      como fonte de veredito graduado — registrado em `FONTES.md`, no catálogo
      de leitura e em `fakerecogna2_transformacao.json`. O mapa de veredito
      versão 1.0.0 segue com as 19 chaves das seis agências do FactCenter,
      porque não há nada a absorver. Texto original abaixo, preservado:
      ~~Absorver os três vocabulários de agência novos da 2.0 no mapa.~~ A 2.0
      não traz vocabulário de veredito: o rótulo é binário (`Label` 0/1), e as
      oito colunas não incluem campo de veredito textual. Não há três
      vocabulários a absorver; há três **agências** novas (AFP Checamos,
      E-farsas, UOL Confere) sem texto de veredito. O que resta fazer é
      registrar que a 2.0 entra como banco de estímulos e nunca como fonte de
      veredito graduado. Ver decisão 12 do `design.md`
- [x] 9.2 Atualizar as tasks 4.1 a 4.4 daquele change, que este desloca;
      verificar que o texto atualizado não afirma a janela 2013–2021 como
      corrente — **não desloca.** A janela 2013–2021 continua corrente para o
      nível citável, que é o único que `frescor-corpus` governa. As bases novas
      entram em níveis não citáveis, e a declaração de quatro níveis
      (`declaracao_cobertura_quatro_niveis.json`) é quem reconcilia as janelas.
      Nenhuma das tasks 4.1 a 4.4 daquele change afirma coisa que deixou de ser
      verdade
- [x] 9.3 Revisar a task 2.8 daquele change (carência de itens `verdadeiro`)
      contra o balanço da 2.0; verificar que o caveat reflete a base nova — a
      2.0 tem 26.400 itens `real`, mas **não resolve a carência**: o rótulo é
      binário de coleta, não veredito de agência, e o texto da classe real vem
      sumarizado. Continua valendo que o corpus de checagem tem 21 itens
      `verdadeiro` em 4.063 e que a coleta desses itens é trabalho manual à
      parte. O caveat foi atualizado com o motivo
- [x] 9.4 Estender o verificador de `integridade-textual` daquele change para
      distinguir perda de caractere de texto transformado na origem; verificar
      que ele reprova a 2.0 como fonte de citação sem reprová-la como estímulo
- [x] 9.5 Estender o contrato de leitura daquele change para leitura em
      streaming por linha de arquivo `.jsonl` que não cabe em memória; verificar
      rodando sobre o corpus de Telegram sem carregá-lo inteiro

## 10. Fechamento

- [x] 10.1 Confirmar que nenhum derivado remanescente aponta para base removida e
      que nenhuma referência órfã sobreviveu, por busca nos quatro arquivos de
      metadado
- [x] 10.2 Promover `frescor-corpus` para `openspec/specs/` via `/opsx:sync` a
      partir de `add-tratamento-datasets-ptbr`; verificar que
      `openspec validate --strict` deixa de emitir o aviso de
      `target spec does not exist` — feito em 19/09/2026. A promoção expôs um
      defeito real: o delta deste change omitia o cenário «Alegação sobre pauta
      posterior ao corpus», que a spec principal tem, e `MODIFIED` substitui o
      bloco inteiro. Cenário reposto
- [x] 10.3 `openspec validate add-ampliacao-corpus-ptbr --strict` limpo
