# Design — Ampliação do corpus PT-BR e índice de checagens recentes

## Context

Motivação em [`proposal.md`](proposal.md) — Why. Requisitos nas specs deste
change. O que importa aqui é o estado do pacote e as restrições que moldam a
abordagem.

O pacote de 08/09/2026 tem três camadas: núcleo metodológico, comparação de
exagero e banco de estímulos. Este change abre a quarta, acervo de circulação —
ver decisão 8. O corpus PT-BR citável são 4.063 checagens do
FactCenter, janela 2013–2021, com texto integral — é essa integralidade que
sustenta citação e RAG. A FakeRecogna v1 ocupa o banco de estímulos, com licença
não declarada e viés de sumarização conhecido nos itens verdadeiros.

Três restrições, em ordem de força:

1. **O repositório é público.** Texto jornalístico de terceiro só entra se a
   licença permitir redistribuição. A Central de Fatos entrou porque é CC BY.
2. **`add-tratamento-datasets-ptbr` está proposto e não aplicado** (0/33). Suas
   quatro capabilities são pré-condição de dado, não trabalho paralelo.
3. **`openspec/specs/` está vazio.** Nenhuma capability é verdade corrente
   ainda, o que tem consequência mecânica para o delta `MODIFIED` deste change
   — ver Migration Plan.

## Goals / Non-Goals

**Goals:**

- Recuar a fronteira do acervo citável e cobrir o que estiver além dela por
  referência, mantendo os dois separados na declaração e na apresentação.
- Deixar a substituição de base auditável por terceiro, e não apenas correta.
- Trazer para o projeto o primeiro material em português com veredito de
  especialista clínico e discordância medida.
- Trazer o primeiro material que mede **difusão**, e mantê-lo categoricamente
  separado de evidência sobre o fato.

**Non-Goals:**

- Igualar o índice ao acervo. O índice é deliberadamente mais fino: localiza e
  atribui, não cita. Tentar aproximá-los é o que produziria a raspagem.
- Cobertura completa por agência. O índice alcança quem publica ClaimReview.
- Reprodutibilidade da amostra de estímulos da v1. Ver decisão 3.
- Detecção de campanha, rede ou coordenação no corpus de Telegram. É pesquisa de
  outro tipo e não cabe em três semanas.

## Decisions

### 1. O índice guarda alegação, não texto

`claims:search` devolve `text`, `claimant`, `claimDate`, `publisher`, `url`,
`title`, `reviewDate`, `textualRating` e `languageCode`. Verificado na referência
da API: **o texto do artigo de checagem não está entre os campos**. É markup
ClaimReview, feito para indexação.

Guardamos os nove campos e paramos aí.

*Alternativa considerada — raspar cada URL para reconstruir o equivalente ao
`text_news` da Central de Fatos.* Rejeitada por dois motivos independentes, e
qualquer um bastaria. Legal: o texto é das agências, e uma raspagem nossa não
seria redistribuível num repositório público que já carrega a pendência do
PUBHEALTH. Operacional: parser por agência é o item que quebra sozinho e
consome manutenção durante uma fase que dura três semanas.

*Alternativa considerada — usar o dump histórico do Data Commons em vez da API.*
Rejeitada como fonte principal: o dataset de pesquisa publicado é de 2019, o que
não serve para o problema. O feed corrente permanece como rota de contingência
caso a chave de API se mostre um obstáculo.

A consequência é assumida e está escrita na spec: item de índice **MUST NOT**
virar trecho citado, nem resumo, nem síntese a partir do título. Essa é a linha
que separa este design de uma raspagem com outro nome.

### 2. O índice melhora a resposta de lacuna em vez de ampliar o corpus

O ganho não é volume de dado, é qualidade do pior caso. Hoje o `frescor-corpus`
faz o sistema responder *"o acervo não cobre esse período"*. Com o índice,
responde *"não tenho o texto, mas a Lupa checou isso em 03/2025 — aqui está"*.

Mandar a pessoa à checagem original é proveniência melhor do que a nossa cópia,
não pior: satisfaz o bullet de auditabilidade do `project.md` pela fonte
primária. Foi isso que justificou incluir a capability apesar do custo.

### 3. Substituir a FakeRecogna v1, não manter as duas

A v1 sai. Três razões: licença não declarada num repositório público, sobreposição
grande com a 2.0 (mesmo grupo, mesma metodologia), e o custo de manter dois
corpora de estímulo divergindo.

