# Proposal: Pergunta como alegação e conduta sem alegação

**Fase do CBL:** Act. Change aberto em 08/10/2026, a partir do teste manual do
MVP com a DeepSeek.

## Why

Duas mensagens receberam "Meu bem, não achei nessa mensagem nada de saúde pra
conferir. Assunto fora da saúde eu não sei responder.":

1. **"Suco detox cura gripe?"** A fronteira deixou seguir, e a extração não
   achou alegação. O prompt da extração diz "Opinião, desabafo, pergunta e
   pedido não são alegação", e o modelo descartou a pergunta inteira, embora
   ela traga a afirmação "suco detox cura gripe". É o jeito mais comum de uma
   pessoa idosa trazer a dúvida. O banco de estímulos não tinha caso só em
   forma de pergunta: todos afirmam e depois perguntam "é verdade?".
2. **"Cortei o pé com uma enxada, o que devo fazer?"** A fronteira classificou
   como conduta individual, como devia. Mas o texto de conduta, que manda
   procurar o serviço de saúde, só sai junto com a resposta da checagem
   (`interface/fluxo.py`). Sem alegação, o fluxo para na extração, e a pessoa
   ferida recebe só o aviso de "assunto fora da saúde", que ainda contradiz a
   mensagem dela.

O grupo decidiu, em 08/10/2026, que ferimento como esse é urgência, não
conduta: a resposta certa é a de emergência, com o SAMU (192), e não o texto
de conduta, que fala de remédio e tratamento.

O segundo defeito existe desde `add-interface-chat-web`. O primeiro apareceu
com a DeepSeek, que segue o prompt ao pé da letra.

## What Changes

- **MODIFICADO (prompt)** extração: pergunta que embute uma afirmação ("X cura
  Y?", "É verdade que X?") tem a afirmação como alegação. Pergunta sem
  afirmação ("o que devo fazer?") continua fora.
- **MODIFICADO (código)** `interface/fluxo.py`: com fronteira em conduta
  individual e sem alegação para checar, a página mostra o texto de conduta,
  não o aviso `sem_alegacao`.
- **MODIFICADO (código e prompt)** fronteira: ferimento recente (corte,
  queimadura, queda com batida na cabeça, osso quebrado, mordida de animal,
  prego) é risco imediato, pelas regras e pelo prompt do modelo.
- **MODIFICADO (prompt e código)** decomposição: no máximo 6 fatos, 4
  evidências e 4 opiniões; se falhar duas vezes, a resposta segue sem ela, em
  vez de mostrar erro (D6, D7). Achado do teste com um link real.
- **NOVO (dados)** três casos na bancada, `P1` ("Suco detox cura gripe?"),
  `C1` ("Cortei o pé…", urgência) e `C2` (pedido de conduta sem alegação),
  com gravação real.

## Capabilities

### Modified Capabilities

- `fronteira-orientacao-saude`: "Prioridade e bypass em sinal de risco
  imediato" passa a incluir ferimento recente.
- `verificacao-alegacao`: "Extração da alegação verificável" ganha o cenário
  de pergunta.
- `interface-chat-web`: "Mensagem sem alegação de saúde" ganha o caso de
  conduta.

As capacidades vivem em `mvp-copiloto-verificacao` e
`add-interface-chat-web`, ainda não arquivados, e `verificacao-alegacao` foi
modificada também por `fix-qualidade-gerador-remoto`. Ordem de arquivamento:
`mvp-copiloto-verificacao`, `add-interface-chat-web`,
`fix-qualidade-gerador-remoto`, depois este.

## Impact

- Muda o prompt da extração: as gravações da bancada precisam ser refeitas,
  com uma rodada real (cerca de US$ 0,05).
- Vale para os dois geradores.
