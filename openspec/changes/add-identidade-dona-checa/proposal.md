# Proposal: Identidade e voz da Dona Checa

**Fase do CBL:** Act. Change aberto em 07/10/2026, ao lado de
`mvp-copiloto-verificacao`, que segue com as tasks restantes dele. A interface
do chat web fica para o change seguinte, `add-interface-chat-web`.

## Why

O assistente não tem nome, rosto nem voz. As respostas de recusa falam como
"um assistente focado em checar informações", e a resposta de verificação abre
direto no veredito. Para o público do projeto, que recebe a desinformação de
gente próxima no WhatsApp, um tom impessoal soa como mais um aviso, e o alerta
repetido gera dessensibilização (ver `proposal.md` de `mvp-copiloto-verificacao`).

O grupo escolheu, em 07/10/2026, uma persona: **Dona Checa**, uma tia
desconfiada e carinhosa que, antes de dizer qualquer coisa, pergunta de onde a
mensagem veio. A pergunta é o próprio gesto que o produto quer ensinar, então a
voz reforça a métrica primária (discernimento) em vez de competir com ela.

## What Changes

- **NOVO** `identidade-dona-checa`: nome, tratamento carinhoso, bordão da
  resposta, chamada de uso, mensagem de abertura com a pergunta de confiança,
  e a logo com a paleta. A pergunta de confiança não é registrada e fica
  desligada nas sessões de piloto.
- **MODIFICADO** `resposta-formativa`: a camada visível passa a começar com o
  bordão fixo "Peraí, de onde veio isso? Vamos olhar juntos, meu bem.", posto
  pelo código e contado no teto de 120 palavras.
- **MODIFICADO** `fronteira-orientacao-saude`: as respostas padrão de recusa de
  conduta e de desmentido de tratamento caseiro passam a falar na voz da Dona
  Checa, nos canais Web e WhatsApp, sem perder nenhum conteúdo obrigatório.
  Urgência médica e sofrimento psíquico **não mudam**: em crise, a mensagem
  precisa ser lida em segundos, sem personagem.

## Capabilities

### New Capabilities

- `identidade-dona-checa`: nome, voz, textos fixos de abertura e chamada,
  pergunta de confiança fora da medição, logo e paleta.

### Modified Capabilities

- `resposta-formativa`: requirement "Estrutura de quatro blocos" ganha o bordão
  de abertura.
- `fronteira-orientacao-saude`: requirements "Recusa de orientação clínica
  individual" e "Veredito sem prescrição alternativa" ganham respostas padrão
  na voz da Dona Checa.

As duas capabilities modificadas ainda vivem em `mvp-copiloto-verificacao`,
sem arquivamento. O delta segue o precedente de `fix-resposta-sem-evidencia`.

## Out of Scope

- Chat web, tela, servidor e escolha de tecnologia de interface
  (`add-interface-chat-web`).
- Extensão para WhatsApp.
- Qualquer mudança no instrumento de avaliação (decisão 28 de
  `mvp-copiloto-verificacao`): a pergunta de confiança não vira métrica.
- Respostas de urgência médica e de sofrimento psíquico.
- Nome definitivo: "Dona Checa" é provisório; trocar o nome depois é mudança
  de texto e de ativo, não de comportamento.

## Impact

**Entregáveis finais do desafio atingidos:**

- **Solução/protótipo com suporte de IA:** a resposta e as recusas ganham voz
  própria; a interface do change seguinte consome os textos e a logo daqui.
- **Apresentação final (Showcase):** a logo e a persona passam a existir no
  repositório como ativos versionados.

**Código afetado:**

- `prototipo/resposta/estrutura.py`: bordão antes do bloco 1, dentro do teto.
- `prototipo/verificacao/fronteira.py`: leitura das respostas padrão passa a
  sobrepor as deste change às de `mvp-copiloto-verificacao`.
- `prototipo/identidade/` (novo): textos da persona lidos da spec e a pergunta
  de confiança condicionada a `piloto`.
- `docs/identidade/` (novo): logo em SVG e paleta.
- Testes em `prototipo/resposta/tests/` e `prototipo/verificacao/tests/`.