*Alternativa considerada — coexistência.* Rejeitada porque preservaria a
pendência de licença exatamente onde ela dói, no que está versionado.

Custo aceito: `fakerecogna_amostra_estimulos_300.csv` é refeita e a seleção com
`random_state=42` sobre a v1 deixa de ser reproduzível. A spec de
`procedencia-substituicao` exige declarar essa perda, e verificar se houve
curadoria manual sobre a amostra antiga antes de descartá-la — se houver, o
trabalho de reancoragem entra como task, não some.

### 4. Variante extrativa da FakeRecogna 2.0, e texto transformado nunca é fonte

A 2.0 vem em duas versões, extrativa e abstrativa. Adotamos a **extrativa**.

É preciso separar duas fidelidades que se confundem com facilidade:

- **fidelidade da frase** — o trecho é idêntico ao que a fonte escreveu;
- **integridade do documento** — o texto é o texto inteiro, não um recorte.

A extrativa garante a primeira e **não** garante a segunda: ela seleciona
sentenças reais, mas o documento continua abreviado. A abstrativa não garante
nenhuma das duas — é texto produzido por modelo, e nenhuma frase dele foi
escrita pela fonte.

Isso importa menos para citação do que parece, porque a FakeRecogna não é fonte
de citação neste pacote e nunca foi: o corpus citável é o FactCenter, com
`text_news` integral. A FakeRecogna é banco de estímulos. O risco real é outro e
é mais grave: apresentar a um participante do teste um texto gerado por modelo
como se fosse a notícia que circulou. Isso contamina o estímulo, e um estudo
sobre discernimento cujo estímulo não é autêntico não mede o que diz medir.

Daí a regra, que vale para qualquer base e não só para esta: **texto que passou
por transformação declara a transformação, e não serve como fonte de trecho
citado.** Está escrita em `procedencia-substituicao`. A escolha pela extrativa é
o que mantém o estímulo composto de linguagem que alguém de fato publicou.

A consequência para o acervo: a FakeRecogna 2.0 entra como estímulo com texto
transformado declarado, não como terceira base citável.

### 5. WhaVax no núcleo metodológico

Mensagem de WhatsApp parece estímulo. Mas o critério de camada neste pacote é
função, não formato: o que define `01_nucleo_metodologico` é servir de instrumento
ou definição. Com quatro anotadores médicos, regra de maioria declarada e
concordância medida, o WhaVax é a única referência de calibração em português que
o projeto tem. Vai para o núcleo.

### 6. A faixa de empate é entregável, não descarte

~8,8% dos itens do WhaVax não alcançaram maioria entre os quatro médicos. O
tratamento usual seria descartar. Aqui é o contrário: são casos de ambiguidade
**atestada por especialistas**, não presumida por nós, e é exatamente o material
que `mvp-copiloto-verificacao` precisa para as armadilhas de evidência ambígua.
A spec obriga a preservá-los como classe própria e consultável.

### 7. Nenhuma janela declarada antes de medida

O "2010–2023" da FakeRecogna 2.0 que circulou na discussão saiu da
pré-visualização do HuggingFace, não de contagem. O pacote anterior declarou
janela, concentração e termos ausentes por medição; este mantém o padrão. A spec
de `frescor-corpus` exige janela medida sobre o arquivo baixado, e caveat quando
divergir do que a fonte anuncia.

### 8. Acervo de circulação é um nível próprio, não um quarto corpus citável

O texto do corpus de Telegram é **íntegro e não transformado**, o que pela regra
da decisão 4 o colocaria no nível citável. Isso seria erro de categoria.

A distinção que faltava não é sobre o estado do texto, é sobre **do que o texto é
evidência**. Uma checagem da Lupa é evidência sobre o fato. Um post de Telegram é
evidência sobre *o que alguém publicou* — informativo sobre difusão, mudo sobre a
verdade da alegação. Citá-lo a um usuário como fonte confundiria as duas coisas
justamente no produto cuja premissa é auditabilidade até a fonte.

Daí o quarto nível em `frescor-corpus`: **acervo de circulação**. Conta para
janela temporal, responde "isso circulou, desde quando e em que canal", e
MUST NOT aparecer como fonte de trecho citado sobre o mérito.

