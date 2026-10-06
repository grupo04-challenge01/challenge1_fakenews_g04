# Design: Copiloto de verificação de informação de saúde

## Decisões

### 1. Veredito primeiro, método depois

O quadro de brainstorming previa modo socrático (perguntas antes da evidência) e
copiloto sem veredito. Ambos foram descartados para o MVP.

Motivo: quem manda a mensagem quer saber se pode acreditar. Segurar a conclusão
aumenta o abandono — que é uma das métricas de guarda do próprio projeto — e
deixa a pessoa sair com a versão errada na memória. A formação não depende de
sonegar a resposta; depende de o raciocínio vir junto com ela.

O argumento textual vem antes do argumento de produto: a Big Idea fala em
**apoiar a investigação** da confiabilidade e a Essential Question em avaliar
confiabilidade **sem substituir** o pensamento crítico — nenhuma das duas proíbe
conclusão. O que a premissa proíbe é o veredito nu; o que ela exige é
auditabilidade até a fonte e ganho que sobrevive à ausência da ferramenta, e
esses ficam garantidos pela revelação progressiva e pelos blocos 3 e 4. A regra
"não emite veredito" era derivação do próprio grupo, revista em `project.md` em
10/09/2026.

Alternativa considerada: modo socrático opcional, acionável depois do veredito.
Fica registrado como possível extensão pós-MVP.

### 2. A unidade de formação é a técnica, não o fato

Saber que uma cura caseira específica não funciona não ajuda no próximo caso.
Reconhecer o padrão "promete cura + fonte sem nome + pede compartilhamento"
ajuda em todos. Por isso o catálogo de técnicas é fechado, pequeno e versionado:
é ele que a métrica de transferência de fato mede.

O catálogo se apoia nos critérios do FakeHealth (qualidade de cobertura de saúde)
e no InSciOut (distância entre estudo e manchete), traduzidos para linguagem
cotidiana.

### 3. Resposta em camadas em vez de dois modos

Não há modo simples e modo avançado. Há uma resposta só, com o essencial visível
e o detalhe sob demanda. Isso atende a restrição de acessibilidade e a exigência
de auditabilidade da tradução PT/EN no mesmo mecanismo.

### 4. Público geral, idoso como restrição

Público-alvo define quem é recrutado e sobre quem se conclui. Restrição define o
que a solução tem que satisfazer. Pessoa idosa com baixo letramento digital é
restrição — por isso os requisitos de acessibilidade são numéricos e testáveis
com qualquer participante.

Permanece fora do escopo, por decisão explícita, quem tem incentivo em acreditar
na desinformação: com amostra pequena, esses participantes medem teimosia, não a
ferramenta.

### 5. Canal: aplicação web com extensão para WhatsApp

Decidido pelo grupo em 25/09/2026 (task 7.1).

O canal primário é uma **aplicação web (chat responsivo)**. Além dela, o
produto terá uma **extensão para WhatsApp** que permite ao usuário enviar
diretamente a mensagem sobre uma notícia recebida pelo WhatsApp, ou o link de
uma notícia que mandaram para ele.

Motivo: a web permite renderização rica das fontes, camadas progressivas de
detalhe e interface acessível sem as limitações de layout do WhatsApp. A
extensão para WhatsApp resolve o problema de travessia de canal — a mensagem
enganosa chega no WhatsApp e a verificação precisa estar acessível ali mesmo,
sem exigir que o usuário copie texto e troque de aplicativo.

Alternativa descartada: apenas WhatsApp (bot). Limitaria a experiência de
revelação progressiva e os requisitos de acessibilidade visual (contraste,
fonte, camada de detalhe). Alternativa descartada: apenas web, sem extensão
WhatsApp. Ignoraria o canal onde a desinformação de fato circula.

### 6. Catálogo de técnicas, versão 1: sete rótulos e uma vaga — 28/09/2026

Task 3.1. Arquivo versionado em `prototipo/resposta/catalogo_tecnicas.json`,
com sinal em linguagem cotidiana, limite e origem de cada rótulo.

| Rótulo | Casos da forense | De onde veio |
| --- | --- | --- |
| `cura milagrosa` | 02 | spec, cenário Promessa de cura |
| `manchete exagerada` | 04 | spec, cenário Estudo real com manchete inflada |
| `fora de contexto` | 03, 05 | cartões-semente de data e de corte |
| `fonte sem nome` | 01, 06 | cartões-semente de autoridade sem nome |
| `estudo inventado` | 02 | cartão-semente de instituição real com estudo inexistente |
| `urgência fabricada` | 06 | decisão 13 de `add-selecao-modelos-arquitetura-rag` |
| `medo de dano oculto` | 01, 03, 04, 06 | decisão 13 de `add-selecao-modelos-arquitetura-rag` |

Todos os seis casos da forense recebem ao menos um rótulo. Cada rótulo tem
**limite** declarado, no formato que o kit da matriz de confiança exige das
dimensões: o que o sinal não determina. Por exemplo, alerta verdadeiro também
pode ser urgente. É o que impede o catálogo de virar detector de falsidade.

**Vaga reservada, não preenchida: `conspiração`.** Aparece nos casos 01 e 06 e
como cartão-semente, mas se confunde com crítica legítima a governo, o mesmo
risco que tirou `indignação` na decisão 13. A decisão fica para a matriz de
confiança (tasks 4.x de `add-engage-desinformacao-saude`), para o catálogo não
virar vocabulário paralelo ao dela, como a `proposal.md` proíbe. A conciliação é
a task 8.1.

**Prevalência no corpus: medida e descartada como critério.** Foram contados
marcadores léxicos nas 4.063 checagens de saúde do FactCenter. Por amostra, a
precisão deles foi baixa: cerca de 1 acerto em 5 para conspiração, 2 em 5 para
urgência e 3 em 5 para medo. "Urgente" aparece mais em manchete política do que
em corrente, e "esconde" aparece no texto do próprio checador. Contagem assim
não sustenta escolha de rótulo. O catálogo se apoia no que foi verificado caso a
caso na forense. Medir prevalência de verdade exige anotação, e cabe na
curadoria da task 6.1.

### 7. Validação do rótulo: marcador explícito, pertinência e não adequação — 28/09/2026

Task 3.3. Código em `prototipo/resposta/catalogo.py`, testes em
`prototipo/resposta/tests/test_catalogo.py`.

O bloco 3 declara a técnica depois do marcador `Técnica:`, e a validação lê só o
que vem depois dele. Sem marcador não há como separar o rótulo do uso comum das
mesmas palavras. "Isso é uma cura milagrosa" pode ser rótulo ou só frase, e a
validação não adivinha. Resposta sem marcador é defeito. O marcador é, portanto,
contrato com o prompt da task 3.2, que MUST exigi-lo. As respostas da sonda de
18/09, anteriores ao contrato, reprovam as três por falta de marcador.

A validação confere **pertinência** ao catálogo, não **adequação** ao caso:
`manchete exagerada` numa promessa de cura passa. A decisão 10 de
`add-selecao-modelos-arquitetura-rag` mediu exatamente essa instabilidade, e o
segundo critério depende de casos rotulados à mão, o que é a curadoria da task
6.1. Fica registrado para que ninguém leia o verde desta validação como rótulo
certo.

