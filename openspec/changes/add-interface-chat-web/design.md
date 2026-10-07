# Design: Interface de chat web da Dona Checa

## Context

Ver `proposal.md` para o porquê. Estado atual que molda a abordagem:

- `bancada/pipeline.py`, `executar(texto, recuperador, chat, canal, ...)` roda
  fronteira, extração, decomposição, recuperação, guarda e resposta, e só
  devolve o rastro no fim. Cada etapa passa por uma função interna `etapa()`
  que registra saída ou erro. `chat` e `recuperador` já são injetáveis.
- O rastro termina em três formas: bypass da fronteira (`parou_em="fronteira"`,
  `motivo="bypass"`), sem alegação verificável (`parou_em="extracao"`) ou
  resposta completa. Erro numa etapa para o fluxo com `motivo="erro"`.
- `Resposta` (`prototipo/resposta/estrutura.py`) tem `texto` (camada visível) e
  `detalhe`: lista de `{agencia, data_publicacao, url, veredito_original,
  trecho}`, com `trecho=None` nas referências inaptas. O rastro guarda a saída
  da etapa `resposta` com `asdict`, então o detalhe já está lá.
- O recuperador carrega fragmentos, matriz densa e BM25 (`prototipo.rag.__main__.carregar`):
  segundos de carga e memória considerável. O modelo é Gemma via Ollama local,
  e a fila do Ollama é serial na máquina de um integrante.
- Os textos da persona vêm de `prototipo/identidade/` (`add-identidade-dona-checa`).

## Goals / Non-Goals

**Goals:**

- Uma página que uma pessoa idosa com fonte ampliada consegue usar no celular.
- Fronteira de saúde nunca atrasada por bordão, pergunta ou animação.
- Rodar com um comando na máquina de um integrante; hospedar depois trocando
  só variáveis de ambiente e a fábrica do modelo.
- Nenhum dado de participante fora do navegador dele.

**Non-Goals:**

- Framework de front, etapa de build ou Node no projeto.
- Concorrência real: a máquina local atende uma verificação por vez.
- Internacionalização: só português.

## Decisions

### 1. FastAPI servindo arquivos estáticos, sem build

`interface/app.py` cria a aplicação por fábrica,
`criar_app(config, chat, recuperador)`, e serve `estatico/` como arquivos.
HTML semântico, CSS com tokens da paleta, JS em módulos ES nativos.

Alternativas descartadas (decididas em 07/10/2026): React com Vite, por trazer
Node, build e dois servidores; Streamlit ou Gradio, por não alcançarem o mock
aprovado nem controlarem alvo de toque e ação primária única.

### 2. Configuração só por ambiente

`interface/config.py` lê e valida, e falha na partida se algo estiver errado:

| Variável | Obrigatória | Padrão | Uso |
|---|---|---|---|
| `DONA_CHECA_MODO` | sim | — | `uso` ou `piloto` |
| `DONA_CHECA_HOST` | não | `127.0.0.1` | `0.0.0.0` para celular na mesma rede |
| `DONA_CHECA_PORTA` | não | `8000` | |
| `DONA_CHECA_TEMPO_MAX` | não | `180` | segundos até o erro por tempo |
| `OLLAMA_HOST` | não | do cliente `ollama` | lido pelo próprio cliente |

O padrão `127.0.0.1` evita expor o servidor na rede sem querer; abrir para o
celular é decisão explícita.

### 3. `POST /verificar` com resposta em streaming, lida por `fetch`

O corpo é `{"texto": "..."}` e a resposta é `text/event-stream`, lida no
navegador com `fetch` e `ReadableStream`. `EventSource` foi descartado: só faz
`GET`, e o texto da pessoa iria na URL, que acaba em log de acesso e histórico.

Eventos, um JSON por `data:`:

- `fronteira`: `{"tipo": "fronteira", "desfecho": "urgencia" | "sofrimento" | "conduta" | "segue", "texto": str | null}`
- `andamento`: `{"tipo": "andamento", "etapa": str, "frase": str}`
- `resposta`: `{"tipo": "resposta", "forma": str, "texto": str, "detalhe": [...], "redirecionamentos": [str]}`
- `aviso`: `{"tipo": "aviso", "texto": str}` para `sem_alegacao` e `so_link`
- `erro`: `{"tipo": "erro", "texto": str}`