*Alternativa considerada — pôr em `03_banco_estimulos`.* Rejeitada pelo mesmo
critério de função da decisão 5: estímulo é item que se apresenta ao participante
esperando julgamento de veracidade, e um post sem rótulo não serve para isso.

### 9. O risco central desta base é veredito por proxy de canal

A base é *de canais antivacina*. A inferência "apareceu aqui, logo é falso" é
fácil de fazer e está errada: canal antivacina também reproduz notícia
verdadeira, e a inferência inversa condenaria o usuário a julgar pela origem em
vez de pela evidência — exatamente o oposto da Essential Question.

Vale o mesmo para o campo `is_vaccine_related`: é rótulo **derivado por modelo**
(Sabiá-3, F1 0,90 medido sobre 600 posts anotados), não anotação humana. F1 0,90
significa aproximadamente um em dez errado, e ele é filtro de recorte, nunca
fato sobre o item.

`acervo-circulacao` proíbe as duas inferências normativamente. É o requisito que
justifica a capability existir em vez de a base entrar só com um caveat no
`FONTES.md`.

### 10. Agregados versionados, texto de post nunca

A CC BY-NC 4.0 permitiria redistribuir os posts. Não vamos.

São mensagens de pessoas reais. Os autores pseudonimizaram (`user_id` em SHA-256,
PII por Presidio), o que reduz o risco e não o elimina: texto livre em corpus
grande é re-identificável por combinação, e o próprio depósito registra que o STF
mandou remover mensagens por ilegalidade. Um repositório público de trabalho de
residência não é o lugar para reespalhar isso.

O que entra versionado são **derivados agregados** — contagem por mês, por canal,
frequência de termo de pauta — mais o script que os produz e o checksum do bruto.
O `.jsonl` de 3,6 GB fica fora do git como os demais brutos.

Custo aceito: quem quiser reproduzir baixa do REDU. É o mesmo contrato dos outros
brutos do pacote, e aqui há razão adicional para ele.

### 11. Portão de medição do índice: mantido, e por uma margem grande — 19/09/2026

Tasks 1.1 a 1.3. A Open Question deixou o limiar de volume em aberto porque não
havia medição. Agora há: `datasets/scripts/sondar_factcheck_api.py`, resultado
versionado em `datasets/derivados/sonda_factcheck_api.json`.

#### O que a API devolve para saúde em `pt`

| Termo de pauta | Checagens | Posteriores a 2021 |
| --- | --- | --- |
| `vacina` | 404 | 239 |
| `covid` | 306 | 136 |
| `gripe` | 80 | 44 |
| `dengue` | 76 | 55 |
| `mpox` | 39 | 36 |
| `qdenga` | 8 | 7 |
| `febre amarela` | 8 | 5 |
| `hpv` | 5 | 3 |
| `sarampo` | 2 | 0 |
| `oropouche` | **0** | 0 |
| `semaglutida` | **0** | 0 |
| **total** | **928** | **525** |

O termo de controle (`vacina`) devolveu 404 checagens, o que é o que autoriza
ler os zeros como ausência de pauta e não como consulta quebrada.

#### A decisão: manter

O critério não é volume absoluto — é se o índice muda a resposta no caso em que
o acervo falha. Muda, e exatamente ali:

- **Qdenga**, que tem **zero ocorrência** no corpus e é o caso de teste da
  lacuna de acervo, tem **8 checagens no índice**, distribuídas em 2023, 2024 e
  2026, por AFP Checamos, Aos Fatos, Estadão, Folha e UOL.
- **Mpox**, também zero no corpus, tem **39**, quase todas de 2024 em diante.
- 525 das 928 checagens são posteriores ao fim do acervo. O índice não duplica o
  corpus; ele começa onde o corpus termina.

#### Ganho lateral não previsto: agências que o acervo não tem

O índice alcança **11 editores**, contra as seis agências do corpus:

```
Estadão 183 · AFP Checamos 178 · Aos Fatos 174 · Observador 158 ·
UOL Notícias 142 · Projeto Comprova 67 · Folha 11 · BOL 8 ·
Nexo 3 · O Globo 2 · Agência Pública 2
```

AFP Checamos, Observador, UOL, Folha, Nexo, O Globo e Agência Pública **não
estão no corpus**. Isso amplia a cobertura por fonte, não só por data — e o
Observador é português, não brasileiro, o que precisa entrar como caveat na
declaração de cobertura: checagem de Portugal responde sobre pauta europeia com
vocabulário próximo, e atribuí-la como se fosse brasileira seria erro de
proveniência.