A forma sem evidência de `fix-resposta-sem-evidencia` inverte a regra: ali
qualquer rótulo é defeito. `rotulos_marcados` serve às duas verificações; o
teste daquele lado é a task 3.3 do fix.

### 8. Extração: o modelo lista e gradua, o código seleciona — 29/09/2026

Task 2.1. Prompt e leitura em `prototipo/verificacao/extracao.py`, testes em
`prototipo/verificacao/tests/test_extracao.py`, sonda em
`prototipo/sonda_extracao_decomposicao.py`.

O modelo devolve JSON com todas as alegações da mensagem, e cada uma traz
`saude` (sim ou não) e `risco` (`alto`, `medio` ou `baixo`). O risco `alto` é o
que leva a agir sobre o corpo: tomar, parar ou recusar remédio, vacina ou
tratamento, ou demorar para procurar atendimento. Quem escolhe a alegação
verificada é o código: a de saúde com maior risco, e no empate a primeira da
mensagem. Assim a regra de desempate fica fixa e testável, e a escolha não muda
de uma tentativa para outra por causa da ordem em que o modelo escreve. As
demais alegações seguem na ordem da mensagem, para o cenário que oferece
verificá-las. Sem alegação de saúde, a mensagem não é verificável, e a opinião
copiada vai para a explicação do cenário Texto sem alegação verificável.

Sonda de 29/09, com Gemma 4 12B QAT, `think: false` e três tentativas por caso:
uma alegação (caso 02 da forense) 3/3, várias alegações 3/3, só opinião 3/3.
Dois achados:

- O modelo parte a mensagem em mais alegações do que há. Por exemplo, "Estudo
  da UFMG" sai como alegação separada. A seleção por risco absorve isso.
- Relato pessoal sai como alegação de risco `alto`: "minha tia parou o remédio
  e melhorou" empata com "o chá de boldo cura hepatite". Nesta mensagem o
  desempate por ordem acerta, mas com o relato antes da alegação o código
  escolheria o relato. Ver Questões em aberto.

### 9. Decomposição: força da evidência separada do salto — 29/09/2026

Task 2.5. Código em `prototipo/verificacao/decomposicao.py`, testes em
`prototipo/verificacao/tests/test_decomposicao.py`, mesma sonda da decisão 8.

A saída tem `fatos`, `evidencias` (cada uma com `forca`: `forte`, `fraca` ou
`ausente`), `opinioes` e `conclusao` (com `decorre` e `salto`). A força diz só
se dá para localizar a evidência. Se ela sustenta a conclusão, quem responde é
o `salto`. Na primeira versão do prompt, "documento real usado para afirmar
mais do que diz" contava como evidência fraca, e o modelo classificou a bula
como `forte` nas três tentativas. Isso estava coerente com a outra metade da
definição, porque a bula existe e dá para localizar. Separar as duas perguntas
tirou a contradição do prompt e deixou o caso 04 onde ele pertence: o fato
confere, e o problema está no salto até a conclusão.

A decomposição não emite veredito. `defeitos` reprova "é falso", "é
verdadeiro", "mentira", "boato" e "fake" em qualquer campo, mas aceita a
palavra solta dentro da alegação ("o verdadeiro remédio é..."). Também reprova
opinião repetida como fato.

Sonda de 29/09: caso misto 3/3 e fato verdadeiro com conclusão que não decorre
3/3. Na primeira rodada o caso misto deu 2/3, porque a tentativa 2 pôs "remédio
de farmácia só faz mal" também em `fatos`. O prompt passou a dizer que cada
frase vai para um lugar só e que "eu acho" marca opinião. A rodada gravada no
relatório é a segunda.

### 10. Fronteira de orientação em saúde: guardrails de tom, recusa e bypass de emergência — 29/09/2026

Task 4.2. Especificação completa em `specs/fronteira-orientacao-saude/spec.md`.

O copiloto de verificação atua exclusivamente na checagem de fatos e desinformação,
não podendo atuar como consultor clínico nem substituir conduta médica. Para
preservar a segurança do usuário e a integridade ética do produto:

1. **Pedido de conduta individual:** Recusa explícita e acolhedora, sem emitir
   juízo afirmativo ou negativo sobre dosagens ou alterações medicamentosas,
   direcionando à UBS / médico de referência.
2. **Sinal de risco imediato / urgência médica:** Prioridade absoluta sobre a
   checagem. Diante de sintomas graves ou agudos (dor torácica, dispneia, desmaio),
   o pipeline de RAG é **bypassado** para orientar busca imediata por SAMU (192)
   e UPA / Pronto-Socorro.
3. **Veredito sem prescrição alternativa:** Ao desmentir boato de cura caseira ou
   tratamento milagroso, o sistema explica a falta de evidência mas MUST NOT
   prescrever fármaco ou terapia substituta, orientando os canais SUS (UBS e 136).
4. **Salvaguarda de saúde mental:** Gatilho protetivo para sofrimento psíquico ou
   ideação suicida direcionando ao CVV (188).
5. **Dualidade de canais (Web e WhatsApp):** Fornece variantes de texto adaptadas
   às convenções de cada canal (markdown padrão para web e microformatação com
   emojis pontuais e bullet points objetivos para WhatsApp).

### 11. Classificação: rótulo, trechos citados e critério — 29/09/2026

Task 2.2. Código em `prototipo/verificacao/classificacao.py`, testes em
`prototipo/verificacao/tests/test_classificacao.py`, sonda em
`prototipo/sonda_classificacao_guarda.py`.

O modelo recebe a alegação e os trechos recuperados, numerados `T1`, `T2`...,
com agência, data e o veredito que a agência deu. Ele devolve três coisas: um
dos quatro rótulos, escrito igual à spec; os identificadores dos trechos que o
sustentam; e o critério. Veredito sem critério é defeito de forma, porque o
veredito é permitido, mas nunca nu. O prompt avisa que o veredito da agência
vale para a alegação que a agência checou, e que o modelo precisa conferir se é
a mesma antes de usá-lo. O prompt também manda não rebaixar a alegação que soa
absurda, conforme o cenário Alegação verdadeira contra-intuitiva.

Sonda de 29/09, com Gemma 4 12B QAT, `think: false`, três tentativas por caso e
fragmentos reais do índice: `falso` (jatobá, Aos Fatos) 3/3; `verdadeiro`
contra-intuitivo (criança em caixão lacrado que testou negativo, Comprova) 3/3;
`verdadeiro fora de contexto ou exagerado` (vídeo de abril postado como atual,
Comprova) 3/3. Nos três casos, o critério cita o que o trecho diz, não o que o
modelo sabe.

### 12. Guarda paramétrica em código, não só no prompt — 29/09/2026

Task 2.3. Código em `prototipo/verificacao/guarda.py`, testes em
`prototipo/verificacao/tests/test_guarda.py`, mesma sonda da decisão 11.

A regra da spec não fica a cargo do prompt. Ela vale em três pontos, todos em
código:

1. **Sem trecho, o modelo não é chamado.** O resultado é `evidência
   insuficiente` direto, e não há como o modelo responder de memória.
2. **Limiar como parâmetro.** Trecho com score abaixo de `limiar` conta como
   não recuperado. O valor é a task 1.5, bloqueada por 1.1 e 1.2. Até lá, o
   parâmetro não tem valor padrão, e todo trecho recuperado vai ao modelo.
