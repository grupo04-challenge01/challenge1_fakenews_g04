# Design: Seleção de modelos e arquitetura de recuperação

## Decisões

### 1. Não existe "o modelo". Existem três papéis

A pergunta "qual modelo pronto usar" não tem resposta única porque o MVP executa
três trabalhos com exigências incompatíveis entre si:

| Papel | O que se exige | Onde aparece |
| --- | --- | --- |
| **Recuperação** | achar a checagem certa entre 4.063, em PT-BR | tasks 1.4–1.6 |
| **Geração** | escrever em PT-BR simples, fiel ao trecho recuperado | tasks 2.1–2.2, 3.2 |
| **Classificação auxiliar** | decidir rótulos fechados e baratos | tasks 2.5, 4.1 |

Tratar os três como um só leva a escolher um modelo grande e caro que resolve mal
o papel que mais importa. A qualidade do produto é decidida na recuperação: se o
trecho certo não é recuperado, nenhum gerador o inventa sem violar
`recuperacao-evidencia`.

### 2. MedGemma é descartado, e o motivo não é qualidade

O MedGemma é um bom modelo para o que se propõe. O que ele se propõe não é o que
este projeto faz. O descarte apoia-se no model card oficial, não em impressão:

- **Modalidade.** O treino cobre radiologia, histopatologia, oftalmologia,
  dermatologia e dados de prontuário em FHIR. O MVP declara imagem, OCR e áudio
  fora de escopo. A especialização não é aproveitável.
- **Idioma.** As avaliações usaram "primarily English language prompts". O corpus
  é PT-BR e `recuperacao-evidencia` exige esgotar português antes do inglês.
- **Multi-turn.** O model card declara que o modelo não foi avaliado nem
  otimizado para aplicações multi-turno. O produto é um copiloto conversacional.
- **Variantes.** A versão 1.5 existe apenas em 4B multimodal; a via text-only é o
  MedGemma 1 de 27B, modelo anterior. Não há variante que case com a necessidade.
- **Licença.** Health AI Developer Foundations, não Apache 2.0 nem os termos
  padrão da Gemma. Precisa de leitura antes de entrar em entregável.

O argumento decisivo, porém, é interno ao projeto. A task 2.3 de
`mvp-copiloto-verificacao` é "guarda contra veredito por conhecimento
paramétrico", e `verificacao-alegacao` determina que o sistema MUST NOT emitir
veredito a partir apenas do conhecimento paramétrico do modelo. Todo o valor do
MedGemma está no conhecimento médico paramétrico. O projeto adquiriria a
capacidade e, por spec, seria obrigado a desligá-la.

A ambiguidade de fundo está na palavra "saúde". No MedGemma ela significa
**medicina clínica**; neste projeto significa **desinformação em saúde**, que é
um problema de recuperação de checagem, leitura crítica e escrita acessível.
Some-se que `fronteira-orientacao-saude` obriga o sistema a **recusar** conduta
clínica individual — exatamente aquilo em que o MedGemma foi especializado.

Registro para o portfólio: o descarte não é do conselho recebido. "Use modelo
pronto, não treine do zero" é adotado integralmente. O que se descarta é um
candidato específico.

### 3. A escala do corpus dispensa infraestrutura de RAG

O corpus de saúde do FactCenter tem 4.063 checagens. Mesmo com fragmentação por
alegação, a ordem de grandeza permanece em milhares, não milhões.

Nessa escala, busca exata por produto escalar sobre matriz densa em memória é
mais rápida que o tempo de rede de um banco vetorial, e é **exata** — não
aproximada. Adotar banco vetorial aqui adiciona dependência, serviço e modo de
falha sem nenhum ganho mensurável.

A decisão é registrada porque a literatura e os tutoriais de RAG pressupõem
escala de produção e induzem ao erro oposto. Se o corpus crescer uma ordem de
grandeza, a decisão se reabre.

### 4. Híbrido léxico + denso é linha de base, não otimização

A ordem natural de construção é "faz denso primeiro, acrescenta BM25 se precisar".
A evidência disponível para português inverte essa ordem: em estudo empírico com
500 consultas clínicas em português, recuperação densa isolada falhou em 22,2%
das consultas mesmo no limiar mais permissivo, e os conjuntos recuperados por
BM25 e por híbrido mostraram-se complementares, não redundantes — centenas de
documentos aparecem em um e não no outro.

Há razão específica do domínio. Checagem de saúde é densa em nomes próprios que
o denso trata mal e o léxico trata bem: `qdenga`, `oropouche`, `semaglutida`,
nomes de agência, números de lote, dosagens. São exatamente os termos pelos quais
uma alegação é identificada.

Consequência para a task 1.5: o limiar de `evidência insuficiente` passa a ser
calibrado sobre o score fundido, não sobre similaridade de cosseno bruta.

### 5. Especialização em português não é o critério; objetivo de treino é

Este é o achado que mais contraria a intuição do grupo, e foi o que corrigiu uma
recomendação anterior feita em conversa.

No MTEB-BR — 22 tarefas nativas em português brasileiro, 93 modelos avaliados,
de 23M a 27B parâmetros — os 16 modelos específicos de português obtiveram média
de **0,331** em recuperação, contra **0,517** dos multilíngues (p = 0,003). O
BERTimbau, modelo português mais citado no grupo, ficou em **0,258** em
recuperação.

Mas a diferença desaparece ao comparar apenas variantes ajustadas para
recuperação: 0,516 contra 0,517 (p = 0,99). Ou seja, o que separa os modelos não
é terem sido pré-treinados em português — é terem sido treinados **para buscar**.

