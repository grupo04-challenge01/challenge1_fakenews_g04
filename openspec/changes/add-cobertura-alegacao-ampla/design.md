# Design: Veredito por cobertura de alegação mais ampla

## Context

Motivação e diagnóstico em `proposal.md`. Requirements em
`specs/verificacao-alegacao/spec.md` e `specs/resposta-formativa/spec.md`.

Estado atual relevante:

- `classificacao.classificar` devolve `rotulo`, `trechos` e `criterio`. O
  prompt manda usar `evidência insuficiente` para "assunto parecido, mas não a
  mesma alegação".
- `guarda.verificar` aplica três travas em código (decisão 12 de
  `mvp-copiloto-verificacao`): sem trecho, o modelo não é chamado; o piso
  `LIMIAR_EVIDENCIA` = 0,55 vale por trecho; e veredito sem trecho citado, ou
  que cita trecho inventado, é rebaixado. Só trecho com `apto_citacao`
  verdadeiro chega ao modelo.
- Cada trecho recuperado traz `agencia`, `alegacao` (o título da checagem),
  `veredito_original`, `veredito_chave` e `trecho`.
- `bancada.pipeline.executar` chama a guarda com `k=5`. A interface entra por
  `interface/fluxo.verificar`, e a configuração vem de variável de ambiente em
  `interface/config.py`.
- `estrutura.ABERTURA` mapeia rótulo para a frase fixa do bloco 1, e
  `estrutura._detalhe` monta o detalhe com `agencia`, `data_publicacao`, `url`,
  `veredito_original` e `trecho`. A página mostra esses campos
  (`interface/estatico/chat.js`, `detalhe`).

Medido em 10/10/2026, com o índice compartilhado e o Gemma local: para o
jacaré, os cinco primeiros trechos ficam entre 0,5925 e 0,5718, todos aptos,
de Boatos.org e Aos Fatos. O modelo devolve `evidência insuficiente` com o
critério "nenhum dos trechos menciona jacarés".

## Goals / Non-Goals

**Goals:**

- Jacaré e chip chinês saem `falso` por cobertura ampla quando só a alegação
  geral está no acervo, e G3, G4 e os contraexemplos continuam `evidência
  insuficiente`.
- Toda trava que pode ser checada sem modelo fica em código, na guarda.
- A regra pode ser desligada sem mudar código.

**Non-Goals:**

- Mudar recuperação, piso, `k` ou índice.
- Detectar implicação sem modelo.
- Cobertura ampla para rótulo diferente de `falso`.

## Decisions

### D1. Classificação declara a cobertura; a guarda decide se ela vale

O prompt de `classificacao.py` ganha três campos de saída:

- `cobertura`: `"mesma"` ou `"ampla"`;
- `ponte`: uma frase, obrigatória quando `ampla`, dizendo por que a alegação é
  caso particular da checada;
- `sujeito`: o produto, a substância ou a intervenção de que a alegação fala,
  com as palavras da própria alegação.

A regra do prompt deixa de ser "assunto parecido é insuficiente" e passa a ser:
"Se nenhum trecho checa esta alegação, mas um trecho checa como falsa uma
alegação mais geral, da qual esta é caso particular (se esta fosse verdade, a
geral também seria), use `falso` com `cobertura` `ampla`. Assunto parecido sem
essa implicação continua `evidência insuficiente`." O prompt traz G4 como
exemplo negativo, porque é o caso que a decisão 12 mediu.

`defeitos` passa a recusar `cobertura` fora de {`mesma`, `ampla`} e a exigir
`ponte` e `sujeito` não vazios quando a cobertura for `ampla`. Defeito de forma
segue o caminho que já existe. Campo `cobertura` ausente conta como `mesma`
(decidido na task 1.1): é exatamente o comportamento anterior, sem trava nova
a contornar, e mantém válidas as saídas fixas dos testes atuais. O rastro
registra `mesma` nesse caso.

**Alternativa descartada:** a guarda detectar sozinha a cobertura ampla,
comparando a alegação com o título da checagem. Isso exige julgamento
semântico, e esse julgamento é a própria tarefa do modelo.

### D2. Travas de código antes da chamada de implicação

`guarda._classificar`, quando `cobertura == "ampla"`, aplica nesta ordem e
para na primeira que falhar, com `rebaixado_por` específico:

1. cobertura ampla desligada → `"cobertura ampla desligada"`;
2. rótulo diferente de `falso` → `"cobertura ampla só vale para falso"`;
3. algum trecho citado com `veredito_chave` fora de {`falso`, `boato`,
   `fake`} → `"cobertura ampla com veredito da agência <v>"`;
