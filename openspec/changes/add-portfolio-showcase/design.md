# Design: Portfólio atualizado para o Showcase

## Context

Motivação em `proposal.md`. Fontes dos números: `tasks.md` de cada change em
`origin/main`, `openspec validate --all --strict`, `pytest`, os `design.md`
dos changes do Act (rodadas da bancada), `exploracao/avaliacao_modelo.ipynb`,
`prototipo/relatorio_sonda_*.json`, `prototipo/indice/manifesto.json` e
`datasets/relatorios_mvp_copiloto/relatorios_metricas.json`.

## Goals / Non-Goals

**Goals:**

- Quem abre o site sabe em um minuto o que existe, o que falta e o que foi
  medido.
- Todo número do site aponta para o arquivo de onde saiu.

**Non-Goals:**

- Reexecutar a bancada ou as sondas. O site cita rodadas já registradas.
- Reescrever as páginas das fases Engage e Investigate, que seguem corretas.

## Decisions

### D1. Histórico preservado, não apagado

O texto de `estado.md` até 01/10 vira a seção «Histórico», com os títulos
rebaixados um nível. Ele registra achados que não estão em outro lugar, como o
caso 05 reclassificado e o `ALFA_PADRAO` de 0,5.

Alternativa descartada: apagar e deixar a história no `git log`. Quem lê o
site não lê o `git log`.

### D2. Uma página para o protótipo, separada do guia do chat

`docs/interface/chat-web.md` ensina a subir o chat. A página nova explica o
que o protótipo faz e o que foi medido. Misturar as duas deixaria o guia
operacional longo demais para quem só quer subir o servidor.

### D3. Limitações e simulação declaradas no site

O site declara que o protocolo do CEP e a emenda 01 são simulados, como o
próprio dossiê declara, e lista o que o protótipo não faz. A métrica primária
é ganho de discernimento, e o piloto tem n = 2. Apresentar o resultado sem
esses limites seria veredito nu sobre o próprio projeto.

### D4. Piloto confirmado pelo grupo

As duas sessões de 08/10/2026 contam como o piloto da task 6.6 do MVP, por
confirmação do grupo em 13/10/2026. O site registra o resultado com a ressalva
de n = 2, que o notebook de avaliação já fazia.

### D5. A demo roda da `main`, marcada por tag

A demonstração de 16/10 roda de um commit da `main`, marcado pela tag
`showcase-demo`. A tag é criada depois do merge do `fix-*` de 14/10 e do ensaio
de 15/10, no commit ensaiado. Quem apresenta faz checkout da tag, não de um
branch.

O branch `act-cobertura-alegacao-ampla` fica fora. O change dele está
bloqueado pelo caso jacaré, e o branch liga a cobertura ampla por padrão
(`DONA_CHECA_COBERTURA_AMPLA`, padrão `sim` em `interface/config.py`). A
`main` não tem essa variável, então a demo usa a regra conservadora sem
configuração extra. O merge do branch fica suspenso até depois da
apresentação.

Alternativa descartada: demo pelo branch com a variável em `nao`. Depende de
quem apresenta lembrar da variável, e o código do branch não passou pela
suíte nem pelo `validate --strict` da task 8.2 dele.

### D6. Nenhum change arquivado antes da apresentação

O chat lê textos de specs em tempo de execução. Os caminhos apontam para
`openspec/changes/<change>/specs/...`, com recuo para `openspec/specs/` só na
spec base. As sobreposições existem só nos changes: `SOBREPOSICAO` em
`interface/fluxo.py` e em `prototipo/verificacao/fronteira.py`.
`prototipo/identidade/__init__.py` e `prototipo/entrada/leitura.py` também leem
do change, com o mesmo recuo.

Arquivar move a pasta do change para `openspec/changes/archive/`, e a subida
do servidor nesse estado nunca foi testada. Até a apresentação de 16/10,
ninguém roda `/opsx:archive` nem `openspec archive`. Depois dela, o
arquivamento segue a ordem de `docs/pendencias.md`, e antes dele o código
passa a ler de `openspec/specs/`.

### D7. Roteiro de demo com aquecimento e casos da bancada

O roteiro fixa:

- **Preparação:** checkout da tag, `.env` conferido, porta livre (a 8000
  conflita com `mkdocs serve`), saldo da conta da API conferido na véspera.
- **Aquecimento:** esperar `/saude` responder 200. A carga do índice roda numa
  thread, e se ela falhar o servidor segue no ar com `/saude` em 503. Depois,
  uma consulta descartável, porque o modelo denso só carrega na primeira.
- **Casos:** só casos que passaram na rodada da bancada da tag, cobrindo
  veredito com fonte, link, fronteira e evidência insuficiente.
- **Gerador:** DeepSeek. O cliente Ollama não tem timeout.
- **Plano B:** vídeo gravado no ensaio e rede alternativa.

### D8. Números da bancada versionados em tabela

`bancada/relatorios/` está no `.gitignore`. A rodada usada na demo vira uma
tabela no portfólio, com data e hora da rodada, gerador, casos aprovados,
acerto por etapa, latência e custo. O JSON bruto segue fora do git.

### D9. Mapa da arquitetura como página autônoma no mesmo site

O mapa da arquitetura é um HTML autocontido, com CSS e JS no próprio arquivo e
só as fontes vindas do Google Fonts. O layout é de tela inteira, com navegação
própria. Ele fica em `docs/arquitetura/index.html`. O MkDocs copia arquivos que
não são Markdown sem passar pelo tema, então o mesmo `deploy.yml` publica o
mapa em `<site>/arquitetura/`, sem o cabeçalho nem o menu do Material. A nav
do Showcase ganha uma entrada que aponta para ele.

Cada card do mapa cita os arquivos de onde saiu. O mapa só é publicado quando
todo caminho citado existe na `main`. Citação de arquivo inexistente sai do
card, em vez de ficar à espera de uma página que ninguém assumiu.

Alternativas descartadas:

- Repositório ou GitHub Pages separado: duplica deploy e endereço sem ganho.
- Página `.md` com `iframe`: herda a largura do tema e perde a tela cheia do
  mapa.
- Commit direto no branch `gh-pages`: o `mkdocs gh-deploy --force` reescreve
  o branch a cada push, e o arquivo sumiria.

## Risks / Trade-offs

- [O site envelhece de novo até 16/10] → a data de atualização fica no topo de
  `estado.md` e `pendencias.md`.
- [Número citado diverge da fonte] → cada número no site cita o arquivo ou a
  rodada de origem.
- [Alguém arquiva um change ou faz merge do branch amplo antes de 16/10] → D5
  e D6 também vão para `docs/pendencias.md` e são combinados com o grupo.
- [A rodada da tag falha num caso do roteiro] → o roteiro troca o caso por
  outro que passou na mesma rodada, sem mudar a regra para o caso passar.
- [O mapa envelhece em relação ao código] → cada card cita o arquivo de
  origem, e a verificação da seção 7 confere que todo caminho citado existe.
