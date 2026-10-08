# Gerador de Modelo

Escolha e chamada do modelo de linguagem que executa as etapas de fronteira,
extração, decomposição, guarda e resposta.

## ADDED Requirements

### Requirement: Escolha do gerador por variável de ambiente

O servidor SHALL ler o gerador da variável `DONA_CHECA_GERADOR`, com valores
`deepseek` ou `ollama`. Sem a variável, o gerador SHALL ser `deepseek` no modo
`uso` e `ollama` no modo `piloto`. O servidor MUST NOT iniciar com valor
inválido. O gerador MUST NOT poder ser alterado pela página, pela URL ou por
qualquer requisição.

#### Scenario: Padrão no modo uso
- **GIVEN** `DONA_CHECA_MODO=uso`, `DEEPSEEK_API_KEY` definida e
  `DONA_CHECA_GERADOR` ausente
- **WHEN** o servidor é iniciado
- **THEN** as etapas chamam a API da DeepSeek

#### Scenario: Padrão no modo piloto
- **GIVEN** `DONA_CHECA_MODO=piloto` e `DONA_CHECA_GERADOR` ausente
- **WHEN** o servidor é iniciado
- **THEN** as etapas chamam o Ollama local

#### Scenario: Valor inválido
- **GIVEN** `DONA_CHECA_GERADOR=gpt`
- **WHEN** o servidor é iniciado
- **THEN** o processo termina com erro que nomeia a variável e os valores aceitos

### Requirement: Chave da API fora do repositório

Com gerador `deepseek`, o servidor SHALL ler a chave de `DEEPSEEK_API_KEY` e
MUST NOT iniciar sem ela. A chave MUST NOT aparecer em arquivo versionado, em
log ou em mensagem de erro. O arquivo `.env` SHALL continuar ignorado pelo `.gitignore`.

#### Scenario: Chave ausente
- **GIVEN** gerador `deepseek` e `DEEPSEEK_API_KEY` ausente
- **WHEN** o servidor é iniciado
- **THEN** o processo termina com erro que nomeia `DEEPSEEK_API_KEY`

#### Scenario: Chave recusada
- **GIVEN** uma chave que a API recusa com 401
- **WHEN** uma mensagem é enviada
- **THEN** a página mostra o texto `erro` de "Erro sem vazamento"
- **AND** o log tem a etapa, o tipo do erro e o status 401, sem a chave e sem o texto da mensagem

### Requirement: Chamada à API com saída JSON e sem raciocínio

Com gerador `deepseek`, cada etapa SHALL pedir saída JSON, raciocínio
desligado, temperatura 0.2 e no máximo 1200 tokens de saída, e SHALL devolver
às etapas o texto do campo `content`, como `chat_ollama` já devolve. O modelo
SHALL vir de `DEEPSEEK_MODELO`, com padrão `deepseek-v4-pro`.

#### Scenario: Pedido montado
- **GIVEN** a API simulada que registra o corpo recebido
- **WHEN** uma etapa chama o gerador com prompt de sistema e mensagem
- **THEN** o corpo tem `response_format` `json_object`, `thinking` `disabled`, `temperature` 0.2 e `max_tokens` 1200
- **AND** as mensagens têm o papel `system` e o papel `user`, nessa ordem

### Requirement: Uma nova tentativa em falha passageira

Com gerador `deepseek`, a resposta 429, 500, 502 ou 503, ou a resposta com
`content` vazio, SHALL causar uma nova tentativa, uma só. A segunda falha, e
qualquer outro status de erro, SHALL virar exceção, que a interface trata
como "Erro sem vazamento".

#### Scenario: Conteúdo vazio uma vez
- **GIVEN** a API simulada que devolve `content` vazio e depois um JSON válido
- **WHEN** uma etapa chama o gerador
- **THEN** a etapa recebe o JSON válido

#### Scenario: Falha repetida
- **GIVEN** a API simulada que devolve 503 duas vezes
- **WHEN** uma etapa chama o gerador
- **THEN** o gerador levanta exceção depois de duas tentativas

### Requirement: Critério de aceite da troca

O gerador `deepseek` SHALL ser o padrão do modo `uso` somente depois de duas
bancadas reais seguidas, completas e com o mesmo código, que cumpram, cada
uma, três condições. Primeira: nenhuma falha eliminatória, isto é, etapa em
erro, rótulo da guarda diferente do esperado, fronteira errada, mito citado
sem marcação de falso ou resposta que insinua veredito sem evidência.
Segunda: no máximo 3 casos com as demais falhas (tamanho, outros defeitos da
resposta, acerto de etapa). Terceira: mediana do tempo total por caso
completo de no máximo metade da mediana de uma bancada `ollama` do mesmo dia.
Toda falha de mito SHALL ser conferida à mão; falso positivo do verificador
SHALL ser corrigido com teste num change, e a rodada SHALL ser refeita. O
relatório da bancada SHALL registrar o gerador, o nome do modelo devolvido pela
API, os casos por tipo de falha e o resultado do critério.

#### Scenario: Rodada que não conta
- **GIVEN** uma bancada `deepseek` com 27/27 casos, exceto um rótulo `falso` onde o esperado era evidência insuficiente
- **WHEN** o critério é conferido
- **THEN** a rodada não conta para a troca

#### Scenario: Falhas de tamanho dentro do limite
- **GIVEN** uma bancada `deepseek` em que só três casos falham, todos por camada visível acima de 120 palavras
- **WHEN** o critério é conferido
- **THEN** a rodada conta para a troca

#### Scenario: Mito repetido
- **GIVEN** uma bancada `deepseek` em que um caso falha por "A mensagem promete curar câncer com casca de fruta", sem negação
- **WHEN** o critério é conferido
- **THEN** a rodada não conta para a troca

#### Scenario: Relatório comparável
- **GIVEN** `python -m bancada rodar --gerador deepseek`
- **WHEN** o relatório é gravado
- **THEN** `parametros` contém `gerador` e `modelo`
- **AND** cada etapa tem `segundos`

#### Scenario: Custo registrado
- **GIVEN** `python -m bancada rodar --gerador deepseek`
- **WHEN** o relatório é gravado
- **THEN** `parametros.uso` traz chamadas e tokens de entrada, de entrada em cache e de saída, como a API informou

### Requirement: Minimização antes do envio

Com gerador `deepseek`, o texto da pessoa SHALL ter telefone, CPF e e-mail
trocados pelos marcadores `[telefone]`, `[cpf]` e `[email]` antes de qualquer
envio ao gerador. A troca MUST NOT alterar o texto mostrado à pessoa.

#### Scenario: Telefone na mensagem
- **GIVEN** gerador `deepseek` e a mensagem "Me liga no (11) 98765-4321, chá de boldo cura hepatite"
- **WHEN** a verificação roda
- **THEN** nenhum pedido ao gerador contém "98765-4321"
- **AND** o pedido contém "[telefone]"
