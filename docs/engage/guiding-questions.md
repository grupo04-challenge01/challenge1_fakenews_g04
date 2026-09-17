# Backlog de Guiding Questions — Fase Engage

**Grupo 04 · Challenge 1 · fechado em 10/09/2026**

Critérios aplicados, conforme a capability `guiding-questions` do change
`add-engage-desinformacao-saude`:

- Pesquisável, não binária, e altera alguma decisão do projeto quando respondida.
- Rastreável ao quadro do brainstorming que a originou.
- Classificada pela fonte que a responde.
- Priorizada por impacto × incerteza. Esforço não é eixo nesta fase.

**Candidatas nos cinco quadros: 40. Mantidas: 12.** Teto de 12 decidido em
10/09/2026 (`design.md`, Decisão 4).

| Classe | Significado | Quantidade |
| --- | --- | --- |
| `dados` | respondível pelos datasets já coletados | 5 |
| `literatura` | respondível por revisão, sem coleta nova | 3 |
| `usuario` | respondível apenas por teste com participantes | 4 |
| `fechada` | já respondida por decisão registrada | 10 |
| `fundida` | absorvida por outra guiding question | 6 |
| `descartada` | falha o critério de qualidade | 12 |

---

## As 12 guiding questions

### Classe `dados`

**GQ-01 · Quais tipos de desinformação em saúde são mais frequentes no contexto brasileiro, e qual deles é mais tratável por um copiloto de verificação?**

- Quadro: Problema
- Fonte: `derivados/factcenter_subset_saude.csv` (campos `categories`, `tags`,
  `rating`) e `derivados/fakerecogna_subset_saude_ciencia.csv` (5.058 itens)
- Impacto alto · incerteza média
- Caveat: a distribuição do corpus é enviesada para 2020 e covid (54% dos
  registros em 2020, 56% mencionam covid). A frequência medida é a frequência
  *do acervo*, não a da pauta atual.

**GQ-02 · Como distinguir, de forma automatizável, alegação falsa de alegação verdadeira exagerada ou fora de contexto?** *(abertura do Investigate)*

- Quadro: Específicas
- Fonte: `derivados/exagero_pares_abstract_vs_release.csv` (663 pares com
  `strength` dos dois lados) e `derivados/factckbr_normalizado.csv` (exagerado
  91, distorcido 54, sem contexto 42)
- Impacto alto · incerteza alta
- Por que abre: é o rótulo central do produto (`verdadeiro fora de contexto ou
  exagerado`) e o menos resolvido. Sem ele o sistema colapsa em binário.

**GQ-03 · Que sinais de qualidade de evidência são extraíveis de um texto de divulgação, e a partir de que ponto é preciso ir ao estudo original?** *(abertura do Investigate)*

- Quadro: Específicas · já registrada como questão aberta 5 do `design.md`
- Fonte: `derivados/fakehealth_matriz_10_criterios.csv` e
  `derivados/fakehealth_criterios_long.csv` (22.959 avaliações de critério)
- Impacto alto · incerteza alta
- Caveat: são 20 perguntas em dois conjuntos distintos, não 10. Ver
  `add-tratamento-datasets-ptbr`, capability `adaptacao-criterios-en`.

**GQ-04 · Como o sistema deve se comportar quando a alegação trata de pauta posterior à cobertura do acervo, ou quando a fonte oficial mudou de posição?** *(abertura do Investigate)*

- Quadro: Específicas · antecipada na Decisão 2 do `design.md` e nunca levada ao
  board
- Fonte: `derivados/factcenter_subset_saude.csv` — janela 2013–2021, e zero
  ocorrência de `qdenga`, `mpox`, `oropouche` e `semaglutida`
- Impacto alto · incerteza alta
- Por que abre: decide se o produto funciona em 2026. Endereçada pela capability
  `frescor-corpus` de `add-tratamento-datasets-ptbr`.

**GQ-05 · Que evidência quantitativa sustenta que o problema vale ser resolvido?**

- Quadro: Problema
- Original: *"Que evidência mostra que esse problema vale ser resolvido? volume
  de checagens, tempo entre publicação e desmentido, alcance"*
- Fonte: `derivados/factcenter_subset_saude.csv`, apenas para **volume por
  agência e por ano**
