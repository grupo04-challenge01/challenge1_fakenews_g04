# Tasks pendentes

**Atualizado em 13/10/2026**, a partir dos `tasks.md` de `origin/main` e do
branch `act-cobertura-alegacao-ampla`. Companheiro de
[Estado do projeto](estado.md), que conta o que já foi entregue; esta página
conta o que falta.

## Resumo

| Change | Fase | Feitas | Pendentes |
| --- | --- | --- | --- |
| `add-tratamento-datasets-ptbr` | Investigate | 34 | **1** |
| `mvp-copiloto-verificacao` | Act | 30 | **1** |
| 13 outros changes na `main` | Engage a Act | 283 | **0** ✅ |
| **total na `main`** | | **347** | **2** |
| `add-cobertura-alegacao-ampla` (fora da `main`) | Act | 13 | **5**, bloqueado |
| Showcase | Showcase | — | *nenhum change existe* |

Em 01/10 eram 23 pendentes em 6 changes. Entre 02/10 e 09/10 fecharam 21
delas, e nove changes novos abriram e fecharam no Act.

## As duas tasks abertas na `main`

| Change | # | Task | Bloqueio | Dono |
| --- | --- | --- | --- | --- |
| `add-tratamento-datasets-ptbr` | 5.4 | Validar a rubrica contra casos brasileiros e remover o que não discrimina | anotação humana dos casos | Jhessica |
| `mvp-copiloto-verificacao` | 6.6 | Rodar piloto com 2 participantes antes da coleta | nenhum no repositório | Breno |

**Sobre a 5.4.** O instrumento está entregue: seis critérios com rubrica de três
níveis e cinco remoções com motivo. Falta a validação empírica. O proxy
automático foi medido e reprovado: sob qualquer piso único, ele removeria
`alarme` e `linguagem`, os dois critérios mais relevantes para desinformação.

**Sobre a 6.6.** A 6.4 (protocolo ético) e a 6.5 (instrumento de coleta)
fecharam em 06/10, então nada no repositório impede o piloto. Em 08/10 entrou
um registro de duas sessões em
`datasets/relatorios_mvp_copiloto/relatorios_metricas.json`, com 4 de 4 em
discernimento e em transferência. A task segue desmarcada. O grupo precisa
decidir se essas sessões contam como o piloto. Com n = 2, o notebook de
avaliação registra que elas não sustentam conclusão sobre efeito.

!!! warning "O CEP é simulado"
    O dossiê da 6.4 e a emenda 01 declaram ser **registros simulados para fins
    acadêmicos**. Nenhum comitê de ética real aprovou o protocolo. Teste com
    pessoas fora do grupo precisa levar isso em conta.

## `add-cobertura-alegacao-ampla` — bloqueado

Branch `act-cobertura-alegacao-ampla`, sem PR. Bloqueado por decisão do grupo
em 13/10/2026.

| # | Task | Situação |
| --- | --- | --- |
| 7.2 | Sonda com o Gemma local, 3 rodadas | rodada feita; jacaré 0 de 3, aceite não cumprido |
| 7.3 | Sonda com o gerador remoto | rodada feita; jacaré 0 de 3, aceite não cumprido |
| 7.4 | Casos novos na bancada (jacaré e autismo vs DNA) | casos e gravações no branch; jacaré falha pela implicação |
| 8.1 | Ponta a ponta no chat, modos `uso` e `piloto` | depende do jacaré passar |
| 8.2 | Suíte verde e `openspec validate --strict` limpo | não conferida no branch |

O que trava é a sexta trava da guarda: um modelo confirma se a alegação nova
implica a checada. Gemma e DeepSeek responderam «não» para jacaré ⇒ DNA em
todas as variantes testadas. Os casos negativos não tiveram falso positivo.

O grupo precisa escolher um caminho:

- **Deixar fora da entrega**, com o achado registrado. A regra conservadora já
  está em vigor na `main`.
- **Rever a spec**: aceitar outra forma de confirmar a implicação, ou tirar o
  jacaré dos cenários. Exige mudar o change, não o código.

## Arquivamento

Nenhum change foi arquivado, e a definição de pronto do projeto pede specs em
`openspec/specs/` quando a fase encerra. Hoje lá está só `frescor-corpus`.
`openspec/specs/01-engage-problem.md` está vazio (0 bytes).

