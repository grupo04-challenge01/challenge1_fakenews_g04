# Roteiro do vídeo

Vídeo explicativo de até 5 minutos, publicado no YouTube, com os cinco
integrantes. Change `add-portfolio-showcase`, decisão D13, tasks 7.4 e 7.5.
Os números seguem a mesma regra dos slides: só os que estão na
[rodada da demo](../act/prototipo-avaliacao.md#rodada-da-demo) ou nas páginas
do portfólio.

!!! note "Divisão proposta"
    Cada trecho ficou com quem foi dono do assunto no projeto
    ([Organização e papéis](organizacao.md)). O grupo pode trocar as falas,
    desde que todos falem e a soma fique em até 5 minutos.

| # | Tópico da coordenação | Quem fala | Tempo | Acumulado |
| --- | --- | --- | --- | --- |
| 1 | Contexto e problema | Breno | 0:50 | 0:50 |
| 2 | Produto e solução | Wingrid | 0:50 | 1:40 |
| 3 | Aplicação e técnicas de IA | Vitor | 1:05 | 2:45 |
| 4 | Principais desafios | Samara | 0:55 | 3:40 |
| 5 | Conclusão e resultados | Jhessica | 1:00 | 4:40 |

Folga de 20 s para abertura e transições. Cerca de 130 palavras por minuto:
cada fala abaixo foi escrita para caber no tempo lido sem pressa.

## 1. Contexto e problema — Breno (0:50)

**Tela:** rosto de quem fala; depois, um print de mensagem de saúde falsa no
WhatsApp.

> Somos o grupo 04 do Challenge 1, e este é o nosso projeto, a Dona Checa.
> Todo dia chega no WhatsApp da família alguma mensagem de saúde: um chá que
> cura câncer, uma vacina que altera o DNA. Quem recebe decide em segundos se
> acredita e se repassa. Para checar direito, a gente cronometrou seis casos
> reais: a mediana foi de 22 minutos por mensagem, e o pior caso levou 43.
> Ninguém faz isso para cada mensagem. A pergunta do desafio era: como a IA
> pode ajudar as pessoas a avaliar se uma informação é confiável, sem
> substituir o pensamento crítico delas?

## 2. Produto e solução — Wingrid (0:50)

**Tela:** gravação do chat: termo aceito, mensagem colada, resposta em quatro
blocos, «Ver fontes e detalhes» aberto.

> A Dona Checa é um chat. A pessoa cola a mensagem ou o link que recebeu, sem
> criar conta. Ela responde em quatro blocos curtos: o veredito, o critério
> que sustenta o veredito, o que é fato e o que é opinião na mensagem, e a
> fonte. A nossa regra é: veredito nunca nu. Todo «falso» ou «verdadeiro» vem
> com o motivo e com o link da checagem de uma agência brasileira, que a
> pessoa pode abrir e conferir. E quando não temos checagem que cubra a
> alegação, ela diz «evidência insuficiente» em vez de chutar.

## 3. Aplicação e técnicas de IA — Vitor (1:05)

**Tela:** diagrama das sete etapas; depois, a tabela de recuperação.

> Por trás do chat há sete etapas. Primeiro, uma fronteira separa pedido de
> conduta médica e urgência, que vai direto para orientação profissional.
> Depois, um modelo de linguagem acha a alegação de saúde e separa fato de
> opinião. A busca é um RAG híbrido: BM25 com um modelo de embeddings
> multilíngue, sobre mais de seis mil checagens de agências brasileiras. Uma
> guarda em código impede veredito sem trecho que o sustente, e a resposta
> passa por quatro conferências antes de sair. Uma decisão importante: não
> treinamos nenhum classificador de veredito. Ele seria opaco e ficaria
> velho. Com RAG, cada resposta aponta a checagem que a sustenta.

## 4. Principais desafios — Samara (0:55)

**Tela:** exemplo de texto com acento corrompido; depois, gráfico de latência
local contra API.

> O primeiro desafio foram os dados. Duas das bases públicas tinham o texto
> estragado: uma perdeu as letras maiúsculas acentuadas, a outra foi
> lematizada. Auditamos tudo, e só uma base ficou citável. O segundo foi a
> segurança: numa sonda, o modelo disse «falso» antes de avisar que parar a
> quimioterapia é perigoso. Por isso a fronteira clínica virou uma etapa
> própria. O terceiro foi a latência: o modelo local levava cerca de 100
> segundos por mensagem. Passamos para uma API, com termo de consentimento e
> remoção de dados pessoais antes do envio.

## 5. Conclusão e resultados — Jhessica (1:00)

**Tela:** tabela da rodada da demo; depois, o grupo todo e os links.

> Nos resultados, a busca acha a checagem certa entre as cinco primeiras em
> 20 de 20 consultas reais. Na bancada de ponta a ponta, 29 de 30 casos
> passaram, sem nenhuma falha grave. A verificação completa leva cerca de 14
> segundos, contra 22 minutos à mão, a menos de um centavo de dólar por
> mensagem. Testamos com duas pessoas: elas acertaram tudo, com e sem a
> ferramenta. Com duas pessoas isso valida o método, não prova o efeito. O
> próximo passo é testar com 20 a 30. A Dona Checa não pensa pela pessoa: ela
> mostra o critério e a fonte, para a pessoa decidir. Obrigado!

## Gravação e publicação

- Cada integrante grava a própria fala; a edição junta na ordem acima.
- Conferir a duração final: até 5:00.
- Publicar no YouTube como «Não listado» ou «Público», conforme a
  coordenação pedir.
- Colocar o link no `README.md` e nesta página (task 7.6).

**Link do vídeo:** pendente.
