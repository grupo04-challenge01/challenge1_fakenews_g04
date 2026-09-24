# Casos selecionados para a investigação forense

Task 1.1 do change `add-engage-desinformacao-saude`. Seleção feita em
20/09/2026 sobre `datasets/derivados/factcenter_subset_saude.csv`.

**Seis casos, três tipos de manipulação.** A capability
`pesquisa-investigativa` exige no mínimo três tipos distintos entre fabricação
integral, recontextualização de mídia ou dado antigo, exagero de estudo real,
distorção estatística e mídia sintética.

## Critério da seleção

Quatro filtros, nesta ordem:

1. **Sub-recorte do projeto.** Todos os seis são sobre **vacinação**, que é o
   recorte fechado em 17/09/2026.
2. **Fora do covid, deliberadamente.** Exigência da decisão 4 do `design.md` de
   `add-tratamento-datasets-ptbr`: caso de teste dentro do recorte covid faz o
   produto parecer funcionar em teste e falhar na pauta real. Cinco dos seis são
   anteriores à pandemia ou não tratam dela.
3. **Alegação única e rótulo consolidado**, para que a ficha tenha um objeto e
   não vários.
4. **Texto integral disponível**, para que a leitura lateral tenha o que
   confrontar.

A classificação de tipo foi feita **por leitura do texto da checagem**, caso a
caso — não por busca de palavra-chave. Palavra-chave classifica errado: «vídeo
manipulado» aparece tanto em mídia sintética quanto em recontextualização de
vídeo íntegro.

---

## Os seis casos

### Caso 01 — Vacina da febre amarela «mata em 50% dos casos»

| | |
| --- | --- |
| **Tipo** | **Fabricação integral** |
| Agência | boatos.org · 22/03/2017 |
| Veredito original | `boato` |
| `registro_id` | `4ebed93208` |
| Fonte | <https://www.boatos.org/saude/vacina-febre-amarela-mata.html> |

A alegação atribui a um «dermatologista» sem nome, num programa de rádio, a
afirmação de que metade das pessoas vacinadas morre. Não há estudo, não há
nome, não há dado. Circulou durante o surto de febre amarela no Rio.

**Por que entra:** é o tipo mais puro de fabricação — número inventado com
verniz de autoridade médica. E tem **contexto de surto**, que é quando a
desinformação em saúde causa dano real.

### Caso 02 — «Estudo da UFMG» sobre suco de inhame e dengue

