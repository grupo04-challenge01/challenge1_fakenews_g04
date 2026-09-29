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

### 8. Fronteira de orientação em saúde: guardrails de tom, recusa e bypass de emergência — 29/09/2026

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

## Questões em aberto

- **Composição do catálogo.** ~~Quais 6 a 8 técnicas, e com que nomes.~~
  Fechada na decisão 6, com a vaga de `conspiração` pendente da matriz.
- **Limiar de recuperação** a partir do qual o veredito cai para `evidência
  insuficiente`.


