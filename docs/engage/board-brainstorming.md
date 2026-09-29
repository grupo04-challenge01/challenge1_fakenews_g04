# Board do brainstorming — cinco quadros

Task 1.3 do change `add-engage-desinformacao-saude`. Template da sessão de
~90 minutos do bloco 3.

As notas efetivamente produzidas na sessão estão transcritas neste arquivo, uma
seção por quadro, com o destino de cada uma. Total: **40 notas** — Problema 19,
Público 5, Específicas 9, Solução 7, Sucesso 0. A transcrição é literal,
inclusive nos erros de digitação das notas originais.

Regra de contagem dos destinos, para que os números fechem:

- **`GQ-nn`** — a nota deu origem àquela guiding question.
- **`fundida em GQ-nn`** — a nota foi absorvida por uma guiding question que
  outra nota já originava. É esta classe que o `guiding-questions.md` conta como
  `fundida`, e por isso seis notas fundidas convivem com doze guiding questions.
- **`fechada`** — já respondida por decisão registrada; não consome tempo do
  Investigate.
- **`descartada`** — falha o critério de qualidade.

Fechamento: 18 notas mantidas (que produzem as 12 guiding questions, sendo 6
fundidas), 10 fechadas e 12 descartadas. 18 + 10 + 12 = 40. O detalhamento por
guiding question está em [Guiding Questions](guiding-questions.md).

Os cinco quadros são os que a capability `guiding-questions` nomeia, e a
rastreabilidade depende deles: **cada guiding question MUST estar associada ao
quadro que a originou**. Quadro improvisado na hora quebra essa rastreabilidade.

## Regras da sessão

Três, e as três existem por um motivo registrado:

**1. Problema e Público rodam em modo privado primeiro.** Cada pessoa escreve
suas notas sem ver as dos outros, e só depois o quadro é aberto. É a task 3.1,
e serve para evitar ancoragem — a primeira ideia dita em voz alta contamina as
seguintes.

Os dois quadros rodaram nessa forma, e o grupo confirmou a condução fechada em
24/09/2026. O quadro Sucesso saiu desta regra na mesma data, por decisão
registrada em `openspec/changes/add-engage-desinformacao-saude/design.md`:
ancoragem só é risco onde há divergência, e o conteúdo de Sucesso já vem
fixado pela restrição de produto.

**2. O quadro Solução é só hipótese.** Nada se decide ali. É a task 3.2. A fase
Engage é para entender o desafio; decidir solução na semana 1 é o modo mais
comum de fechar escopo antes de conhecer o problema.

**3. Na matriz de priorização entram perguntas, não soluções.** É a task 3.3, e
os eixos são **impacto × incerteza**. Esforço MUST NOT ser eixo nesta fase —
está em texto expresso na capability.

---

## Quadro 1 — Problema

> O que torna difícil, hoje, distinguir fato de boato em saúde?

Notas aqui descrevem o problema como ele é vivido, não a solução.

**Este quadro tem evidência quantitativa disponível.** Os tempos medidos na
investigação forense (campo 6 das fichas) entram aqui como dado, consolidados em
mínimo, máximo e mediano. É a task 2.4. Sem eles, o quadro vira opinião — e a
capability exige que esse dado seja referenciado como justificativa do problema.

| Modo | Privado primeiro, depois aberto |
| --- | --- |

### Notas da sessão — 19

| ID | Nota | Destino |
| --- | --- | --- |
| PR-01 | O quanto a qualidade de ensino afeta para alguém cair em uma fake news? | descartada |
| PR-02 | quais são os perigos imediatos do consumo descontrolado de substâncias ineficazes ou tóxicas incentivadas por correntes de redes sociais? | fundida em GQ-08 |
| PR-03 | Como a desinformação afeta a saúde em geral? | descartada |
| PR-04 | Como sistemas de IA podem ajudar as pessoas a avaliar a confiabilidade de informações sem substituir seu pensamento crítico? | descartada |
| PR-05 | Como o design das redes sociais e os algoritmos de recomendação favorecem conteúdos sensacionalistas ou inverídicos? | descartada |
| PR-06 | Qual sistema de ia pode ajudar as pessoas a terem informações mais confiáveis em relação à saúde? | descartada |
| PR-07 | Como avaliar a confiabilidade e raiz dessas notícias? | fechada |
| PR-08 | Quais tipos de desinformação são mais frequentes no contexto brasileiro e qual deles é mais tratável? | GQ-01 |
| PR-09 | Como a informação fornecida pela IA pode impactar no pensamento crítico do usuário? | GQ-12 |
| PR-10 | Como diferenciar "usar a IA como ferramenta" de "deixar a IA pensar por nós"? | fundida em GQ-12 |
| PR-11 | De que forma a IA pode estimular o pensamento crítico em vez de substituí-lo? | fundida em GQ-12 |
| PR-12 | Em que ponto a verificação falha hoje: falta de método, custo de tempo, ou falta de intenção? | GQ-10 |
| PR-13 | Qual o dano concreto de acreditar errado nesse recorte específico (saúde, eleição, golpe financeiro)? | fechada |
| PR-14 | Que evidência mostra que esse problema vale ser resolvido? volume de checagens, tempo entre publicação e desmentido, alcance | GQ-05 |
| PR-15 | A IA deveria sempre apresentar as fontes utilizadas para chegar a uma resposta? | fechada |
| PR-16 | O que já existe relacionado a este tema que pode ser utilizado para compreender como ajudar na confiabilidade de informações sobre saúde utilizando IA? | descartada |
| PR-17 | de que forma boatos e promessas de "curas milagrosas" fazem com que pacientes abandonem tratamentos convencionais comprovados (como quimioterapia, insulina ou medicamentos de uso contínuo)? | GQ-08 |
| PR-18 | Como o tempo para combater a desinformação ajuda a fazer com que a desinformação se espalhe menos e se torne menos impactante? | descartada |
| PR-19 | Como esse tema ajuda na ODS 3? | descartada |

