# Ficha de caso — template da investigação forense

Template da task 1.2 do change `add-engage-desinformacao-saude`, conforme a
capability `pesquisa-investigativa`.

**Uma ficha por caso, uma pessoa por caso.** Ficha incompleta MUST NOT entrar no
portfólio de pesquisa — é exigência da spec, não preferência de formato.

---

## Como preencher

Os oito campos abaixo são os que a capability exige, na ordem. Nenhum é
opcional. Dois pedem atenção especial:

**O tempo é dado, não burocracia.** O campo de tempo mede o intervalo entre
abrir o caso e chegar a uma conclusão fundamentada — incluindo as buscas que não
deram em nada. Esses tempos viram a evidência quantitativa do quadro Problema no
brainstorming. Sem eles, o argumento do projeto vira opinião.

**Leitura lateral é obrigatória.** A avaliação da fonte é feita **saindo** da
página analisada e consultando fontes externas independentes. Aparência, layout
e tom da própria página MUST NOT ser aceitos como evidência de confiabilidade.
Se o veículo é desconhecido, a checagem do veículo é parte da análise.

---

## Template

Copie o bloco abaixo para um arquivo novo em `docs/engage/fichas/`, nomeado
`caso-NN-palavra-chave.md`.

```markdown
# Caso 01 — <Vacina Febre Amarela>

| Campo | Conteúdo |
| --- | --- |
| **Analisado por** | <Samara Letícia Alves dos Santos> |
| **Data da análise** | <22/09/2026> |

## 1. Afirmação central

Vacina contra Febre Amarela mata em 50% dos casos .

## 2. Veículo e data de publicação

Foi através de um áudio de whatsapp entre 20 e 22 de março de 2017.

## 3. Tipo de manipulação

recontextualização de mídia ou dado
antigo

## 4. Sinais de não-confiabilidade observados

- Não há link para a fonte citada.
- Pede repasse urgente.
- Atribui a fala a um dermatologista sem nome
- Estatística extremamente alta

## 5. Estudo ou fonte primária de origem

Nenhuma fonte primária localizada.

## 6. Tempo gasto na verificação

| Medida | Valor |
| --- | --- |
| Início | <15:00> |
| Conclusão fundamentada | <15:10:MM> |
| **Total** | **<10 min>** |

<Descreva o que consumiu o tempo. Buscas que não deram em nada contam e devem
ser mencionadas — elas são metade do argumento sobre o custo da verificação.>

Buscar o contexto da frase e também as fontes. 

## 7. O que uma IA teria adiantado

<Concreto, ligado ao que você fez. "Teria localizado a bula em segundos" é
útil; "teria ajudado" não é.>

Teria localizado a verdadeira porcentagem de óbito da vacina de febre amarela em segundos.

## 8. O que uma IA não resolveria

<Também concreto. Este campo é o mais importante da ficha para o projeto:
ele alimenta os limites da matriz de confiança e o princípio de que o sistema
não substitui o julgamento do usuário.>

Não teria conseguido encontrar o link da fonte da notícia.
```

---

## Checklist antes de fechar a ficha

- [x] Os oito campos estão preenchidos — nenhum vazio, nenhum «n/a» sem motivo
- [x] O tipo de manipulação é um dos cinco nomeados
- [x] Os sinais do campo 4 são observações, não conclusões
- [x] A leitura lateral foi feita, e as fontes externas consultadas estão citadas
- [x] O tempo do campo 6 inclui as buscas infrutíferas
- [x] O campo 8 diz algo específico, não uma ressalva genérica

## Consolidação, depois de todas as fichas

Quando todas as fichas estiverem preenchidas, o portfólio apresenta o tempo
**mínimo, máximo e mediano** de verificação, e esse dado é referenciado como
justificativa do problema. É a task 2.4.
