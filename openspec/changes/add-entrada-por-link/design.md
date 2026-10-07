# Design: Entrada por link

## Context

Motivação em `proposal.md`. Requisitos em `specs/entrada-por-link`,
`specs/acessibilidade-leitura` e `specs/interface-chat-web`.

Estado atual:

- `bancada/pipeline.py`, `executar(texto, recuperador, chat=...)`, roda
  fronteira, extração, decomposição, recuperação, guarda e resposta. `chat` e
  `recuperador` são injetáveis; testes e bancada usam gravações
  (`bancada/gravacoes/`), sem modelo nem índice reais.
- `add-interface-chat-web` define a interface (`interface/`, FastAPI + SSE)
  com o requirement provisório "Mensagem só com link". Código da interface
  ainda não está em `main`.
- Servidor roda na máquina de um integrante; desenho deve servir também para
  hospedagem (decisão de `add-interface-chat-web`).
- Modelo local Gemma 4 12B QAT: cada chamada custa segundos.

## Goals / Non-Goals

**Goals:**

- Link vira texto antes da extração, sem mudar as etapas seguintes.
- Nenhum caminho de rede leva o servidor a falar com endereço interno.
- Toda falha de leitura vira uma de quatro causas legíveis.
- Testes e bancada rodam sem rede.

**Non-Goals:**

- Renderizar JavaScript.
- Ler mais de um link por mensagem.
- Cache de páginas (contraria "Nada guardado").

## Decisions

### D1. Pacote `prototipo/entrada/` com três unidades

| Arquivo | Responsabilidade | Depende de |
| --- | --- | --- |
| `link.py` | `separar(mensagem) -> (texto_sem_url, urls)`, `limpar(url)`, `classificar_antes(url) -> causa \| None` | stdlib |
| `rede.py` | `buscar(url) -> Pagina(corpo, url_final, tipo)`, levanta `Recusa(motivo)` | `httpx`, `httpcore` |
| `leitura.py` | `ler(url, buscar=rede.buscar) -> Leitura \| Falha` | `trafilatura`, `rede` |

`Leitura(texto, titulo, veiculo, data, url, parcial, cortado)`;
`Falha(causa)` com `causa` em `nao_abriu | fechada | video | vazia`.

Unidades separadas porque cada uma tem risco diferente: `rede` é segurança,
`leitura` é qualidade de extração, `link` é parsing. Cada uma é testada
isolada. Alternativa descartada: módulo único, que misturaria testes de SSRF
com testes de HTML.

### D2. Etapa `leitura` dentro de `executar`, depois de `fronteira`

`ETAPAS = ("fronteira", "leitura", "extracao", "decomposicao", "recuperacao",
"guarda", "resposta")`. `executar` ganha `buscar=rede.buscar`, injetável como
`chat`.

Ordem dentro de `executar`:

1. `separar` a mensagem. Fronteira roda sobre `texto_sem_url`; string vazia
   não tem categoria e segue.
2. Sem URL: etapa `leitura` registra `origem.tipo = "texto"` e segue.
3. Com URL e texto < 30 palavras: lê a página.
4. Com URL e texto ≥ 30 palavras: extração roda sobre o texto. Verificável →
   segue com o texto. Não verificável → lê a página e roda a extração de novo
   sobre ela. O rastro registra as duas extrações.
5. `Falha` → `parar("leitura", causa)`, `resposta = {"forma": "leitura",
   "causa": causa}`.
6. Leitura parcial sem alegação verificável → `parar("leitura", "vazia")`, não
   `parar("extracao", ...)`.

Rastro ganha `rastro["origem"] = {"tipo", "url", "titulo", "veiculo", "data",
"parcial", "cortado", "ignorados"}`.

Por que dentro de `executar`, não em `interface/fluxo.py`: a regra do passo 4
depende da extração, que mora no pipeline; e a bancada precisa exercitar link
com as mesmas gravações dos outros casos. O aviso por etapa que
`add-interface-chat-web` adiciona a `executar` cobre a linha de andamento
"Abrindo o link…" sem código extra.