3. **Veredito tem de citar trecho recuperado.** Veredito sem trecho citado, ou
   que cita identificador que não foi enviado, cai para `evidência
   insuficiente`. O que o modelo disse fica em `original`, para auditoria.

Sonda de 29/09, quatro casos com alegação que o modelo conhece: sem trecho
3/3; trecho de outro assunto 3/3; mesmo remédio, outra alegação (cloroquina)
3/3; regra parecida para outra doença (jatobá e câncer diante de goiabeira e
dengue) 3/3. Nos três casos com trecho, quem disse `evidência insuficiente` foi
o próprio modelo, e o ponto 3 da guarda não precisou agir. Por isso ele fica
coberto só pelos testes.

**Limite declarado.** A guarda não pega veredito que cita um trecho real que
não cobre a alegação. Isso depende do prompt, e os casos G3 e G4 medem
exatamente isso. Pegar esse caso em código exige o limiar da task 1.5 ou a
ancoragem trecho a afirmação da task 1.6.

### 13. Protocolo ético: TCLE e debriefing operacional — 29/09/2026

Task 6.3. Documento em `specs/avaliacao-instrumento/protocolo-etico-tcle-debriefing.md`.

O teste do copiloto com usuários (prioritariamente idosos) e o uso de 4 a 6 itens-armadilha para medir aceitação cega exigem conformidade estrita com o Conep/CEP (Resoluções CNS 510/2016 e 466/2012):

1. **TCLE com linguagem acessível e consentimento sobre itens-armadilha:** O participante é previamente esclarecido de que o sistema contém simulações de testes com deduções intencionalmente incorretas para aferir confiabilidade, sem adiantar quais são os itens.
2. **Debriefing supervisionado obrigatório:** Imediatamente após a sessão, o pesquisador abre o gabarito oficial com a verdade científica baseada em fontes do SUS (MS, Fiocruz, Anvisa), neutralizando qualquer risco de fixação de desinformação.
3. **Privacidade e proteção de dados:** Processamento local e anonimização estrita, sem exposição de dados do usuário a APIs comerciais externas (consistente com Decisão 8 do RAG).

### 14. Reforço do mito: menção reconhecida pelas palavras da alegação — 29/09/2026

Task 3.4. Código em `prototipo/resposta/mito.py`, testes em
`prototipo/resposta/tests/test_mito.py`.

`verificar_mito(resposta, alegacao)` confere as três exigências do requirement
Ausência de reforço do mito, frase a frase, sem os títulos de bloco:

1. A primeira frase não menciona a alegação.
2. Toda frase que menciona a alegação traz marcação de falso: "é falso",
   "não é verdade", "não há comprovação", "boato", "desmentido", ou negação
   direta de uma palavra da alegação ("a casca não cura o câncer").
3. Depois da última menção vem pelo menos uma frase sem menção. É a afirmação
   correta que fecha o sanduíche.

Uma frase menciona a alegação quando traz pelo menos 60% das palavras de
conteúdo dela, e no mínimo duas. A comparação é pelo começo da palavra, sem
acento, para que "cura" e "cure" contem como a mesma. Vale para o veredito
`falso`. Quem chama a verificação é a montagem da resposta, que é a task 3.2.
Assim como o marcador `Técnica:` da decisão 7, este verificador é contrato com
o prompt da 3.2: a resposta que ele reprovar é defeito do prompt.

As duas respostas `falso` da sonda de 18/09 (T2 e T3, jatobá) passam. Ambas
abrem com "VEREDITO: Falso." e marcam a menção com "não é verdade que" e "não
existe comprovação de que".

**Limite declarado.** Menção por paráfrase, com outras palavras, escapa. Menção
por pronome ("essa informação") também escapa, mas essa não repete o mito. O
limiar de 60% foi escolhido nos exemplos dos testes, não medido em corpus.
Medir exige respostas reais da 3.2.

### 15. Fronteira: regras antes do modelo, respostas padrão lidas da spec — 29/09/2026

Task 4.1. Código em `prototipo/verificacao/fronteira.py`, testes em
`prototipo/verificacao/tests/test_fronteira.py`, sonda em
`prototipo/sonda_fronteira.py`. Segue o contrato da decisão 10.

São quatro categorias, em ordem de prioridade: `risco_imediato`,
`sofrimento_psiquico`, `conduta_individual` e `checagem`. A mensagem pode ter
mais de uma, e as respostas padrão se empilham nessa ordem.

- **Regras primeiro.** O léxico em PT-BR roda em microssegundos. Se ele acha
  risco imediato ou sofrimento psíquico, o resultado sai sem chamar o modelo, e
  o bypass da checagem cumpre os 500 ms do contrato. Sintoma de risco só conta
  com marca de que está acontecendo com alguém ("estou com", "meu pai",
  "agora"). Sem essa marca, "recebi que dor no peito se cura com água" viraria
  emergência.
- **Modelo depois.** O modelo pega pedido indireto ("o que você acha?") e
  sofrimento dito sem as palavras fortes. Conduta achada pelas regras se soma à
  do modelo. Saída inválida do modelo deixa só as regras.
- **Respostas padrão lidas da spec.** `carregar_respostas` lê os blocos
  "Resposta Padrão" de `fronteira-orientacao-saude` direto do arquivo da spec.
  Não há cópia do texto no código que possa divergir dela.

Sonda de 29/09, com Gemma 4 12B QAT, `think: false`, 14 mensagens e três
tentativas cada: classificador 42/42, e modelo sozinho também 42/42. Bypass em
0 ms nas 15 tentativas de risco e de sofrimento; o caminho pelo modelo levou de
3,2 a 9,6 s. Na primeira rodada, a regra de sintoma "não acorda" casou com "seria
melhor não acordar mais" e mandou ao SAMU quem precisava do CVV (F10, 0/3). A
regra foi corrigida e F10 virou teste.

**Limites declarados.**

- As regras foram ajustadas com as mesmas mensagens da sonda. O acerto delas
  fora dessas mensagens é o que a bateria adversarial da task 4.3 mede.
- Emergência que o léxico não reconhece ainda chega ao bypass pelo modelo, mas
  em segundos, fora dos 500 ms.
- Quando as regras acham risco imediato, o modelo não roda. Sofrimento
  psíquico dito de forma indireta na mesma mensagem fica sem a resposta do CVV,
  e a resposta do SAMU vai sozinha.

### 16. Esquema de indexação, versão 1.0.0 — 29/09/2026

Task 1.1. Contrato em `prototipo/indice/esquema_indexacao.json` (JSON Schema
draft-07), validador em `prototipo/rag/esquema.py`, testes em
`prototipo/rag/tests/test_esquema.py`, laudo em
`prototipo/indice/validacao_esquema.json`. Reexecução:
`python -m prototipo.rag.esquema`.

**O que já existia e o que faltava.** As unidades e os fragmentos do recorte de
saúde do FactCenter foram construídos na task 2.2 de
`add-selecao-modelos-arquitetura-rag` (decisão 11 daquele change), mas a forma
deles estava só no código. O MVP exige do índice quatro coisas que a prova de
conceito não gravava: saber de que corpus veio o registro (FACTCK.BR entra na
1.2), se é checagem ou comunicado oficial (1.3), em que idioma está (a prioridade
PT-BR antes de EN da 1.4) e o nome exibível da agência (atribuição em
`recuperacao-evidencia`). E `integridade-textual` exige saber, por registro, se o
texto pode virar citação.