#### O que a medição não resolve

`oropouche` e `semaglutida` continuam em **zero mesmo no índice**. As duas
pautas que o corpus não cobre também não têm checagem indexada em português —
logo, para elas, a resposta correta continua sendo lacuna de acervo **sem**
ponteiro, e a task 8.2 precisa de um terceiro caso de teste: pauta ausente dos
dois níveis. Isso não derruba o índice; delimita o que ele promete.

#### Consequência para as tasks

A capability `indice-checagens-recentes` **permanece na proposal e nas specs**.
O bloco 7 (construção do índice) fica autorizado a executar.

### 12. Conferência de licença da FakeRecogna 2.0, e dois achados que mexem em tasks — 19/09/2026

Task 2.1, conferida na fonte dos autores. O resultado tem uma ressalva sobre a
própria premissa da task e dois achados que deslocam o bloco 9.

#### O que foi conferido

| Fonte | O que declara |
| --- | --- |
| Artigo — Garcia et al., PROPOR 2024, `aclanthology.org/2024.propor-1.9` | descreve a base: 26.569 notícias falsas coletadas, 26.400 após remoção de duplicatas, de **nove** agências brasileiras; total do conjunto acima de 52 mil com as reais. O artigo em si é CC BY 4.0 |
| Cartão da variante extrativa, `recogna-nlp/fakerecogna2-extrativa` | **MIT**, 52.800 linhas, oito colunas: `Title`, `Subtitle`, `News`, `Category`, `Author`, `Date`, `URL`, `Label` (0 real, 1 falsa) |
| Repositório dos autores da v1, `Gabriel-Lino-Garcia/FakeRecogna` | **nenhum arquivo de licença**; não menciona a 2.0 |

**Ressalva sobre a premissa da task.** A task manda conferir "na fonte primária
dos autores, não no cartão do HuggingFace", supondo que o HuggingFace seja
agregador de terceiro. Aqui ele não é: `recogna-nlp` é a organização do próprio
laboratório dos autores, e o cartão é publicação deles. A divergência real não é
entre autor e agregador — é entre **o repositório da v1, sem licença nenhuma, e
o cartão da 2.0, com MIT**. Entra como caveat: a licença MIT vale para a 2.0
conforme declarada pelos autores no cartão; o artigo não repete a declaração, e
a v1 nunca teve licença explícita.

#### Achado 1: a 2.0 não tem vocabulário de veredito

As oito colunas não incluem campo de veredito textual. O rótulo é **binário**
(`Label` 0/1), atribuído pela coleta, não a etiqueta publicada pela agência.

Isso derruba a premissa da **task 9.1**, que manda "absorver os três
vocabulários de agência novos da 2.0 no mapa de rótulos" e conferir que "os nove
vocabulários têm destino definido". Não há três vocabulários novos a absorver,
porque não há vocabulário nenhum: há três **agências** novas sem texto de
veredito. O mapa de `normalizacao-rotulos`, versão 1.0.0, continua com as 19
chaves das seis agências do FactCenter, e nada a acrescentar vindo daqui.

A task 9.1 precisa ser reescrita para o que de fato resta fazer: registrar que a
2.0 entra com rótulo binário e, portanto, **como banco de estímulos, nunca como
fonte de veredito graduado** — o que já é exigência do `project.md`.

#### Achado 2: as três agências novas são AFP Checamos, E-farsas e UOL Confere

A Tabela 1 do artigo lista as nove agências com a contagem de cada uma:

| Agência | Notícias | Está no corpus do FactCenter? |
| --- | --- | --- |
| Boatos.org | 8.654 | sim |
| E-farsas | 3.330 | **não** |
| Agência Lupa | 3.147 | sim |
| Aos Fatos | 2.720 | sim |
| UOL Confere | 2.579 | **não** |
| Fato ou Fake | 2.270 | sim |
| AFP Checamos | 1.587 | **não** |
| Estadão Verifica | 1.405 | sim |
| Projeto Comprova | 877 | sim |
| **total** | **26.569** | |

São exatamente três agências novas, como a task 9.1 antecipou — o número estava
certo, o objeto é que não. E duas delas, **AFP Checamos e UOL**, já apareceram
na sonda da Fact Check Tools API da decisão 11, com 178 e 142 checagens. As três
fontes convergem para as mesmas agências ausentes do nosso acervo, o que é
confirmação independente de onde está a lacuna de cobertura por fonte.

