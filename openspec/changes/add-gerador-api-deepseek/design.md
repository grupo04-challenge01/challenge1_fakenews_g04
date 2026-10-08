# Design: Gerador por API (DeepSeek)

## Context

Motivação em `proposal.md`. Requisitos em `specs/gerador-modelo` e
`specs/interface-chat-web`.

Estado atual:

- Toda chamada ao modelo passa por `chat_ollama(sistema, usuario, modelo, cpu)`
  em `prototipo/verificacao/modelo.py`. Saída em modo JSON, temperatura 0.2,
  `num_predict` 1200.
- `bancada/pipeline.executar`, `interface/fluxo.verificar` e
  `interface/app.criar_app` recebem `chat` injetado. Testes e bancada offline
  usam gravações, sem modelo.
- `interface/config.py` lê tudo de variável de ambiente e recusa subir com
  configuração inválida.
- Os cinco prompts (fronteira, extração, decomposição, guarda, resposta)
  pedem JSON e citam a palavra "JSON", que a API da DeepSeek exige no modo
  JSON.

## Goals / Non-Goals

**Goals:**

- Cortar pelo menos pela metade a mediana do tempo por mensagem completa.
- Manter a bancada real em 17/17.
- Trocar o gerador sem tocar em prompt, etapa ou página, exceto o aviso.
- Testes continuam sem rede.

**Non-Goals:**

- Streaming de tokens para a página. A resposta é JSON e só vale inteira.
- Paralelizar etapas. É outro ganho de latência, mas muda o fluxo.
- Trocar embeddings ou índice para API.
- Troca automática para Ollama quando a API falha.

## Decisions

### D1. `ChatDeepSeek` com `httpx`, sem SDK

A API da DeepSeek segue o formato OpenAI (`POST /chat/completions`). `httpx`
já está em `requirements-rag.txt` (D3 de `add-entrada-por-link`). Uma função
pequena evita a dependência `openai`. `ChatDeepSeek` é um objeto chamável com
a assinatura de `chat_ollama`; objeto, e não função, para guardar chave,
modelo, cliente e o `model` da última resposta (`modelo_servido`, D7).

Corpo do pedido:

```json
{
  "model": "deepseek-v4-pro",
  "messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}],
  "response_format": {"type": "json_object"},
  "thinking": {"type": "disabled"},
  "temperature": 0.2,
  "max_tokens": 1200
}
```

- `thinking` desligado: o raciocínio vem ligado por padrão e custa tempo.
  Equivale ao `think=False` de hoje. Sem raciocínio, a API respeita
  `temperature`.
- `max_tokens` 1200 espelha `num_predict`.
- Cliente `httpx.Client` criado uma vez por processo e reaproveitado, para
  não repetir o handshake TLS a cada etapa.
- Tempo limite de 60 s por chamada. O tempo máximo da verificação continua
  sendo `DONA_CHECA_TEMPO_MAX`.

Alternativa descartada: SDK `openai`. Funciona, mas é dependência nova para
uma chamada só.

### D2. Modelo `deepseek-v4-pro`

Conferido em 08/10/2026 na documentação oficial: `deepseek-flash` é o modelo
padrão da API, e `deepseek-v4-pro` é o maior. Os nomes antigos `deepseek-chat`
e `deepseek-reasoner` não aparecem mais. A escolha inicial foi o `flash`, pelo
menor tempo e custo. A bancada de 08/10 mudou a escolha: o `flash` deu rótulo
`falso` sem evidência da alegação (S1), e o `pro` não errou rótulo em três
rodadas, com mediana de 10 a 11 s e cerca de US$ 0,003 por mensagem. O nome
vem de `DEEPSEEK_MODELO`, com padrão `deepseek-v4-pro`.

### D10. Critério de aceite revisto

Segunda revisão, decisão do grupo em 08/10/2026, depois de nove rodadas com
`deepseek-v4-pro`: nenhuma com rótulo errado, e as falhas restantes variando
de rodada para rodada na forma da resposta. Exigir no máximo uma falha de
forma em duas rodadas seguidas virou sorteio. O critério separa:

