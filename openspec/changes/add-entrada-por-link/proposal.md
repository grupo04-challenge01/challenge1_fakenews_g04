# Proposal: Entrada por link

**Fase do CBL:** Act. Change aberto em 07/10/2026 durante o brainstorming de
`add-interface-chat-web`, para registrar a lacuna. **Só a proposta existe.**
Specs, design e tasks dependem de brainstorming próprio; até lá o change não
passa em `openspec validate --strict`, de propósito.

## Why

`acessibilidade-leitura` / "Entrada sem barreira" (em `mvp-copiloto-verificacao`)
diz que o sistema SHALL aceitar texto colado ou encaminhado **e link** como
entrada. O fluxo atual (`bancada/pipeline.py`, `executar`) só recebe texto:
nada baixa nem extrai o conteúdo de uma URL. Hoje a spec é descumprida.

O descumprimento pesa: no WhatsApp, a desinformação de saúde circula muito como
link de notícia ou de blog, não só como texto. Uma pessoa que cola o link e
recebe "não consigo abrir" aprende que a ferramenta não serve para o caso dela.

Até este change ser aplicado, `add-interface-chat-web` trata mensagem que é só
link com uma resposta na voz da Dona Checa pedindo o texto da notícia, e
registra a pendência apontando para cá.

## What Changes

A definir no brainstorming. Escopo provável:

- Detectar link na mensagem e separar link de texto.
- Baixar a página no servidor e extrair o texto principal, título, veículo e
  data de publicação.
- Entregar o texto extraído ao fluxo existente (`executar`), sem mudar as
  etapas seguintes.
- Mostrar na camada de detalhe de onde o texto veio (URL, veículo, data), para
  que a pessoa confira que foi lido o que ela mandou.
- Falhar com resposta na voz da Dona Checa quando não der para ler a página.

## Capabilities

### New Capabilities

- `entrada-por-link` (provável): recebimento, busca e extração de conteúdo de
  link, com limites de segurança.

### Modified Capabilities

- `acessibilidade-leitura` (provável): o requirement "Entrada sem barreira"
  pode precisar dizer o que acontece quando o link não pode ser lido.

## Questões para o brainstorming

- **Segurança da busca.** Buscar URL arbitrária no servidor abre SSRF (acesso a
  endereço interno da rede). Que bloqueios: só `http`/`https`, nada de IP
  privado ou `localhost`, limite de redirecionamentos, tamanho máximo e tempo
  máximo.
- **Encurtadores e redirecionamentos.** `bit.ly`, `encurtador.com.br` e links
  do próprio WhatsApp: seguir até onde.
- **Página que não entrega o texto.** Paywall, página montada por JavaScript,
  vídeo do YouTube, post de rede social que exige login. O que a Dona Checa
  diz em cada caso.
- **Biblioteca de extração.** Por exemplo `trafilatura` ou `readability-lxml`:
  qualidade em sites brasileiros, licença, dependências.
- **Link e texto juntos.** Quando a pessoa cola um texto que também traz link,
  o que é verificado: o texto, a página ou os dois.
- **Privacidade.** O servidor acessar a URL revela ao site que alguém a
  consultou. Isso entra no TCLE do piloto?
- **Hospedagem.** Local agora, desenhado para hospedar (decisão de
  `add-interface-chat-web`): a busca precisa funcionar nos dois cenários.

## Out of Scope

- Entrada por imagem, OCR, áudio e vídeo (já fora do MVP).
- Verificar a reputação do domínio como critério de veredito: isso é mudança
  de método, não de entrada.

## Impact

**Entregáveis finais do desafio atingidos:**

- **Solução/protótipo com suporte de IA:** fecha uma lacuna entre a spec de
  acessibilidade e o produto.

**Código afetado (provável):** novo módulo de entrada em `prototipo/`, o
`executar` de `bancada/pipeline.py` (ou quem o envolve na interface) e a
camada de detalhe da interface.
