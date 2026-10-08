# Delta para Interface de Chat Web

## REMOVED Requirements

### Requirement: Mensagem só com link

**Reason**: Requirement provisório, que valia até `add-entrada-por-link` ser
aplicado. A entrada por link passa a existir.

**Migration**: Substituído por "Mensagem com link" abaixo. O texto `so_link`
deixa de ser usado; a mensagem só com link roda o fluxo com a etapa de
leitura.

## ADDED Requirements

### Requirement: Mensagem com link

Quando a mensagem tiver link e a página for buscada, a linha de andamento SHALL
mostrar o texto `leitura` abaixo durante a busca. Quando a leitura falhar, a
página SHALL responder com o texto da causa (`nao_abriu`, `fechada`, `video`
ou `vazia`), sem bordão, sem pergunta de confiança e sem o botão "Tentar de
novo". Quando a leitura for parcial, a bolha SHALL mostrar a resposta como ela
vem do fluxo, com o aviso de leitura parcial de `entrada-por-link` entre o
bordão e o primeiro bloco. Sempre que o texto verificado vier
de página, a camada de detalhe SHALL abrir com um cartão de origem com título,
veículo, data quando houver e link para a URL lida, antes dos cartões de
fonte.

##### Texto — leitura
> Abrindo o link…

##### Texto — nao_abriu
> Meu bem, tentei abrir esse link e não consegui. Cola aqui o texto da notícia que eu confiro.

##### Texto — fechada
> Meu bem, essa página só abre pra quem é assinante ou tem login. Cola aqui o texto que eu confiro.

##### Texto — video
> Meu bem, isso é vídeo, e vídeo eu ainda não consigo assistir. Me conta com suas palavras o que ele diz que eu confiro.

##### Texto — vazia
> Meu bem, abri a página mas veio quase nada de texto. Cola aqui o trecho que te deixou na dúvida.

##### Texto — origem
> Li esta página:

#### Scenario: Só link legível
- **GIVEN** a mensagem `https://exemplo.com.br/noticia` com página legível
- **WHEN** ela é enviada
- **THEN** a linha de andamento mostra o texto `leitura` da spec
- **AND** a resposta aparece com o bordão e os quatro blocos
- **AND** a camada de detalhe abre com o cartão de origem

#### Scenario: Vídeo
- **GIVEN** a mensagem `https://youtu.be/abc123`
- **WHEN** ela é enviada
- **THEN** a página mostra o texto `video` da spec
- **AND** nenhum bordão, pergunta de confiança ou botão "Tentar de novo" aparece

#### Scenario: Leitura parcial
- **GIVEN** um link do qual só se lê título e começo
- **WHEN** a resposta chega
- **THEN** o aviso de leitura parcial aparece entre o bordão e o primeiro bloco