### D3. `httpx` + `trafilatura`, sem navegador

- `httpx` já está no lock (`requirements-rag.lock.txt`), entra explícito em
  `requirements-rag.txt`.
- `trafilatura` (Apache-2.0 desde 1.8): melhor resultado em benchmarks
  públicos de extração, bom em português, devolve título, `sitename` e data, e
  lê `JSON-LD` e `og:`. Usado só sobre HTML já baixado (`extract` sobre
  string); a busca própria do `trafilatura` não é usada, porque não tem os
  bloqueios de D4.
- Alternativas: `readability-lxml` (sem metadados, mais código nosso) e
  Playwright (2–5 s por link, Chromium executando código de site hostil).
  Playwright fica para change futuro se o piloto mostrar muitas falhas `vazia`.

Compatibilidade com Python 3.14.6 (fixado no lock) é a primeira task; se
`trafilatura` ou `lxml` não instalarem, o change volta para design.

### D4. Bloqueio de SSRF no momento da conexão

Validar o IP antes e deixar o `httpx` resolver de novo permite DNS rebinding.
Solução: `httpcore.NetworkBackend` próprio, passado ao transporte do `httpx`,
cujo `connect_tcp(host, port)` resolve com `socket.getaddrinfo`, recusa se
**qualquer** endereço não for `ipaddress.ip_address(a).is_global` (tratando
`ipv4_mapped` e `6to4`), e conecta no próprio endereço validado. TLS segue
usando o nome original para SNI e certificado, porque o backend só troca a
abertura do socket.

Demais regras, todas em `rede.py`:

- esquema `http`/`https`, porta 80/443 (explícita ou implícita), sem
  `userinfo`;
- `follow_redirects=False`; laço manual de até 5 saltos, cada `Location`
  resolvida contra a URL atual e repassada por `limpar` e pelas regras acima;
- `httpx.Timeout(10, connect=5)` e prazo total medido no laço;
- `client.stream`, soma bytes de `iter_bytes()` (já descomprimidos) e aborta
  acima de 2 MB;
- `Content-Type` só `text/html` ou `application/xhtml+xml`;
- cliente novo por busca, sem cookies persistidos, `trust_env=False` (não usa
  proxy do ambiente);
- `User-Agent: DonaChecaBot/0.1 (+https://github.com/grupo04-challenge01/challenge1_fakenews_g04)`.

`robots.txt` não é consultado: busca única, pedida pela pessoa, como a prévia
de link do próprio WhatsApp. Não é rastreamento.

### D5. Limpeza de rastreio e reconhecimento sem busca

`limpar` remove parâmetros cujo nome começa com `utm_` ou está em
`{fbclid, gclid, dclid, gbraid, wbraid, msclkid, igshid, mc_cid, mc_eid,
_hsenc, _hsmi, ref_src, si}`, e remove o fragmento (`#...`).

`classificar_antes`:

- `video`: hosts `youtube.com`, `m.youtube.com`, `youtu.be`, `tiktok.com`,
  `vm.tiktok.com`, `kwai.com`, `vimeo.com`, e caminhos `/reel/` e `/reels/`
  em `instagram.com` e `facebook.com`;
- `nao_abriu`: `chat.whatsapp.com`, `wa.me`, `api.whatsapp.com`.

Depois da busca, `fechada` quando a leitura não é completa e (a) o `JSON-LD`
traz `isAccessibleForFree: false`, ou (b) o host é `instagram.com`,
`facebook.com`, `x.com`, `twitter.com` ou `threads.com`.

Por que "não completa" e não "abaixo do limiar de parcial": na coleta de
07/10/2026, o perfil do Ministério da Saúde no Instagram rendeu 32 palavras de
texto de login, e uma página com paywall sinalizado rende o aviso de
assinatura. Pelos limiares de parcial, os dois seriam verificados como
conteúdo e cairiam em `vazia`, com a mensagem errada. Já a Folha, que se
declara paga mas entrega a matéria inteira no HTML (491 palavras), segue
completa. Página paga sem o sinal no `JSON-LD` (Valor, 47 palavras) segue
parcial, como decidido.

