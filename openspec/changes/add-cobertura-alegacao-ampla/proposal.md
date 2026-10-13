# Proposal: Veredito por cobertura de alegação mais ampla

**Fase do CBL:** Act. Change aberto em 10/10/2026, a partir do diagnóstico de
duas perguntas que voltaram `evidência insuficiente` no chat.

## Why

Uma pergunta simples, "Vacina de Covid-19 transformam pessoas em jacarés",
recebe `evidência insuficiente`, e a resposta acrescenta "isso não quer dizer
que é falso". Para quem usa a ferramenta, isso é o contrário de ganho de
discernimento: a dúvida sai maior do que entrou.

O diagnóstico de 10/10/2026 mostrou que **não falta corpus**:

- A recuperação devolve, acima do piso de 0,55 e de trechos aptos do
  FactCenter, a checagem da alegação mãe: Boatos.org (04/08/2020), "Vacina
  contra a Covid-19 vai modificar o DNA das pessoas e nos transformar em seres
  geneticamente modificados", e Aos Fatos (04/12/2020), "Vacinas de RNA contra
  a Covid-19 não são capazes de alterar o DNA".
- Não existe checagem da versão "jacaré". O acervo local, a Google Fact Check
  API (0 resultados para "vacina jacaré") e a planilha de notícias de 2026
  recebida pelo grupo foram conferidos.
- Quem devolve `evidência insuficiente` é o modelo, obedecendo ao prompt de
  `prototipo/verificacao/classificacao.py`: "Use este rótulo também quando o
  trecho for de assunto parecido, mas não da mesma alegação". A regra existe
  para os casos G3 (cloroquina) e G4 (jatobá diante de goiabeira) da decisão 12
  de `mvp-copiloto-verificacao`, e precisa continuar valendo para eles.

O que separa o jacaré de G3 e G4 é **implicação**. Se a vacina transformasse
pessoas em jacarés, ela necessariamente alteraria o organismo e o DNA de quem a
toma. A checagem mostra que isso é falso, e, portanto, a versão particular
também é falsa. "Goiabeira cura dengue" não implica "jatobá cura câncer"; por
isso G4 continua sem veredito.

Boato de saúde costuma circular em variações cada vez mais exageradas de uma
alegação que as agências já checaram uma vez. Sem esta regra, a variação
escapa justamente por ser mais absurda.

## What Changes

- **MODIFICADO (prompt)** classificação: além do rótulo, o modelo declara
  `cobertura` (`mesma` ou `ampla`), a `ponte` (por que a alegação da pessoa é
  caso particular da checada) e o `sujeito` da alegação da pessoa.
- **NOVO (código)** verificação de implicação: uma segunda chamada,
  independente, responde só "se P fosse verdade, G seria necessariamente
  verdade?". Qualquer resposta diferente de `sim` rebaixa o veredito.
- **MODIFICADO (código)** `prototipo/verificacao/guarda.py`: veredito com
  `cobertura` `ampla` só sobrevive se passar por todas as travas abaixo; se
  falhar em qualquer uma, cai para `evidência insuficiente` e registra o motivo
  em `rebaixado_por`.
  - rótulo `falso`;
  - veredito da agência `falso`, `boato` ou `fake` em todo trecho citado;
  - checagens de pelo menos duas agências distintas;
  - `sujeito` presente na alegação da pessoa e no texto de cada trecho citado;
  - `ponte` não vazia;
  - verificação de implicação respondida com `sim`.
- **MODIFICADO (código)** `prototipo/resposta/estrutura.py`: abertura própria
  para o veredito por alegação mais ampla ("Falso. Não achamos checagem desta
  versão, mas a alegação mais geral já foi checada como falsa."), e o detalhe
  mostra a alegação checada **literal**, para que a pessoa possa auditar a
  ponte e discordar dela.
- **NOVO (configuração)** `DONA_CHECA_COBERTURA_AMPLA` (`sim`|`nao`, padrão
  `sim`): `nao` desliga a regra sem novo deploy de código, e a guarda volta ao
  comportamento atual.
- **MODIFICADO (avaliação)** o rastro registra `cobertura`, `ponte`, `sujeito`
  e a resposta da implicação. A métrica conta vereditos `ampla` à parte dos
  diretos, e o relatório do piloto traz a revisão humana de cada ponte.
- **NOVO (sonda e bancada)** sonda de cobertura ampla com casos positivos e
  contraexemplos vizinhos sem implicação; casos novos na bancada.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `verificacao-alegacao`: "Classificação com incerteza explícita" passa a
  admitir cobertura por alegação mais ampla, e o requirement novo "Cobertura
  por alegação mais ampla" define as travas e a chave de desligar.
- `resposta-formativa`: o requirement novo "Veredito por alegação mais ampla
  declarado" define a abertura própria e a alegação checada literal no
  detalhe.

As duas capacidades vivem em `mvp-copiloto-verificacao`, ainda não arquivado.
Ordem de arquivamento: `mvp-copiloto-verificacao` e os changes `fix-*` que
modificam as mesmas capacidades antes deste.

## Out of Scope

- **Chip chinês dando "sem dados" online.** Localmente, com o mesmo código e o
  índice compartilhado no Teams, o caso sai `falso` com cobertura direta (Lupa,
  04/08/2020). A divergência é do servidor (índice ausente ou diferente,
  gerador, ou erro exibido como falta de dados) e se investiga lá, com
  `python -m bancada`, sem change de spec.
- **Ampliação de corpus.** A planilha de notícias de 2026 recebida em
  10/10/2026 não tem rótulo de veracidade nem checagem, e nenhuma linha trata
  das alegações do diagnóstico. Não entra.
- **Veredito ampliado para `verdadeiro` ou `fora de contexto`.** Generalização
  verdadeira não torna verdadeira a versão particular. A regra vale só na
  direção do falso.
- **Veredito por conhecimento do modelo** sobre o absurdo da alegação. Continua
  proibido: sem checagem recuperada da alegação mais geral, nada muda.
- Técnica de manipulação errada no bloco 3 ("cura milagrosa" para o caso do
  chip), notada no diagnóstico. É defeito de qualidade da resposta e fica para
  outro change.

## Impact

- **Entregáveis do desafio:** protótipo funcional (copiloto de verificação) e
  relatório de avaliação do piloto, que ganha a contagem separada e a revisão
  das pontes.
- **Código:** `prototipo/verificacao/classificacao.py`, `guarda.py`, novo
  módulo de implicação em `prototipo/verificacao/`, `prototipo/resposta/
  estrutura.py`, `bancada/pipeline.py`, `interface/config.py`,
  `prototipo/avaliacao/metricas.py`; testes ao lado de cada um.
- **Custo:** uma chamada a mais ao modelo **só** quando `cobertura` vier
  `ampla` e as travas de código já tiverem passado. Os casos diretos não ficam
  mais lentos.
- **Bancada:** a mudança do prompt muda a chave de gravação, e as gravações de
  `bancada/gravacoes/` precisam ser regravadas.