### Evidência quantitativa — tempos da investigação forense

Dados consolidados a partir do campo 6 das seis fichas em `docs/forense/`
(task 2.4 de `add-engage-desinformacao-saude`).

| Caso | Tipo de manipulação | Tempo (min) |
| --- | --- | ---: |
| 01 — Febre amarela | Fabricação integral | 10 |
| 02 — Inhame e dengue | Fabricação integral (atribuição falsa) | 20 |
| 03 — Vídeo de 2018 | Recontextualização de mídia antiga | 20 |
| 04 — Bula e autismo | Exagero / distorção de documento real | 24 |
| 05 — Vídeo Anvisa | Recontextualização de mídia antiga | 33 |
| 06 — Fígado Sorocaba | Exagero / distorção de documento real | 43 |

| Medida | Valor |
| --- | ---: |
| **Mínimo** | **10 min** |
| **Mediana** | **22 min** |
| **Máximo** | **43 min** |

**Leitura do dado.** Verificar com rigor custa de 10 a 43 minutos; decidir
acreditar custa 3 segundos. A assimetria é o problema: o custo de tempo da
verificação é incompatível com o ritmo de chegada das mensagens. É essa
assimetria que a ferramenta precisa comprimir — sem eliminar o raciocínio, que é
o que a Essential Question exige preservar.

Consolidação registrada em 25/09/2026. Os dados também constam no Miro do grupo.

---

## Quadro 2 — Público

> Quem é a pessoa que recebe a mensagem e precisa decidir se acredita?

Notas sobre quem é, onde recebe, o que já sabe, quanto tempo tem, e o que a faz
encaminhar.

O projeto já tem material que informa este quadro, e convém trazê-lo: o acervo
de circulação mostra **o que circulou, em que canal e quando**, e o viés de
amostra dele está declarado — comunidades públicas e engajadas, não a pessoa
comum. Isso é insumo, não resposta.

| Modo | Privado primeiro, depois aberto |
| --- | --- |

### Notas da sessão — 5

| ID | Nota | Destino |
| --- | --- | --- |
| PU-01 | Quais critérios as pessoas realmente usam para decidir se acreditam e onde esses critérios falham? | GQ-09 |
| PU-02 | Quem é o usuário-alvo: o cético que quer verificar mas desiste, ou quem nem cogita verificar? | fechada |
| PU-03 | Quem fica explicitamente fora do escopo, e por quê? | fechada |
| PU-04 | Que alternativas o usuário usa hoje (perguntar no grupo, googlar a manchete, ChatGPT) e por que elas bastam ou não? | fundida em GQ-09 |
| PU-05 | o que faz uma pessoa confiar imediatamente em uma postagem de saúde: o visual bonito, o número de seguidores de quem postou ou se foi enviado por alguém próximo? | fundida em GQ-09 |

O insumo do acervo de circulação citado acima não foi trazido à sessão. As cinco
notas são do grupo, não do acervo.

---

## Quadro 3 — Específicas

> O que precisamos descobrir para agir?

É o quadro que mais alimenta as guiding questions. Notas aqui são lacunas de
conhecimento, não tarefas.

| Modo | Aberto |
| --- | --- |

### Notas da sessão — 9

| ID | Nota | Destino |
| --- | --- | --- |
| ES-01 | como o bombardeio contínuo de conteúdos alarmistas (sobre falsas contaminações ou efeitos colaterais inexistentes) afeta a ansiedade e o bem-estar psicológico da população? | descartada |
| ES-02 | Como um sistema de IA pode identificar informações falsas sobre saúde a partir da análise de evidências científicas e fontes confiáveis? | fechada |
| ES-03 | Como fazer a informação confiável chegar também a quem tem dificuldade de acesso, conhecimento técnico ou letramento digital? | fechada |
| ES-04 | Como comunicar que o consenso científico é provisório sem alimentar a ideia de que "então ninguém sabe nada"? | GQ-07 |
| ES-05 | Como distinguir, de forma automatizável, alegação falsa de alegação real exagerada? | GQ-02 |
| ES-06 | O que a literatura já mostra sobre eficácia de correção de desinformação em saúde, incluindo efeitos contraproducentes? | GQ-06 |
| ES-07 | Que sinais de qualidade de evidência são extraíveis de um texto de divulgação, e quando é preciso ir ao artigo original? | GQ-03 |
| ES-08 | Onde traçar a fronteira entre avaliar informação e dar orientação de saúde? | fechada |
| ES-09 | Como lidar com o caso em que a fonte oficial mudou de posição? | GQ-04 |