- **Eliminatórias**, sem tolerância: etapa em erro, rótulo errado, fronteira
  errada, mito citado sem marcação e veredito insinuado sem evidência (técnica
  nomeada ou "a mensagem engana" na forma sem evidência). Chegam à pessoa como
  veredito sem base, reforço da desinformação, urgência não desviada ou
  mensagem de erro. Mito sem marcação era tratado como forma na proposta do
  grupo e passou a eliminatório: repetir o mito sem desmentir pode reforçá-lo.
- **Demais**, até 3 de 27 por rodada (cerca de 11%): tamanho, outros defeitos
  da resposta e acerto de etapa. A página entrega a resposta mesmo assim.

`python -m bancada rodar` classifica e imprime o critério
(`resumo.por_tipo`, `resumo.criterio`), para acompanhar a taxa ao longo do
tempo. Toda falha de mito é conferida à mão: falso positivo do verificador é
corrigido com teste num change (como D1 e D7 de
`fix-qualidade-gerador-remoto`) e a rodada é refeita, nunca aceita no olho.
Falso positivo conhecido e aberto: F03 do Gemma (`143536`), "A idosa já tinha
problemas cardíacos…", que traz contexto e não repete o mito.

Reclassificadas com o critério e a régua da época: `154244` cumpre;
`154557`, `155424` e `155808` não. As falhas de mito de `155424` ("foi
retratado") e `155808` ("tira de contexto") foram falsos positivos, corrigidos
pelo D7. A rodada interrompida depois do D7 falhou por mito real no R1.

Primeira revisão, mesmo dia: O critério original, 27/27 casos, era mais
rígido do que o Gemma cumpre (26/27 no mesmo dia), e a forma da resposta varia
de uma rodada para outra. O critério passou a ser, em duas rodadas seguidas:
nenhum rótulo errado, nenhuma etapa em erro, pelo menos o número de casos do
Gemma e mediana até a metade. Rótulo errado e erro de etapa continuam
eliminatórios, porque chegam à pessoa como veredito sem base ou como mensagem
de erro.

### D3. Escolha do gerador em `interface/config.py`

| Variável | Valores | Padrão |
| --- | --- | --- |
| `DONA_CHECA_GERADOR` | `deepseek`, `ollama` | `deepseek` em `uso`, `ollama` em `piloto` |
| `DEEPSEEK_API_KEY` | chave | nenhum; obrigatória com `deepseek` |
| `DEEPSEEK_MODELO` | nome do modelo | `deepseek-v4-pro` |

`Config` ganha o campo `gerador`. `interface/__main__.py` escolhe a função
`chat` a partir dele e passa para `criar_app`. Valor inválido ou chave ausente
termina o processo com erro que nomeia a variável, como já acontece com
`DONA_CHECA_MODO`. A mensagem de erro nunca contém o valor da chave.

### D4. Segredo da chave

- A chave só existe em variável de ambiente. Nenhum arquivo versionado a
  contém.
- `.env` já é ignorado (`.gitignore`, regra `*.env`). `.env.example`
  versionado, liberado pela regra `!*.env.example`, lista as variáveis
  com valor vazio.
- O log nunca registra cabeçalhos do pedido. Erro HTTP vira só tipo e status
  (`HTTPStatusError 401`), seguindo "Erro sem vazamento".

### D5. Falhas

| Situação | Comportamento |
| --- | --- |
| 429, 500, 502, 503 ou `content` vazio | uma nova tentativa depois de 1 s |
| Segunda falha, 401, 402, 400, tempo limite | exceção; o fluxo emite `erro` |

A documentação avisa que a API às vezes devolve `content` vazio no modo JSON.
Uma nova tentativa cobre esse caso sem esconder falha persistente. A exceção
segue o caminho que `chat_ollama` já usa quando o Ollama está fora do ar.

### D6. Aviso na página e modo piloto

Com gerador `deepseek`, a página mostra o texto `servico-externo` no rodapé,
sempre visível, antes da primeira mensagem. Com `ollama`, o aviso não aparece.

No modo `piloto`, o padrão é `ollama`, porque o TCLE de
`mvp-copiloto-verificacao` não fala em envio a terceiro. O grupo pode decidir
usar DeepSeek no piloto. Nesse caso, a frase abaixo entra antes na seção 5 do
TCLE, e o servidor sobe com `DONA_CHECA_GERADOR=deepseek` explícito:

> Para montar a resposta, o texto que você mandar é enviado a um serviço de
> inteligência artificial de uma empresa de fora do Brasil (DeepSeek). O
> projeto não manda seu nome nem seu telefone, mas não controla o que essa
> empresa guarda.

**Decisão do grupo, 08/10/2026:** a DeepSeek pode ser usada no piloto. A
frase entrou na seção 5 do TCLE no lugar da frase que dizia que os modelos
não repassam informações a empresas comerciais, que deixou de ser verdade. O
risco LGPD do dossiê do CEP passou de «Nulo» para «Baixo». Como o protocolo
já tinha parecer (06/10), a mudança foi registrada como emenda 01, pendente de
submissão (task 0.3). O padrão do modo `piloto` continua `ollama`; o piloto
usa a DeepSeek com `DONA_CHECA_GERADOR=deepseek` explícito, depois da emenda.

### D7. Bancada

`python -m bancada rodar --gerador deepseek|ollama`, com padrão `ollama`, para
os relatórios antigos continuarem comparáveis. `parametros` do relatório
ganha `gerador` e `modelo`, e, na DeepSeek, `uso`: chamadas e tokens de
entrada, de entrada em cache e de saída, somados do campo `usage` de cada
resposta. O custo sai desses números e da tabela de preço do dia. Para a DeepSeek, `modelo` é o campo `model` da
resposta, não o nome pedido.

A gravação (`bancada/gravacoes/`) não muda: grava texto de saída, qualquer que
seja o gerador.

Antes do primeiro caso, a bancada faz uma chamada curta ao gerador. Se ela
falhar, a rodada termina com código 2, sem rodar caso nem sobrescrever
gravação. Motivo: em 08/10/2026 uma chave recusada (401) rodou os 27 casos e
trocou 22 gravações reais por gravações de erro.

Linha de base de 08/10/2026 com `ollama` (`gemma4:12b-it-qat`, relatório
`20261008-143536.json`): 26/27 casos; F03 falhou na resposta (124 palavras,
teto 120, e mito citado sem marcação de falso). Mediana de 102,4 s nos 18
casos que chegam à resposta, de 77,2 s (S3) a 238,0 s (L01).

Primeira rodada com `deepseek-flash`, mesmo dia e mesma máquina (relatório
`20261008-144402.json`): **19/27 casos**, mediana de **7,1 s** nos 16 casos
que chegam à resposta. A latência cumpre o critério com folga; o acerto não.

| Caso | Etapa | Falha |
| --- | --- | --- |
| S1 | guarda | rótulo `falso` com trechos sobre outro remédio (inhame); o próprio critério admite que nenhum trecho fala da goiabeira. Esperado: evidência insuficiente |
| L01 | extracao | JSON cortado: o modelo listou toda alegação da página e passou de 1200 tokens |
| L10 | decomposicao | opinião repetida como fato; a validação barrou |
| F01 | resposta | 132 palavras na camada visível, teto 120 |
| F04, R1, R2, S1, X2 | resposta | menção ao mito sem marcação de falso. Parte é paráfrase que o verificador léxico não reconhece ("não achou prova de que…", "nenhum estudo comprova…"); parte é repetição real ("A mensagem promete curar dengue em 24 horas") |

S1 é a falha grave: veredito sustentado por evidência de outra alegação, o
contrário de "veredito nunca nu". Próximo passo, conforme a task 4.3: rodar
com `DEEPSEEK_MODELO=deepseek-v4-pro` antes de mexer em prompt, limite de
tokens ou verificador.

Segunda rodada com `deepseek-v4-pro` (relatório `20261008-145132.json`):
**23/27 casos**, mediana de **11,1 s** nos 16 casos que chegam à resposta,
máximo de 20,0 s. S1, L01 e F01 passaram.

| Caso | Etapa | Falha |
| --- | --- | --- |
| R3 | decomposicao | dois fatos do relato marcados como opinião, e veredito dentro da decomposição; a validação barrou e o caso verdadeiro terminou em erro |
| R2, X2 | resposta | menção ao mito sem marcação: "não encontrou nenhum estudo que mostre que…" e "Nenhum estudo mostra que…". As duas negam a alegação, mas o verificador léxico não reconhece a forma |
| F05 | resposta | uma frase com mais de 20 palavras |

Com o `pro`, nenhum rótulo da guarda saiu errado: o 11/12 da guarda é o R3,
que parou antes dela.

Repetições com `deepseek-v4-pro` (task 4.7), fora do horário de pico:

| Relatório | Casos | Mediana | Máximo | Tokens (entrada / cache / saída) |
| --- | --- | --- | --- | --- |
| `20261008-145132` | 23/27 | 11,1 s | 20,0 s | não registrado |
| `20261008-150944` | 25/27 | 9,9 s | 18,1 s | 115.236 / 81.536 / 11.357 |
| `20261008-151357` | 22/27 | 9,7 s | 17,6 s | 115.116 / 83.456 / 11.218 |

Custo por rodada, pelos preços de 08/10: cerca de US$ 0,05 fora do pico e
US$ 0,09 no pico. O cache cobre cerca de 70% da entrada. Uma mensagem
completa custa perto de US$ 0,003 fora do pico.

Falhas somadas nas três rodadas:

| Tipo | Casos | Coberto por `fix-qualidade-gerador-remoto` |
| --- | --- | --- |
| Negação de evidência não reconhecida como marcação | R2, X2 (1ª); R1, R2, X2 (3ª) | sim (D1) |
| Camada visível acima de 120 palavras ou frase acima de 20 | F05 (1ª); F03, R3 (2ª); R3 (3ª) | sim (D5) |
| Mito citado sem marca ("estudo … foi retratado") | F04 (3ª) | sim (D5) |
| Decomposição com defeito | R3 (1ª) | sim (D2) |

Em nenhuma das três rodadas a guarda deu rótulo errado, e nenhuma etapa
terminou em erro nas duas últimas. Todas as falhas restantes são defeitos de
forma da resposta, que a página entrega mesmo assim. O padrão não troca
enquanto o critério de 27/27 não for cumprido ou revisto pelo grupo.

Conferência do critério revisto (D10), com `fix-qualidade-gerador-remoto`
aplicado até D5 e `deepseek-v4-pro` como padrão:

| Relatório | Casos | Rótulo errado | Etapa em erro | Mediana | Tokens (entrada / cache / saída) | Cumpre D10 |
| --- | --- | --- | --- | --- | --- | --- |
| `20261008-154244` | 26/27 | 0 | 0 | 10,9 s | 137.162 / 107.648 / 13.029 | sim |
| `20261008-154557` | 25/27 | 0 | 1 (L01, extração) | 9,9 s | 118.965 / 99.456 / 11.322 | não |

Na primeira, F03 saiu na forma sem evidência: a ancoragem rebaixou a
resposta, sem rótulo errado. Na segunda, o L01 teve a saída da extração cortada
no limite de tokens (D6 de `fix-qualidade-gerador-remoto`), e F04 citou o mito
sem marca. Como o código mudou depois delas, a conferência recomeça com duas
rodadas novas.

Com D6 aplicado:

| Relatório | Casos | Rótulo errado | Etapa em erro | Mediana | Tokens (entrada / cache / saída) | Cumpre D10 |
| --- | --- | --- | --- | --- | --- | --- |
| `20261008-155424` | 24/27 | 0 | 0 | 11,6 s | 139.953 / 108.288 / 13.184 | não |
| `20261008-155808` | 26/27 | 0 | 0 | 10,1 s | 131.019 / 108.160 / 13.184 | sim |

Falhas: F01 com 121 palavras e F04 com 122 palavras e "foi retratado" sem
marca, os dois depois da nova tentativa por defeito; R4 com 126 palavras, sem
nova tentativa porque a ancoragem já tinha usado a sua; na segunda rodada, F01
com "A mensagem tira de contexto uma entrevista para afirmar que…". A nova
tentativa corrigiu R3 nas duas rodadas.

O bordão e os títulos somam 26 palavras fixas. O prompt da resposta pede 90
palavras para "a resposta inteira", mas o modelo entende como os blocos: 90 +
26 = 116 deixa 4 palavras de folga para o teto de 120, e os blocos saíram com
95 a 100.

**Conferência final do critério (D10, segunda revisão)**, com
`fix-qualidade-gerador-remoto` (D1 a D7) e `fix-teto-resposta` aplicados, duas
rodadas seguidas e completas com o mesmo código. Base: Gemma `143536`, do
mesmo dia, mediana 102,4 s; metade, 51,2 s.

| Relatório | Casos | Eliminatórias | Demais | Mediana | Máximo | Tokens (entrada / cache / saída) | Cumpre |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `20261008-163411` | 26/27 | nenhuma | F03 (acerto) | 9,1 s | 22,0 s | 133.180 / 99.840 / 13.670 | sim |
| `20261008-163734` | 27/27 | nenhuma | nenhuma | 9,9 s | 20,2 s | 129.357 / 104.576 / 12.311 | sim |

O F03 da primeira saiu na forma sem evidência: a ancoragem rebaixou a
resposta, sem rótulo errado. É a segunda vez (também em `154244`); fica de
olho como padrão. Nenhuma das duas rodadas precisou do corte de teto: o alvo
de 80 palavras (D7 de `fix-qualidade-gerador-remoto`) bastou. As gravações da
segunda rodada são as da bancada offline, que volta a 27/27.

Com isso, `deepseek` como padrão do modo `uso` cumpre "Critério de aceite da
troca". O servidor só sobe com ele depois do contato preenchido no termo
(task 5.1).

### D8. Termo de consentimento na página

Pedido do grupo em 08/10/2026 para cumprir a LGPD. O texto pode ter dado
sensível de saúde (art. 11, I) e vai para empresa na China, país sem decisão
de adequação da ANPD; o termo busca o consentimento específico e em destaque
dos arts. 11, I, e 33, VIII.

- O termo é um diálogo na abertura, não o rodapé. O rodapé de D6 continua,
  como lembrete.
- A página manda `consentimento` com a versão do termo (`TERMO_VERSAO`, hoje
  `3`) em cada `POST /verificar`. O servidor confere antes de chamar o gerador.
  A página não é a única barreira.
- Prova do aceite: o log registra "consentimento versão N", com data e hora, a cada verificação,
  sem identificador. É prova fraca, escolhida para não ferir "Nada guardado";
  o piloto tem o TCLE assinado como prova forte.
- Recusa: sem alternativa, o texto `recusa` aponta agências de checagem. Com
  `DONA_CHECA_ALTERNATIVA_LOCAL=sim`, a recusa usa o Ollama, para que o
  consentimento seja livre de fato. A página manda `consentimento: "recusado"`
  e o servidor escolhe `chat_ollama`.
- `CONTATO_DO_GRUPO` no texto era marcador, trocado pelo contato indicado no
  parecer (abaixo).
  Com gerador `deepseek`, o servidor não sobe enquanto o marcador estiver no
  termo, em qualquer modo. Um teste vermelho na suíte travaria o trabalho do
  grupo sem impedir a publicação; a recusa na subida impede.
- Nada disso substitui revisão jurídica; ver task 5.1.

**Parecer de 08/10/2026** (`docs/interface/parecer-termo-lgpd.md`), sobre o
documento `docs/interface/revisao-termo-lgpd.md`:

- O termo atende aos arts. 11, I, e 33, VIII, com correções. A frase "sem seu
  nome e sem seu telefone" saiu, porque prometia uma anonimização que não
  existe; o termo agora diz que nomes no meio do texto não são apagados.
- Controlador: "Residência em IA (UnB / Instituto Eldorado — Grupo 04)".
  Contato: `donacheca@checatudo.com`, no termo e no rodapé.
- O tom da personagem não compromete o consentimento.
- O registro do aceite sem identidade basta; coletar IP ou cookie só para
  provar o aceite feriria a minimização.
- A alternativa local é boa prática, não obrigação.
- O consentimento basta para a transferência internacional, sem
  cláusulas-padrão.
- No piloto, TCLE e termo da página coexistem.
- O rodapé avisa que o serviço é para maiores de 18 anos (art. 14).
- Se a política da DeepSeek (task 5.2) indicar treino com os dados da API, o
  termo ganha a frase "A DeepSeek pode utilizar o texto enviado para
  aprimoramento dos seus sistemas."

Com os textos novos, `TERMO_VERSAO` passou a `2`: quem aceitou a versão 1
aceita de novo. Desvios do texto do parecer: sem negrito e itálico, que a
página mostraria como asteriscos, e "agências de checagem" no lugar de
"agências públicas", porque Lupa, Aos Fatos e Fato ou Fake são empresas
privadas.

### D9. Minimização

`prototipo/entrada/minimizar.py` troca telefone, CPF e e-mail por marcadores
com expressões regulares, só no texto da pessoa, antes da fronteira. Página
lida de link é pública e segue como está. Nome próprio não é removido: não há
como reconhecer nome sem modelo, e erro aí apagaria nome de remédio ou de
cidade.

## Risks / Trade-offs

- [Prompts afinados para Gemma podem render pior na DeepSeek] → a bancada
  real é o portão (task 4.2). Se falhar, primeiro tentar `deepseek-v4-pro`
  (D2). Só depois mexer em prompt, e em change próprio.
- [Rede lenta da máquina do servidor] → a latência medida inclui a rede, e o
  critério usa essa medida.
- [Provedor muda o modelo por trás do nome] → `modelo` gravado no relatório
  (D7). Rodar a bancada de novo antes de cada piloto.
- [Custo foge do controle] → limite de gasto de US$ 5 configurado no painel
  da DeepSeek em 08/10/2026 (task 0.2).
- [Dado de saúde sai do país] → termo de consentimento (D8), minimização
  (D9), aviso no rodapé e TCLE no piloto (D6). Revisão jurídica pendente
  (task 5.1).
- [O que a DeepSeek faz com os dados] → conferido na task 5.2 (abaixo); o
  termo, na versão 3, diz o que a política prevê.

**Política de dados da DeepSeek (task 5.2, issue #197), consultada em
08/10/2026:**

- **Fontes:**
  - [DeepSeek Privacy Policy](https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html),
    atualizada em 10/02/2026;
  - [DeepSeek Open Platform Terms of Service](https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html),
    em vigor desde 29/04/2026.
- **Política separada para a API:** não existe. Os termos da plataforma não
  falam de treino nem de retenção e remetem à política de privacidade geral.
  As páginas `platform.deepseek.com/privacy` e `/terms` recusam acesso
  automático (HTTP 403).
- **Treino:** a política prevê usar os dados pessoais coletados para treinar e
  aprimorar modelos de aprendizado de máquina. Ela lista o direito de recusar
  esse uso (opt-out), sem dizer como pedir. O grupo decidiu não pedir: o
  projeto é trabalho acadêmico, não produto.
- **Retenção:** sem prazo fixo, "for as long as necessary" para as
  finalidades da coleta.
- **Local:** República Popular da China, sob a Hangzhou DeepSeek Artificial
  Intelligence Co., Ltd.; os termos se regem pela lei da China continental.
- **Afirmações descartadas:** um primeiro levantamento afirmou que a API não
  treina com os dados e que os guarda por até 30 dias. Nenhum dos dois
  documentos traz esses trechos, e o próprio levantamento corrigiu isso
  depois. Esses compromissos são de outros provedores de API.
- **Ressalva:** as citações foram lidas por ferramenta automática. As duas
  leituras feitas pelo grupo divergem levemente na redação, mas não no
  sentido. Antes de citar em documento externo, conferir o texto exato no
  navegador.
- **Efeito no termo (versão 3):** "A DeepSeek pode guardar esse texto pelo
  tempo que considerar necessário. A DeepSeek pode utilizar o texto enviado
  para aprimoramento dos seus sistemas." A segunda frase é a que o parecer
  previu na resposta 10 para o caso de treino. Ela substitui "recebe e trata
  o texto conforme as regras do serviço dela". A minimização (D9) e o pedido
  para não escrever nome e dado de saúde ganham peso, porque não há garantia
  de que o texto fique fora do treino.

## Migration Plan

1. Código e testes com a API simulada (tasks 1 a 3).
2. Bancada real com `--gerador deepseek` e com `--gerador ollama` no mesmo
   dia e na mesma rede (task 4).
3. Só com 17/17 e mediana pela metade, `deepseek` vira o padrão do modo `uso`.

Rollback: `DONA_CHECA_GERADOR=ollama`. Nenhum dado migra.
