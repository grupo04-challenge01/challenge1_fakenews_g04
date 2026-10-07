# Design: Identidade e voz da Dona Checa

## Context

Ver `proposal.md` para o porquê. Estado atual que molda a abordagem:

- `prototipo/resposta/estrutura.py` monta a camada visível como títulos mais
  blocos (`Resposta.texto`). O prompt pede ao modelo 90 palavras; o código
  barra acima de `TETO_PALAVRAS = 120` e de `TETO_FRASE = 20` por frase. A
  contagem é `len(texto.split())`.
- `prototipo/verificacao/fronteira.py` lê as respostas padrão dos blocos
  `##### Resposta Padrão — <canal>` da spec, do **primeiro** arquivo que existir
  na lista `SPEC`: a spec dentro de `mvp-copiloto-verificacao` e, depois do
  arquivamento, a de `openspec/specs/` (decisão 15 de
  `mvp-copiloto-verificacao`). O delta deste change só traz dois dos quatro
  requirements, então ler "o primeiro que existir" não serve.
- `resposta-formativa` / "Estrutura de quatro blocos" já foi modificado por
  `fix-resposta-sem-evidencia`, também não arquivado. O texto MODIFIED deste
  change parte da versão do fix e só acrescenta o bordão.
- Não há interface no repositório. Nenhum código hoje sabe se uma sessão é de
  piloto: `prototipo/avaliacao/` trata registros depois da sessão.

## Goals / Non-Goals

**Goals:**

- Uma única fonte para cada texto da persona: a spec. O código lê, não copia.
- Bordão sempre igual, em toda resposta de verificação, dentro do teto.
- Pergunta de confiança impossível de ligar por esquecimento numa sessão de
  piloto.
- Logo e paleta versionadas, prontas para `add-interface-chat-web`.

**Non-Goals:**

- Renderizar a pergunta de confiança ou a abertura em tela: isso é da interface.
- Reescrever prompts do modelo com a persona. O modelo continua escrevendo os
  blocos como hoje; a voz entra pelos textos fixos.
- Regerar os relatórios `prototipo/relatorio_sonda_*.json`, que registram
  execuções passadas.

## Decisions

### 1. Bordão posto pelo código, lido da spec

`estrutura.py` lê o bloco `##### Texto — bordao` da spec de
`resposta-formativa` deste change (com fallback para `openspec/specs/` depois
do arquivamento) e o põe antes do primeiro título em `Resposta.texto`. A
verificação de legibilidade passa a contar o texto com o bordão.

O bordão tem 10 palavras pela contagem do código e frases de 5 palavras. Cabe
na folga entre as 90 pedidas ao modelo e as 120 do teto.

Alternativa descartada: pedir o bordão ao modelo no prompt. O modelo varia o
texto e às vezes omite; a regra de "o modelo escreve o conteúdo, o código a
forma" (decisão 18 de `mvp-copiloto-verificacao`) já põe aberturas fixas no
código.

### 2. Respostas padrão por sobreposição

`fronteira.carregar_respostas()` passa a ler uma **base** (a spec de
`mvp-copiloto-verificacao` ou, arquivada, a de `openspec/specs/`) e, por cima,
uma **sobreposição**: a spec delta deste change, quando existir. Chaves
presentes na sobreposição substituem as da base, canal a canal; as ausentes
(urgência e sofrimento psíquico) vêm da base intactas.

Depois que os dois changes forem arquivados, a sobreposição deixa de existir e
`openspec/specs/` já traz o texto novo. Nenhuma mudança de código é necessária
na hora do arquivamento.

Alternativa descartada: copiar os quatro requirements no delta para manter a
leitura de um arquivo só. Duplicaria urgência e CVV num delta que diz não
mexer neles.

### 3. Módulo `prototipo/identidade/`

Funções puras, sem estado:

- `textos() -> dict[str, str]`: lê os blocos `##### Texto — <chave>` da spec
  `identidade-dona-checa` (abertura, pergunta_confianca, opcoes_confianca,
  chamada), mesmo padrão de leitura de `fronteira.py`.
- `pergunta_confianca(*, piloto: bool) -> dict | None`: devolve
  `{"pergunta": str, "opcoes": [str, str, str]}` ou `None` quando
  `piloto=True`. O parâmetro é obrigatório e só aceita palavra-chave: sem
  padrão, quem chama tem de decidir, e o esquecimento vira erro em vez de
  contaminar o piloto.

O módulo não recebe nem devolve a resposta da pessoa. Como não há onde
guardar, "nunca registrar" vale por construção neste change; a interface
herda a obrigação pela spec.

### 4. Logo exportada do canvas aprovado

Os SVGs saem do canvas de 07/10/2026 (marca refinada e retrato original),
autocontidos, sem fonte externa. Arquivos em `docs/identidade/`:

- `dona-checa.svg`: marca refinada em círculo verde-azulado, cabelo `#16292B`,
  detalhes âmbar `#F2A93B` (padrão).
- `dona-checa-original.svg`: retrato original, sem fundo (alternativa).
- `paleta.md`: os cinco valores e as razões de contraste dos pares de texto.

### 5. Pergunta de confiança antes da camada visível

A spec põe a pergunta depois do envio da mensagem e antes da resposta. A
reflexão só tem valor se a pessoa se posicionar antes de ver o veredito. O mock
aprovado já tem esse "Antes, me conta"; a interface decide como intercalar
bordão, pergunta e blocos na tela.

## Risks / Trade-offs

- [Testes que comparam o texto antigo das recusas quebram] → As mudanças são
  esperadas. Os testes passam a comparar com a spec via `carregar_respostas()`,
  não com string literal.
- [Bordão empurra respostas que hoje ficam entre 111 e 120 palavras para fora do
  teto] → A sonda de legibilidade (task 5.4 de `mvp-copiloto-verificacao`)
  passa a contar com bordão. Se a taxa de defeito subir, reduzir as 90 palavras
  pedidas ao modelo, não tirar o bordão da conta.
- [Voz carinhosa lida como infantilização por parte do público] → A spec limita
  "meu bem" a uma vez por mensagem e proíbe ironia. Observação a colher no
  piloto (6.6), sem mudar o instrumento.
- [Dois changes não arquivados modificam o mesmo requirement] → Arquivar
  `fix-resposta-sem-evidencia` antes deste. O texto daqui já contém o do fix.

## Migration Plan

Sem migração de dados. Ordem de arquivamento: `fix-resposta-sem-evidencia`,
`mvp-copiloto-verificacao`, este. Para desfazer, reverter o change: o
fallback de leitura volta aos textos da base.
