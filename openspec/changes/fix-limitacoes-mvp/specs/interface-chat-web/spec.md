# Delta para Interface de Chat Web

## MODIFIED Requirements

### Requirement: Consentimento antes do envio ao serviço externo

Quando o gerador for `deepseek`, a página SHALL mostrar o texto
`termo-servico-externo` antes de liberar o campo de mensagem, com os botões
"Aceito" e "Não aceito", nenhum pré-selecionado. O campo de mensagem MUST NOT
aceitar envio antes de uma escolha. O servidor MUST NOT enviar texto ao
gerador remoto sem o campo `consentimento` igual à versão atual do termo no
pedido, e SHALL registrar no log a versão aceita, sem identificador de pessoa.
O aceite SHALL valer só para a página aberta: ao recarregar, o termo volta.
O termo SHALL aparecer em parágrafos curtos, um por assunto.

Com "Não aceito", a página SHALL mostrar o texto `recusa`. Quando o servidor
tiver alternativa local configurada (`DONA_CHECA_ALTERNATIVA_LOCAL=sim`), a
página SHALL mostrar o texto `recusa-local`, e as verificações dessa página
SHALL usar o gerador `ollama`.

##### Texto — termo-servico-externo
> Antes de começar, meu bem: para checar sua mensagem, eu envio o texto dela para a DeepSeek, um serviço de inteligência artificial localizado na China.
>
> Nós apagamos automaticamente números de telefone, CPF e e-mail antes de enviar. Porém, como nomes próprios no meio do texto não são apagados automaticamente, pedimos que você não inclua seu nome, telefone, CPF ou informações sobre sua saúde.
>
> A DeepSeek pode guardar esse texto pelo tempo que considerar necessário. A DeepSeek pode utilizar o texto enviado para aprimoramento dos seus sistemas.
>
> Do nosso lado, nada fica guardado: ao fechar ou recarregar a página, a conversa apaga.
>
> Este serviço é mantido pela Residência em IA (UnB / Instituto Eldorado — Grupo 04). Se tiver dúvidas, fale conosco em donacheca@checatudo.com.
>
> Você aceita que o texto da sua mensagem seja enviado para a DeepSeek?

##### Texto — recusa
> Tudo bem, meu bem. Sem o seu aceite eu não consigo checar a mensagem por
> aqui. Você pode pesquisar a checagem diretamente nos sites de agências de
> checagem, como a Lupa, o Aos Fatos ou o Fato ou Fake.

##### Texto — recusa-local
> Tudo bem, meu bem. Vou checar aqui no computador do projeto, sem mandar sua
> mensagem para fora. Essa opção é mais privativa, mas pode demorar cerca de
> dois minutos.

#### Scenario: Termo antes do primeiro envio
- **GIVEN** o servidor com gerador `deepseek`
- **WHEN** a página é aberta
- **THEN** o texto `termo-servico-externo` aparece com "Aceito" e "Não aceito"
- **AND** o campo de mensagem não envia nada

#### Scenario: Pedido sem consentimento
- **GIVEN** o servidor com gerador `deepseek`
- **WHEN** chega `POST /verificar` sem `consentimento` ou com versão antiga
- **THEN** o servidor responde 403 e o gerador não é chamado

#### Scenario: Recusa com alternativa local
- **GIVEN** o servidor com gerador `deepseek` e `DONA_CHECA_ALTERNATIVA_LOCAL=sim`
- **WHEN** a pessoa escolhe "Não aceito" e envia uma mensagem
- **THEN** a página mostra `recusa-local`
- **AND** a verificação usa o gerador `ollama`

#### Scenario: Recarregar pede de novo
- **GIVEN** uma página em que a pessoa escolheu "Aceito"
- **WHEN** a página é recarregada
- **THEN** o termo aparece de novo antes do campo de mensagem

#### Scenario: Termo em parágrafos
- **GIVEN** o servidor com gerador `deepseek`
- **WHEN** a página é aberta
- **THEN** o termo aparece em seis parágrafos, com as mesmas palavras da versão 3