**Duas coleções, campos fechados.**

| Coleção | O que é | Campos novos nesta versão |
| --- | --- | --- |
| unidade | uma alegação com veredito e justificativa; unidade de citação e de atribuição | `corpus`, `tipo_fonte`, `idioma`, `apto_citacao`, `agencia_nome` |
| fragmento | pedaço da justificativa com cabeçalho alegação + veredito; é o que os braços léxico e denso indexam | os mesmos cinco, repetidos da unidade |

`additionalProperties` é `false`: campo, corpus ou valor de enum novo passa pelo
esquema antes de chegar ao construtor. O rótulo nos quatro valores de
`verificacao-alegacao` **não** está no esquema. Ele é da task 2.3 de
`add-tratamento-datasets-ptbr`, e o teste `test_campo_fora_do_esquema_e_recusado`
garante que ele não entre por fora.

**Doze invariantes que JSON Schema não expressa** (`x-invariantes`), conferidas
pelo validador. As que carregam as specs: I3, agência, data e URL em todo
fragmento, sem divergência da unidade; I4, alegação nunca separada do veredito;
I5, trecho literal da justificativa; I10, a mesma URL não entra por dois corpora;
I12, a contagem fecha contra os registros declarados.

**Identidade preservada.** `registro_id` continua `sha1(url)[:10]` no FactCenter,
com prefixo vazio. As 20 chaves de `prototipo/rag/consultas_afericao.json`
seguem válidas, e a aferição da decisão 15 daquele change não precisa ser
refeita por causa do esquema. O FACTCK.BR recebe o prefixo `fb-`.

**Achado: uma alegação indexada sem justificativa.** O validador reprovou o
índice da prova de conceito em um registro. Na checagem da Lupa sobre câncer de
pele (05/03/2020), o texto raspado termina na quinta alegação, «A quantidade de
filtro solar influencia na prevenção do câncer de pele», que tem veredito
`VERDADEIRO` e nenhuma justificativa. Resultado: um fragmento só com cabeçalho,
que nenhuma afirmação da resposta consegue ancorar. O construtor agora manda a
unidade para a quarentena com motivo `justificativa_ausente` e mantém as quatro
irmãs. O índice passa de 5.090 unidades e 22.464 fragmentos para **5.089 e
22.463**. Os 88 registros mistos continuam em quarentena. A contagem fecha:
3.975 registros com unidade mais 88 em quarentena dão 4.063.

**Mapeamento do FACTCK.BR, medido e não executado.** A indexação é da 1.2. O
esquema só fixa o mapeamento, para a 1.2 não mudar o contrato. Medido em
`FACTCKBR.tsv` em 29/09/2026: 1.313 linhas de três agências (Lupa 528, Truco 415,
Aos Fatos 370), de 2016 a 2019. Cada linha já é uma alegação com seu próprio
veredito, então não existe o problema de segmentação do FactCenter. Há 91 URLs
com mais de uma alegação, até 27. Quatro pontos ficam para a 1.2:

- **Não é apto a citação.** O próprio TSV distribuído tem `Ã` 0 contra `ã`
  3.625, `Ç` 0 contra `ç` 2.312 e `Ú` 0 contra `ú` 973. A perda é irreversível
  (`integridade-textual`), por isso `apto_citacao` fica `false`. O corpus serve à
  recuperação, não a trecho exibido.
- **Sobreposição com o FactCenter.** 106 linhas (74 URLs) já estão no recorte de
  saúde do FactCenter. Pela I10, o corpus apto a citação vence.
- **Campos vazios.** `claimReviewed` vazio em 13 linhas, `reviewBody` em 12 e
  `alternativeName` em 4. Todas vão para a quarentena; o título não substitui a
  alegação.
- **Veredito e data.** A escala de `ratingValue` muda por agência (5, 6 e 8), e
  só `alternativeName` é usado. A Lupa grava data e hora, que são truncadas.

O FACTCK.BR **não é um recorte de saúde**: cobre política e outros temas. Filtrar
por tema, ou não filtrar, é decisão da 1.2.

**Consequência operacional.** O índice foi reconstruído em 29/09/2026 com
`python -m prototipo.rag construir` (2.454 s de braço denso), mas a execução
rodou sobre o código anterior ao esquema, porque um `git pull` guardou esta task
em stash. Em vez de reconstruir outra vez, a linha do fragmento
`4ce7e4777f-04-00` foi removida da matriz densa, e as 22.463 restantes foram
conferidas contra os fragmentos novos, com texto e id iguais na mesma ordem. O
`manifesto.json` agora declara esquema 1.0.0, 5.089 unidades e 22.463
fragmentos, e registra a derivação em `matriz_densa`.

A matriz densa tem uma linha por fragmento e MUST ser reconstruída junto com os
`.jsonl`. Rodar só `python -m prototipo.rag.unidades` sobre uma `densa.npy`
antiga desalinha fragmento e vetor. `construir` agora avisa cada etapa em stderr.
`jsonschema` entrou em `requirements-rag.txt`, mas o `.lock` só pode ser
regenerado no ambiente fixado (Python 3.14.6, M4), que não é o desta
verificação.

### 17. FACTCK.BR indexado como fonte auxiliar, esquema 1.1.0 — 01/10/2026

Task 1.2. Construtor em `prototipo/rag/unidades.py` (`construir_factckbr` e
`construir_indice`), leitura e portão em `prototipo/rag/corpus.py`, testes em
`prototipo/rag/tests/test_factckbr.py`, laudo em
`prototipo/indice/validacao_esquema.json`. Reexecução: `python -m
prototipo.rag.esquema` (sem braço denso) e `python -m prototipo.rag construir
--estender` (índice completo).

**Três decisões do grupo, tomadas antes do código** (Samara e Vitor, 01/10/2026):

1. **Contradição entre specs, resolvida a favor da recuperação.**
   `integridade-textual` vedava o arquivo reprovado também para recuperação, e
   `recuperacao-evidencia` manda indexar o FACTCK.BR. As duas não cabiam juntas.
   O requirement de `integridade-textual` foi revisado em
   `add-tratamento-datasets-ptbr`: o arquivo reprovado não serve a citação, mas
   pode entrar no índice com todo registro em `apto_citacao=false`, e o texto
   dele MUST NOT chegar ao usuário. Serve para nomear a agência, ligar para a
   checagem e contar rótulo. A alternativa, o FACTCK.BR só para contagem, foi
   descartada porque deixaria fora da busca 898 checagens que o FactCenter não
   tem.
2. **Mapa de vereditos 1.1.0.** Quatro chaves do FACTCK.BR não constavam do mapa
   e, por `normalizacao-rotulos`, interrompiam o processamento (75 linhas):
   `sem contexto` (Truco, 42) → `verdadeiro fora de contexto ou exagerado`, como
   `fora de contexto` do Estadão; `impossivel provar` (Truco, 20),
   `discutivel` (Truco, 12) e `outros` (Aos Fatos, 1) → `nao_mapeavel`. O rótulo
   de destino continua fora do índice (decisão 16); o portão só garante que toda
   `veredito_chave` indexada tem decisão registrada.