Isso não desqualifica o BERTimbau; realoca-o. O mesmo BERTimbau-large de 335M
fica em **3º lugar entre 93 modelos** em classificação, 2º entre os de peso
aberto. Ele é o modelo certo para o papel 3 da decisão 1, e o errado para o
papel 1.

### 6. RAG carrega conhecimento; fine-tuning carrega comportamento

A orientação de "mesclar fine-tuning ao RAG" é adotada, com a divisão explicitada,
porque a mescla errada é o erro mais caro disponível neste projeto:

- **Recuperação carrega o que o sistema sabe.** As checagens mudam toda semana —
  o projeto tem uma capability chamada `frescor-corpus` justamente por isso.
  Conhecimento que muda não entra em peso.
- **Fine-tuning carrega como o sistema se comporta.** Estrutura de quatro blocos,
  vocabulário fechado do catálogo de técnicas, recusa de conduta clínica, nível
  de leitura.

Duas proibições decorrem disso, ambas já ancoradas em regra existente:

1. Fine-tuning para injetar fato destrói a auditabilidade até a fonte, que é o
   princípio arquitetural inviolável de `openspec/project.md`.
2. Fine-tuning de classificador de veredito sobre os datasets de rótulo binário é
   vedado em texto expresso: eles são "banco de estímulos para teste com
   usuários, nunca alvo de treino de classificador de veredito".

**Sequência adotada: RAG puro primeiro, sem nenhum fine-tuning.** Fine-tuning só
é considerado para os classificadores auxiliares do papel 3, e só depois de
medida a falha do prompt. Fine-tunar antes de existir linha de base é o modo mais
comum de consumir as semanas 4 e 5 sem entregável.

### 7. Sentimento é explicativo, nunca evidenciário

Foi pedido pesquisar análise de sentimento — positivo, negativo, neutro. A
pesquisa foi feita e o resultado é que **polaridade não pode entrar no veredito**,
por três motivos convergentes:

- **Colide com spec existente.** `verificacao-alegacao` determina que o sistema
  MUST NOT tratar presença de opinião como indício de falsidade. Um classificador
  que aprenda "texto emocionado → falso" viola isso por construção.
- **Erra nos dois sentidos, e erra pior no caso que importa.** Marcaria como falso
  um alerta verdadeiro de surto, e como confiável um texto antivacina em tom
  calmo e pseudo-técnico — que é o formato predominante no corpus de Telegram de
  `acervo-circulacao`, o corpus que motivou o próprio sub-recorte de vacinação.
- **A literatura sustenta correlação com propagação, não com falsidade.** Emoção
  prediz o quanto algo circula. Circulação não é valor de verdade.

A reformulação preserva o pedido em dois usos legítimos:

- **Explicativo**, no catálogo de técnicas (task 3.1): "apelo ao medo",
  "urgência", "indignação" são técnicas reconhecíveis, e o bloco 4 da resposta
  existe para ensinar o usuário a reconhecê-las. Aqui a emoção é conteúdo
  formativo, e é medida no texto do usuário para ser nomeada a ele, nunca para
  classificá-lo.
- **Descritivo**, na análise do corpus de circulação, como caracterização do que
  circulou. Resultado de pesquisa para o portfólio, fora do caminho da resposta.

Nos dois usos, a granularidade adotada é **emoção discreta** (medo, raiva,
urgência), não polaridade. A revisão de literatura sobre detecção de emoção em
desinformação é consistente em que polaridade positivo/negativo/neutro informa
menos que a emoção nomeada, e é a emoção nomeada que serve ao propósito
formativo — "isso está usando medo para te apressar" é ensinável; "isso é
negativo" não é.

### 8. Geração roda localmente, em Gemma 4 12B

Decidido em 17/09/2026. A via local foi escolhida sobre a via de API, e a
questão em aberto correspondente está encerrada.

O que pesou não foi custo. Foi o protocolo de ética: `avaliacao-instrumento`
prevê itens-armadilha, TCLE e submissão ao CEP, e a via de API faria as
mensagens dos participantes de teste saírem para terceiro durante a sessão.
Isso precisaria entrar no TCLE, ampliaria a submissão e daria ao participante
um motivo a mais para recusar. Rodando local, o dado não sai da máquina e a
questão desaparece do protocolo em vez de ser mitigada nele.

Ganhos secundários: nenhuma dependência de rede no momento do teste com usuário
— falha de rede durante sessão agendada com participante idoso é perda de
coleta, não inconveniência — e custo marginal zero por iteração de prompt, o que
importa numa fase em que as tasks 2.1, 2.2 e 3.2 são iteração de prompt.

O custo aceito é de aderência a instrução. O prompt do projeto é exigente
(quatro blocos, catálogo fechado, recusa de conduta clínica, nível de leitura),
e modelo local sustenta isso pior que modelo de API. A mitigação é a validação
automática já prevista na task 3.3 de `mvp-copiloto-verificacao` — rótulo usado
pertence ao catálogo — que transforma o desvio em falha detectável em vez de
silenciosa. Se a medição mostrar que a estrutura não se sustenta, a decisão
reabre.

**Modelo: Gemma 4 12B instruction-tuned, variante QAT q4_0.** A escolha da
geração 4 sobre a 3, verificada em 17/09/2026:

| | Gemma 3 12B | Gemma 4 12B |
| --- | --- | --- |
| Licença | Gemma Terms of Use (própria) | **Apache 2.0** |
| Contexto | 128K | 256K |
| Idiomas | 140+ | 140+ pré-treinados, 35+ diretos |

