# Apresentação — conteúdo dos slides

Conteúdo da apresentação para a banca em 16/10/2026, slide por slide, para o
grupo montar no editor de slides. Change `add-portfolio-showcase`, tasks 5.1
e 7.3. Todo número sai da [rodada da demo](../act/prototipo-avaliacao.md#rodada-da-demo)
ou das páginas do portfólio, citadas em cada slide. Número que não está lá
não entra no slide.

!!! note "Duração: 10 minutos, com a demo"
    Nove slides na ordem pedida pela coordenação: problema → solução → IA →
    demonstração → resultados. O tempo de cada slide soma 9 min 30 s e deixa
    30 s de folga. Se o ensaio estourar, o slide 8 cai para uma frase, e a
    demo fica com dois casos.

| # | Slide | Tempo | Acumulado |
| --- | --- | --- | --- |
| 1 | Dona Checa | 0:15 | 0:15 |
| 2 | O problema | 1:00 | 1:15 |
| 3 | A tese: veredito nunca nu | 0:45 | 2:00 |
| 4 | A solução | 0:45 | 2:45 |
| 5 | Como a IA trabalha | 1:15 | 4:00 |
| 6 | Demo ao vivo | 3:00 | 7:00 |
| 7 | Resultados técnicos | 1:00 | 8:00 |
| 8 | Com pessoas, e o que ela não faz | 1:00 | 9:00 |
| 9 | Valor e próximos passos | 0:30 | 9:30 |

---

## 1. Dona Checa

- Copiloto de verificação de mensagens de saúde, em português.
- Grupo 04, Challenge 1, residência em IA do Instituto Eldorado.
- Imagem: a Dona Checa ([identidade](../identidade/paleta.md)).

## 2. O problema

- Mensagens de saúde falsas chegam pelo WhatsApp da família, e quem recebe
  decide em segundos.
- Checar com rigor custa caro: nos seis casos forenses, **mediana de 22 min**
  por mensagem, de 10 a 43 min.
- **Essential Question:** como a IA pode ajudar as pessoas a avaliar a
  confiabilidade de informações **sem substituir o pensamento crítico**.
- Recorte: desinformação em saúde pública; sub-recorte, vacinação.
- Fonte: [portfólio do Engage](../engage/portfolio-engage.md), seção 4;
  [O desafio](../visao-geral.md).

## 3. A tese: veredito nunca nu

- Um selo «falso» sem motivo não ensina nada, e a pessoa cai no próximo
  boato.
- Esconder a conclusão também não ajuda: devolve o trabalho de 22 minutos
  para quem não tem tempo.
- A Dona Checa dá o veredito **com o critério e com a fonte**, que a pessoa
  pode conferir e da qual pode discordar.
- Sucesso não é acurácia de classificador. É o **ganho de discernimento**: a
  pessoa acertar depois, sem a ferramenta.
- Fonte: `openspec/project.md`, nota de revisão de 10/09/2026;
  [Início](../index.md).

## 4. A solução

- A pessoa cola a mensagem ou o link que recebeu. Não precisa de conta.
- A resposta tem quatro blocos, até 120 palavras: veredito, critério,
  o que é fato e o que é opinião, e a fonte.
- Quatro rótulos possíveis, e um deles é «evidência insuficiente».
- Pedido de conduta médica ou urgência sai do caminho normal e vai para
  orientação profissional.
- Fonte: [Protótipo e avaliação](../act/prototipo-avaliacao.md#o-que-ela-faz).

## 5. Como a IA trabalha

- Sete etapas: fronteira, leitura, extração, decomposição, recuperação,
  guarda, resposta.
- **RAG híbrido** sobre 6.279 checagens de agências brasileiras (23.655
  fragmentos): BM25 + `multilingual-e5-base`, fusão com α = 0,9.
- Gerador: `deepseek-v4-pro`, instruído por prompt. **Nenhum modelo treinado
  para dar veredito.**
- **Guarda:** sem trecho que cubra a alegação, o rótulo é «evidência
  insuficiente». Veredito não sai da memória do modelo.
- Antes de sair, a resposta passa por quatro conferências em código: técnica
  do catálogo, mito sempre marcado, frase sem base removida, teto de 120
  palavras.
- Fonte: [Protótipo e avaliação](../act/prototipo-avaliacao.md#o-fluxo);
  [Relatório técnico](../act/relatorio-tecnico.md), seção 3.

## 6. Demo ao vivo

- Três casos do [roteiro](roteiro-demo.md), na ordem: 1 (veredito com fonte),
  4 (sem evidência, sem veredito) e 5 (fronteira de saúde).
- No caso 1, abrir «Ver fontes e detalhes» e mostrar agência, data e link.
- Se sobrar tempo: caso 2 (verdadeiro contra-intuitivo).
- Plano B: vídeo gravado no ensaio.

## 7. Resultados técnicos

- **Recuperação:** a checagem certa aparece entre as 5 primeiras em 20 de 20
  consultas reais (Recall@5 1,00, MRR 0,897).
- **Bancada ponta a ponta:** 29 de 30 casos, sem falha eliminatória. A falha
  (F06) é de forma.
- 10 de 10 respostas com evidência trazem o link da checagem.
- Verificação completa em **13,8 s** de mediana, contra 22 min à mão; de
  US$ 0,002 a 0,004 por mensagem.
- Fonte: rodada `20261013-104226`, [rodada da demo](../act/prototipo-avaliacao.md#rodada-da-demo).

## 8. Com pessoas, e o que ela não faz

- Piloto com duas pessoas em 08/10: discernimento 4 de 4, transferência sem a
  ferramenta 4 de 4.
- **n = 2, sem linha de base:** valida o instrumento, não o efeito.
- Pauta fora do acervo (mpox, oropouche, Qdenga): responde «evidência
  insuficiente» em vez de chutar.
- Fonte: [Com pessoas](../act/prototipo-avaliacao.md#com-pessoas) e
  [limitações](../pendencias.md#limitacoes-conhecidas-do-prototipo).

## 9. Valor e próximos passos

- Valor: transforma 22 minutos de checagem em segundos, **sem tirar da pessoa
  o julgamento**: ela vê o critério e a fonte.
- Próximo passo: coleta com 20 a 30 pessoas, com linha de base e
  item-armadilha, e acervo atualizado depois de 2021.
- Repositório, portfólio e vídeo: links e QR code.

---

## Fora do deck, pronto para perguntas

O que saiu dos 14 slides anteriores vira resposta preparada.

| Pergunta provável | Resposta | Fonte |
| --- | --- | --- |
| Por que não treinaram um classificador? | Seria opaco e congelaria o conhecimento na data do treino; com RAG, checagem nova vale sem retreino | [Relatório técnico](../act/relatorio-tecnico.md), seção 2.1 |
| Por que não rodar local? | Gemma 4 local levava 102,4 s de mediana por mensagem | [Relatório técnico](../act/relatorio-tecnico.md), seção 3.4 |
| E a privacidade, com API externa? | Termo de consentimento, remoção de telefone, CPF e e-mail no servidor; CEP simulado | [Relatório técnico](../act/relatorio-tecnico.md), seção 3.4 |
| Como investigaram o problema? | Seis casos forenses de vacinação e matriz de confiança v1 | [casos](../forense/casos-forense.md), [matriz](../engage/kit-matriz-confianca.md) |
| E se a mensagem exagera uma alegação já checada? | Caso jacaré: «vacina transforma em jacaré» recebe «evidência insuficiente». Gemma e DeepSeek negaram a implicação jacaré ⇒ DNA, e o grupo manteve a regra conservadora | `add-cobertura-alegacao-ampla`, [pendências](../pendencias.md) |
| Quando mudaram de ideia sobre o veredito? | Em 10/09: «não emitir veredito» era regra nossa, não do enunciado | `openspec/project.md` |
