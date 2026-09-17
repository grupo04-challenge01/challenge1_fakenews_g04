# Design — Decisões da Fase Engage

## Decisão 1: andaime cognitivo em vez de classificador

**Contexto.** A formulação padrão da tarefa em NLP é classificação binária de
veracidade, e a maior parte dos datasets públicos existe para servir a essa
formulação.

**Decisão.** O produto não emite veredito **nu**. O veredito é permitido e vem
primeiro, mas nunca sozinho: junto dele vão a proveniência, as afirmações
checáveis, a cobertura independente e o enquadramento, e o caminho até a fonte
fica aberto para que o usuário possa discordar do que leu.

**Consequências.**
- A métrica primária deixa de ser acurácia de modelo e passa a ser ganho de
  discernimento do usuário, medido com e sem a ferramenta.
- Datasets de rótulo perdem o papel de alvo de treino e ganham o papel de banco
  de estímulos para teste com usuários.
- Datasets que trazem cadeia de raciocínio (explicação junto do rótulo) passam a
  ser o núcleo do portfólio.

**Alternativa descartada.** Classificador com camada de explicabilidade (XAI)
sobre a predição. Descartada não por emitir veredito, mas porque a explicação,
nesse desenho, é racionalização posterior de uma predição: justifica o rótulo em
vez de apresentar a evidência que o sustenta. Falha na auditabilidade até a
fonte, que é o que a Big Idea exige ao falar de *apoiar a investigação*.

**Nota de revisão — 10/09/2026.** Até esta data a decisão dizia "o produto não
emite veredito como saída principal". O andaime cognitivo continua sendo a
decisão desta fase; o que mudou é o mecanismo. Segurar a conclusão não era
exigência do challenge — era derivação do grupo, e contrariava a própria Big
Idea, cujo problema declarado é excesso de informação. As duas exigências que
sobrevivem, e que este change herda como inegociáveis, são auditabilidade até a
fonte e transferência como métrica primária. Ver `openspec/project.md`.

## Decisão 2: recorte em saúde pública

**A favor.** Existe hierarquia de evidência estabelecida e consultável, o que
resolve a pergunta "quem decide o que é confiável" sem que o grupo precise
arbitrar. Ler evidência de saúde (tipo de estudo, tamanho amostral, risco
relativo vs. absoluto) é uma habilidade transferível, que é exatamente o que a
Essential Question pede. E o dano é concreto e documentado.

**Contra, e como tratar.**
- *O consenso se move.* Recomendações mudam. Tratar fonte oficial como verdade
  atemporal ensina obediência, não avaliação. Vira guiding question aberta.
- *A maior parte do conteúdo problemático não é falso, é exagerado.* Estudo real
  inflado em manchete não é detectado por classificador de veracidade e é bem
  tratado por comparação entre manchete e estudo de origem. Reforça a Decisão 1.
- *Fronteira com aconselhamento médico.* O sistema avalia informação; não
  recomenda conduta. Precisa de rota explícita para profissional de saúde.
  Registrado como restrição para a fase Act.

## Decisão 3: capabilities de pesquisa, não de software

Enquanto o projeto estiver em Engage e Investigate, cada capability corresponde
a um artefato entregável (ficha de caso, matriz, backlog de GQs), com critérios
de aceitação verificáveis. Isso mantém o SDD útil sem exigir que o grupo invente
comportamento de sistema antes de ter feito a pesquisa.

## Decisão 4: teto de 12 guiding questions

O board produziu cerca de 40 candidatas. O spec admite backlog de 8 a 12; o teto
de **12** foi escolhido em 10/09/2026, em vez do corte mais agressivo em 8.

**Motivo.** A classificação por fonte de resposta separa as GQs em trilhas que
não competem entre si — `literatura` não consome tempo de coleta, `fechada` não
consome tempo nenhum. Cortar em 8 obrigaria a descartar pergunta boa só por
volume, quando o custo real depende da classe, não da contagem.

**Consequência.** Aproximadamente 28 candidatas serão fundidas ou descartadas
com motivo registrado, como o requirement de qualidade já exige.

## Riscos registrados

| Risco | Efeito | Mitigação prevista |
| --- | --- | --- |
| Viés de automação | Usuário aceita a saída da IA sem pensar | Métrica de guarda; itens em que a ferramenta erra de propósito no instrumento de avaliação |
| Falso positivo em conteúdo legítimo | Alimenta descrédito generalizado | Métrica de guarda; rubrica exige distinguir sinal fraco de sinal ausente |
| Ceticismo indiscriminado | Usuário passa a desconfiar de orientação legítima | Medido no pós-teste, não só o acerto |
| Alucinação de citação científica | Referência inventada em contexto de saúde | Recuperação restrita a índice fechado com identificador verificável; nunca geração livre de referência |
| Efeito da verdade ilusória no teste | Exposição a manchete falsa aumenta credibilidade percebida | Debriefing estruturado obrigatório ao final da sessão |
| Solução travada antes da pesquisa | Investigate vira justificativa retroativa | Quadro Solução do board tratado como parking lot; capabilities de produto adiadas para a fase Act |

## Questões em aberto

1. Qual sub-recorte dentro de saúde pública.
2. Em que ponto da jornada (antes de ler, ao ler, antes de compartilhar) a
   intervenção tem mais efeito.
3. Qual atrito o usuário aceita antes de abandonar.
4. Como comunicar que o consenso científico é provisório sem produzir a
   conclusão de que "ninguém sabe nada".
5. Quais sinais de qualidade de evidência são extraíveis de um texto de
   divulgação e quando é preciso ir ao artigo original.

Nenhuma dessas questões é decidida neste change. Todas entram no backlog de
`guiding-questions`.