- Impacto médio · incerteza baixa
- **Reclassificação registrada:** as outras duas evidências pedidas na nota
  original não são obteníveis. *Tempo entre publicação e desmentido* exigiria a
  data de origem do boato, que o corpus não contém — só a data da checagem.
  *Alcance* exigiria os `engagements` do FakeHealth, que são apenas IDs de tweet
  e dependem de uma API inviável. Ambas viram caveat de dataset, conforme o
  cenário "Análise exige campo que nenhum dataset possui".

### Classe `literatura`

**GQ-06 · O que a literatura mostra sobre eficácia de correção de desinformação em saúde, incluindo efeitos contraproducentes?**

- Quadro: Específicas
- Impacto alto · incerteza média
- Por que importa: se a correção produz efeito reverso em parte dos casos, a
  estrutura de quatro blocos da `resposta-formativa` precisa de ajuste, não o
  copiloto inteiro. O risco de verdade ilusória já está registrado no `design.md`.

**GQ-07 · Como comunicar que o consenso científico é provisório sem alimentar a conclusão de que "ninguém sabe nada"?**

- Quadro: Específicas · questão aberta 4 do `design.md`
- Impacto alto · incerteza alta
- Liga-se à métrica de guarda de ceticismo indiscriminado e à GQ-04.

**GQ-08 · De que forma promessas de cura sem evidência levam pacientes a abandonar tratamento convencional, e quais alegações têm dano imediato maior?**

- Quadro: Problema · funde duas notas (perigos do consumo de substâncias
  ineficazes; abandono de quimioterapia, insulina e uso contínuo)
- Impacto alto · incerteza média
- Por que importa: é o que dá conteúdo ao requirement de selecionar "a alegação
  de saúde de maior risco potencial" em `verificacao-alegacao`. Hoje o critério
  de risco não está definido em nenhum lugar.

### Classe `usuario`

**GQ-09 · Quais critérios as pessoas realmente usam para decidir se acreditam numa mensagem de saúde, e onde esses critérios falham?** *(abertura do Investigate)*

- Quadro: Público · funde três notas (critérios declarados; alternativas usadas
  hoje; gatilhos imediatos de confiança — visual, número de seguidores, ter sido
  enviado por alguém próximo)
- Impacto alto · incerteza alta
- Por que abre: é a entrada da `matriz-confianca`. Dimensão que ninguém usa na
  prática não deveria estar na matriz.

**GQ-10 · Em que ponto a verificação falha hoje: falta de método, custo de tempo, ou falta de intenção?**

- Quadro: Problema
- Impacto alto · incerteza média
- Decide onde o produto intervém. Já há evidência parcial na forense: o tempo
  medido por caso pelos próprios integrantes.

**GQ-11 · Qual o atrito máximo que o usuário aceita antes de abandonar a verificação?**

- Quadro: Solução · funde a nota sobre atrito no WhatsApp (abrir link, responder
  perguntas, ler matéria completa) · questão aberta 3 do `design.md`
- Impacto alto · incerteza alta
- É métrica de guarda declarada. Depende parcialmente da decisão de canal.

**GQ-12 · Como medir se o uso do copiloto fortalece o pensamento crítico em vez de substituí-lo?**

- Quadro: Problema · funde três notas (impacto da IA no pensamento crítico;
  diferenciar "usar como ferramenta" de "deixar a IA pensar por nós"; de que
  forma a IA estimula em vez de substituir)
- Impacto alto · incerteza alta
- É a operacionalização da Essential Question. Métricas previstas: transferência
  (acerto sem a ferramenta) e taxa de aceitação cega quando o sistema erra.

---

## Matriz impacto × incerteza

```
            incerteza baixa            incerteza alta
          +-------------------------+-------------------------+
  impacto |                         |  GQ-02 * GQ-03 *        |
  alto    |                         |  GQ-04 * GQ-09 *        |
          |  GQ-01  GQ-06  GQ-08    |  GQ-07   GQ-11  GQ-12   |
          |  GQ-10                  |                         |
          +-------------------------+-------------------------+
  impacto |  GQ-05                  |                         |
  medio   |                         |                         |
          +-------------------------+-------------------------+

  * = abertura da fase Investigate (semanas 2 e 3)
```

Aberturas: **GQ-02, GQ-03, GQ-04 e GQ-09** — quatro, contra o mínimo de três
exigido pela capability.

Candidatas a escopo de protótipo (alto impacto, baixa incerteza): GQ-01, GQ-06,
GQ-08 e GQ-10.

---

## Registro de fechamento

