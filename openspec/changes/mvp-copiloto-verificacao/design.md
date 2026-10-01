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

## Questões em aberto

- **Composição do catálogo.** ~~Quais 6 a 8 técnicas, e com que nomes.~~
  Fechada na decisão 6, com a vaga de `conspiração` pendente da matriz.
- **Limiar de recuperação** a partir do qual o veredito cai para `evidência
  insuficiente`.
- **Relato pessoal como alegação.** A extração gradua "minha tia parou o remédio
  e melhorou" como alegação de risco `alto` (decisão 8). A spec não diz se relato
  pessoal é alegação a verificar ou evidência fraca da alegação ao lado. Da
  resposta depende o desempate por ordem. Cabe à curadoria da task 6.1 trazer
  casos com relato antes da alegação.