#### O que continua pendente

A conferência de contagem sobre o arquivo baixado (task 2.3) e o versionamento
do texto da licença junto da base (tasks 2.1 e 2.2) exigem o download, que não
foi autorizado nesta sessão. O que está conferido é a declaração na fonte.

### 13. Licenças do WhaVax e do acervo de circulação, conferidas na fonte — 19/09/2026

Tasks 2.2 e 2.5, na parte que não depende do download. O que exige o arquivo
baixado — versionar o texto da licença junto da base, conferir contagem e campos
— continua pendente.

#### WhaVax (task 2.2)

| Item | O que a fonte declara |
| --- | --- |
| Depósito | Zenodo, registro `18190030` |
| Licença | **CC BY 4.0** — não confundir com a licença do artigo no arXiv, que é a mesma sigla mas outro objeto |
| Anotadores | **quatro profissionais de medicina**, sem experiência prévia em rotulagem computacional, submetidos a refinamento de protocolo |
| Regra de agregação | maioria de **pelo menos três votos em quatro** |
| Concordância | Fleiss' Kappa **0,621** no resultado final (0,65 no estágio intermediário) |
| Janela | mensagens de **2020 a 2023**, com análise até o início de 2024 |
| Viés declarado | grupos públicos brasileiros do WhatsApp; sobre-representa comunidades politicamente engajadas e vocais, sub-representa conversa privada e familiar |

**Achado que ameaça a task 5.3.** Os autores declaram que **8,8% dos casos (84)
terminaram empatados** entre os quatro especialistas, e que adotaram estratégia
conservadora: **os empates foram rotulados como não-desinformação**. A task 5.3
manda "isolar a faixa de empate como classe própria, recuperável por consulta".
Isso só é possível se o pacote publicar o voto **por anotador**; se publicar
apenas o rótulo agregado, o empate já foi absorvido na classe negativa e é
irrecuperável. É exatamente o que a task 2.4 manda verificar no download, e o
resultado dela decide se a 5.3 sobrevive.

**Segundo achado, de escala.** Os 84 empates sobre 8,8% implicam um conjunto
anotado da ordem de **950 mensagens**, não de 84.640. O número de 84.640 é o
corpus filtrado de mensagens relacionadas a vacinação, de 15.148 usuários; o
conjunto padrão-ouro anotado por especialista é muito menor. Tratar os dois como
o mesmo número superestimaria em quase cem vezes o material com veredito
clínico, e a declaração de cobertura da task 8.1 precisa separá-los.

#### Acervo de circulação — Telegram antivacina (task 2.5)

Conferido no depósito do REDU (Unicamp), não no arXiv, como a task exige.

| Item | O que o registro declara |
| --- | --- |
| DOI | `10.25824/redu/5JIVDT` |
| Licença | **CC BY-NC 4.0** — confirmada no registro |
| `telegram-vaccine-info-disorder-dataset-2020-2025.jsonl` | **3,608 GB** (3,36 GiB), acesso **público** |
| `readme.pdf` | 35 KB, acesso público |
| Mídia (imagem, vídeo, áudio) | **5,5 TB**, acesso **restrito**, exige assinatura de acordo específico |
| Escala | 3.998.633 mensagens, 119 canais, 1,44 milhão de itens de mídia |
| Janela | janeiro de 2020 a junho de 2025 |
| Citação | Cardenuto, Monari, Lopes, Lusquino Filho, Rocha (2025) |

A condição de acesso é **assimétrica**, exatamente como a task antecipou: o
texto é aberto, a mídia é restrita. A task 2.6 manda baixar só o `.jsonl` e o
`readme.pdf`, e essa separação agora tem respaldo no registro — baixar mídia
exigiria acordo assinado, que o projeto não tem nem precisa.

**Sobre o tamanho.** A página web do REDU mostra «3.4 GB» e a task diz 3,6 GB.
Não há divergência: a API do depósito declara 3.608.168.366 bytes, que são
3,608 GB decimais e 3,36 GiB. A página exibe GiB com rótulo de GB. O arquivo
baixado em 19/09/2026 tem exatamente esse tamanho em bytes.

#### Convergência entre as três fontes

