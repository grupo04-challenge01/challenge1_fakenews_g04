# Proposal: Qualidade com gerador remoto

**Fase do CBL:** Act. Change aberto em 08/10/2026, a partir da bancada de
`add-gerador-api-deepseek`.

## Why

A troca para a DeepSeek cortou a mediana de 102 s para 11 s com
`deepseek-v4-pro`, mas a bancada ficou em 23/27, e o critério de aceite exige
27/27 (relatório `20261008-145132.json`). Três das quatro falhas vêm de duas
fragilidades do protótipo que o Gemma não expunha:

1. **Verificador de mito.** R2 e X2 falharam por frases como "A checagem não
   encontrou nenhum estudo que mostre que a casca do jatobá cura o câncer" e
   "Nenhum estudo mostra que chá de boldo cura hepatite". As duas negam a
   alegação. O verificador (`prototipo/resposta/mito.py`, decisão 14 de
   `mvp-copiloto-verificacao`) já aceita "não há estudo" e "sem prova", mas
   não essas formas. Com o `flash`, o mesmo padrão derrubou F04 e R1.
2. **Decomposição sem nova tentativa.** Em R3, o modelo marcou fatos do relato
   também como opinião e escreveu "a afirmação é verdadeira" dentro do salto.
   A validação barrou, como deve, mas a decomposição não tem a nova tentativa
   com aviso que a resposta já tem (`estrutura.responder`). A pessoa recebeu
   erro num caso verdadeiro.

3. **Defeito de forma sem correção.** Nas três rodadas com `pro`, F03, F05,
   R3 e F04 falharam por camada visível acima de 120 palavras, frase acima de
   20 ou mito citado sem marca. A resposta só pede de novo quando a ancoragem
   falha; defeito de forma sai para a pessoa.

Afrouxar o verificador mexe na régua de avaliação. Por isso o change existe
separado e só aceita formas de negação explícita da existência de evidência,
as mesmas que a régua já aceita com outras palavras. Repetição real do mito,
como "A mensagem promete curar dengue em 24 horas", continua defeito.

## What Changes

- **MODIFICADO (código)** `prototipo/resposta/mito.py`: `MARCA` aceita
  "nenhum/nenhuma (estudo|prova|evidência|pesquisa|dado) (mostra|comprova|
  confirma|indica)" e "não (encontrou|achou|encontramos|achamos) … (estudo|
  prova|evidência|comprovação|dado)" e "sem estudo", ao lado de "sem prova",
  que já conta.
- **MODIFICADO (código)** `prototipo/verificacao/decomposicao.py`: uma nova
  tentativa com os defeitos listados no pedido, como em `estrutura.responder`.
- **MODIFICADO (código)** `prototipo/resposta/estrutura.py`: a nova tentativa
  da resposta passa a valer também para defeito de forma (D5).
- **MODIFICADO (prompt e código)** extração: no máximo 8 alegações, as de
  saúde primeiro, e nova tentativa quando a saída tiver defeito (D6).
- **MODIFICADO (código)** `ChatDeepSeek`: log de saída cortada por limite de
  tokens (D6).
- **MODIFICADO (prompt)** decomposição: pergunta e exclamação da pessoa ("Isso
  é verdade?", "Absurdo!") não são fato, opinião nem conclusão; o salto não
  comenta se algo é verdadeiro.
- **MODIFICADO (dados)** `bancada/gravacoes/`: regravadas, porque a mudança do
  prompt muda a chave de gravação.

## Capabilities

### Modified Capabilities

- `resposta-formativa`: "Ausência de reforço do mito" ganha cenário de negação
  sem a palavra "falso". A nova tentativa por defeito de forma é decisão de
  implementação (D5), sem mudança de requirement.
- `verificacao-alegacao`: "Separação entre tipo de afirmação e valor de
  verdade" ganha cenários de pergunta da pessoa e de nova tentativa;
  "Extração da alegação verificável" ganha o teto de alegações e a nova
  tentativa.

As duas capacidades vivem em `mvp-copiloto-verificacao`, ainda não arquivado.
Ordem de arquivamento: `mvp-copiloto-verificacao` antes deste.

## Impact

- Mais uma chamada ao modelo só quando a decomposição vier com defeito: cerca
  de 10 s e US$ 0,002 com `deepseek-v4-pro`.
- Regravar a bancada custa uma rodada real (US$ 0,11 a 0,21 com `pro`).
- Vale para os dois geradores: o Gemma também passa a ter a nova tentativa.