A licença é o fator decisivo, e é exatamente o tipo de achado que a capability
`selecao-modelo` existe para capturar. A Gemma Terms of Use do Gemma 3 traz uma
Prohibited Use Policy que veda "the unauthorized or unlicensed practice of any
profession including ... medical/health", além de reservar ao Google o direito
de restringir remotamente o uso e de obrigar a repassar os termos a quem receba
o modelo. Nenhuma dessas cláusulas provavelmente impediria este projeto — a
capability `fronteira-orientacao-saude` já obriga o sistema a recusar conduta
clínica individual, que é o que a política veda — mas depender dessa leitura num
entregável acadêmico é risco desnecessário quando existe alternativa Apache 2.0
de mesma família, mesmo porte e geração mais nova.

Registre-se que o Apache 2.0 elimina a restrição de licença, não a obrigação
ética: `fronteira-orientacao-saude` continua valendo por decisão de produto e
por protocolo do CEP, não por termo de uso.

O QAT q4_0 é publicado pelo próprio Google e preserva qualidade próxima do
bf16 reduzindo memória em cerca de 3x, o que põe o 12B com folga nos 24 GB
unificados do M4 e deixa margem para o modelo de embedding coexistir.

**Procedência exata do artefato.** Conferida em 18/09/2026 contra o manifesto
local do Ollama, não contra memória ou documentação.

- Tag: `gemma4:12b-it-qat` — digest `38044be4f923`, 7.2 GB, Q4_0, 11.9B
  parâmetros, contexto de 262144, com projetor CLIP de visão (52.38M).
- Download por Ollama: `ollama pull gemma4:12b-it-qat`, em
  <https://ollama.com/library/gemma4:12b-it-qat>. O digest publicado no registro
  bate com o da máquina.
- Upstream oficial do Google, os mesmos pesos em GGUF:
  <https://huggingface.co/google/gemma-4-12B-it-qat-q4_0-gguf>, com
  `gemma-4-12b-it-qat-q4_0.gguf` e `mmproj-gemma-4-12b-it-qat-q4_0.gguf`. A
  correspondência entre os dois caminhos não é inferida do nome: a camada de
  projetor do manifesto local registra o arquivo de origem como
  `mmproj-gemma-4-12b-it-qat-q4_0.gguf`, idêntico ao do repositório.
- Apache 2.0 conferida no blob de licença local e no card do repositório, que
  ainda remete a <https://ai.google.dev/gemma/docs/gemma_4_license>. A task 1.7
  deve ler esse link antes do entregável.

**Piso de versão do runtime: Ollama >= 0.30.5.** O GGUF declara `requires:
0.30.5`, e sem isso o modelo não carrega. `requirements-rag.txt` fixa apenas o
cliente Python (`ollama>=0.4`), que é outra dependência — o runtime não está
registrado em lugar nenhum do projeto. Quem reproduzir o ambiente só pelo
requirements pode ficar com um Ollama velho e um erro de carga sem explicação.


### 9. Conferência de consistência com o MVP — 18/09/2026

A task 6.1 foi executada contra `recuperacao-evidencia`, `verificacao-alegacao`,
`fronteira-orientacao-saude` e `resposta-formativa`. Nenhuma contradição.
Três precisões foram incorporadas:

- **Auditabilidade não é exibição.** `fronteira-treino-recuperacao` exigia trecho
  de origem por afirmação; `resposta-formativa` manda fonte e trecho para a
  camada de detalhe. Sem ressalva, a primeira leitura obrigaria a poluir a
  camada visível. Ficou explícito que o vínculo sempre existe e a exibição
  obedece à revelação progressiva.
- **Indexar não é reproduzir.** A unidade de indexação guarda o texto da
  checagem, mas `recuperacao-evidencia` proíbe reproduzir o texto integral ao
  usuário. O cenário novo impede que a conveniência do índice seja lida como
  autorização.
- **O catálogo tem orçamento apertado.** `resposta-formativa` fixa o catálogo em
  6 a 8 rótulos, e ele já precisa acomodar técnicas não emocionais como
  `cura milagrosa` e `manchete exagerada`. Os rótulos de emoção nomeada da
  decisão 7 competem por essas vagas — não são acréscimo livre. A task 3.1 de
  `mvp-copiloto-verificacao` precisa tratar o catálogo como orçamento, e a task
  5.2 deste change MUST propor os rótulos de emoção já cientes desse limite.

### 10. Achados da primeira sonda do gerador — 18/09/2026

Gemma 4 12B QAT instalado e sondado contra um caso real do corpus (Aos Fatos,
08/01/2021, jatobá que "cura câncer"), com o trecho de evidência injetado à mão,
já que o índice ainda não existe. Arranjo em `prototipo/teste_gemma4.py`,
resultado em `prototipo/relatorio_teste_gemma4.json`. **1 de 3 sondas passou.**

**Achado operacional: Gemma 4 é modelo de raciocínio.** Pela API do Ollama ele
vem com `think` ligado: preenche o campo `thinking` e pode devolver `content`
vazio. Na primeira execução gastou 1.286 tokens pensando, não respondeu e o
request caiu em 500 após 1m58s. Com `think: false` responde normalmente. Isso
não estava previsto na decisão 8 e é pré-requisito de qualquer task que chame o
modelo.

As duas configurações foram medidas sobre as mesmas sondas: com `think: false`,
3 de 3 produziram resposta, média de 17 s; com `think: true`, apenas 1 de 3
produziu resposta, média de 112 s, porque T1 e T2 gastaram cerca de 4.600
caracteres de raciocínio e esgotaram o orçamento de tokens antes de escrever.
Houve um ganho isolado — em T3 o raciocínio escolheu `cura milagrosa`, o rótulo
correto, contra `manchete exagerada` sem raciocínio. Não compensa: duas
respostas vazias em três é falha de produto, não perda de qualidade. Toda
chamada ao gerador MUST passar `think: false`. O ganho de rótulo sustenta
tratar a escolha de rótulo como etapa separada, não religar o raciocínio na
resposta inteira.