4. menos de duas agências distintas entre os trechos citados →
   `"cobertura ampla com uma agência só"`;
5. `sujeito` ausente da alegação ou de algum trecho citado (D3) →
   `"sujeito <s> ausente de <onde>"`;
6. implicação (D4) diferente de `sim` → `"implicação não confirmada: <r>"`.

As travas 1 a 5 são baratas e rodam antes da 6, que custa uma chamada. Os
valores aceitos de `veredito_chave` saem do mapa de vereditos já normalizado
(`tratamento/mapa_vereditos.json`); a lista fica numa constante, com teste
contra o mapa.

### D3. Âncora do sujeito por palavra normalizada, não por `ancoragem.termos`

O plano da exploração era usar `ancoragem.termos`. Lendo o código, `termos` só
devolve número, mês, número por extenso e palavra com inicial maiúscula fora
do início de frase. Para "Vacinas causam autismo", ela devolve lista vazia, e
uma âncora vazia passaria sempre.

A âncora usa `ancoragem.normalizar` (minúscula, sem acento) sobre as palavras
do `sujeito`, sem as palavras vazias (`de`, `da`, `do`, `contra`, `a`, `o`…) e
com o `s` final retirado, para que "vacinas" case com "vacina". Cada palavra que
sobra precisa aparecer na alegação da pessoa e no texto (`alegacao` mais
`trecho`) de cada trecho citado. Se o sujeito ficar vazio depois da limpeza,
a trava falha.

Exemplo: o sujeito "vacinas da COVID-19" vira {`vacina`, `covid`, `19`}. O
trecho da Lupa traz "vacinas contra a Covid-19" e passa. Uma checagem de
cloroquina diante de "vacina" não passa.

### D4. Verificação de implicação: chamada independente e cega

Módulo novo, `prototipo/verificacao/implicacao.py`, com `confirmar(p, g,
chat)`. O modelo recebe só duas frases: P, a alegação da pessoa, e G, o campo
`alegacao` do trecho citado de maior score. Não recebe a `ponte`, o critério nem
o rótulo da classificação, para não ser induzido a concordar. A pergunta:
"Se a frase A fosse verdade, a frase B seria necessariamente verdade? Responda
só com JSON: {"resposta": "sim" | "não" | "incerto"}".

Só `"sim"` confirma. `"não"`, `"incerto"`, saída que não é JSON e erro do
gerador rebaixam. Uma tentativa, sem nova tentativa: na dúvida, a regra cai
para o comportamento atual.

**Alternativa descartada:** pedir à mesma chamada da classificação que se
autoconfira. Isso não acrescenta independência. Também foi descartado
conferir a implicação contra todos os trechos citados: a primeira checagem
de maior score já é a alegação geral, e cada chamada a mais custa latência.

### D5. Chave de desligar

`interface/config.py` ganha `cobertura_ampla: bool`, lido de
`DONA_CHECA_COBERTURA_AMPLA` (`sim` | `nao`, padrão `sim`), com o mesmo erro de
configuração das outras variáveis para valor inválido. O valor desce por
`fluxo.verificar` → `executar(cobertura_ampla=…)` → `guarda.verificar(ampla=…)`
e fica registrado em `rastro["parametros"]`. A bancada ganha
`--sem-cobertura-ampla`.

Desligada, a classificação continua pedindo `cobertura`; a guarda é que
rebaixa (trava 1). Assim o rastro mostra quantos vereditos a regra teria dado.

### D6. Resposta: abertura própria e alegação literal no detalhe

`Veredito` ganha `cobertura`, `ponte` e `sujeito`. Em `estrutura`:

- `_abertura` devolve o texto `abertura_ampla` da spec quando
  `veredito.cobertura == "ampla"`. O texto é lido da spec, como o bordão, e
  nunca vem do modelo.
- O pedido ao modelo (`mensagem`) informa `COBERTURA: alegação mais ampla` e a
  ponte, para que o bloco 1 diga qual alegação geral foi checada.
- `_detalhe` acrescenta `alegacao_checada` (o campo `alegacao` do trecho,
  literal) a cada item. A `ponte` vai uma vez, em `Resposta.ponte`, e o evento
  `resposta` da interface a leva ao lado do `detalhe`. `chat.js` mostra os
  dois. Só na cobertura ampla; nas demais respostas o detalhe não muda.

Rebaixamento pela ancoragem ou pela conferência já troca a forma para sem
evidência; a abertura ampla some junto, porque depende do rótulo final.

### D7. Rastro, métrica e revisão das pontes