Quadro de maior rendimento: cinco das nove notas viraram guiding question.

---

## Quadro 4 — Solução

> Que formas isso poderia ter?

**Hipóteses apenas.** Nada aqui é decisão, e nada daqui entra na matriz de
priorização — a matriz é de perguntas.

| Modo | Aberto |
| --- | --- |

### Notas da sessão — 7

| ID | Nota | Destino |
| --- | --- | --- |
| SO-01 | Em que momento da jornada (antes de ler, ao ler, antes de compartilhar) a intervenção tem mais efeito? | descartada |
| SO-02 | Como apresentar evidência sem induzir a conclusão: perguntas socráticas, evidência crua ou resumo? | fechada |
| SO-03 | Como representar confiança sem colapsar em nota única ou veredito? | fechada |
| SO-04 | Quais arquiteturas ou modelos de IA são mais adequados para verificar fontes sem gerar respostas absolutistas? | descartada |
| SO-05 | Qual o atrito máximo que o usuário aceita antes de abandonar? | GQ-11 |
| SO-06 | Quis as premissas mais arriscadas? Que as pessoas aceitam não receber veredito; que evidência muda decisão; que o efeito persiste sem a ferramenta. | descartada |
| SO-07 | quanto atrito o usuário tolera antes de desistir de checar uma informação no whatsapp ou nas redes? (Ex: abrir um bot, responder a 3 perguntas ou ler uma matéria rapida) | fundida em GQ-11 |

As sete notas estão em forma de pergunta ou de lista de suposição. Nenhuma
decisão foi tomada no quadro, como a regra 2 exige. A única nota que chegou à
matriz de priorização, SO-05, chegou como pergunta (GQ-11).

---

## Quadro 5 — Sucesso

> Como saberíamos que funcionou?

Notas sobre o que seria observável se o projeto desse certo.

A restrição do projeto já fixa parte disso e vale relembrar antes de abrir o
quadro: a métrica primária é **ganho de discernimento do usuário, incluindo
transferência** — desempenho sem a ferramenta —, e não acurácia de
classificador. Notas que proponham acurácia como medida de sucesso devem ser
confrontadas com essa restrição na hora.

| Modo | Privado primeiro, depois aberto |
| --- | --- |

### Notas da sessão — 0

**Este quadro não recebeu nenhuma nota do grupo, e não vai receber.** Os bullets
acima são texto do template, escrito antes da sessão, não produção dela.

**Decisão de 24/09/2026:** Sucesso não roda como quadro de divergência. O
requirement «Rastreabilidade até o brainstorming» exige que cada guiding
question tenha um quadro de origem declarado, não que todo quadro produza
guiding question — e as 12 têm. As métricas que este quadro produziria já estão
fixadas pela restrição de produto de `openspec/project.md` e absorvidas pela
capability `avaliacao-instrumento` de `mvp-copiloto-verificacao`, onde são
tratadas pelas tasks 6.1 a 6.6.

Motivos completos em
`openspec/changes/add-engage-desinformacao-saude/design.md`, nota de 24/09/2026.
A decisão reabre se a métrica primária do projeto mudar.

---

## Depois dos quadros: derivar as guiding questions

O bloco 5 já foi executado em 11/09 e o backlog existe. O que a sessão nova faz
é **dar rastreabilidade ao que já existe** e cobrir o que ficou de fora.

Para cada agrupamento de notas:

1. Derivar uma pergunta, registrando **de qual quadro ela veio**.
2. Aplicar o critério de qualidade — pesquisável, não-binária, e **muda alguma
   decisão do projeto quando respondida**. Falhou um dos três, é descartada com
   o motivo registrado.
3. Classificar em `dados`, `literatura`, `usuario`, `fechada` ou `descartada`.
   Se for `dados`, **nomear o arquivo derivado** que sustenta a análise.
4. Agrupamento que não produz nenhuma pergunta pesquisável é marcado como
   **opinião do grupo** e não vai para o Investigate.

Só depois da classificação vem a priorização na matriz, e GQ `fechada` ou
`descartada` MUST NOT ser plotada.

## Fechamento

O backlog precisa terminar com **8 a 12 guiding questions priorizadas**, das
quais **no mínimo 3** marcadas como abertura do Investigate. Abaixo de 8, a
capability manda conduzir nova rodada de divergência antes de fechar a fase.

Estado atual do backlog: ver [Guiding Questions](guiding-questions.md).
