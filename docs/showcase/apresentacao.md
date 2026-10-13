# Apresentação — conteúdo dos slides

Conteúdo da apresentação de 16/10/2026, slide por slide, para o grupo montar
no editor de slides. Change `add-portfolio-showcase`, task 5.1. Todo número
sai da [rodada da demo](../act/prototipo-avaliacao.md#rodada-da-demo) ou das
páginas do portfólio, citadas em cada slide. Número que não está lá não entra
no slide.

!!! note "Duração"
    Quatorze slides, pensados para cerca de 15 minutos com a demo ao vivo
    (slide 9). Ajustar ao tempo que a banca der: os slides 6 e 12 são os
    primeiros a cortar.

---

## 1. Dona Checa

- Copiloto de verificação de mensagens de saúde, em português.
- Grupo 04, Challenge 1, residência em IA do Instituto Eldorado.
- Imagem: a Dona Checa ([identidade](../identidade/paleta.md)).

## 2. O problema

- **Big Idea:** em um mundo com excesso de informação, como distinguir fatos,
  evidências e opiniões.
- **Essential Question:** como a IA pode ajudar as pessoas a avaliar a
  confiabilidade de informações **sem substituir o pensamento crítico**.
- Recorte: desinformação em saúde pública; sub-recorte, vacinação
  (decidido em 17/09).
- Fonte: [O desafio](../visao-geral.md), `openspec/project.md`.

## 3. A virada de 10/09: veredito permitido, nunca nu

- Antes: «o sistema não emite veredito». Regra nossa, não do enunciado.
- Ela confundia *não substituir o julgamento* com *não oferecer um
  julgamento*. E segurar a conclusão aumenta o atrito num problema de excesso.
- Depois: o veredito vem sempre com o critério que o sustenta e com a fonte,
  que a pessoa pode conferir e da qual pode discordar.
- Fonte: `openspec/project.md`, nota de revisão de 10/09/2026.

## 4. O que conta como sucesso

- Não é a acurácia do classificador.
- É o **ganho de discernimento**: o acerto da pessoa depois, sem a ferramenta
  (transferência).
- Dataset de rótulo binário serve de banco de estímulos, nunca de alvo de
  treino.
- Fonte: [Início](../index.md).

## 5. Como investigamos

- Engage: seis casos forenses de vacinação, três tipos de manipulação
  ([casos](../forense/casos-forense.md)).
- Matriz de confiança, versão 1: falsa autoridade, recontextualização de
  mídia, distorção de documento real, enquadramento conspiratório
  ([matriz](../engage/kit-matriz-confianca.md)).
- Investigate: acervo de checagens, índice híbrido, aferição da recuperação.

## 6. O acervo

- 6.279 unidades e 23.655 fragmentos de checagens de agências brasileiras.
- Checagens com texto integral de julho de 2013 a maio de 2021; um índice de
  checagens recentes aponta as mais novas.
- Recuperação híbrida: recall@5 1,00 e MRR 0,897 em 20 consultas reais.
- Fonte: [Protótipo e avaliação](../act/prototipo-avaliacao.md).

## 7. Como a Dona Checa responde

- Sete etapas: fronteira, leitura, extração, decomposição, recuperação,
  guarda, resposta.
- **Guarda:** sem trecho que cubra a alegação, o rótulo é «evidência
  insuficiente». Veredito não sai do conhecimento do modelo.
- Resposta em quatro blocos, até 120 palavras, cada frase ancorada num trecho.
- Fonte: [Protótipo e avaliação](../act/prototipo-avaliacao.md#o-fluxo).

## 8. Quatro conferências antes de a resposta sair

- Técnica de manipulação nomeada pertence ao catálogo de sete.
- A alegação falsa nunca aparece sem a marca de falsa.
- Frase sem base no trecho sai da resposta.
- Acima de 120 palavras, o fim dos blocos é cortado.

## 9. Demo ao vivo

- Cinco casos do [roteiro](roteiro-demo.md): veredito com fonte, verdadeiro
  contra-intuitivo, opinião separada, sem evidência, fronteira de saúde.
- Abrir «Ver fontes e detalhes» em cada veredito.
- Plano B: vídeo gravado no ensaio.

## 10. Bancada ponta a ponta

- **29 de 30** casos, sem falha eliminatória.
- Veredito com fonte: 10 de 10 respostas com evidência, todas com link.
- Verificação completa: mediana de 13,8 s; custo de US$ 0,002 a 0,004 por
  mensagem.
- A falha (F06) é de forma: o bloco 2 não separou a opinião.
- Fonte: rodada `20261013-104226`, [rodada da demo](../act/prototipo-avaliacao.md#rodada-da-demo).

## 11. Com pessoas: o piloto

- Duas pessoas, em 08/10. Discernimento 4 de 4, transferência 4 de 4,
  transferência com critério 4 de 4.
- **n = 2, sem linha de base:** valida o instrumento e o roteiro, não o
  efeito.
- O item-armadilha não foi exercido: a aceitação cega ficou em 0 de 0.
- Fonte: [Com pessoas](../act/prototipo-avaliacao.md#com-pessoas) e
  [limitações da avaliação](../pendencias.md#limitacoes-da-avaliacao).

## 12. O caso jacaré

- «Vacina de covid transforma pessoas em jacaré» recebe «evidência
  insuficiente». Não há checagem da versão jacaré, só da alegação mãe, sobre
  o DNA.
- Tentamos aceitar veredito por implicação. Gemma e DeepSeek negaram jacaré ⇒
  DNA em todas as variantes testadas.
- O grupo manteve a regra conservadora e não mudou a spec para o caso passar.
- Fonte: `add-cobertura-alegacao-ampla`, branch fora da `main`.

## 13. O que ela não faz

- Pauta fora do acervo (mpox, oropouche, Qdenga): responde «evidência
  insuficiente».
- Fontes oficiais ainda fora do fluxo.
- Protocolo de ética simulado para fins acadêmicos.
- Fonte: [limitações](../pendencias.md#limitacoes-conhecidas-do-prototipo).

## 14. Os quatro entregáveis e próximos passos

- Portfólio, matriz de confiança, protótipo, esta apresentação e a
  [reflexão](reflexao.md).
- Próximo passo de pesquisa: a coleta com 20 a 30 pessoas, com a armadilha
  decidida e linha de base.
- Repositório e portfólio: link e QR code.