| | |
| --- | --- |
| **Tipo** | **Fabricação integral** (atribuição falsa de estudo) |
| Agência | fato-ou-fake (G1) · 18/02/2020 |
| Veredito original | `fake` |
| `registro_id` | `c5d4b94adb` |
| Fonte | [g1.globo.com/fato-ou-fake](https://g1.globo.com/fato-ou-fake/noticia/2020/02/18/e-fake-que-ufmg-fez-estudo-que-diz-que-suco-de-inhame-corta-os-efeitos-da-dengue-em-apenas-quatro-horas.ghtml) |

Atribui a uma universidade real um estudo que não existe. A assessoria da UFMG
confirmou não ter identificado nenhum estudo com esse teor. A mensagem se
antecipa à objeção dizendo que o estudo «ainda não foi divulgado».

**Por que entra:** mesmo tipo do caso 01, variante diferente e mais difícil — a
instituição citada é real e verificável, o que torna a leitura lateral **o
único** caminho de checagem. É o caso que melhor demonstra o protocolo.

### Caso 03 — Vídeo de 2018 usado para afirmar morte após vacina

| | |
| --- | --- |
| **Tipo** | **Recontextualização de mídia antiga** |
| Agência | COMPROVA · 04/02/2021 |
| Veredito original | `Enganoso` |
| `registro_id` | `0dc8e869e9` |
| Fonte | [projetocomprova.com.br](https://projetocomprova.com.br/publica%C3%A7%C3%B5es/postagem-usa-video-de-2018-para-afirmar-que-idosa-morreu-apos-tomar-vacina/) |

Reportagem real de 2018 sobre uma idosa que passou mal, republicada em 2021
como se fosse sobre a vacinação corrente. Os trechos em que se dizem as
palavras «gripe» e «H1N1» foram **cortados propositalmente**. O laudo de óbito
não indica relação com a vacina.

**Por que entra:** o material de origem é **verdadeiro e verificável**. O que
engana é a data e o corte. É o caso que mostra por que verificar a alegação
isolada não basta.

### Caso 04 — «A bula confirma que a vacina causa autismo»

| | |
| --- | --- |
| **Tipo** | **Exagero / distorção de documento real** |
| Agência | Lupa · 18/02/2019 |
| Veredito original | `FALSO` |
| `registro_id` | `b103a02dd7` |
| Fonte | [piaui.folha.uol.com.br/lupa](https://piaui.folha.uol.com.br/lupa/2019/02/18/verificamos-bula-autismo/) |

A bula em inglês da vacina Tríplice Bacteriana é um documento **real e
público**. A alegação lê nela uma relação causal com autismo que ela não
afirma — a bula lista eventos relatados, não causas estabelecidas.

**Por que entra:** é a categoria mais próxima do que o produto precisa fazer.
A fonte primária existe, está acessível, e o erro está **na distância entre o
que ela diz e o que a mensagem afirma**. É o caso de teste natural do campo 5 da
ficha.

### Caso 05 — Vídeo editado do presidente da Anvisa

| | |
| --- | --- |
| **Tipo** | **Recontextualização de mídia ou dado antigo** |
| Agência | COMPROVA · 18/02/2021 |
| Veredito original | `Falso` |
| `registro_id` | `eb77180631` |
| Fonte | [projetocomprova.com.br](https://projetocomprova.com.br/publica%C3%A7%C3%B5es/video-manipulado-deturpa-entrevista-de-presidente-da-anvisa-para-sugerir-risco-sanitario-grave-na-vacinacao/) |

Antônio Barra Torres aparece dizendo que a população «corre risco sanitário
grave». As imagens foram **editadas** para fazer parecer que ele se referia às
vacinas já aprovadas.

**Por que entra:** autoridade real, fala real, sentido invertido pela edição. É
o único dos seis em que a verificação exige acesso à gravação original — e é o
caso que mais expõe o limite do que uma IA de texto resolve.

**Reclassificado em 24/09/2026.** A seleção de 20/09 marcou este caso como mídia
sintética. A ficha do caso 05 mostrou que não há síntese: o material é autêntico e
o engano vem do **corte** e da supressão da pergunta da jornalista. É o mesmo
mecanismo do caso 03, aplicado a um recorte dentro da peça em vez da data.

### Caso 06 — «Vacina da febre amarela paralisa o fígado, diz médico de Sorocaba»

| | |
| --- | --- |
| **Tipo** | **Fabricação integral** (corrente de WhatsApp) |
| Agência | boatos.org · 28/01/2018 |
| Veredito original | `boato` |
| `registro_id` | `ad3b65d166` |
| Fonte | <https://www.boatos.org/saude/vacina-febre-amarela-figado-sorocaba.html> |

«O marido da Simone, médico de Sorocaba, disse que...» — autoridade de segunda
mão, não nomeada e não localizável, somada a motivação conspiratória («o
governo quer matar as pessoas sem elas perceberem»).

**Por que entra:** é o **formato de corrente**, que é o canal real do problema
e o formato que o produto vai receber colado. Os casos 01 a 05 vêm de postagem
pública; este vem de mensagem privada encaminhada.

---

## Cobertura de tipos

| Tipo | Casos | Cobertura |
| --- | --- | --- |
| Fabricação integral | 01, 02, 06 | ✅ |
| Recontextualização de mídia ou dado antigo | 03, 05 | ✅ |
| Exagero de estudo real | 04 | ✅ |
| **Mídia sintética** | — | ❌ **não coberta** |
| **Distorção estatística** | — | ❌ **não coberta** |

**Três tipos contra o mínimo de três da spec.** O cenário «Cobertura
insuficiente de tipos» não é acionado, mas a margem acabou: qualquer
reclassificação a menos aciona o cenário.

São **duas** lacunas registradas. A primeira é **mídia sintética**, que a seleção
de 20/09 dava por coberta pelo caso 05 e a ficha desse caso desmentiu. Cobri-la
exige um caso de vídeo ou áudio gerado ou alterado por síntese, não recortado.

A segunda é **distorção estatística**: manipulação de dado real e
verificável, do tipo «as mortes subiram X% depois da vacinação». O recorte
não-covid de vacinação do corpus tem poucos casos assim — os que existem são
quase todos sobre números da pandemia, que o filtro 2 exclui de propósito.

Se o grupo quiser cobrir os cinco tipos, o caminho é aceitar **um** caso do
recorte covid para essa categoria, registrando a exceção. Fica como decisão.

## Distribuição

| Dimensão | Resultado |
| --- | --- |
| Agências | boatos.org (2), COMPROVA (2), Lupa (1), fato-ou-fake (1) |
| Período | 2017 a 2021 |
| Fora do covid | 5 de 6 |
| Sobre vacinação | 6 de 6 |
| Formato de origem | postagem pública (5), corrente privada (1) |

## Próximo passo

As tasks 2.1, 2.2 e 2.3 estão fechadas: os seis casos foram distribuídos entre
cinco integrantes e as seis [fichas](ficha-de-caso.md) estão preenchidas e
cronometradas, cada uma citando a checagem externa consultada.

Falta a **task 2.4** — levar os tempos medidos para o quadro Problema do
brainstorming. Os valores são mínimo de 10 min, mediana de 22 min e máximo de
43 min, sobre seis verificações.

Os `registro_id` acima permitem recuperar o texto integral da checagem direto do
corpus, o que **não substitui** a leitura lateral: a checagem da agência é o
gabarito, e a forense é sobre o caminho até ele.