3. **Sem filtro de tema.** O FACTCK.BR cobre política e outros temas. Um filtro
   por termo foi medido e reprovado: pegou 243 linhas com falso positivo
   evidente (STF, eleição) e perderia alegação de saúde dentro de pauta política
   (insulina no SUS, Mais Médicos, febre amarela). O corpus entra inteiro, e a
   aferição das 20 consultas confere se a busca piora.

**Achado: a contagem declarada no esquema 1.0.0 reprovaria qualquer
construção.** `registros_declarados` era 1.313, o número de linhas, mas a I12
conta registros por URL, e são 984. O esquema 1.1.0 declara 984 registros e
1.313 linhas (`linhas_declaradas`, conferida na leitura). Campo novo em
`x-corpora`, versão menor.

**Como o TSV vira unidade.** Registro é a URL. Cada linha já é uma alegação com
seu veredito: URL de uma linha é `unica`, de várias é `segmentada` com origem
`claim_review`. `indice_alegacao` é a ordem da linha na URL e preserva a lacuna
quando uma irmã vai para a quarentena. A data da Lupa perde a hora. O cabeçalho
dos fragmentos usa o nome exibível da agência, porque a grafia do corpus é um
pedaço de URL (`https:apublica.org`) que só poluiria os braços léxico e denso. No
FactCenter o cabeçalho não mudou.

**Números, conferidos pelo validador.**

| | FactCenter | FACTCK.BR |
| --- | --- | --- |
| registros declarados | 4.063 | 984 (1.313 linhas) |
| com unidade | 3.975 | 898 (813 `unica`, 85 `segmentada`) |
| em quarentena inteira | 88 | 86 (74 `duplicata_factcenter`, 12 `campo_vazio`) |
| unidades | 5.089 | 1.190 |
| unidades em quarentena | 1 | 5 (`campo_vazio`) |
| fragmentos | 22.463 | 1.192 |

As 74 URLs duplicadas estão todas indexadas no FactCenter, e a I10 dá a
checagem ao corpus apto a citação. Índice total: 6.279 unidades, 23.655
fragmentos, esquema 1.1.0 aprovado sem violação.

**Aferição sem filtro de tema: a busca não piorou.** `python -m prototipo.rag
aferir` com `multilingual-e5-base`, no ambiente fixado, 01/10/2026, sobre as 20
consultas de `consultas_afericao.json`, contra a aferição da decisão 16:

| modo | recall@1 | recall@5 | MRR antes | MRR depois |
| --- | --- | --- | --- | --- |
| léxica | 0,60 | 0,85 | 0,725 | 0,725 |
| densa | 0,80 | 1,00 | 0,877 | 0,877 |
| híbrida, score (padrão) | 0,85 | 1,00 | 0,897 | 0,897 |
| híbrida, RRF | 0,85 | 0,85 | 0,850 | 0,855 |

Nos três primeiros modos a posição do alvo é a mesma em todas as 20 consultas.
No RRF, a16 passou de não encontrada para a décima posição (recall@10 de 0,85
para 0,90). Nas oito consultas sem alvo da calibração do limiar, o primeiro
recuperado é o mesmo de antes e nenhum é do FACTCK.BR. Os scores mudam na
terceira casa decimal porque o fundo de cada consulta (percentis 50 e 99) agora
inclui 1.192 fragmentos a mais. As faixas continuam sobrepostas: alvo de 0,5785
a 0,7831, ruído de 0,5739 a 0,69. A conclusão da task 1.5 não muda: não há
limiar sobre score bruto. No braço léxico, nenhum fragmento do FACTCK.BR ficou
entre os cinco primeiros de nenhuma consulta. O conjunto de aferição só tem
alvos no FactCenter, então mede que o FACTCK.BR não atrapalha, e não que ele
ajuda.

**A matriz densa é estendida, não refeita.** O FactCenter fica à frente e
idêntico, e o teste `test_factcenter_continua_identico_e_na_frente` garante isso
por id e texto. `construir --estender` reaproveita as 22.463 linhas gravadas
depois de conferir que os fragmentos em disco são prefixo exato dos novos, e
calcula só os 1.192 vetores do FACTCK.BR (20 s no M4, contra 2.454 s da
reconstrução inteira). Qualquer divergência recusa a extensão. Matriz final:
23.655 × 768, uma linha por fragmento.

**Portão de integridade invertido.** Para o FACTCK.BR, o portão não exige
aprovação: exige que o laudo concorde com `apto_citacao` do esquema
(`verificar_integridade_auxiliar`). Se a recoleta da task 3.5 de
`add-tratamento-datasets-ptbr` um dia aprovar o arquivo, a construção para, e
alguém troca o esquema de propósito.

**Correção colateral.** `verificar_fidelidade_dos_trechos`, de
`tratamento/integridade.py`, construía o índice sobre uma amostra de 500
registros com o esquema ligado, e a I12 o reprovava desde a decisão 16. O
teste ficava vermelho na `main`. A verificação de fidelidade agora constrói sem
validar o esquema, porque a I12 só vale para o corpus inteiro.

**Fica para a 1.6.** A busca (`hibrida.py`) ainda não lê `apto_citacao`. Até a
ancoragem trecho a afirmação existir, nada no código impede que um trecho do
FACTCK.BR seja exibido. A 1.6 MUST descartar como âncora todo fragmento com
`apto_citacao=false` e usar dele só agência, link e veredito.

### 18. Quatro blocos: o modelo escreve o conteúdo, o código a forma — 01/10/2026

Task 3.2. Código em `prototipo/resposta/estrutura.py`, testes em
`prototipo/resposta/tests/test_estrutura.py`, sonda em
`prototipo/sonda_resposta.py`, resultado por tentativa em
`prototipo/relatorio_sonda_resposta.json`.

`responder(texto, alegacao, veredito, decomposicao, lacuna)` recebe o
`Veredito` da guarda (decisão 12) e devolve a camada visível, a camada de
detalhe e a lista de defeitos. Segue a redação do requirement Estrutura de
quatro blocos dada por `fix-resposta-sem-evidencia`, com as duas formas.

**O que sai do código.** A forma, escolhida pelo estado da recuperação: com
evidência quando o veredito cita trecho, sem evidência quando é `evidência
insuficiente` ou lacuna de acervo. Lacuna com trecho recuperado é recusada,
porque trocaria a forma. Também saem do código a ordem e os títulos dos blocos,
a abertura do bloco 1 com o rótulo da guarda, a frase da data de corte e o
ponteiro da lacuna, e a camada de detalhe com agência, data, link, veredito da
agência e trecho. O modelo não muda o veredito: se ele escrever "Verdadeiro" no
bloco 1, a abertura continua "Falso.". Data de corte e ponteiro seguem a
recomendação da decisão 4 do fix: lá o modelo omitiu a data 9 vezes em 9.

**O que sai do modelo.** O texto dos quatro blocos, em JSON. Um prompt só para
as duas formas, com o estado na mensagem (risco 1 do fix).

**O que é conferido depois**, sem derrubar a resposta. Os defeitos ficam em
`Resposta.defeitos`, para quem chama decidir:

- forma com evidência: rótulo do catálogo depois de `Técnica:` no bloco 3
  (contrato da decisão 7), reforço do mito no `falso` (contrato da decisão 14)
  e, quando a decomposição traz opinião, o bloco 2 dizendo que aquela parte é
  opinião (`verificacao-alegacao`);