`desfecho` sai das categorias da fronteira: `risco_imediato` vira `urgencia`,
`sofrimento_psiquico` vira `sofrimento`, ambos com bypass; `conduta_individual`
sem bypass vira `conduta` e o fluxo segue com a recusa em `redirecionamentos`.

### 4. Aviso por etapa em `executar`

`executar` ganha `ao_etapa=None`, chamado com o registro de cada etapa logo
depois de ele entrar no rastro. Sem o parâmetro, nada muda: os testes da
bancada continuam valendo como estão. `interface/fluxo.py` roda `executar`
numa thread, recebe os avisos por uma fila e os converte em eventos.

Alternativa descartada: reimplementar o encadeamento das etapas na interface.
Duplicaria a ordem do fluxo, que a bancada já testa ponta a ponta.

### 5. Uma verificação por vez, com tempo máximo

Um semáforo de tamanho 1 serializa as verificações; quem espera vê o aviso de
leitura. Passado `DONA_CHECA_TEMPO_MAX`, a página recebe `erro`. A thread não é
interrompida (Python não mata thread): termina sozinha e o resultado é
descartado.

### 6. Recuperador carregado na partida

O `lifespan` do FastAPI carrega o recuperador uma vez. `GET /saude` responde
`503` até a carga terminar e `200` depois, para o integrante saber quando abrir
o navegador.

### 7. Textos injetados na página, não buscados

O servidor lê os textos de `identidade-dona-checa` e os desta spec (`lendo`,
`andamento`, `sem_alegacao`, `so_link`, `erro`), com o mesmo leitor de blocos
`##### Texto — <chave>` do módulo `prototipo/identidade/`, e os injeta em
`index.html` num `<script type="application/json" id="config">` junto com o
modo. Em modo piloto a chave da pergunta de confiança vai `null`. Assim a
página funciona sem requisição extra e o modo vem só do servidor.

### 8. Fontes servidas localmente

Bricolage Grotesque e DM Sans (licença OFL) em `estatico/fontes/` como `woff2`.
Sem Google Fonts: a demo funciona sem internet e nenhum terceiro sabe quem
abriu a página. Pilha de fallback do sistema caso a fonte não carregue.

### 9. Log sem texto da pessoa

Logger próprio da interface registra etapa, tipo de erro e segundos. O texto
da mensagem e da resposta nunca é passado ao logger. O log de acesso do
`uvicorn` não registra corpo de requisição, e o texto não vai na URL
(decisão 3).

### 10. Detecção de link

Mensagem que, sem espaços nas pontas, casa com `^https?://\S+$` recebe o aviso
`so_link` sem chamar o fluxo. Qualquer outra mensagem vai ao fluxo, mesmo com
link dentro.

### 11. Testes em duas camadas

- **Servidor:** pytest com `TestClient`, `chat` e `recuperador` falsos ou
  reproduzidos de `bancada/gravacao.py`. Sem Ollama e sem índice.
- **Página:** Playwright para Python contra o servidor de teste com fluxo
  falso; axe-core versionado em `interface/tests/vendor/` (licença MPL-2.0) e
  injetado na página. O navegador do Playwright é baixado uma vez
  (`playwright install chromium`), só em desenvolvimento.

## Risks / Trade-offs

- [Thread presa depois do tempo máximo ocupa o Ollama] → O semáforo só libera
  quando a thread termina de fato; a próxima pessoa espera em vez de empilhar
  chamadas no modelo.
- [Resposta depende de `add-identidade-dona-checa`] → Tasks deste change
  começam pelo servidor e pela página com textos lidos por função; aplicar a
  identidade antes da task de textos.
- [Entrada por link continua descumprida] → Pendência declarada na spec e no
  change `add-entrada-por-link`, com só a proposta escrita.
- [Fonte do navegador em 200% quebra o layout das bolhas] → Teste de 320px com
  fonte ampliada na suíte Playwright.
- [`0.0.0.0` numa rede pública expõe o servidor] → Padrão `127.0.0.1`; o guia
  de uso avisa que abrir para a rede é só em rede de confiança.

## Migration Plan

Nada a migrar. Para hospedar depois: trocar a fábrica do `chat` (Ollama remoto
via `OLLAMA_HOST` ou outra API), apontar o recuperador para o índice no
servidor e pôr um proxy com HTTPS na frente. Nenhuma mudança na página.

## Open Questions

- Nome definitivo do produto: "Dona Checa" é provisório; trocar é texto e
  ativo, sem mudança de comportamento.
