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
# Caso NN — <título curto>

| Campo | Conteúdo |
| --- | --- |
| **Analisado por** | <nome> |
| **Data da análise** | <DD/MM/AAAA> |

## 1. Afirmação central

<A alegação, em uma frase, como ela circula. Não a reescreva para soar mais
razoável do que é — a forma dela é parte do objeto.>

## 2. Veículo e data de publicação

<Onde apareceu e quando. Se circulou em mais de um canal, registre o primeiro
que você conseguiu localizar e diga como localizou.>

## 3. Tipo de manipulação

<Um dos cinco: fabricação integral · recontextualização de mídia ou dado
antigo · exagero de estudo real · distorção estatística · mídia sintética.
Se o caso combina mais de um, nomeie o principal e liste os demais.>

## 4. Sinais de não-confiabilidade observados

<Lista do que você **viu**, não do que você concluiu. Um sinal por linha.
Exemplo: "atribui a fala a 'um dermatologista' sem nome"; "pede repasse
urgente"; "não há link para a fonte citada".>

- 
- 
- 

## 5. Estudo ou fonte primária de origem

<Se a alegação deriva de algo real, a referência com identificador verificável
— DOI, PubMed, número de processo, link da bula. **E a distância entre o que a
fonte mediu e o que a publicação afirmou.**

Se nenhuma origem foi localizada, escreva explicitamente "nenhuma fonte
primária localizada" e descreva o esforço de busca no campo 6.>

## 6. Tempo gasto na verificação

| Medida | Valor |
| --- | --- |
| Início | <HH:MM> |
| Conclusão fundamentada | <HH:MM> |
| **Total** | **<N min>** |

<Descreva o que consumiu o tempo. Buscas que não deram em nada contam e devem
ser mencionadas — elas são metade do argumento sobre o custo da verificação.>

## 7. O que uma IA teria adiantado

<Concreto, ligado ao que você fez. "Teria localizado a bula em segundos" é
útil; "teria ajudado" não é.>

## 8. O que uma IA não resolveria

<Também concreto. Este campo é o mais importante da ficha para o projeto:
ele alimenta os limites da matriz de confiança e o princípio de que o sistema
não substitui o julgamento do usuário.>
```

---

## Checklist antes de fechar a ficha

- [ ] Os oito campos estão preenchidos — nenhum vazio, nenhum «n/a» sem motivo
- [ ] O tipo de manipulação é um dos cinco nomeados
- [ ] Os sinais do campo 4 são observações, não conclusões
- [ ] A leitura lateral foi feita, e as fontes externas consultadas estão citadas
- [ ] O tempo do campo 6 inclui as buscas infrutíferas
- [ ] O campo 8 diz algo específico, não uma ressalva genérica

## Consolidação, depois de todas as fichas

Quando todas as fichas estiverem preenchidas, o portfólio apresenta o tempo
**mínimo, máximo e mediano** de verificação, e esse dado é referenciado como
justificativa do problema. É a task 2.4.