**Falha real na fronteira clínica (sonda T2).** Perguntado se a mãe com câncer
pode parar a quimioterapia e tomar o chá, o modelo respondeu com a estrutura de
verificação normal, abrindo com `VEREDITO: Falso`, e só mencionou procurar
médico no último bloco. Ele nunca disse que a decisão depende de avaliação
individual, que o cenário de `fronteira-orientacao-saude` exige. Abrir com
"Falso" para quem perguntou se pode parar a quimio é ambíguo no pior lugar
possível: o leitor de baixo letramento pode ler o veredito como resposta à
pergunta que fez.

A conclusão não é que o modelo é ruim, é que **prompt não sustenta a fronteira
clínica**. A task 4.1 de `mvp-copiloto-verificacao` já prevê um classificador de
pedido de conduta; esta sonda mostra que ele é obrigatório e precisa rodar
**antes** do caminho de verificação, desviando a mensagem em vez de anotá-la.

**Defeito de spec exposto pela sonda T1.** `resposta-formativa` exige os quatro
blocos sempre e ao menos um rótulo do catálogo no bloco 3. Quando o veredito é
`evidência insuficiente`, isso é incoerente: não há mensagem enganosa cuja
técnica nomear. O modelo degenerou, repetindo "evidência insuficiente" dentro do
bloco 3. O defeito é da spec, não do modelo, e MUST ser corrigido em
`mvp-copiloto-verificacao` antes da task 3.2 — ou a estrutura passa a ter forma
própria para `evidência insuficiente`, ou o catálogo deixa de ser obrigatório
nesse caso.

**Latência.** Cerca de 12 tokens/s, 17 a 23 segundos por resposta completa. Não
inviabiliza, mas é material para `acessibilidade-leitura` e para o teste com
usuário: espera de 20 segundos sem retorno visível é abandono provável. Sugere
resposta em streaming, e reforça o `gemma4:12b-mlx` como candidato da task 3.4.

**Instabilidade de rótulo.** A mesma alegação de cura do câncer recebeu
`cura milagrosa` em uma sonda e `manchete exagerada` em outra. As duas pertencem
ao catálogo, então a validação da task 3.3 do MVP passaria — ela verifica
pertinência, não adequação. Para uma promessa de cura, `manchete exagerada` é o
rótulo errado. A validação automática precisa de um segundo critério.

**Lição de método.** A primeira versão das verificações declarou 3 de 3. As
sondas T1 e T2 passavam por checagem frouxa — ausência de regex proibido e
presença da palavra "médico". Endurecidas contra o texto literal dos cenários,
viraram 1 de 3. Registro porque a mesma armadilha espera a task 3.3 do MVP:
validação automática mal calibrada produz falso verde, que é pior que não medir,
e porque a acurácia aparente do protótipo vai depender de quem escreve o teste.

### 11. Índice construído: unidades, fragmentos e fusão — 18/09/2026

Tasks 2.2 a 2.5 executadas. Código em `prototipo/rag/`, artefatos em
`prototipo/indice/`, declaração auditável em `prototipo/indice/manifesto.json`.

**Números do índice.** 4.063 registros lidos, 5.090 unidades de indexação,
22.464 fragmentos, 88 registros em quarentena. Busca exata por produto escalar
sobre matriz `float32` de 22.464 × 768 (69 MB), sem banco vetorial, confirmando
a decisão 3 na prática: a consulta completa custa de 12 a 33 ms.

**A dificuldade real da task 2.2 foi a alegação múltipla.** 587 dos 4.063
registros trazem mais de um veredito, e o corpus não marca onde uma alegação
termina e a outra começa — os selos eram elementos visuais da página e não
sobreviveram à raspagem. Alinhar veredito a alegação por ordem, sem verificação,
é exatamente o que `arquitetura-recuperacao` proíbe ao exigir que nenhuma
unidade receba veredito de alegação diferente da sua.

O único marcador de formato disponível está na Lupa, que publica cada alegação
como linha inteira entre aspas. A regra adotada aceita a segmentação **apenas
quando o número de segmentos encontrados iguala o número de vereditos
declarados**. A igualdade não prova o alinhamento, mas é a evidência disponível,
e falha ruidosamente: uma alegação a mais ou a menos derruba o registro para a
via conservadora. A disposição resultante:

| Disposição | Registros | Tratamento |
| --- | --- | --- |
| Veredito único | 3.476 | unidade direta, título como alegação |
| Segmentação verificada | 221 | uma unidade por alegação, veredito alinhado |
| Multi sem segmentação, vereditos iguais | 278 | unidade única, marcada `cobre_multiplas_alegacoes` |
| Multi sem segmentação, vereditos divergentes | 88 | quarentena como `misto` |

A terceira linha é um desvio declarado, não um acerto. A unidade fica mais grossa
que o ideal e formalmente não é "uma unidade por alegação". O que a autoriza é
que, com todos os vereditos iguais, não existe veredito alheio a atribuir — a
proibição substantiva é respeitada. A unidade carrega a marca para que quem for
citar saiba que a citação tem de sair do fragmento recuperado, nunca da unidade
inteira. Quem fechar isso é a task 2.6 de `add-tratamento-datasets-ptbr`; a
quarentena dos 88 já é o conjunto de casos que aquela task reserva.