AFP Checamos e UOL aparecem na sonda da API (decisão 11) e entre as três
agências novas da FakeRecogna 2.0 (decisão 12). O acervo de circulação cobre
janeiro de 2020 a junho de 2025, e o WhaVax cobre 2020 a 2023 — as duas janelas
começam onde o nosso acervo de checagem está mais denso (2020) e seguem quatro
anos além do seu fim (2021). A lacuna temporal do projeto é a mesma vista por
três instrumentos independentes.

## Risks / Trade-offs

- **Volume do índice em `pt` para saúde é desconhecido** → Portão de medição na
  primeira task: amostra, contagem por ano e por agência. Abaixo do limiar útil,
  a capability é descartada com motivo registrado, e o change entrega as duas
  bases. Não se entrega capability oca.
- **A 2.0 traz nove vocabulários de agência contra os seis inventariados** →
  Motivo pelo qual este change sucede `add-tratamento-datasets-ptbr` em vez de
  correr junto. O mapa de rótulos daquele change precisa absorver três
  vocabulários novos; a task de reconciliação existe para isso.
- **Licença MIT da 2.0 vista em cartão de repositório de terceiro** →
  `procedencia-substituicao` proíbe aceitar agregador como prova. Conferir na
  fonte dos autores antes de versionar qualquer derivado.
- **Dependência de serviço de terceiro e de chave de API** → O snapshot fica
  versionado; a indisponibilidade posterior da API degrada a atualização, não o
  entregável.
- **950 itens do WhaVax vêm de grupos públicos brasileiros** → Viés declarado
  pelos próprios autores, para comunidades politicamente engajadas. Entra como
  caveat; o uso é calibração e seleção de caso, onde o viés de amostra pesa menos
  do que pesaria em estimativa de prevalência.
- **O índice pode ser confundido com corpus na implementação** → É o risco
  central deste change. Mitigado por proibição normativa explícita na spec e por
  task de verificação no fechamento.
- **Este change não fecha 2024–2026 com texto citável** → Assumido e nomeado. O
  acervo citável recua até onde a FakeRecogna 2.0 alcançar; daí em diante existem
  referência e circulação, não citação.
- **3,6 GB de `.jsonl` não abrem em planilha nem cabem em memória de notebook
  modesto** → O contrato de leitura de `add-tratamento-datasets-ptbr` precisa
  cobrir leitura em streaming por linha. É task de reconciliação, não risco
  aberto.
- **O recorte da base é antivacina, e a amostra é enviesada por construção** →
  Viés não é defeito aqui, é o objeto: a base descreve um ecossistema
  específico, não a população. O caveat MUST proibir leitura de prevalência.
  Registrado em `acervo-circulacao`.
- **Fixar o sub-recorte em vacinação estreita o teste com usuário** → Assumido em
  `project.md`. A mitigação é que o protótipo não fica restrito ao tema; só a
  curadoria de casos e a medição de cobertura ficam.
- **Quatro níveis de cobertura podem virar taxonomia decorativa** → Cada nível só
  se justifica por mudar uma resposta do sistema. A task de fechamento verifica
  isso caso a caso; nível que não mudar resposta alguma sai.

## Migration Plan

Ordem obrigatória:

1. `add-tratamento-datasets-ptbr` aplicado — contrato de leitura, normalização de
   rótulo e integridade textual existindo antes de qualquer base nova entrar.
2. Este change aplicado.
3. **Antes do arquivamento deste change:** `frescor-corpus` promovida para
   `openspec/specs/` via `/opsx:sync` a partir de `add-tratamento-datasets-ptbr`.

O passo 3 não é burocracia. `openspec validate --strict` aceita o delta
`MODIFIED` deste change, mas o archive o recusa com
`target spec does not exist; only ADDED requirements are allowed for new specs`.
A capability existe hoje apenas como delta em change não aplicado. Sem a
promoção, este change fica preso na definição de pronto.

Rollback: os brutos ficam fora do git e são reconstituíveis por checksum a partir
das fontes primárias; os derivados e a documentação revertem por git. A
substituição da v1 é o único passo com perda real — a amostra de 300 — e por isso
a spec exige declará-la antes de executá-la.

## Open Questions

- Limiar de volume abaixo do qual o índice não se justifica. Depende da medição
  da primeira task e não altera specs, abordagem nem quebra de tasks: se o índice
  cair, a capability é descartada com motivo e o resto do change segue intacto.