- O rastro da etapa `guarda` já serializa o `Veredito`; com os campos novos,
  passa a trazer `cobertura`, `ponte`, `sujeito` e a resposta da implicação.
- `prototipo/avaliacao/metricas.py` separa por cobertura as taxas que dependem
  do rótulo exibido (discernimento e aceitação cega quando a IA erra). Item sem
  o campo conta como `mesma`.
- A bancada grava, a cada rodada, uma lista das pontes emitidas (caso,
  alegação, alegação checada, ponte, resposta da implicação) em
  `bancada/relatorios/`, que o relatório do piloto usa para a revisão humana.

### D8. Sonda antes da bancada

Sonda nova, `prototipo/sonda_cobertura_ampla.py`, no molde de
`sonda_classificacao_guarda.py`: trechos fixos, sem recuperação, rodando a
guarda inteira. Casos:

| id | alegação | trechos | esperado |
| --- | --- | --- | --- |
| A1_jacare | Vacina de Covid-19 transformam pessoas em jacarés | Boatos.org DNA + Aos Fatos DNA | `falso`, `ampla` |
| A2_chip_chines | Vacinas da COVID-19 têm chips chineses para nos monitorar | Boatos.org "nanochip 5G" + Fato ou Fake "chip líquido" | `falso` (`mesma` ou `ampla`) |
| N1_goiabeira_2ag | Chá de folha de goiabeira cura a dengue em 24 horas | jatobá de duas agências | insuficiente |
| N2_cloroquina_2ag | Tomar hidroxicloroquina toda semana previne a covid | cloroquina de duas agências, sem tratar de eficácia (Lupa "Doria proibiu" + Aos Fatos "Bruno Covas não proibiu") | insuficiente |
| N3_autismo_dna | Vacinas causam autismo | Boatos.org DNA + Aos Fatos DNA | insuficiente |
| N4_miocardite | A vacina da covid pode causar miocardite em alguns jovens | "vacina causa danos graves ao coração de todos" de duas agências | insuficiente |
| N5_uma_agencia | Vacina de Covid-19 transformam pessoas em jacarés | só Boatos.org DNA | insuficiente (trava 4) |
| N6_enganoso | (A1) | Boatos.org DNA + checagem com veredito enganoso | insuficiente (trava 3) |

N1 e N2 repetem G4 e G3 com duas agências, para que a trava 4 não esconda uma
falha da implicação. Aceite: A1 e A2 `falso` em 3 de 3 rodadas; N1 a N6
insuficientes em 3 de 3 rodadas, sem exceção. Basta um falso positivo para
reprovar.

**Troca dos trechos do N2 (13/10/2026).** A primeira versão do N2 usava
`6c68e7c0eb-00-00` (Aos Fatos, médica engana ao dizer que cloroquina cura) e
`3fe3ac1240-00-00` (Lupa, cloroquina não é "100% eficiente"). Os dois dizem
que a hidroxicloroquina não tem efeito sobre a Covid-19, o que refuta
"previne" diretamente: o `falso` com cobertura `mesma` estava certo, e o caso
não media a implicação. A sonda com o Gemma de 10/10/2026 expôs o problema
(N2 0/3, `falso`/`mesma`; o prompt da `main` dá o mesmo resultado 3 de 3), e a
rodada com o DeepSeek de 13/10/2026 repetiu (0/3, `falso`/`mesma`). Os trechos
passaram a ser `17683b01f4-00-00` (Lupa, é falso que Doria proibiu cloroquina)
e `e1320a8aaf-00-00` (Aos Fatos, Bruno Covas não proibiu cloroquina): mesmo
remédio, duas agências, veredito `falso`, aptos, e nenhuma palavra sobre
eficácia.

O texto de cada trecho vem do índice (`unidades.jsonl`), escolhido pelo
`unidade_id` e congelado na sonda, como na sonda da decisão 12. Para N4, se o
acervo não tiver checagem com essa forma, o caso usa trecho escrito para a
sonda e marcado como sintético.

**Troca do texto sintético do N4 (13/10/2026).** O trecho dizia que "casos de
inflamação no coração são raros e em geral leves", o que sustenta "pode causar
miocardite em alguns jovens" diretamente. Com o DeepSeek, o prompt da `main`
deu `verdadeiro` 3 de 3 nesse caso, e o do change deu `falso`/`mesma` uma vez.
Os dois trechos passaram a negar só a alegação geral, sem dizer nada sobre a
miocardite existir ou não.

**Resultados de 13/10/2026** (trechos novos do N2 e do N4, prompts do commit
`d0c4fb4b`):