Dez candidatas já tinham resposta em decisão registrada. Não consomem tempo do
Investigate.

| Pergunta do quadro | Fechada por |
| --- | --- |
| Como avaliar a confiabilidade e a raiz dessas notícias | `matriz-confianca`, dimensões e rubrica |
| Como representar confiança sem colapsar em nota única ou veredito | `matriz-confianca`, *Ausência de score agregado* |
| Onde traçar a fronteira entre avaliar informação e dar orientação de saúde | `fronteira-orientacao-saude` |
| Como um sistema de IA identifica informação falsa a partir de evidência científica e fontes confiáveis | `recuperacao-evidencia` |
| Como apresentar evidência sem induzir a conclusão: socrático, evidência crua ou resumo | `mvp-copiloto-verificacao`, `design.md` Decisão 1 e *Revelação progressiva* |
| A IA deveria sempre apresentar as fontes utilizadas | `resposta-formativa`, *Revelação progressiva* — e a formulação era binária |
| Como fazer a informação confiável chegar a quem tem dificuldade de acesso ou letramento | `acessibilidade-leitura` (a parte de canal segue como questão aberta, não como GQ) |
| Quem é o usuário-alvo: o cético que desiste ou quem nem cogita verificar | `mvp-copiloto-verificacao`, `proposal.md` — público geral, idoso como restrição |
| Quem fica explicitamente fora do escopo, e por quê | `mvp-copiloto-verificacao`, `design.md` Decisão 4 |
| Qual o dano concreto de acreditar errado neste recorte | `add-engage-desinformacao-saude`, `design.md` Decisão 2 |

## Registro de fusão

Seis candidatas foram absorvidas: duas em GQ-08, três em GQ-09, uma em GQ-11, e
três em GQ-12. As formulações originais ficam registradas nas entradas
correspondentes acima, para rastreabilidade.

## Registro de descarte

Doze candidatas descartadas, com motivo.

| Pergunta do quadro | Motivo |
| --- | --- |
| Como sistemas de IA podem ajudar as pessoas a avaliar confiabilidade sem substituir seu pensamento crítico | É a Essential Question, não uma GQ derivada dela. Operacionalizada em GQ-12 |
| Qual sistema de IA pode ajudar as pessoas a terem informações mais confiáveis sobre saúde | Reformulação da Essential Question como solução; ampla e não pesquisável |
| Como a desinformação afeta a saúde em geral | Escopo amplo demais para o prazo; nenhuma decisão do projeto depende da resposta em nível geral. Recorte útil está em GQ-08 |
| O quanto a qualidade do ensino afeta alguém cair em fake news | Variável não medível com a amostra prevista; nenhum dataset coletado tem escolaridade |
| Como o design das redes sociais e os algoritmos de recomendação favorecem conteúdo sensacionalista | Fora do escopo declarado — moderação de plataforma consta em *Out of Scope* |
| Como o tempo para combater a desinformação reduz o alcance dela | Exige a data de origem do boato, que nenhum dataset coletado contém. Mesma lacuna registrada em GQ-05 |
| Como esse tema ajuda na ODS 3 | Nenhuma decisão do projeto depende da resposta |
| Como o bombardeio de conteúdo alarmista afeta a ansiedade e o bem-estar da população | Fora do recorte; efeito populacional não é decidível pelo grupo nesta fase |
| O que já existe relacionado a este tema que pode ser usado | Vira task de consolidação do portfólio, não guiding question |
| Quais arquiteturas ou modelos de IA são mais adequados | Decisão de implementação; *Out of Scope* do Engage |
| Quais as suposições mais arriscadas do produto | Não é pergunta: é lista de riscos, já absorvida no `design.md` e em `avaliacao-instrumento`. A suposição *"que as pessoas aceitem não receber veredito"* deixou de existir com a revisão de 10/09/2026 |
| Em que momento da jornada a intervenção tem mais efeito | Depende da decisão de canal, ainda aberta. Permanece como questão aberta 2 do `design.md`, não como item de pesquisa |

## Agrupamento que não gerou pergunta pesquisável

O quadro **Sucesso** não produziu guiding question. Produziu métricas —
discernimento, transferência, tempo até decisão fundamentada, consulta a fonte
externa, e as quatro métricas de guarda. Não são opinião do grupo: foram
absorvidas pela capability `avaliacao-instrumento` de
`mvp-copiloto-verificacao`, e por isso saem do escopo de pesquisa desta fase
como perguntas.
