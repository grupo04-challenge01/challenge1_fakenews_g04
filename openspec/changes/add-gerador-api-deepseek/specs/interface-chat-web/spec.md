# Delta para Interface de Chat Web

## ADDED Requirements

### Requirement: Aviso de serviço externo

Quando o gerador for `deepseek`, a página SHALL mostrar o texto abaixo no
rodapé, visível antes da primeira mensagem e durante toda a conversa. Quando
o gerador for `ollama`, a página MUST NOT mostrar o texto. O texto SHALL vir
do servidor, como o modo de execução.

##### Texto — servico-externo
> Para te responder, eu mando sua mensagem para um serviço de inteligência
> artificial de fora do Brasil. Não coloque seu nome, telefone ou dados de
> saúde seus na mensagem.

#### Scenario: Gerador remoto
- **GIVEN** o servidor com gerador `deepseek`
- **WHEN** a página é aberta
- **THEN** o rodapé mostra o texto `servico-externo` antes de qualquer envio

#### Scenario: Gerador local
- **GIVEN** o servidor com gerador `ollama`
- **WHEN** a página é aberta
- **THEN** o texto `servico-externo` não aparece

### Requirement: Consentimento antes do envio ao serviço externo

Quando o gerador for `deepseek`, a página SHALL mostrar o texto
`termo-servico-externo` antes de liberar o campo de mensagem, com os botões
"Aceito" e "Não aceito", nenhum pré-selecionado. O campo de mensagem MUST NOT
aceitar envio antes de uma escolha. O servidor MUST NOT enviar texto ao
gerador remoto sem o campo `consentimento` igual à versão atual do termo no
pedido, e SHALL registrar no log a versão aceita, sem identificador de pessoa.
O aceite SHALL valer só para a página aberta: ao recarregar, o termo volta.

Com "Não aceito", a página SHALL mostrar o texto `recusa`. Quando o servidor
tiver alternativa local configurada (`DONA_CHECA_ALTERNATIVA_LOCAL=sim`), a
página SHALL mostrar o texto `recusa-local`, e as verificações dessa página
SHALL usar o gerador `ollama`.

##### Texto — termo-servico-externo
> Antes de começar, meu bem: para te responder, eu mando o texto da sua
> mensagem para a DeepSeek, uma empresa de inteligência artificial da China.
> Ela recebe só o texto, sem seu nome e sem seu telefone, e pode guardar esse
> texto pelas regras dela. Aqui do nosso lado nada fica guardado: fechou a
> página, a conversa some. Por isso, não escreva dados seus, como nome,
> telefone, CPF ou doença que você tem. Quem responde por este serviço é o
> grupo 04 da Residência em IA, pelo contato CONTATO_DO_GRUPO. Você aceita que
> sua mensagem vá para a DeepSeek?

##### Texto — recusa
> Tudo bem, meu bem. Sem esse aceite eu não consigo checar por aqui. Você pode
> procurar a checagem no site de uma agência, como a Lupa, o Aos Fatos ou o
> Fato ou Fake.

##### Texto — recusa-local
> Tudo bem, meu bem. Vou checar aqui no computador do projeto, sem mandar sua
> mensagem para fora. Só que demora mais, uns dois minutos.

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