| caso | DeepSeek (`deepseek-v4-pro`) | Gemma (`gemma4:12b-it-qat`) |
| --- | --- | --- |
| A1_jacare | 0/3, `ampla`, implicação "não" 3/3 | 0/3, `ampla`, citou um trecho só (trava 4) |
| A2_chip_chines | 3/3, `mesma` | 3/3, `mesma` |
| N1_goiabeira_2ag | 3/3 | 3/3 |
| N2_cloroquina_2ag | 3/3 | 3/3 |
| N3_autismo_dna | 3/3 | 3/3 |
| N4_miocardite | 2/3; 1 `verdadeiro fora de contexto` (`mesma`) | 3/3 |
| N5_uma_agencia | 3/3 | 3/3 |
| N6_enganoso | 3/3 | 3/3 |

Aceite não cumprido nos dois geradores, só por A1. Nenhum `falso` em caso N, e
nenhum veredito saiu pelo caminho `ampla`. A falha do N4 no DeepSeek não vem da
cobertura: com os trechos novos, o prompt da `main` dá `verdadeiro fora de
contexto` 5 de 5 no mesmo caso.

**A implicação não confirma jacaré => DNA em nenhum dos dois modelos.** Em
bancada isolada, só com a chamada de implicação, os dois responderam "não" em
todas as tentativas. Testamos três formas de G: a alegação do Boatos.org, a do
Aos Fatos e uma frase limpa ("A vacina contra a Covid-19 altera o DNA de quem a
toma"). Testamos também a pergunta pela contrapositiva ("se B for falsa, A
também tem de ser falsa?") e duas revisões do prompt: o que A exigiria, exemplo
negativo autismo diante de DNA e proibição de mecanismo fora da ciência. Nada
mudou o resultado. A justificativa pedida ao DeepSeek foi a mesma nas duas
revisões: "transformar em jacaré não exige alteração de DNA". Os contraexemplos
seguiram em "não" em todas as variantes. As revisões não entraram no código,
porque não houve ganho medido e havia risco de deixar a verificação mais
leniente.

**Change bloqueado (decisão do grupo, 13/10/2026).** A regra fica como está,
conservadora, e a spec não muda. Os cenários "Versão exagerada de alegação já
checada" (`verificacao-alegacao`) e "Jacaré" (`resposta-formativa`) não são
cumpridos pelo código atual. Por isso as tasks 7.2, 7.3, 7.4 e 8.1 seguem
abertas, e o change não vai para merge como pronto. Na bancada de 13/10/2026
(`deepseek-v4-pro`), os casos atuais ficaram em 28/30, a mesma contagem da
rodada anterior. A1_jacare_ampla falhou pela implicação, e N3_autismo_sem_ampla
passou.

## Risks / Trade-offs

- [O modelo classifica como `mesma` um caso que é `ampla` e escapa das travas]
  → A sonda confere a cobertura declarada em A1 e N3. O prompt dá a definição
  de `mesma` ("o trecho checa esta alegação, com outras palavras"). O rastro
  conta as duas coberturas, e a revisão das pontes pega o padrão no piloto.
- [Implicação aprovada por um modelo leniente] → Chamada cega (D4), e só `sim`
  confirma. Os contraexemplos N1 a N4 medem exatamente isso, com o Gemma e com
  o gerador remoto.
- [A âncora do sujeito barra caso legítimo por variação de palavra
  ("imunizante" no lugar de "vacina")] → Aceito: o custo é voltar ao
  comportamento atual, `evidência insuficiente`, nunca um veredito errado.
- [Duas agências reduzem a cobertura] → Aceito, por decisão de 10/10/2026.
  Fica registrado em `rebaixado_por`, e a contagem no piloto diz se a trava
  custa caro.
- [Latência] → Uma chamada a mais, só no caminho `ampla` depois das travas de
  código. O caminho direto não muda.
- [A pessoa lê o veredito ampla como checagem direta] → Abertura fixa que diz
  o contrário, e alegação checada literal no detalhe para auditar a ponte.

## Migration Plan

1. Mesclar com `DONA_CHECA_COBERTURA_AMPLA` no padrão `sim`.
2. Regravar a bancada (o prompt muda a chave de gravação). A regravação com o
   gerador remoto exige a chave DeepSeek válida, que não está em todas as
   máquinas do grupo; quem tem a chave roda.
3. Rollback: `DONA_CHECA_COBERTURA_AMPLA=nao` no servidor. Reverter o código só
   se o prompt novo piorar os casos de cobertura `mesma`, o que a bancada
   mostra.