**Precisão em `integridade-textual`.** O portão de acentuação roda antes de
qualquer unidade ser construída. A leitura literal da capability — "ausência
total de uma letra é corrupção sistemática" — reprova este corpus por causa do
`Ü`, que tem zero ocorrências em 21,5 milhões de caracteres. Não por defeito: o
trema foi abolido pelo Acordo Ortográfico de 1990 e o corpus cobre 2013 a 2021.
O `ü` minúsculo aparece 57 vezes, o que mostra que o pipeline não descarta o
caractere.

O critério implementado é o que de fato separa os dois casos observados: a
maiúscula tem zero ocorrências **e** a minúscula correspondente é frequente. Em
`factckbr_normalizado.csv`, reprovado pela capability, sete letras batem nesse
critério — `ã` 3.625 contra `Ã` 0, `ç` 2.312 contra `Ç` 0. Aqui, nenhuma bate. A
precisão MUST ser levada à task 3.1 de `add-tratamento-datasets-ptbr`, que é
quem escreve o verificador definitivo; sem ela, o verificador reprova um corpus
íntegro e bloqueia o índice.

**Defeito encontrado e corrigido na fusão — o braço denso estava anulado.** A
primeira versão da task 2.5 somava cosseno cru a BM25 saturado. A medição
mostrou que isso não funde nada:

| Consulta | cosseno mediano | cosseno máximo | BM25 máximo |
| --- | --- | --- | --- |
| `chá da casca do jatobá cura câncer` | 0,787 | 0,893 | 35,1 |
| `hidroxicloroquina previne covid-19` | 0,816 | 0,903 | 11,3 |
| `como faço bolo de cenoura` | 0,762 | 0,826 | 13,2 |

O cosseno do e5 não é centrado: a mediana fica perto de 0,79 em qualquer
consulta e o topo raramente passa de 0,90. Todo o sinal vive numa faixa de cerca
de 0,06, muito longe do zero. Somado a um BM25 que varia de 0 a 35, ele vira
constante, e a ordem final sai inteira do braço léxico. O sintoma foi concreto:
em `hidroxicloroquina previne covid-19` o braço denso achou a checagem certa
(Stella Emanuel), o léxico achou `dexametasona` e `própolis`, e a fusão premiou
o léxico. O híbrido estava de pé na forma e desligado no efeito.

A correção normaliza cada braço contra o **fundo da própria consulta**: a mediana
sobre os 22.464 fragmentos é o que aquele braço devolve para qualquer coisa, e a
distância até o percentil 99 é a escala em que ele separa. Normalização min-max
foi descartada pelo mesmo motivo do RRF — força o primeiro colocado a 1,0 sempre
e apaga a diferença entre achar e não achar.

**RRF não é a forma padrão, e o motivo é a decisão 4.** Reciprocal Rank Fusion
está implementada para a comparação da task 3.1, mas não pode ser a forma padrão
porque seu score é função da posição, não da relevância: numa consulta sobre
pauta ausente, o primeiro colocado recebe o mesmo score que receberia numa
consulta perfeitamente atendida. O limiar de `evidência insuficiente` é calibrado
sobre o score fundido, e um limiar sobre RRF não distingue os dois casos — que é
precisamente o caso que `frescor-corpus` manda distinguir.

**A decisão 4 se sustentou na medição.** Sobre 12 consultas, a sobreposição média
entre o top-10 léxico e o top-10 denso foi de **35%** — as listas são
complementares, não redundantes, como o estudo em português previa. No top-5
híbrido, 14 das 60 vagas foram ocupadas por unidades que só o braço léxico
encontrou e 6 por unidades que só o denso encontrou: **um terço do top-5 se
perderia ao remover qualquer um dos dois braços**. Em `hidroxicloroquina previne
covid-19` a interseção foi zero. A medição formal de recall contra documento
correto conhecido continua sendo a task 3.1; isto é sanidade, não aferição.

**Limite que este desenho não resolve.** Nem cosseno nem BM25 separam bem pauta
ausente do corpus: `como faço bolo de cenoura` alcança cosseno máximo de 0,826
contra 0,893 de uma consulta perfeitamente atendida. O realce contra o fundo
reduz a distorção, não a elimina. A consulta `Qdenga causa a própria dengue`
devolve checagens de dengue e zika com score alto e nenhuma sobre Qdenga — o
corpus termina em 2021 e a vacina é posterior. A task 3.5 herda o problema com a
medição já feita: o limiar não sai de similaridade bruta, e o caso Qdenga é o
teste de lacuna de acervo que a task 4.3 de `add-tratamento-datasets-ptbr`
especifica.

**Custo.** Indexação densa de 22.464 fragmentos em 13,2 minutos no M4 com MPS
(`intfloat/multilingual-e5-base`, 768 dimensões); índice léxico em 2,1 segundos.
Consulta: 12 a 20 ms só léxica, 14 a 18 ms só densa, 26 a 33 ms híbrida, já com
o modelo carregado. A carga do modelo custa cerca de 9 segundos e acontece uma
vez por processo.

**Observação para a task 2.3 de `add-tratamento-datasets-ptbr`.** Vereditos como
`DE OLHO`, da série de acompanhamento de promessas da Lupa, entraram no índice
com a grafia original e chave canônica. Não são veredito de checagem de alegação
e devem receber `nao_mapeavel` no mapa de vocabulário, não rótulo por
semelhança.

### 12. Fronteira treino/recuperação em linguagem operacional — 19/09/2026

A decisão 6 fixa o princípio; as tasks 4.1 a 4.3 pedem a forma operacional, que
é o que alguém consegue aplicar sem reabrir a discussão.

#### A regra, em uma frase

**Peso carrega forma; trecho carrega fato.** Se a afirmação pode ficar falsa
amanhã sem que ninguém treine nada, ela vem de trecho recuperado.

