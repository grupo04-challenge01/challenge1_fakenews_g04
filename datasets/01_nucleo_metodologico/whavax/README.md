# WhaVax — WhatsApp Vaccine Discourse

Mensagens sobre vacinação de grupos públicos brasileiros do WhatsApp, anotadas
por especialistas médicos. Integrada ao núcleo metodológico em **19/09/2026**
pelo change `add-ampliacao-corpus-ptbr`, bloco 5.

## Citação e licença

- **Citação:** *WhatsApp Vaccine Discourse (WhaVax): An Expert-Annotated Dataset
  and Benchmark for Health Misinformation Detection.* ICWSM 2026.
  arXiv:2605.12510.
- **Depósito:** Zenodo, registro `18190030`.
- **Licença:** **CC BY 4.0** — conferida no registro do Zenodo em 19/09/2026,
  não no arXiv. Atribuição é condição de uso.
- **Arquivo bruto:** `WhaVax_dataset.csv`, SHA-256
  `5f9e9381551f4244882f9586072d557888d391bb491d6e109a2f78ad7b7f52f1`.
  **Fora do git** — ver a seção de privacidade.

## O que a base é, medido

| Medida | Valor |
| --- | --- |
| Mensagens anotadas | **950** |
| Janela medida | 02/03/2020 a 07/11/2023 |
| Por ano | 2020: 156 · 2021: 475 · 2022: 210 · 2023: 109 |
| Usuários distintos (pseudonimizados) | 746 |
| Grupos distintos | 398 |

**O número de 84.640 mensagens que aparece no artigo é outra coisa.** Aquele é o
corpus filtrado de mensagens relacionadas a vacinação, de 15.148 usuários. O
conjunto **anotado por especialista** — o que dá valor à base para este projeto —
tem 950 mensagens. Tratar os dois como o mesmo número superestimaria em quase
cem vezes o material com veredito clínico.

## Proveniência da anotação (task 5.2)

Está aqui, e não por referência ao artigo, porque é isso que sustenta qualquer
afirmação feita a partir do rótulo:

| Item | Valor |
| --- | --- |
| Anotadores | **quatro profissionais de medicina** |
| Qualificação | especialistas clínicos, sem experiência prévia em rotulagem computacional, submetidos a refinamento de protocolo |
| Regra de agregação | maioria de **ao menos 3 votos em 4** |
| Concordância medida | **Fleiss' Kappa 0,621** (0,65 no estágio intermediário) |
| Votos individuais | presentes: colunas `av1_desinfo` a `av4_desinfo`, binárias |

## A faixa de empate é entregável, não descarte (task 5.3)

Distribuição da soma dos quatro votos, medida sobre o arquivo:

| Votos de desinformação | Mensagens | Leitura |
| --- | --- | --- |
| 0 | 442 | consenso de não-desinformação |
| 1 | 138 | maioria de não-desinformação |
| **2** | **84** | **empate — 8,8%** |
| 3 | 82 | maioria de desinformação |
| 4 | 204 | consenso de desinformação |

Os **84 empates batem exatamente com o declarado pelos autores**. E eles são
recuperáveis por consulta justamente porque o pacote publica o voto por
anotador — se publicasse só o rótulo agregado, o empate seria irrecuperável,
porque a estratégia conservadora dos autores os absorveu na classe
não-desinformação.

Essa faixa é o material mais valioso da base para este projeto: são as
mensagens em que **quatro médicos olharam e não concordaram**. É o oposto de
ruído — é a evidência de que a fronteira existe e de onde ela passa.

## Usos permitidos e vedados (task 5.4)

**Vedado:**

- **Treino de classificador de veredito**, em qualquer rótulo. Vedação em texto
  expresso de `openspec/project.md`: dataset de rótulo binário é banco de
  estímulos, nunca alvo de treino de veredito.
- Apresentar o rótulo como verdade clínica corrente. Ver o período de validade
  abaixo.
- Versionar o texto das mensagens ou o `sender` no repositório público.

**Permitido:**

- Banco de estímulos para teste com usuário, com a proveniência declarada.
- Caracterização descritiva do que circulou, para o portfólio.
- A faixa de empate como conjunto de casos difíceis, para a curadoria de
  `avaliacao-instrumento`.

## Caveats (task 5.5)

**Viés de amostra, declarado pelos autores.** A base vem de grupos **públicos**
do WhatsApp e sobre-representa comunidades politicamente engajadas e vocais;
sub-representa conversa privada e familiar, que é justamente o canal em que a
desinformação em saúde mais circula no Brasil. Nenhuma leitura de prevalência é
autorizada a partir desta base.

**Período de validade do rótulo.** O veredito clínico foi emitido entre 2020 e
2023, no contexto da pandemia. Afirmação sobre vacinas muda com a evidência: um
rótulo de 2021 sobre eficácia ou efeito adverso **não é** veredito corrente. O
rótulo é válido na data, e a data precisa acompanhar o rótulo em qualquer uso.

**Cobertura temática.** Medido no texto: `covid` em 228 mensagens, `vacina` em
497, `dengue` em 3, `sarampo` em 3, e **zero** para `qdenga`, `mpox`,
`oropouche` e `semaglutida`. A base amplia o veredito clínico, não a janela de
pauta.

## Privacidade

O bruto **não é versionado**. Ele contém texto de mensagem de pessoa real e
identificador de remetente — pseudonimizado (hash de 32 caracteres), mas ainda
assim identificador, acompanhado de DDD. `acervo-circulacao` veda versionar as
duas coisas, e a mesma regra é aplicada aqui por coerência, ainda que a base
esteja no núcleo metodológico.

Versionados: esta documentação, a citação, a licença e os agregados em
`derivados/whavax_agregados.json`, que não contêm texto nem identificador.

## Reconstituir

```bash
curl -L -o WhaVax_dataset.csv \
  https://zenodo.org/api/records/18190030/files/WhaVax_dataset.csv/content
sha256sum -c ../../SHA256SUMS
```
