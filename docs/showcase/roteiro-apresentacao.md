# Roteiro da apresentação

Roteiro da apresentação de 16/10/2026 para a banca: 10 minutos, sem slides.
O grupo mostra o produto funcionando e o
[mapa da arquitetura](../mapa/arquitetura.html). Change
`add-portfolio-showcase`, decisão D15. Os números são os mesmos dos slides:
só os da [rodada da demo](../act/prototipo-avaliacao.md#rodada-da-demo) e das
páginas do portfólio.

!!! note "A ordem da coordenação continua valendo"
    O pedido é problema → solução → IA → demonstração → resultados. Sem
    slides, a tela alterna entre duas abas: o **chat** da Dona Checa e o
    **mapa** da arquitetura. São quatro trocas de aba, e cada bloco tem uma
    tela só.

## Visão geral

| # | Bloco | Quem fala | Tela | Tempo | Acumulado |
| --- | --- | --- | --- | --- | --- |
| 1 | Problema | Breno | Chat, só a abertura | 1:15 | 1:15 |
| 2 | Solução | Wingrid | Chat: termo e campo | 1:00 | 2:15 |
| 3 | IA | Vitor | Mapa: fluxo «Na linha da verificação» | 2:15 | 4:30 |
| 4 | Demonstração | Jhessica | Chat: casos 1, 4 e 5 | 3:00 | 7:30 |
| 5 | Resultados | Samara | Mapa: faixa 07 e fluxo «Dados e avaliação» | 1:30 | 9:00 |
| 6 | Valor e fechamento | Breno | Mapa: «Ver tudo» | 0:35 | 9:35 |

Folga: 25 s. **Operador:** Wingrid fica no teclado do começo ao fim, para
ninguém perder tempo trocando de lugar. Quem fala aponta, Wingrid clica. A
divisão segue os donos de cada assunto em [Organização e papéis](organizacao.md);
o grupo pode trocar as falas, desde que todos falem.

## Preparação (30 min antes)

1. Subir o chat e aquecer o índice, como no [roteiro da demo](roteiro-demo.md#preparacao-30-min-antes).
2. Abrir **duas abas** no mesmo navegador, nesta ordem:
    - aba 1: `http://127.0.0.1:8000`, recarregada, com o termo ainda não aceito;
    - aba 2: o mapa, pelo portfólio publicado ou pelo arquivo
      `docs/mapa/arquitetura.html`. Clicar em **Ver tudo**.
3. Trocar de aba com `Cmd+1` e `Cmd+2`. No mapa, durante um fluxo guiado,
   `→` avança e `←` volta.
4. Zoom do navegador em 125% nas duas abas, para a última fileira ler.
5. Mensagens dos casos 1, 4 e 5 num bloco de notas fora da tela projetada,
   prontas para copiar.
6. Vídeo de backup aberto numa terceira aba, pausado no início da demo.

## 1. Problema — Breno (1:15)

**Tela:** aba 1, chat recém-aberto, com a abertura da Dona Checa e o termo.

> Boa tarde. Somos o grupo 04, e esta é a Dona Checa.
>
> Todo dia chega no WhatsApp da família uma mensagem de saúde: um chá que
> cura a dengue, uma vacina que altera o DNA. Quem recebe decide em segundos
> se acredita e se repassa.
>
> Para saber quanto custa checar direito, a gente cronometrou seis casos
> reais: a mediana foi de 22 minutos por mensagem, e o pior levou 43.
> Ninguém faz isso para cada mensagem.
>
> A pergunta do desafio era: como a IA pode ajudar as pessoas a avaliar se
> uma informação é confiável, sem substituir o pensamento crítico delas? Um
> selo de «falso» sem motivo não ensina nada: a pessoa cai no próximo boato.
> Esconder a conclusão também não ajuda, porque devolve os 22 minutos para
> quem não tem tempo.

## 2. Solução — Wingrid (1:00)

**Tela:** aba 1. Ler o termo em uma frase e **aceitar ao vivo**. Mostrar o
campo vazio.

> A nossa resposta é um chat. A pessoa cola a mensagem ou o link que
> recebeu, sem criar conta.
>
> Antes, ela aceita este termo: o texto vai para um modelo de linguagem
> externo, mas sem e-mail, CPF e telefone, que o servidor tira antes.
>
> A Dona Checa responde em quatro blocos curtos: o veredito, o que se sabe,
> por que a mensagem engana e o que observar da próxima vez. A regra do
> projeto é **veredito nunca nu**: todo «falso» ou «verdadeiro» vem com o
> critério e com o link da checagem de uma agência brasileira. E quando não
> há checagem que cubra a alegação, ela diz «evidência insuficiente» em vez
> de chutar.
>
> Como ela chega nisso? O Vitor mostra.

**Ação:** `Cmd+2`. No mapa, abrir o fluxo guiado **02 · Na linha da
verificação**.

## 3. IA — Vitor (2:15)

**Tela:** aba 2, fluxo «Na linha da verificação», um passo por estação. O
balão da Dona Checa já resume cada estação; a fala completa o balão, sem
ler o balão em voz alta.

| Passo | Estação | Fala | Tempo |
| --- | --- | --- | --- |
| 1 | Fronteira | Antes de checar, uma fronteira: urgência e sofrimento psíquico saem por este ramal, direto para SAMU ou CVV. Saúde tem casos em que checar é o passo errado. | 0:20 |
| 2 | Leitura | Se a pessoa só colou um link, a página é lida com proteção: o servidor não acessa a rede interna. | 0:15 |
| 3 | Extração | Um modelo de linguagem lista as alegações de saúde, e o código escolhe a de maior risco. | 0:15 |
| 4 | Decomposição | O modelo separa fato de opinião, que vai para o segundo bloco. | 0:10 |
| 5 | Recuperação | Aqui está o RAG: BM25 e um modelo de embeddings multilíngue, combinados, sobre 6.279 checagens de agências brasileiras. | 0:25 |
| 6 | Guarda | Este é o ponto da tese. Sem trecho com escore acima de 0,55, o modelo nem é chamado para classificar: a resposta é «evidência insuficiente». O veredito sai de uma checagem que a pessoa pode abrir, não da memória do modelo. | 0:30 |
| 7 | Resposta | O código escreve o veredito, e cada frase dos blocos tem de estar ancorada num trecho. Frase sem base é cortada antes de sair. | 0:20 |

> Não treinamos nenhum classificador de veredito: o dataset é acervo para
> citar. O gerador é o DeepSeek, por API, porque o modelo local levava mais de
> um minuto e meio por mensagem. Vamos ver funcionando.

**Ação:** `Esc` para sair do fluxo, `Cmd+1`.

## 4. Demonstração — Jhessica (3:00)

**Tela:** aba 1. Wingrid cola, Jhessica narra. Casos do
[roteiro da demo](roteiro-demo.md#casos).

| Caso | O que mostrar | Fala de apoio | Tempo |
| --- | --- | --- | --- |
| 1 · inhame e dengue | Andamento ao vivo; resposta «Falso»; abrir **Ver fontes e detalhes** e apontar agência, data e link | «Enquanto ela confere, a página mostra em que estação está. Veredito: falso. E aqui o que importa: a agência, a data e o link da checagem. A pessoa pode abrir e discordar.» | 1:20 |
| 4 · goiabeira e dengue | Resposta sem veredito | «Esta alegação não está no nosso acervo. Ela não chuta: diz o que procurou e onde a pessoa pode conferir.» | 0:50 |
| 5 · dor no peito | Orientação de urgência imediata | «Dor no peito agora não é caso de checagem. A fronteira manda direto para o SAMU, sem passar pelo modelo.» | 0:40 |
| Transição | — | «E como sabemos que isso funciona fora destes três casos? A Samara mostra.» | 0:10 |

**Ação:** `Cmd+2`. No mapa, clicar na faixa **07 · Dados e avaliação** na
barra lateral.

## 5. Resultados — Samara (1:30)

**Tela:** aba 2, faixa 07. Clicar no card **Rodada da demo**: o painel
lateral mostra os números. Depois, o card **Aferição da recuperação**.

> Medimos em duas camadas. A primeira é a busca: em 20 consultas reais, a
> checagem certa apareceu entre as cinco primeiras em todas, com MRR de
> 0,897. A combinação de BM25 com embeddings ganhou de cada um sozinho.
>
> A segunda é a bancada: 30 casos com o esperado de cada estação, rodando o
> mesmo código do chat. Na rodada da demo, 29 de 30 passaram, sem falha
> grave. A que falhou é de forma: o bloco 2 não separou a opinião.
>
> Todas as dez respostas com evidência trouxeram o link da checagem. A
> verificação completa leva 13,8 segundos de mediana, contra 22 minutos à
> mão, e custa menos de meio centavo de dólar por mensagem.

**Ação:** «Ver tudo» na barra lateral.

## 6. Valor e fechamento — Breno (0:35)

**Tela:** aba 2, mapa inteiro.

> Num piloto com duas pessoas, as duas acertaram depois, sem a ferramenta.
> É pouco para medir efeito, mas valida o instrumento. O próximo passo é uma
> coleta com 20 a 30 pessoas e o acervo atualizado depois de 2021.
>
> A Dona Checa transforma 22 minutos de checagem em segundos, sem tirar da
> pessoa o julgamento: ela vê o critério e a fonte. Este mapa, o código e o
> portfólio estão no nosso repositório. Obrigado.

## Pontos de controle

Quem estiver fora do palco segura o cronômetro e mostra o tempo nestes pontos.

| Marca | Deveria estar em | Se estiver atrasado |
| --- | --- | --- |
| 2:15 | fim da solução | Vitor corta os passos 2 e 4 do fluxo |
| 4:30 | fim da IA | Demo só com os casos 1 e 5 |
| 7:30 | fim da demo | Samara fala só a bancada e o custo |
| 9:00 | fim dos resultados | Breno fala só a última frase |

## Plano B

| Sintoma | Ação |
| --- | --- |
| Chat com erro ou sem rede | Vídeo de backup na aba 3, a partir da demo. A fala do bloco 4 continua igual. |
| Resposta diferente da esperada | Não improvisar: «o modelo varia, e a bancada mede isso», e seguir para o próximo caso. |
| Mapa sem as fontes do Google | Funciona com a fonte do sistema; seguir. |
| Projetor corta as laterais | Zoom do navegador em 110% e «Ver tudo» de novo. |

## Ensaio

- [ ] Rodada 1: cada um lê a própria fala com cronômetro; ajustar o texto de
      quem passar do tempo.
- [ ] Rodada 2: completa, com o chat ao vivo e as trocas de aba, cronometrada
      do «Boa tarde» ao «Obrigado».
- [ ] Rodada 3: completa, simulando uma falha no caso 4 e passando para o
      vídeo de backup.
- [ ] Perguntas: um integrante faz as perguntas da tabela
      [Fora do deck](apresentacao.md#fora-do-deck-pronto-para-perguntas) e
      quem é dono do assunto responde em até 30 s.
