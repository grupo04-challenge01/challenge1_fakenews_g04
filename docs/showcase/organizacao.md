# Organização e papéis

Como o grupo 04 dividiu e acompanhou o trabalho no Challenge 1. Change
`add-portfolio-showcase`, task 7.1. Contagens de issues e pull requests
tiradas do GitHub em 15/10/2026.

## Integrantes e papéis

Os papéis seguem a lista R1 a R7 do challenge. Foram registrados no
[portfólio do Engage](../engage/portfolio-engage.md) e usados na divisão das
tasks do Act.

| Integrante | Papel | Foco no projeto |
| --- | --- | --- |
| Breno | R1 Business Stakeholder | portfólio e matriz consolidados, respostas de redirecionamento, termo de consentimento, protocolo de ética e piloto com pessoas |
| Wingrid | R2 Solution Architect | forma da resposta sem evidência, fontes oficiais, camadas da interface, consistência entre catálogo e matriz |
| Vitor | R3 Data Scientist, modelagem | gerador, prompts de extração, classificação, decomposição e resposta, guarda e catálogo de técnicas |
| Jhessica | R3 Data Scientist, instrumento e avaliação | matriz de confiança e rubrica, casos de teste, bateria adversarial, acessibilidade e legibilidade |
| Samara | R4 Data Engineer, R6 DevOps e R7 MLOps | recoleta e indexação dos corpora, recuperação, instrumentação das métricas, site e publicação |

R5 Software Engineer não virou pessoa. As tasks de interface foram para
Wingrid e Jhessica, e as de validação para Vitor. Ninguém ficou dono do padrão
de código. Foi uma escolha assumida na divisão, não um esquecimento.

## Cadência

O grupo seguiu o calendário de fases do challenge. Cada fase funcionou como
um sprint, com entregável próprio no fim.

| Semana | Fase | Datas | Entregável da fase |
| --- | --- | --- | --- |
| 1 | Engage | 07/09 a 11/09 | Guiding Questions, board, casos forenses, matriz de confiança v1 |
| 2 e 3 | Investigate | 14/09 a 25/09 | datasets tratados, índice híbrido, aferição da recuperação, sonda do gerador |
| 4 e 5 | Act | 28/09 a 09/10 | protótipo Dona Checa, chat web, bancada de casos, piloto com pessoas |
| 6 | Showcase | 12/10 a 16/10 | portfólio, demo, apresentação, vídeo e reflexão |

A comunicação foi principalmente presencial, nos encontros da residência, e
pelo WhatsApp do grupo.

## Backlog

O backlog teve duas camadas.

- **Specs e tasks.** O projeto segue Spec-Driven Development com
  [OpenSpec](https://github.com/Fission-AI/OpenSpec). Cada trabalho abre um
  *change* em `openspec/changes/` com proposta, design, specs e um `tasks.md`.
  O `tasks.md` é a lista de itens do change, e um change só fica pronto com
  todas as tasks marcadas e `openspec validate --strict` limpo.
- **Issues do GitHub.** As tasks viraram 105 issues, com etiquetas de fase
  (`fase:engage`, `fase:investigate`, `fase:act`), de change
  (`change:mvp-copiloto`, `change:interface-chat` e outras) e de dono
  (`papel:<nome>`).

O estado do backlog fica em [Estado do projeto](../estado.md) e
[Tasks pendentes](../pendencias.md), com data no topo.

## Divisão das tasks no Act

No Act, as 47 tasks abertas foram divididas entre os cinco, com um dono por
task e nenhuma órfã. A divisão juntou tasks que dividem contexto: as de prompt
e gerador ficaram com uma pessoa só, porque usam o mesmo gerador, o mesmo
prompt base e a mesma sonda.

| Integrante | Tasks |
| --- | --- |
| Breno | 8 |
| Wingrid | 9 |
| Vitor | 12 |
| Jhessica | 11 |
| Samara | 7, mais 3 novas de CI e rastreio |

A divisão fixou também a ordem que não podia furar:

1. Breno submete o protocolo de ética primeiro, porque tinha prazo externo.
2. Wingrid fecha a forma da resposta sem evidência, o que libera o prompt dos
   quatro blocos.
3. Jhessica fecha a matriz de confiança, o que libera a conferência do
   catálogo e o portfólio consolidado.
4. Samara fecha a indexação, o que libera a calibração do limiar.
5. Jhessica fecha os casos e os itens-armadilha, o que libera o piloto.

A divisão nomeou um risco: o conhecimento de `prototipo/indice/` e
`tratamento/` estava concentrado em uma pessoa, e passar as tasks de corpus
exigia uma sessão de passagem de conhecimento.

## Fluxo de trabalho

1. A task vira issue, com fase, change e dono.
2. O dono trabalha num branch próprio.
3. O pull request descreve o que muda e qual task fecha.
4. Depois da revisão, o merge vai para a `main`. Até 13/10 foram 79 pull
   requests integrados.
5. O merge na `main` publica o portfólio no GitHub Pages
   (`.github/workflows/deploy.yml`).

A regra do repositório é «spec antes de implementação». Pedido de trabalho
sem change primeiro vira proposta, e divergência entre spec e código se
resolve mudando o change, nunca ajustando a spec ao que já foi feito. Ver
[Metodologia](../metodologia.md).
