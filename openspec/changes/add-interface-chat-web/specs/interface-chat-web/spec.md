# Delta para Interface de Chat Web

Tela de conversa da Dona Checa servida pelo pacote `interface/`. Os textos da
persona vêm de `identidade-dona-checa`; os blocos `##### Texto` abaixo são os
textos próprios da interface, lidos pelo código.

## ADDED Requirements

### Requirement: Modo de execução obrigatório

O servidor SHALL ler o modo de execução da variável de ambiente
`DONA_CHECA_MODO`, com valores `uso` ou `piloto`, e MUST NOT iniciar quando a
variável estiver ausente ou tiver outro valor. Em modo `piloto`, a página SHALL
exibir a marca "modo piloto" no rodapé. O modo MUST NOT poder ser alterado pela
página, pela URL ou por qualquer requisição.

#### Scenario: Variável ausente
- **GIVEN** um ambiente sem `DONA_CHECA_MODO`
- **WHEN** o servidor é iniciado
- **THEN** o processo termina com erro que nomeia a variável e os valores aceitos

#### Scenario: Modo piloto
- **GIVEN** o servidor iniciado com `DONA_CHECA_MODO=piloto`
- **WHEN** a página é aberta, inclusive com parâmetros de URL quaisquer
- **THEN** o rodapé mostra "modo piloto"
- **AND** a pergunta de confiança nunca é oferecida

### Requirement: Fronteira antes de tudo

Depois do envio de uma mensagem, a página SHALL mostrar apenas o aviso de
leitura até a etapa de fronteira terminar. Quando a fronteira encerrar o fluxo
por urgência médica ou sofrimento psíquico, a resposta padrão SHALL aparecer
imediatamente, com destaque visual, anunciada com prioridade a leitores de
tela e com os telefones como links `tel:`; nesse caso a página MUST NOT
mostrar o bordão nem a pergunta de confiança. Quando a fronteira identificar
pedido de conduta individual, a recusa padrão SHALL aparecer, e a pergunta de
confiança MUST NOT ser oferecida.

##### Texto — lendo
> Dona Checa está lendo…

#### Scenario: Relato de urgência
- **GIVEN** uma mensagem que relata dor no peito acontecendo agora
- **WHEN** a mensagem é enviada
- **THEN** a resposta padrão de urgência é a primeira resposta exibida
- **AND** nenhum bordão nem pergunta de confiança aparece
- **AND** "192" é um link `tel:192`

#### Scenario: Mensagem comum
- **GIVEN** uma mensagem sem sinal de urgência nem pedido de conduta
- **WHEN** a etapa de fronteira termina
- **THEN** a página troca o aviso de leitura pelo bordão e, fora do modo piloto, pela pergunta de confiança

### Requirement: Pergunta de confiança só no navegador

A pergunta de confiança de `identidade-dona-checa` SHALL ser oferecida durante
a espera da resposta, com as três opções como botões, e a pessoa SHALL poder
ignorá-la. A resposta escolhida MUST NOT sair do navegador: nenhuma rota do
servidor a aceita, e ela MUST NOT ser gravada em `localStorage`, cookie ou
qualquer armazenamento do navegador.

#### Scenario: Resposta ignorada
- **GIVEN** a pergunta de confiança oferecida
- **WHEN** a resposta de verificação fica pronta sem que a pessoa tenha respondido
- **THEN** a resposta aparece normalmente

#### Scenario: Resposta escolhida não sai do navegador
- **GIVEN** a pessoa escolheu "4 a 6"
- **WHEN** o tráfego de rede e o armazenamento do navegador são inspecionados
- **THEN** a escolha não aparece em nenhuma requisição nem em nenhum armazenamento

### Requirement: Andamento durante a espera

Enquanto o fluxo roda, a página SHALL mostrar uma linha de andamento com a
frase da etapa em curso, recebida do servidor por SSE, e SHALL anunciá-la de
forma educada (não prioritária) a leitores de tela.

##### Texto — andamento
> extracao: Entendendo o que a mensagem diz…
> decomposicao: Separando o fato da conclusão…
> recuperacao: Procurando checagens…
> guarda: Conferindo as fontes…
> resposta: Escrevendo a resposta…

#### Scenario: Etapas em ordem
- **GIVEN** uma verificação completa
- **WHEN** os eventos SSE são lidos
- **THEN** o primeiro evento é o da fronteira e os de andamento seguem a ordem do fluxo
- **AND** o último evento traz a resposta ou o erro