A ordem importa. Sete changes modificam specs que só existem em outros changes
ainda não arquivados: `acessibilidade-leitura`, `resposta-formativa`,
`fronteira-orientacao-saude`, `interface-chat-web` e `verificacao-alegacao`.
O `openspec validate` avisa que o arquivamento recusaria esses deltas fora de
ordem. A ordem segura:

1. Engage e Investigate: `add-engage-desinformacao-saude`,
   `add-ampliacao-corpus-ptbr`, `add-selecao-modelos-arquitetura-rag`,
   `add-tratamento-datasets-ptbr` (depois da 5.4).
2. `mvp-copiloto-verificacao` (depois da 6.6), que cria as specs de produto.
3. `add-interface-chat-web` e `add-identidade-dona-checa`.
4. `add-entrada-por-link` (decisão D10 dele) e `add-gerador-api-deepseek`.
5. Os `fix-*` e `add-notebook-avaliacao-modelo`.

## Showcase — nenhum change existe

Estamos na semana 6 (12 a 16/10). A metodologia pede um change por fase, e o
Showcase não tem. Os entregáveis «apresentação» e «reflexão» não têm task no
repositório.

| Entregável final | Situação |
| --- | --- |
| Portfólio de pesquisa | este site; atualizado em 13/10 |
| Estrutura de avaliação de confiança | [matriz de confiança](engage/kit-matriz-confianca.md), versão 1 |
| Solução/protótipo com suporte de IA | [protótipo](act/prototipo-avaliacao.md) funcionando, bancada em 28 de 30 |
| Apresentação e reflexão | **sem change e sem task** |

## Decisões em aberto

Nenhuma bloqueia o protótipo. Todas aparecem se alguém perguntar na
apresentação.

| # | Decisão | Situação |
| --- | --- | --- |
| 1 | Destino de `enganoso` (218) e `impreciso` (64) no mapa de veredito | marcados «a confirmar pelo grupo» |
| 2 | «Identificar vieses»: requisito ou *Out of Scope*? | cobertura parcial, ver abaixo |
| 3 | `add-cobertura-alegacao-ampla`: fora da entrega ou spec revista? | bloqueado em 13/10 |
| 4 | As duas sessões de 08/10 contam como o piloto da 6.6? | task desmarcada |

**Sobre «identificar vieses».** É uma das três competências da Essential
Question. A cobertura é parcial: `acervo-circulacao` trata procedência e
alcance, e o critério `conflito_de_interesse` da rubrica trata quem publicou e
o que ganha com isso. O **viés de confirmação de quem lê** segue sem
capability. É a face mais próxima da métrica primária do projeto, o ganho de
discernimento do usuário.

## Limitações conhecidas do protótipo

Achados da bancada e das sondas, para a apresentação não prometer o que o
protótipo não faz.

- **Pauta fora do acervo.** O corpus de checagens com texto integral vai até
  maio de 2021. Para mpox, oropouche, Qdenga e semaglutida, o acervo tem zero
  checagens. A resposta é «evidência insuficiente», com ponteiro quando o
  índice de checagens recentes acha algo.
- **Fontes oficiais fora do fluxo.** A lista da task 1.3
  (`prototipo/indice/fontes_oficiais.json`) existe, mas o fluxo ainda não a usa.
- **Lacuna detectada pelo caso, não pelo sistema.** O pipeline ainda não detecta
  sozinho a lacuna de acervo. Na bancada, ela vem do caso.
- **Variação exagerada de alegação checada.** Ver o bloqueio acima: o jacaré
  recebe «evidência insuficiente».
- **Dois casos da bancada com falha de forma** (`R3` e `L01`), nenhuma
  eliminatória.
- **Texto curto junto com link.** A fronteira por modelo erra com frases como
  «Olha isso que saiu:», e as regras classificam certo.
- **Ficção lida como alegação.** Numa crítica de filme, a extração tomou a fala
  de uma personagem como alegação de saúde.

## Onde estamos no cronograma

| Semana | Fase | Datas | Situação |
| --- | --- | --- | --- |
| 1 | Engage | 07/09 a 11/09 | encerrada, 25 de 25 |
| 2–3 | Investigate | 14/09 a 25/09 | encerrada, 135 de 136 |
| 4–5 | Act | 28/09 a 09/10 | encerrada, 187 de 188 na `main` |
| **6** | **Showcase** | **12/10 a 16/10** | **em curso, sem change** |

As contagens por fase somam os changes de cada uma: Investigate inclui
`fix-resposta-sem-evidencia`; o Act soma o MVP e os nove changes abertos
nele.
