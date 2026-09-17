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

## Questões em aberto

- **Canal.** Se a mensagem chega no WhatsApp e a verificação mora em outro app,
  a maior parte das pessoas não faz a travessia. A decisão de canal precisa ser
  tomada antes da fase de testes, porque muda a arquitetura, não só a interface.
- **Composição do catálogo.** Quais 6 a 8 técnicas, e com que nomes. Depende de
  uma passada de leitura no recorte de saúde do FactCenter.
- **Limiar de recuperação** a partir do qual o veredito cai para `evidência
  insuficiente`.