- forma sem evidência: nenhum rótulo do catálogo, marcado ou solto, e o bloco 3
  sem dizer que a mensagem engana;
- as duas formas: até 120 palavras na camada visível, frases de até 20
  palavras (`acessibilidade-leitura`) e nenhum "T1" visível, porque os trechos
  ficam na camada de detalhe.

**Veredito `verdadeiro` não nomeia técnica.** A spec manda o bloco 3 da forma
com evidência nomear técnica, e o cenário Alegação verdadeira manda o mesmo
bloco explicar por que a mensagem era difícil de avaliar. Rótulo de manipulação
em mensagem verdadeira desdiria o veredito. Na sonda isso aconteceu uma vez,
com `fora de contexto` no caso do caixão. A leitura adotada segue o cenário:
técnica em `verdadeiro` é defeito, e o título do bloco 3 muda para "POR QUE
PARECIA DIFÍCIL DE ACREDITAR:". Fica como questão aberta abaixo, para a spec
dizer isso em texto expresso.

**Sonda, 21 de 21.** Gemma 4 12B QAT, `think: false`, três tentativas por caso,
no MacBook Air M4, sem `--cpu`. Os vereditos entram prontos, com fragmentos
reais do índice.

| Caso | Estado | Técnica na resposta | Passou |
| --- | --- | --- | --- |
| R1 | `falso`, jatobá, "um médico confirmou" | `cura milagrosa, fonte sem nome` | 3/3 |
| R2 | `falso`, jatobá, com opinião | `cura milagrosa` | 3/3 |
| R3 | `verdadeiro` contra-intuitivo, caixão | nenhuma | 3/3 |
| R4 | fora de contexto, vídeo da cloroquina | `fora de contexto` | 3/3 |
| S1 | `evidência insuficiente`, goiabeira | nenhuma | 3/3 |
| S2 | lacuna com ponteiro, vacina da dengue | nenhuma | 3/3 |
| S3 | lacuna sem ponteiro, oropouche | nenhuma | 3/3 |

As respostas tiveram de 64 a 80 palavras, com mediana de 9,8 s (de 6,5 a
23,4 s). O 21 de 21 é da terceira versão do prompt. As anteriores mostraram três
defeitos, e cada um virou regra:

1. O bloco 3 levava "por que engana" em cima de veredito `verdadeiro`.
2. No R1, a escolha foi `fonte sem nome` 3 vezes em 3, embora a mensagem
   prometesse cura. O cenário Promessa de cura pede `cura milagrosa`. O prompt
   agora aceita até dois rótulos e diz que promessa de cura é sempre
   `cura milagrosa`.
3. O bloco 1 abriu com "A informação diz que a casca do jatobá cura o câncer",
   sem marcação de falso. O verificador da 3.4 pegou a frase.

**Bloco 2 com ponteiro, 01/10.** A decisão 5 do fix definiu que, na lacuna
com ponteiro, o bloco 2 fala só do acervo consultado e não julga a alegação. Na
primeira sonda o S2 escreveu "não encontrar não significa que seja falsa" 3
vezes em 3, ao lado de um ponteiro com veredito `falso`. A instrução no prompt
não resolveu: com ela, o S2 repetiu a frase 3 vezes em 3, e o R3 deixou o bloco 3
vazio em 2 de 3. Pelo mesmo motivo da data de corte, o bloco 2 com ponteiro
passou a sair do código (`BLOCO_2_COM_PONTEIRO`): «O acervo consultado aqui não
cobre esta mensagem. Não achar nele não confirma nem desmente nada.» O prompt
voltou a ser o da rodada anterior. A sonda refeita deu 21 de 21, com respostas
de 65 a 82 palavras e mediana de 11,2 s (de 6,2 a 27,1 s).

**Limites declarados.**

- A adequação do rótulo ao caso continua fora do código, como na decisão 7. O
  defeito 2 só apareceu porque as respostas foram lidas.
- Afirmação do bloco 2 sem trecho de origem não é pega aqui: ancorar cada
  afirmação a um trecho é a task 1.6. Exemplo: no R3, "o exame saiu uma semana
  depois".
- Defeito não gera nova tentativa. Se a montagem final repete a chamada ou
  devolve a resposta com o defeito registrado é decisão de quem integra o
  fluxo.

### 19. Lista de fontes oficiais aceitas: Ministério da Saúde, Fiocruz e Anvisa — 01/10/2026

Task 1.3. R2 Wingrid. Registro estruturado em `prototipo/indice/fontes_oficiais.json`.

O índice reserva `tipo_fonte: "comunicado_oficial"` para documentos institucionais de saúde pública brasileira (decisão 16). Ao contrário das checagens de agências, comunicados oficiais **não têm veredito**: trazem evidência sanitária, regulatória e epidemiológica oficial.

**Critérios de inclusão e domínios:**
1. **Ministério da Saúde (MS):** autoridade sanitária nacional do SUS. Domínios autorizados: `gov.br/saude` e `saude.gov.br`. Documentos aceitos: notas técnicas, boletins epidemiológicos, informes do PNI e desmentidos do programa *Saúde com Ciência*.
2. **Fundação Oswaldo Cruz (Fiocruz):** principal instituição de C&T em saúde pública da América Latina. Domínios autorizados: `fiocruz.br`, `portal.fiocruz.br`, `agencia.fiocruz.br` e `observatorio.fiocruz.br`. Documentos aceitos: relatórios de pesquisa, boletins InfoGripe e pareceres institucionais.
3. **Agência Nacional de Vigilância Sanitária (Anvisa):** autoridade regulatória federal. Domínios autorizados: `gov.br/anvisa`, `anvisa.gov.br` e `consultas.anvisa.gov.br`. Documentos aceitos: alertas sanitários, resoluções (RDC), registros de medicamentos/vacinas e notas regulatórias.

**Vedação:** pronunciamentos e posts em redes sociais sem publicação em diário ou portal oficial não são indexados como comunicado oficial.

### 20. Camada visível e camada de detalhe: separação arquitetural e de interface — 01/10/2026

Task 5.1. R2 Wingrid.

A experiência do usuário organiza-se em duas camadas complementares, assegurando acessibilidade imediata e auditabilidade integral:

1. **Camada Visível (Entrega Primária — Web e WhatsApp):**
   - Resumo rápido de alta legibilidade, respeitando o teto de 120 palavras e frases de até 20–25 palavras (`acessibilidade-leitura`).
   - Apresenta rigorosamente os 4 blocos ordenados de `resposta-formativa`.
   - Veda termos técnicos herméticos e jargões metodológicos sem glossário explicativo entre parênteses.
   - Possui uma única ação primária por tela (ex.: botão "Ver fontes e detalhes" ou "Fazer nova pergunta").

2. **Camada de Detalhe (Auditabilidade e Aprofundamento — por Ação Explícita):**
   - Acessível sob demanda (toque/clique no botão de detalhes no chat web ou link com payload no WhatsApp).
   - Contém: trecho literal da justificativa recuperada, identificação e data da agência/órgão, URL original, critérios de checagem, e versão original em inglês quando houver tradução (auditabilidade de tradução).

### 21. Fluxo de primeira verificação sem cadastro — 01/10/2026

Task 5.3. R2 Wingrid.

Para maximizar o impacto social e garantir acesso universal à checagem de saúde, a primeira verificação elimina completamente barreiras de entrada (zero-friction):

