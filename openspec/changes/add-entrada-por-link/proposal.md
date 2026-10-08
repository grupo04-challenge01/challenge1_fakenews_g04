# Proposal: Entrada por link

**Fase do CBL:** Act. Change aberto em 07/10/2026 durante o brainstorming de
`add-interface-chat-web`, para registrar a lacuna, e detalhado no brainstorming
próprio do mesmo dia.

## Why

`acessibilidade-leitura` / "Entrada sem barreira" (em `mvp-copiloto-verificacao`)
diz que o sistema SHALL aceitar texto colado ou encaminhado **e link** como
entrada. O fluxo atual (`bancada/pipeline.py`, `executar`) só recebe texto:
nada baixa nem extrai o conteúdo de uma URL. Hoje a spec é descumprida.

O descumprimento pesa: no WhatsApp, a desinformação de saúde circula muito como
link de notícia ou de blog, não só como texto. Uma pessoa que cola o link e
recebe "não consigo abrir" aprende que a ferramenta não serve para o caso dela.

Até este change ser aplicado, `add-interface-chat-web` trata mensagem que é só
link com o texto `so_link`, pedindo o texto da notícia.

## What Changes

- **NOVO** pacote `prototipo/entrada/`: separa link de texto, limpa parâmetros
  de rastreio, busca a página com bloqueios contra acesso à rede interna
  (SSRF) e extrai texto principal, título, veículo e data.
- **NOVO** regra de escolha entre texto e página: texto da pessoa curto
  verifica a página; texto longo verifica o texto, e só cai para a página
  quando o texto não tiver alegação de saúde verificável. Com vários links,
  só o primeiro é buscado.
- **NOVO** leitura parcial: quando só título e começo puderem ser lidos
  (paywall, extração pobre), a verificação segue com o que foi lido e a
  resposta avisa disso.
- **NOVO** quatro falhas de leitura respondidas na voz da Dona Checa, cada uma
  pedindo o texto colado: `nao_abriu`, `fechada`, `video`, `vazia`.
- **MODIFICADO (código)** `bancada/pipeline.py`: etapa `leitura` entre
  `fronteira` e `extracao`; a fronteira passa a ler só o texto da pessoa, sem
  a URL; o rastro ganha a origem do texto verificado.
- **MODIFICADO (código)** `interface/`: substitui a resposta `so_link` por
  andamento "Abrindo o link…", textos de falha, aviso de leitura parcial e
  cartão de origem na camada de detalhe.
- **MODIFICADO (documento)** TCLE do piloto: uma frase sobre o servidor abrir
  a página do link, inserida antes da submissão ao CEP.
- Nenhum contorno de paywall: sem se passar por navegador ou robô de busca,
  sem serviço de arquivo de terceiros.

## Capabilities

### New Capabilities

- `entrada-por-link`: escolha entre texto e página, limites de segurança da
  busca, limpeza de rastreio, extração, leitura parcial, falhas de leitura e
  origem auditável.

### Modified Capabilities

- `acessibilidade-leitura`: "Entrada sem barreira" passa a dizer o que acontece
  quando o link não pode ser lido.
- `interface-chat-web`: "Mensagem só com link" sai; entra "Mensagem com link".

As duas capacidades modificadas ainda vivem em changes não arquivados
(`mvp-copiloto-verificacao` e `add-interface-chat-web`). Este change só pode
ser arquivado depois deles; ver `design.md`.

## Out of Scope

- Entrada por imagem, OCR, áudio e vídeo (já fora do MVP). Link de vídeo é
  reconhecido só para responder que vídeo não é lido.
- Renderizar JavaScript com navegador headless. Página que só monta o texto
  no navegador cai em `vazia`.
- Contornar paywall ou login.
- Verificar a reputação do domínio como critério de veredito: isso é mudança
  de método, não de entrada.
- Buscar mais de um link por mensagem.
- Limite de taxa e controle de abuso (já fora em `add-interface-chat-web`).

## Impact

**Entregáveis finais do desafio atingidos:**

- **Solução/protótipo com suporte de IA:** fecha uma lacuna entre a spec de
  acessibilidade e o produto.
- **Apresentação final (Showcase):** a demo pode partir de um link real, que é
  como a desinformação chega.

**Código afetado:**

- `prototipo/entrada/` (novo): `link.py`, `rede.py`, `leitura.py`, testes e
  páginas gravadas.
- `bancada/pipeline.py`: etapa `leitura`, parâmetro injetável `buscar`.
- `bancada/casos.json` e `bancada/gravacoes/`: casos com link.
- `interface/`: textos, andamento, aviso parcial, cartão de origem.
- `requirements-rag.txt` e lock: `httpx`, `trafilatura`.
- `openspec/changes/mvp-copiloto-verificacao/specs/avaliacao-instrumento/protocolo-etico-tcle-debriefing.md`:
  frase de privacidade.
