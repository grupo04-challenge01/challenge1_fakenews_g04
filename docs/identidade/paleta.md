# Identidade da Dona Checa

Persona do assistente, definida pelo grupo em 07/10/2026. Change
`add-identidade-dona-checa`, requirement Logo e paleta de
`identidade-dona-checa`. O nome é provisório.

## Logo

| Padrão | Alternativa |
|---|---|
| ![Dona Checa, marca refinada sobre verde-azulado](dona-checa.svg){ width="160" } | ![Dona Checa, retrato original](dona-checa-original.svg){ width="160" } |
| `dona-checa.svg`: retrato refinado (cordinha de contas nos óculos, armação gatinho, franja, brincos de pérola) em círculo verde-azulado | `dona-checa-original.svg`: retrato original, sem fundo |

Os dois arquivos são SVG autocontidos, sem fonte externa, e servem de avatar,
favicon e logo.

## Paleta

| Cor | Valor | Uso |
|---|---|---|
| Verde-azulado | `#0F5E63` | Fundo da logo, cabeçalho, títulos e links |
| Coral | `#E0573B` | Destaques gráficos: botão de enviar, bochechas da versão original |
| Âmbar | `#F2A93B` | Detalhes da logo sobre verde-azulado |
| Creme | `#FFE7A8` | Fundo do avatar no cabeçalho |
| Tinta | `#1C2B2E` | Texto corrido e traços da logo |

Fundo de página usado nos mocks: `#F3F7F6`.

## Contraste

A spec exige **4,5:1** para texto sobre cor da paleta. Razões calculadas pela
fórmula de luminância relativa da WCAG 2.

**Liberados para texto:**

| Texto | Fundo | Razão |
|---|---|---|
| Tinta | Branco | 14,64 |
| Tinta | `#F3F7F6` | 13,56 |
| Tinta | Creme | 12,02 |
| Branco | Verde-azulado | 7,50 |
| Verde-azulado | Branco | 7,50 |
| Tinta | Âmbar | 7,33 |
| Verde-azulado | `#F3F7F6` | 6,94 |
| Creme | Verde-azulado | 6,16 |

**Proibidos para texto, liberados só para elemento gráfico** (ícone, borda,
ilustração, que pedem 3:1):

| Primeiro plano | Fundo | Razão |
|---|---|---|
| Tinta | Coral | 3,90 |
| Branco | Coral | 3,75 |
| Coral | Branco | 3,75 |
| Âmbar | Verde-azulado | 3,75 |

Botão com texto, portanto, nunca é coral: o coral fica no botão só de ícone
(Enviar), que tem nome acessível próprio.

## Voz

Os textos fixos estão nas specs e o código os lê de lá:

- abertura, pergunta de confiança e chamada: `identidade-dona-checa`;
- bordão "Peraí, de onde veio isso? Vamos olhar juntos, meu bem.":
  `resposta-formativa`;
- recusa de conduta e desmentido de tratamento caseiro:
  `fronteira-orientacao-saude`. Urgência e CVV não usam a voz da persona.
