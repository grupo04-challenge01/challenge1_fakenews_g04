# O desafio

## Big Idea

> Em um mundo com excesso de informação, como distinguir fatos, evidências e
> opiniões? A IA pode apoiar a investigação da confiabilidade das informações,
> fortalecendo o pensamento crítico em vez de substituí-lo.

## Essential Question

> Como sistemas de IA podem ajudar as pessoas a avaliar a confiabilidade de
> informações sem substituir seu pensamento crítico?

O enunciado nomeia **três competências**, e nenhuma é opcional:

| Competência | Como o projeto responde |
| --- | --- |
| Investigar evidências | Recuperação sobre checagens brasileiras, com toda afirmação ancorada num trecho citado e rastreável até a fonte |
| Identificar vieses | **Lacuna aberta.** Nenhuma capability cobre isso ainda — ver [Estado do projeto](estado.md) |
| Construir critérios de confiança | Matriz de confiança (dimensões, sinais, limites, rubrica) e o bloco "o que observar da próxima vez" na resposta |

## O que o enunciado exige, e o que não exige

Este ponto custou uma revisão inteira ao grupo, então vale registrar.

O enunciado **exige** duas coisas, que valem como regra inegociável:

- **Auditabilidade até a fonte** — é o que significa "apoiar a *investigação*".
- **Transferência como métrica primária** — é o que significa "*fortalecendo* o
  pensamento crítico".

O enunciado **não** proíbe que o sistema dê um veredito. Durante uma semana o
grupo trabalhou com a regra "o sistema não emite veredito", derivada de
"não substituir o pensamento crítico". As duas coisas são diferentes: não
substituir o julgamento da pessoa não é o mesmo que não oferecer um julgamento.

O que substitui pensamento crítico é o **veredito nu** — conclusão sem
raciocínio e sem proveniência, que a pessoa só pode aceitar ou recusar. Um
veredito auditável, acompanhado do critério, apoia a investigação em vez de
substituí-la.

!!! warning "E havia uma contradição interna"
    A Big Idea diz que o problema é **excesso** de informação. Segurar a
    conclusão adiciona atrito a um problema de atrito — e o abandono por atrito
    excessivo é uma das nossas próprias métricas de guarda.

## Roadmap

| Fase | Período | Foco |
| --- | --- | --- |
| Engage | Semana 1 · 07/09 a 11/09 | Entender o desafio |
| Investigate | Semanas 2–3 | Pesquisa e descoberta |
| Act | Semanas 4–5 | Desenvolvimento |
| Showcase | Semana 6 | Partilha de conhecimento |

07/09 é feriado; a semana operacional do Engage começa em 08/09.

## Entregáveis finais

| Entregável | Onde está sendo construído |
| --- | --- |
| Portfólio de pesquisa | este site, mais os caveats de dataset |
| Estrutura de avaliação de confiança | capability `matriz-confianca` |
| Solução/protótipo com suporte de IA | change `mvp-copiloto-verificacao` |
| Apresentação e reflexão | fase Showcase |

## Recorte adotado

**Desinformação em saúde pública.** Escolhido porque existe hierarquia de
evidência consultável — o que resolve "quem decide o que é confiável" sem que o
grupo precise arbitrar —, porque ler evidência de saúde é habilidade
transferível, e porque o dano é imediato e documentado.

Sub-recorte (vacinação, doença crônica, suplementos) segue em aberto para a fase
Investigate.