1. **Entrada Direta:** o usuário acessa a aplicação web (ou inicia conversa no WhatsApp) e pode imediatamente colar texto, encaminhar mensagem ou enviar link de notícia.
2. **Sem Cadastro Prévio:** o sistema não exige login, senha, cadastro, e-mail nem CPF para processar a verificação e entregar a resposta formativa.
3. **Aderência à LGPD:** mensagens de consulta são processadas de forma anônima e desidentificada, sem retenção de dados pessoais identificáveis.
4. **Jornada do Usuário:** Input do texto -> Feedback acessível de processamento -> Exibição da Camada Visível (4 blocos) -> Opção de aprofundamento na Camada de Detalhe.

### 22. Consistência do catálogo de técnicas com as dimensões da matriz de confiança — 01/10/2026

Task 8.1. R2 Wingrid.

Conferência entre o catálogo fechado de técnicas de manipulação (`prototipo/resposta/catalogo_tecnicas.json`, 7 rótulos fixados na decisão 6) e as 4 dimensões empíricas da `matriz-confianca` da fase Engage (`docs/engage/kit-matriz-confianca.md`):

| Dimensão na Matriz de Confiança | Rótulo(s) Correspondente(s) no Catálogo | Cobertura e Raciocínio |
| --- | --- | --- |
| **Dimensão 1: Falsa Autoridade ou Fonte Inexistente** | `autoridade falsa`, `fonte sem nome` | Cobre tanto a citação de falsos médicos quanto fontes anônimas/vagas. |
| **Dimensão 2: Recontextualização e Edição de Mídia** | `fora de contexto` | Cobre uso de declarações ou vídeos reais fora do momento/contexto original. |
| **Dimensão 3: Distorção de Documento Real** | `manchete exagerada`, `dado distorcido` | Cobre inflar conclusões de bulas/estudos reais ou distorcer estatísticas. |
| **Dimensão 4: Enquadramento Conspiratório** | 8ª vaga reservada (`conspiracao`), amparada por `cura milagrosa` e `urgência fabricada` | Promessas mirabolantes e senso de perigo artificial que alimentam teorias conspiratórias. |

Ficam confirmadas as remoções de "ausência genérica de link" (variância zero) e "polaridade emocional" (não é critério de veracidade), preservando a decisão 7.

### 23. Prioridade de idioma: um score, camadas cortadas dele — 01/10/2026

Task 1.4. Código em `prototipo/rag/hibrida.py` (`Recuperador.recuperar`,
`PRIORIDADE_IDIOMA`, `cobertura_padrao`, `Recuperacao`), testes em
`prototipo/rag/tests/test_prioridade_idioma.py`. A CLI `python -m prototipo.rag
buscar` passa a consultar por `recuperar` e mostra a camada.

**Duas decisões, tomadas antes do código** (Samara, 01/10/2026):

1. **"Esgotar" pede critério de cobertura.** Ordenar português antes de inglês
   não basta: as 6.279 unidades em português sempre enchem o top‑k, e o inglês
   nunca entraria. Por isso `recuperar` percorre as camadas em
   `PRIORIDADE_IDIOMA` (`pt-BR`, depois `en`) e só corta a camada seguinte quando
   o critério `cobre` recusa a anterior. Se o português cobre, nenhuma fonte em
   inglês entra, que é o cenário Alegação já checada em português. O critério é
   parâmetro, como o limiar da guarda (decisão 12). O valor é da 1.5. Até lá vale
   `cobertura_padrao`: a camada cobre se trouxe ao menos uma unidade, a leitura
   mais estrita de "esgotar". Alternativa descartada: recorrer ao inglês só com o
   português vazio como mecanismo fixo. Hoje ela é o padrão provisório, mas, fixa
   no código, obrigaria a 1.5 a mudar a 1.4.
2. **Só o mecanismo.** Nenhum corpus em inglês está indexado. O esquema 1.1.0 tem
   `en` no enum `idioma`, mas os dois corpora de `x-corpora` são `pt-BR`. O braço
   inglês está pronto e inerte, e é provado com fragmentos sintéticos. Indexar
   uma fonte em inglês amplia o escopo e fica como questão aberta.

**Pontuar uma vez, cortar depois.** A consulta é pontuada sobre o índice
inteiro, e cada camada é uma máscara sobre o mesmo vetor: o excluído vai a −∞, o
score de quem fica não muda. Dois índices separados dariam a cada camada o
próprio fundo em `_sobre_o_fundo` (mediana e percentil 99 da consulta naquela
camada). O mesmo número significaria coisas diferentes em português e em inglês,
e o limiar da 1.5 não valeria igual nas duas. O custo também fica igual: o braço
denso codifica a consulta uma vez, mesmo quando recorre ao inglês.

**O que a verificação recebe.** `Recuperacao` traz quatro campos: `idioma`, a
camada dos resultados; `resultados`, que agora têm `idioma` por unidade;
`consultados`, as camadas percorridas, na ordem; e `coberto`. Camada sem fonte
indexada não é consultada. Se nenhuma camada cobre, voltam os resultados da
primeira camada não vazia com `coberto=False`, e decidir se o veredito cai para
`evidência insuficiente` é de quem chama. `buscar` continua sendo o ranking cru
que a aferição mede.

**Com o índice de hoje, nada muda.** O `buscar` foi dividido em `_pontuar` e
`_reduzir`. No índice real (23.655 fragmentos, todos `pt-BR`), 20 consultas de
aferição mais 8 sem alvo, nos quatro modos (léxica, densa, híbrida por score e
por RRF), o `buscar` da `main`, o `buscar` novo e o `recuperar` devolveram as
mesmas unidades, na mesma ordem e com o mesmo score: 0 divergências em 112
comparações. Só o campo `idioma` é novo. O braço denso dessa conferência usou
scores sintéticos com empates, porque o modelo não estava na máquina da
verificação. A aferição com `multilingual-e5-base` não foi refeita, porque com
máscara toda verdadeira o vetor de score é o mesmo, com a mesma ordem e os mesmos
empates. O teste `test_indice_real_nas_20_consultas_da_afericao_nao_muda` repete
a conferência no braço léxico sempre que o índice existe na máquina.

**Índice que não diz o idioma não é priorizado.** Fragmento sem `idioma` (índice
anterior ao esquema 1.0.0) ou com valor fora de `PRIORIDADE_IDIOMA` faz
`recuperar` parar com erro. A busca crua continua funcionando, para não quebrar a
aferição de índices antigos.

**Fica para outras tasks.**

- **1.5:** o critério de cobertura entra por `recuperar(..., cobre=...)`, sem
  mudar a 1.4.
- **1.6:** `apto_citacao` continua sem ser lido pela busca (decisão 17).
- **Resposta e interface:** a paráfrase em português com o trecho original em
  inglês na camada de detalhe (`recuperacao-evidencia`, Auditabilidade da
  tradução). A recuperação só entrega o `idioma` de cada unidade, para que isso
  seja possível.

### 24. Ancoragem trecho a afirmação: marca declarada, termos conferidos — 06/10/2026