### Requirement: Resposta e camada de detalhe na bolha

A resposta de verificação SHALL aparecer numa bolha com o bordão e os quatro
blocos de `resposta-formativa`, títulos destacados, e um único botão primário
"Ver fontes e detalhes". O botão SHALL expandir a camada de detalhe dentro da
mesma bolha, um cartão por fonte com veículo ou órgão, data, trecho literal e
link para o original, e SHALL recolhê-la num segundo acionamento. O foco SHALL
ir para a resposta quando ela chega.

#### Scenario: Abrir o detalhe
- **GIVEN** uma resposta com duas fontes
- **WHEN** a pessoa aciona "Ver fontes e detalhes"
- **THEN** dois cartões aparecem dentro da bolha
- **AND** o botão informa estado expandido a leitores de tela

### Requirement: Mensagem sem alegação de saúde

Quando a extração não achar alegação de saúde verificável, a página SHALL
responder com o texto abaixo, sem bordão.

##### Texto — sem_alegacao
> Meu bem, não achei nessa mensagem nada de saúde pra conferir. Se for outra coisa, cola aqui o trecho que te deixou na dúvida.

#### Scenario: Mensagem sem saúde
- **GIVEN** uma mensagem sobre futebol
- **WHEN** o fluxo para na extração
- **THEN** a página mostra o texto `sem_alegacao` da spec

### Requirement: Mensagem só com link

Até `add-entrada-por-link` ser aplicado, quando a mensagem, sem espaços nas
pontas, for apenas uma URL `http` ou `https`, o servidor MUST NOT rodar o fluxo
e a página SHALL responder com o texto abaixo. Mensagem com texto e link junto
SHALL ser verificada como texto.

##### Texto — so_link
> Meu bem, ainda não consigo abrir link. Cola aqui o texto da notícia que eu confiro.

#### Scenario: Só link
- **GIVEN** a mensagem `https://exemplo.com.br/noticia`
- **WHEN** ela é enviada
- **THEN** a página mostra o texto `so_link` da spec
- **AND** o modelo não é chamado

### Requirement: Erro sem vazamento

Quando o fluxo falhar ou passar do tempo máximo configurado, a página SHALL
mostrar o texto abaixo com o botão "Tentar de novo", que reenvia a mesma
mensagem. A página MUST NOT exibir detalhe técnico. O log do servidor SHALL
registrar a etapa e o tipo do erro e MUST NOT conter o texto enviado pela
pessoa.

##### Texto — erro
> Ih, meu bem, deu um problema aqui do meu lado. Tenta de novo daqui a pouco?

#### Scenario: Modelo fora do ar
- **GIVEN** o modelo indisponível
- **WHEN** uma mensagem é enviada
- **THEN** a página mostra o texto `erro` da spec e o botão "Tentar de novo"
- **AND** o log tem a etapa e o tipo do erro, sem o texto da mensagem

### Requirement: Nada guardado

O servidor MUST NOT persistir mensagens, respostas ou identificadores de
pessoa: sem banco, sem arquivo, sem sessão. Cada verificação SHALL ser uma
requisição independente. O histórico SHALL existir só na página aberta e
SHALL sumir ao recarregar.

#### Scenario: Recarregar a página
- **GIVEN** uma conversa com duas verificações
- **WHEN** a página é recarregada
- **THEN** só a mensagem de abertura aparece

#### Scenario: Disco do servidor
- **GIVEN** o servidor depois de dez verificações
- **WHEN** o diretório de trabalho e o log são inspecionados
- **THEN** nenhum texto de mensagem ou de resposta aparece neles

### Requirement: Acessibilidade verificada por teste

A página SHALL passar em teste automatizado que confere: fonte base calculada
de no mínimo 18px e em `rem`; alvos de toque de no mínimo 44px; nenhuma violação
de contraste ou de nome acessível na auditoria axe-core; nenhuma rolagem
horizontal em 320px de largura; envio, pergunta de confiança e detalhe
operáveis só pelo teclado; nenhuma animação quando o sistema pede movimento
reduzido.

#### Scenario: Tela estreita com fonte ampliada
- **GIVEN** viewport de 320px e fonte do navegador em 200%
- **WHEN** a página mostra uma resposta com detalhe aberto
- **THEN** não há rolagem horizontal
- **AND** o botão de envio continua alcançável