O teste prático, aplicável a qualquer proposta de treino: *o que esta proposta
ensina ao modelo muda quando o mundo muda?* Se muda, é recuperação. Se não muda,
é comportamento, e pode ir para peso.

#### Os dois casos vedados, nomeados

| Caso vedado | Como costuma ser proposto | Por que cai |
| --- | --- | --- |
| **Treinar fato** | "fine-tuning com pares alegação → veredito melhora a acurácia" | destrói a auditabilidade até a fonte, princípio inviolável de `openspec/project.md`. O ganho de acurácia MUST NOT ser aceito como compensação |
| **Treinar classificador de veredito** | "temos 12 mil itens rotulados no PUBHEALTH, dá para treinar" | os datasets de rótulo binário são banco de estímulos, nunca alvo de treino de veredito, em texto expresso de `project.md` |

Um terceiro caso, mais escorregadio, cai pela mesma regra sem estar nomeado nas
duas linhas: **adotar modelo cuja especialização de domínio permita responder
sem recuperar**. É o que fecha o descarte do MedGemma na decisão 2 — a
capacidade de responder sem recuperar é registrada como risco, não como
vantagem.

#### Procedimento de auditoria de afirmação sem trecho de origem (task 4.2)

A auditoria roda sobre resposta já emitida, percorre camada visível e camada de
detalhe, e é de passo único por afirmação:

1. **Segmentar** a resposta em afirmações. Afirmação é toda sentença que possa
   ser verdadeira ou falsa sobre o mundo. Instrução ao leitor, pergunta e nome
   de técnica do catálogo não são afirmações factuais e saem da conta.
2. **Casar** cada afirmação com o `fragmento_id` que a sustenta. O vínculo é
   registrado pelo sistema no momento da geração, não reconstruído depois — e
   reconstruir depois MUST NOT ser aceito como prova, porque a reconstrução
   encontra um trecho plausível mesmo quando a geração não usou nenhum.
3. **Conferir literalidade** do trecho contra o corpus, com
   `tratamento.integridade.trecho_e_fiel`. Trecho que não é subcadeia exata do
   texto de origem reprova junto com a afirmação.
4. **Classificar o que sobrou.** Afirmação sem `fragmento_id` é **defeito**, não
   estilo. Sai da resposta. Não é reescrita para soar mais vaga, não é movida
   para a camada de detalhe, não recebe ressalva — é removida.
5. **Registrar** a contagem: afirmações auditadas, com trecho, sem trecho e com
   trecho infiel. A taxa de afirmação sem trecho é métrica de guarda, e sobe
   antes de qualquer outra coisa quebrar.

O passo 2 é o que distingue esta auditoria de uma inspeção de plausibilidade. O
sistema precisa **já saber** de onde tirou cada frase; se precisa procurar, a
fronteira já foi cruzada.

#### Sequência adotada e o critério que autoriza o primeiro treino (task 4.3)

1. **RAG puro, sem nenhum fine-tuning** — estado atual. A sonda de 18/09 e a
   aferição de 19/09 são a linha de base exigida por
   `fronteira-treino-recuperacao`.
2. **Prompt medido** para cada classificador auxiliar do papel 3. Medir por
   prompt antes é obrigatório: sem isso não existe o número contra o qual o
   treino se justifica.
3. **Primeiro treino autorizado** quando, e só quando, as quatro condições
   valerem juntas:
   - o alvo é **comportamento** (forma de resposta, vocabulário do catálogo,
     recusa de conduta clínica, nível de leitura) — nunca valor de verdade;
   - existe linha de base por prompt **medida e registrada**, com o conjunto de
     avaliação versionado;
   - a falha do prompt é **reprodutível**, não anedótica — a sonda de 18/09 é o
     formato: três tentativas, resultado por tentativa, caso a caso;
   - o ganho esperado é maior que o custo de perder a reexecutabilidade do
     experimento em outra máquina.

O detector de pedido de conduta clínica da task 4.1 de `mvp-copiloto-verificacao`
é o **único candidato hoje**, e já tem meio caminho andado: a sonda mediu que o
Gemma 4 não sustenta a fronteira clínica por prompt (decisão 10). Falta a
condição 2 — conjunto de avaliação versionado — antes de o treino ser
autorizado.

### 13. Emoção nomeada: rótulos, ferramentas e o teste cruzado — 19/09/2026

A decisão 7 estabeleceu que polaridade não entra no veredito e que a
granularidade adotada é emoção discreta. As tasks 5.2 a 5.4 pedem o que vem
depois disso.

#### Rótulos candidatos ao catálogo de técnicas (task 5.2)

O catálogo de `resposta-formativa` é **fechado, de 6 a 8 rótulos**, e já está
ocupado por técnicas não emocionais — `cura milagrosa` e `manchete exagerada`
constam em texto expresso da spec. O orçamento não comporta uma família
emocional inteira, então a proposta é de **dois rótulos**, escolhidos por serem
os mais frequentes no corpus e os mais ensináveis:

| Rótulo proposto | O sinal, em linguagem cotidiana | Por que este |
| --- | --- | --- |
| `urgência fabricada` | manda repassar agora, antes que apaguem, antes que seja tarde | é a emoção que produz o encaminhamento, que é o comportamento que o produto quer interromper |
| `medo de dano oculto` | afirma que algo que você já usa esconde um perigo grave | é o formato dominante da desinformação antivacina, que é o sub-recorte do projeto |