Task 1.6. Código em `prototipo/resposta/ancoragem.py`, `prototipo/verificacao/guarda.py`
(`Veredito.referencias`), `prototipo/resposta/estrutura.py` (`_ancorar`,
`Resposta.descartadas`, `Resposta.rebaixada_por`) e `prototipo/rag/hibrida.py`
(`apto_citacao` no resultado). Testes em `prototipo/rag/tests/test_apto_citacao.py`,
`prototipo/verificacao/tests/test_guarda.py`, `prototipo/resposta/tests/test_ancoragem.py`
e `prototipo/resposta/tests/test_estrutura.py`.

**Três decisões, tomadas antes do código** (Samara, 06/10/2026):

1. **Fragmento inapto é só metadado.** Fecha o que a decisão 17 deixou para a
   1.6. A busca entrega `apto_citacao` por resultado, e a guarda separa: o
   trecho apto vai ao modelo, numerado T1, T2...; do inapto, nem o texto nem o
   metadado vão ao modelo. Agência, data, link e veredito da agência saem em
   `Veredito.referencias` e chegam à camada de detalhe com `trecho` vazio.
   Sem trecho apto, o modelo não é chamado e o veredito é `evidência
   insuficiente`, como no ponto 1 da guarda (decisão 12). Marca ausente conta
   como inapta: índice que não diz se o trecho é citável não autoriza citá-lo.
   Alternativas descartadas: mandar o metadado ao modelo, porque convida a um
   veredito copiado da agência sem trecho que o sustente; e mandar o texto e só
   proibir a citação, porque a paráfrase de texto reprovado entraria no bloco 2.
2. **O modelo declara a âncora, o código confere por termos.** Na forma com
   evidência, os blocos 1 e 2 são listas de frases, cada uma com o trecho que a
   sustenta: `{"frase": "Nenhum estudo mostra isso.", "trecho": "T1"}`. (A
   primeira versão pedia a marca inline, `[T1]`; ver a sonda abaixo.) A frase
   passa se o trecho declarado é apto e contém os **termos
   verificáveis** dela: número em algarismos (casado inteiro), mês, quantidade
   por extenso («uma semana», «dois dias»; `um`/`uma` sozinhos são artigo) e
   nome próprio (maiúscula que não abre a frase). Agência e data de publicação
   da fonte contam como fonte. Maiúscula e acento não contam. Alternativas
   descartadas: só conferir que a marca existe (repete o limite da guarda);
   modelo como juiz por frase (soma latência a uma resposta que já leva de 6 a
   27 s, e não é determinístico); similaridade de embedding com limiar (exige
   calibração que encosta na 1.5).
3. **Frase essencial.** Frase que não passa sai da resposta e fica em
   `Resposta.descartadas`, com o motivo. O veredito cai para `evidência
   insuficiente` se a frase descartada é do bloco 1, ou se o bloco 2 fica sem
   frase ancorada. A resposta é refeita na forma sem evidência, numa segunda
   chamada ao modelo, com as referências do veredito original. A frase que
   separa a opinião da mensagem pode ficar sem marca, quando a decomposição
   achou opinião, mas não conta como ancorada: bloco 2 só com ela também
   rebaixa. Os blocos 3 e 4 tratam da técnica e do que observar, não de fato
   sobre o mundo, e não passam pela ancoragem.

**Por que agência e data contam como fonte.** No R4 da sonda da resposta, o
modelo escreveu «O prefeito fez esse anúncio em abril de 2020». «Abril» está no
trecho; «2020» não, mas é o ano da checagem (2020-07-31). A spec pede afirmação
ancorada «com fonte e data acessíveis», e a data da fonte está na camada de
detalhe ao lado do trecho.

**O exemplo da decisão 18 não se sustenta.** Lá, «o exame saiu uma semana
depois», do R3, aparece como afirmação sem trecho de origem. O trecho do R3
diz «O resultado do exame foi divulgado somente uma semana depois». A frase está
ancorada, e a regra a aceita (`test_r3_uma_semana_depois_esta_no_trecho`).

**Medição sobre respostas reais.** As 31 frases dos blocos 1 e 2 das 12
respostas R registradas em `relatorio_sonda_resposta.json` (prompt anterior,
sem marca) foram conferidas contra os trechos de cada caso: 31 de 31 ancoradas,
nenhum falso descarte. Isso mede a regra de termos, não o prompt novo.

**Primeira sonda, marca inline: 1 de 12.** A sonda da resposta passa a
reprovar caso R rebaixado pela ancoragem e a registrar as frases descartadas.
Com o prompt pedindo a marca no fim de cada frase («... isso [T1].»), a rodada
de 06/10 deu 9 de 9 nos casos S e 1 de 12 nos R: 11 rebaixados por «bloco 2
sem frase ancorada». Nenhum descarte foi por termo fora do trecho. O modelo
marcou o bloco 1 e deixou o bloco 2 sem marca, com frases legítimas, como
«Nenhum alimento pode prevenir ou curar essa doença» no R1. É o mesmo padrão
das decisões 4 do fix e 18: o que depende de o modelo lembrar uma instrução de
forma falha. A âncora passou a campo próprio no JSON, que o modo JSON obriga a
existir. A marca inline continua aceita. Alternativas descartadas: reforçar a
instrução no prompt (o padrão acima); conferir contra T1 a frase sem marca
quando há um só trecho (não resolve o R4, que tem dois, e deixa de ser âncora
declarada). Achado lateral: em 4 das 11 respostas refeitas na forma sem
evidência, o modelo deixou o bloco 4 vazio, o que não ocorreu no S1.

**Pendente: a sonda com a âncora em campo próprio.** A `Resposta` passa a
guardar a saída crua do modelo (`bruto`, as duas no rebaixamento), e o relatório
a registra.

**Limites declarados.**

- Paráfrase sem termo verificável passa sempre. Frase que inverte o sentido do
  trecho com as mesmas palavras («o exame deu positivo») não é pega.
- O limite da guarda (decisão 12) continua: a ancoragem confere a resposta, não
  o veredito. Veredito que cita trecho real que não cobre a alegação ainda
  depende do prompt da classificação ou do limiar da 1.5.
- Nome próprio composto é conferido palavra a palavra: «Rio Grande» passa se
  «rio» e «grande» estão no trecho, mesmo que separados.
- O rebaixamento custa uma segunda chamada ao modelo.

## Questões em aberto

- **Técnica em veredito `verdadeiro`.** O requirement Catálogo fechado manda o
  bloco 3 da forma com evidência nomear técnica, sem exceção. O cenário Alegação
  verdadeira, e a decisão 18, dizem que não. A spec precisa dizer qual vale.
- **Composição do catálogo.** ~~Quais 6 a 8 técnicas, e com que nomes.~~
  Fechada na decisão 6, com a vaga de `conspiração` pendente da matriz.
- **Limiar de recuperação** a partir do qual o veredito cai para `evidência
  insuficiente`. Entra na recuperação como o critério `cobre`
  de `recuperar` (decisão 19).
- **Fonte em inglês.** Nenhum corpus em inglês está indexado (decisão 19). Falta
  decidir qual fonte entra, se alguma entra, e com que licença. Até lá, o braço
  inglês da prioridade de idioma não é exercido com dados reais.
- **Relato pessoal como alegação.** A extração gradua "minha tia parou o remédio
  e melhorou" como alegação de risco `alto` (decisão 8). A spec não diz se relato
  pessoal é alegação a verificar ou evidência fraca da alegação ao lado. Da
  resposta depende o desempate por ordem. Cabe à curadoria da task 6.1 trazer
  casos com relato antes da alegação.



