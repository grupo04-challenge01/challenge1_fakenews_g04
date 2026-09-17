# Metodologia

O projeto combina duas coisas: **CBL** (Challenge Based Learning), que é a
metodologia da residência, e **SDD** (Spec-Driven Development) via OpenSpec, que
é como o grupo organiza o repositório.

## A regra central

**Nada entra no repositório sem um *change* ativo que o cubra.** Código,
dataset, documento ou entregável.

Isento: correção de typo, formatação, configuração de ferramenta e bump de
dependência sem mudança de comportamento.

## O que é um change

Um pacote de planejamento com quatro artefatos:

| Artefato | Responde |
| --- | --- |
| `proposal.md` | Por que este trabalho existe, e o que ele atinge |
| `design.md` | As decisões tomadas, com as alternativas descartadas e o motivo |
| `specs/<capability>/spec.md` | O que o entregável tem de satisfazer, em requisitos verificáveis |
| `tasks.md` | O trabalho, em granularidade de meio dia |

## O fluxo

```text
1. Explorar   /opsx:explore     entendimento; nada é escrito
2. Propor     /opsx:propose     os quatro artefatos
3. Validar    openspec validate <change> --strict
4. Aplicar    /opsx:apply       executa as tasks e marca os checkboxes
5. Promover   /opsx:sync        specs migram para openspec/specs/
```

Um change por fase do CBL. Specs só migram para `openspec/specs/` quando a fase
encerra **e** o entregável existe de fato.

## Como um requisito é escrito

O ponto do SDD aqui é transformar intenção em coisa verificável. "Não substituir
o pensamento crítico" não é verificável. Isto é:

```text
O sistema MUST usar `evidência insuficiente` quando a recuperação não
retornar fonte que cubra a alegação, e MUST NOT emitir veredito a partir
apenas do conhecimento paramétrico do modelo.
```

Cada requisito precisa de ao menos um cenário no formato
**GIVEN / WHEN / THEN**, e os critérios têm de ser conferíveis por inspeção do
artefato. As palavras normativas (`SHALL`, `MUST`, `MUST NOT`, `WHEN`, `THEN`,
`AND`, `GIVEN`) ficam em inglês para que o validador funcione; o resto do texto
é em português.

## Precedência

**spec > tasks > código.** Divergência se resolve atualizando o change, nunca
ajustando a spec ao que já foi feito.

!!! danger "O validador não checa coerência"
    `openspec validate --strict` confere estrutura: requisito tem cenário,
    palavra normativa está no lugar. Ele **não** percebe quando um change
    contradiz o documento de contexto do projeto ou outro change. Isso aconteceu
    de fato aqui, e só apareceu na leitura humana.

## Definição de pronto

Três coisas ao mesmo tempo, não duas:

1. `tasks.md` 100% marcado
2. `openspec validate --strict` limpo
3. entregável existindo no repositório