Listas ficam em constantes do módulo, cobertas por teste.

### D6. Extração e limiares

Ordem: `trafilatura.extract(html, output_format="json", with_metadata=True,
include_comments=False, favor_recall=True)`; se o corpo vier com menos de 150
palavras, tenta `articleBody` do `JSON-LD` e depois `og:description`, ficando
com o mais longo. Limiares da spec: 150 palavras para completa, 15 para
parcial, 800 de corte, 30 para texto curto da pessoa.

Os limiares são da spec. Calibração na bancada que peça outro valor exige
atualizar este change antes do código.

### D7. Aviso de leitura parcial posto por `estrutura.responder`

`estrutura.responder` ganha `aviso=None`. Com aviso, o texto `leitura_parcial`
(lido do bloco `##### Texto` da spec `entrada-por-link`, mesmo mecanismo de
`prototipo/identidade/`) entra entre o bordão e o bloco 1 e conta no teto de
120 palavras. Assim o teto continua verificado num lugar só.

### D8. Página entra no prompt como conteúdo citado

Quando o texto vem de página, extração e decomposição recebem o texto entre
delimitadores `<<<PAGINA` / `PAGINA>>>`, e o prompt diz que o conteúdo
delimitado é material a analisar, não instrução. A guarda já decide só sobre
trechos do acervo. Caso de bancada com tentativa de injeção fixa o
comportamento.

### D9. Privacidade e TCLE

A frase entra na seção 5 do TCLE
(`mvp-copiloto-verificacao/specs/avaliacao-instrumento/protocolo-etico-tcle-debriefing.md`):
"Se você mandar um link, o servidor do projeto abre essa página para ler o
texto. O site vê que o servidor do projeto acessou, não vê você. Parâmetros
de rastreio do link são apagados antes." Precisa entrar antes da submissão ao
CEP (task 6.4 daquele change); depois vira emenda, com prazo de terceiro.

### D10. Ordem de arquivamento

Os deltas de `acessibilidade-leitura` (MODIFIED) e `interface-chat-web`
(REMOVED) miram specs que só existem em `mvp-copiloto-verificacao` e
`add-interface-chat-web`. Ordem: `mvp-copiloto-verificacao`, depois
`add-interface-chat-web`, depois este. Mesma situação já registrada em
`add-identidade-dona-checa`.

## Risks / Trade-offs

- [Muitos sites brasileiros montam o texto por JavaScript] → cai em `vazia`
  com pedido de texto. Bancada mede a taxa; Playwright é o próximo passo se
  alta.
- [User-Agent honesto é bloqueado por alguns sites] → `nao_abriu`. Aceito:
  fingir navegador contradiz a decisão de não contornar acesso.
- [Servidor local expõe o IP do integrante ao site de desinformação] →
  aceito para piloto e demo; declarado no TCLE. Hospedagem resolve.
- [Busca soma até 10 s à espera] → a linha de andamento mostra "Abrindo o
  link…"; prazo total do fluxo em `add-interface-chat-web` precisa
  acomodar isso.
- [Texto longo sem alegação custa duas extrações] → só ocorre com link;
  segunda extração é sobre a página, que é o que a pessoa queria checar.
- [Injeção via página muda a alegação extraída] → veredito continua preso ao
  acervo; alegação extraída aparece no detalhe, auditável.
- [Lista de domínios de vídeo e rede social envelhece] → constante única,
  teste por domínio; atualização é config, isenta de change.
- [`trafilatura` não instala em Python 3.14] → task 1.1 verifica antes de
  qualquer código.

## Migration Plan

Sem migração de dados. A interface troca `so_link` por "Mensagem com link"
no mesmo PR que liga a etapa `leitura`. Reverter = remover a etapa e
restaurar `so_link`.
