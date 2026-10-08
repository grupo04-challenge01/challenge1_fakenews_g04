# Proposal: Gerador por API (DeepSeek)

**Fase do CBL:** Act. Change aberto em 08/10/2026. O grupo decidiu que reduzir
a latência das respostas é a prioridade, e que o principal passo é trocar o
modelo local por um modelo servido por API.

## Why

Hoje cada verificação demora demais para quem está do outro lado. Na bancada
real de 06/10 (`bancada/relatorios/20261006-160955.json`, `gemma4:12b-it-qat`,
MacBook Air M4, 14 casos completos), as medianas por etapa foram:

| Etapa | Mediana (s) | Usa o modelo |
| --- | --- | --- |
| fronteira | 7,6 | sim |
| extracao | 10,6 | sim |
| decomposicao | 15,0 | sim |
| recuperacao | 0,3 | não |
| guarda | 28,1 | sim |
| resposta | 37,3 | sim |

Somadas, as medianas dão cerca de 99 s por mensagem, e mais de 99% desse
tempo é geração. Com link, a bancada de 08/10 passou de 200 s em um caso, e o
servidor real chegou ao tempo máximo (D11 de `add-entrada-por-link`). Pessoa
idosa esperando dois minutos por uma resposta desiste antes de ler.

A recuperação já é rápida. O gargalo é o modelo local de 12B rodando em
notebook. Um modelo servido por API roda em hardware de datacenter e não
disputa memória com o índice.

`add-selecao-modelos-arquitetura-rag` excluiu "contratação de API paga" do
escopo. Este change reabre essa decisão para o gerador, só para o gerador.
Embeddings e índice continuam locais.

## What Changes

- **NOVO** `ChatDeepSeek` em `prototipo/verificacao/modelo.py`, com a mesma
  assinatura de `chat_ollama` (`sistema`, `usuario` → texto JSON). Fala com a
  API compatível com OpenAI da DeepSeek via `httpx`, que já está nas
  dependências. Modelo `deepseek-v4-pro` (design D2), modo sem raciocínio,
  saída JSON.
- **NOVO** escolha do gerador por variável de ambiente `DONA_CHECA_GERADOR`
  (`deepseek` ou `ollama`). Padrão `deepseek` no modo `uso` e `ollama` no
  modo `piloto`. Sem `DEEPSEEK_API_KEY`, o servidor não sobe com gerador
  `deepseek`.
- **NOVO** aviso fixo na página quando o gerador é remoto: a mensagem vai para
  um serviço de fora do Brasil, e a pessoa não deve mandar dados pessoais.
- **NOVO** termo de consentimento na abertura da página quando o gerador é
  remoto: "Aceito" ou "Não aceito" antes de qualquer envio, com conferência no
  servidor e alternativa local opcional para quem recusa (D8, pedido do grupo
  em 08/10/2026 para cumprir a LGPD).
- **NOVO** minimização: telefone, CPF e e-mail saem do texto antes do envio ao
  gerador remoto (D9).
- **MODIFICADO (código)** `bancada`: opção `--gerador`, e o relatório passa a
  registrar gerador, modelo e tokens usados, para comparar latência, acerto e
  custo antes e depois.
- **NOVO (configuração)** `.env.example` sem chave. `.env` já é ignorado
  pelo `.gitignore`.
- Prompts, etapas, guarda e regras de veredito não mudam.

## Capabilities

### New Capabilities

- `gerador-modelo`: escolha do gerador, chamada à API remota, segredo da
  chave, falhas e critério de aceite (latência e bancada).

### Modified Capabilities

- `interface-chat-web`: novos requirements "Aviso de serviço externo" e
  "Consentimento antes do envio ao serviço externo".

## Impact

- **Custo:** API paga por token. Preço de `deepseek-v4-pro` conferido em
  08/10/2026 na página oficial: US$ 0,66 a 1,32 por milhão de tokens de
  entrada sem cache, US$ 0,022 a 0,044 com cache e US$ 1,98 a 3,96 por milhão
  de saída, conforme o horário. Medido na bancada: cerca de US$ 0,003 por
  mensagem fora do pico. Limite de gasto de US$ 5 na conta.
- **Privacidade:** o texto da pessoa sai do servidor do projeto e vai para a
  DeepSeek. "Nada guardado" continua valendo para o nosso servidor, mas o
  projeto não controla o que o provedor retém. Por isso o aviso na página e o
  padrão `ollama` no modo piloto. Usar DeepSeek no piloto exige frase nova no
  TCLE antes, e essa decisão fica com o grupo (design D6).
- **Dependência de terceiro:** sem internet ou com a API fora do ar, a
  verificação falha com o texto `erro`. O Ollama continua disponível pela
  variável.
- **Reprodutibilidade:** o modelo remoto pode mudar sem aviso. A bancada
  registra o nome do modelo devolvido pela API em cada relatório.
- **Avaliação:** o modelo muda, então o comportamento dos prompts pode mudar.
  A bancada real precisa passar 17/17 de novo antes de a troca valer.