Descartados como rótulo próprio, com motivo: `indignação` (frequente, mas o
sinal se confunde com crítica política legítima, e nomear isso como técnica
arrisca o sistema parecer partidário); `apelo à autoridade emocional` ("médico
chorando no vídeo"), que cai melhor dentro do critério de conflito de interesse
da rubrica; `esperança milagrosa`, já coberto por `cura milagrosa`.

A composição final do catálogo continua sendo questão em aberto de
`mvp-copiloto-verificacao`; o que esta task entrega é a proposta com o motivo,
para consumo da task 3.1 daquele change.

#### Ferramentas de emoção em PT-BR, com licença (task 5.3)

| Ferramenta | O que faz | Licença | Serve a quê aqui |
| --- | --- | --- | --- |
| **LeIA** (`rafjaa/LeIA`) | fork do VADER adaptado ao português, léxico, com emoji e negação | **MIT** | **só polaridade** (`pos`/`neg`/`neu`/`compound`), não emoção nomeada — não serve ao uso formativo, e o uso a que serviria é o vedado pela decisão 7 |
| **pysentimiento** | toolkit multilíngue com emoção, ódio e ironia; PT entre os idiomas suportados | código aberto, mas **os modelos herdam licença de datasets de terceiro, vários não comerciais** | candidato real para o uso descritivo; licença a conferir modelo a modelo antes de entrar em entregável |
| **BERTimbau ajustado para emoção** | transformer PT-BR ajustado sobre GoEmotions traduzido ou sobre as oito emoções de Plutchik | base `neuralmind/bert-base-portuguese-cased` é **MIT**; o ajuste herda a licença do dataset de treino | encaixa no papel 3 da decisão 1, coerente com o achado do MTEB-BR de que o BERTimbau é forte em classificação e fraco em recuperação |
| **EmoAtlas** (léxico) | detecção interpretável por léxico, oito emoções de Plutchik | conferir na fonte | alternativa barata; o benchmark de 2025 em PT-BR o põe abaixo dos transformers em acurácia, com custo computacional até 40× menor |

Nenhuma é adotada nesta fase. O que a task entrega é o levantamento com a
restrição de licença visível, e uma conclusão: **a única ferramenta PT-BR madura
e de licença limpa (LeIA, MIT) faz justamente o que a decisão 7 proibiu usar**,
o que reforça que a via de emoção nomeada é trabalho de prompt sobre o gerador
local, não de biblioteca pronta.

Fontes conferidas em 19/09/2026: repositório do LeIA (licença MIT, saída de
polaridade), README do pysentimiento (idiomas suportados e a ressalva de que os
modelos herdam licença de dataset de terceiro), e o benchmark de detecção de
emoção em português de 2025 que compara léxico, BERTimbau e LLM.

#### O teste dos dois casos cruzados (task 5.4)

O teste existe para provar que o sistema **não** usa carga emocional como
indício de falsidade. São dois casos, e os dois precisam passar:

| Caso | Entrada | O que DEVE acontecer | O que reprova |
| --- | --- | --- | --- |
| **C1 — verdadeiro com carga emocional alta** | alerta real de surto, em caixa alta, com pedido de repasse e apelo ao medo | o veredito acompanha o trecho recuperado e sai `verdadeiro`; a técnica `urgência fabricada` pode ser nomeada no bloco formativo | qualquer rebaixamento do veredito por causa do tom |
| **C2 — falso em tom neutro** | texto antivacina calmo, pseudo-técnico, com citação de estudo inexistente | o veredito sai `falso` ou `evidência insuficiente` conforme o trecho, sem que a ausência de emoção pese a favor | o tom sóbrio elevar a confiança atribuída |

C2 é o caso que importa: é o formato predominante do corpus de Telegram de
`acervo-circulacao`, e é exatamente onde um classificador de polaridade erraria.
Os dois casos entram como itens-armadilha de `avaliacao-instrumento`, e a
construção dos estímulos depende da curadoria dos 20 a 30 casos daquele change.

### 14. Candidatos por papel, licenças e a Prohibited Use Policy — 19/09/2026

Tasks 1.3 a 1.5 e 1.7. A decisão 1 fixou os três papéis e a decisão 5 fixou o
critério de seleção do papel de recuperação; falta a lista de candidatos com o
que cada um custa em tamanho e obriga em licença.

#### Papel 1 — recuperação (task 1.3)

| Candidato | Parâmetros | Dimensão | Janela | Licença | Prefixo assimétrico |
| --- | --- | --- | --- | --- | --- |
| `intfloat/multilingual-e5-small` | ~118 M | 384 | 512 | MIT | `query:` / `passage:` |
| **`intfloat/multilingual-e5-base`** (adotado) | ~278 M | 768 | 512 | MIT | `query:` / `passage:` |
| `intfloat/multilingual-e5-large` | ~560 M | 1024 | 512 | MIT | `query:` / `passage:` |
| `BAAI/bge-m3` | ~568 M | 1024 | **8192** | MIT | não exige |
| `neuralmind/bert-base-portuguese-cased` (BERTimbau) | ~110 M | 768 | 512 | MIT | não se aplica |

**Sobre a coluna de score.** A decisão 5 já registra o que o MTEB-BR mostra no
agregado: 0,331 de média em recuperação para os 16 modelos específicos de
português contra 0,517 dos multilíngues (p = 0,003), BERTimbau em 0,258, e a
diferença desaparecendo entre variantes ajustadas para recuperação (0,516 contra
0,517, p = 0,99). **O score por modelo não foi transcrito para esta tabela**
porque não foi possível extrair a tabela do artigo em texto conferível — e
número de benchmark copiado de segunda mão é exatamente o tipo de afirmação que
este projeto não aceita sobre dado de terceiro.

O que substitui isso, e é mais forte para a decisão: a medição própria da task
3.3, sobre o conjunto de aferição de 20 consultas do nosso corpus. Benchmark
público mede tarefa genérica; a aferição mede a tarefa que o produto faz.

**Restrições que a tabela impõe.** A janela de 512 tokens do e5 é o que ditou o
fragmento de 1.100 caracteres da decisão 11 — o `bge-m3`, com 8.192, dispensaria
a fragmentação, e é a razão pela qual ele permanece candidato apesar do custo.
Trocar o modelo obriga a **reindexar**: usar modelos diferentes na indexação e
na consulta quebra o espaço vetorial, e isso não é negociável.

#### Papel 2 — geração (task 1.4)

| Via | Candidato | Licença | Por que entra ou sai |
| --- | --- | --- | --- |
| **local** | **Gemma 4 12B QAT q4_0** (adotado) | termos da Gemma, com Prohibited Use Policy | decisão 8; o dado não sai da máquina, o que retira a questão do TCLE em vez de mitigá-la |
| local | Gemma 3 12B QAT | termos da Gemma, com Prohibited Use Policy | contingência da decisão 8, se o ferramental da geração 4 falhar |
| local | Qwen 3 14B | Apache 2.0 | licença mais limpa; não adotado por não ter sido sondado, e sondar custa o mesmo que já foi gasto no Gemma 4 |
| API | Gemini, GPT, Claude | termos de serviço do provedor | **descartada em 17/09/2026**: mensagem de participante de teste sairia para terceiro durante a sessão, o que entra no TCLE e amplia a submissão ao CEP |
| local | MedGemma | Health AI Developer Foundations | **descartado** — decisão 2 |

#### Licenças dos modelos adotados, pelo nome (task 1.5)

| Modelo adotado | Papel | Licença | Restrição que importa aqui |
| --- | --- | --- | --- |
| `intfloat/multilingual-e5-base` | recuperação | MIT | nenhuma restrição de uso; exige atribuição da licença |
| Gemma 4 12B QAT | geração | termos da Gemma + Prohibited Use Policy | ver a seção seguinte |
| BERTimbau (se usado no papel 3) | classificação auxiliar | MIT (modelo base) | o ajuste herda a licença do dataset de treino, que precisa ser conferida separadamente |

#### A Prohibited Use Policy contra `fronteira-orientacao-saude` (task 1.7)

Conferida em 19/09/2026. A política é a mesma para Gemma 3 e Gemma 4, então a
conferência vale também para a contingência.

Três cláusulas tocam este projeto:

1. **Prática não licenciada de profissão**, incluindo explicitamente
   medicina/saúde. Proíbe o sistema exercer medicina sem licença.
2. **Alegação enganosa de perícia ou capacidade**, "particularmente em áreas
   sensíveis (por exemplo, saúde, finanças, serviços de governo ou jurídico)".
   Proíbe o sistema se apresentar como fonte clínica.
3. **Decisão automatizada de alto risco** em domínios que afetam direitos ou
   bem-estar individual, saúde incluída.

**Resultado da conferência: não há conflito. Há convergência.** A política proíbe
exatamente o que `fronteira-orientacao-saude` já obriga o sistema a recusar —
conduta clínica individual. As três cláusulas são mais restritivas que a nossa
spec em nenhum ponto e coincidentes nela em todos.

Duas consequências práticas, ambas já ancoradas:

- A cláusula 3 reforça que o veredito **não pode** ser saída única e
  automatizada sobre conduta: o princípio arquitetural de `openspec/project.md`
  já exige critério e proveniência junto, e a política torna isso também uma
  obrigação de licença.
- A falha da sonda T2 (decisão 10), em que o modelo abriu com `VEREDITO: Falso`
  para quem perguntou se podia parar a quimioterapia, é uma aproximação da
  cláusula 1. O classificador de pedido de conduta da task 4.1 do MVP passa a
  ter, além da razão de produto, uma razão de conformidade de licença.

A contingência do Gemma 3 fica **autorizada quanto à política**; o que restaria
conferir, se acionada, são os termos de uso da versão específica, não a PUP.

## Questões em aberto

- ~~Local ou API para o papel de geração.~~ **Fechada em 17/09/2026** — ver
  decisão 8.
- **Maturidade de ferramentas do Gemma 4.** A geração 4 é recente. Se o
  ferramental local (Ollama, llama.cpp) apresentar defeito que consuma tempo de
  projeto, a alternativa de contingência é o Gemma 3 12B QAT, aceitando a
  licença própria e conferindo a Prohibited Use Policy contra
  `fronteira-orientacao-saude`. A contingência MUST ser registrada se acionada.
- **Necessidade de reranker.** O híbrido está de pé desde 18/09/2026, então a
  questão deixou de ser adiada por impossibilidade e passou a depender da
  medição da task 3.1: o ganho de um cross-encoder sobre o top-20 só compensa se
  a aferição mostrar o documento correto aparecendo no top-20 e fora do top-3.
- **Tamanho do modelo de embedding.** A assimetria está medida para o `e5-base`:
  13,2 minutos para indexar 22.464 fragmentos contra 14 a 18 ms por consulta. O
  custo de indexação é lote único e cabe com folga; o de consulta é que compete
  com os 17 a 23 segundos do gerador, e nesse orçamento ele é ruído. Um modelo
  quatro vezes maior ainda caberia na consulta, e a questão passa a ser de
  qualidade, não de latência — o que a task 3.3 mede e a 3.4 confirma. Usar
  modelos diferentes nas duas pontas continua fora de questão: quebra o espaço
  vetorial.
- ~~Provisionamento do ambiente.~~ **Fechada em 18/09/2026.** Python 3.14.6,
  `requirements-rag.lock.txt`, `torch` 2.14.0 com MPS ativo e CLI `openspec`
  disponível. O índice foi construído nesse ambiente.
