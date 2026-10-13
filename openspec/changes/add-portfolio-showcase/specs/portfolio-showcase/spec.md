# Delta para portfolio-showcase

## ADDED Requirements

### Requirement: Estado datado e conferível

O portfólio SHALL declarar no topo de `docs/estado.md` e de
`docs/pendencias.md` a data da atualização. As contagens de tasks MUST
coincidir com os `tasks.md` de `origin/main` nessa data.

#### Scenario: Conferência das contagens
- **GIVEN** a data declarada no topo de `docs/estado.md`
- **WHEN** alguém conta `- [x]` e `- [ ]` nos `tasks.md` da `main` nessa data
- **THEN** o total bate com o declarado no site

### Requirement: Protótipo e avaliação em página própria

O portfólio SHALL ter uma página que descreve o fluxo do protótipo, os modelos
usados e os resultados da avaliação. Cada resultado MUST citar o arquivo, a
rodada ou o notebook de origem.

#### Scenario: Leitura de um número
- **GIVEN** a página `docs/act/prototipo-avaliacao.md`
- **WHEN** o leitor procura a origem de um número de recuperação ou de bancada
- **THEN** encontra o arquivo, a rodada ou o notebook que o produziu

### Requirement: Limitações declaradas

O portfólio SHALL listar as limitações conhecidas do protótipo e MUST
declarar que o protocolo do comitê de ética é simulado para fins acadêmicos.

#### Scenario: Leitura das limitações
- **WHEN** o leitor abre `docs/pendencias.md`
- **THEN** encontra a seção de limitações conhecidas do protótipo
- **AND** encontra o aviso de que o CEP é simulado

### Requirement: Site publicável sem aviso

O site SHALL construir com `mkdocs build` sem aviso de página ausente da nav
nem de link interno quebrado.

#### Scenario: Build
- **WHEN** `mkdocs build` roda sobre a `main`
- **THEN** a saída não traz `WARNING`

### Requirement: Versão da demonstração fixada

A demonstração da apresentação SHALL rodar do commit da `main` marcado pela
tag `showcase-demo`. Ela MUST NOT rodar de branch com change não integrado à
`main`.

#### Scenario: Checkout para a demo
- **GIVEN** a tag `showcase-demo` criada depois do ensaio
- **WHEN** quem apresenta prepara a máquina da demo
- **THEN** faz checkout da tag
- **AND** o commit da tag está contido na `main`

### Requirement: Roteiro de demonstração

O portfólio SHALL ter um roteiro de demo com preparação, aquecimento, casos e
plano B. Cada caso do roteiro MUST ter passado na rodada da bancada registrada
para a versão da demo.

#### Scenario: Escolha de um caso
- **GIVEN** um caso listado no roteiro
- **WHEN** o leitor procura o caso na tabela da rodada da bancada da demo
- **THEN** encontra o caso marcado como aprovado

#### Scenario: Aquecimento antes da plateia
- **WHEN** quem apresenta segue o roteiro
- **THEN** espera `/saude` responder 200 e faz uma consulta descartável antes
  de abrir o chat para a plateia

### Requirement: Números da bancada versionados

O portfólio SHALL publicar uma tabela da rodada da bancada usada na demo, com
data e hora da rodada, gerador, casos aprovados, acerto por etapa, latência e
custo. A tabela MUST nomear o arquivo de relatório de origem.

#### Scenario: Número da bancada nos slides
- **WHEN** um slide cita um número da bancada
- **THEN** o número está na tabela versionada
- **AND** a tabela nomeia o relatório de origem

### Requirement: Porta de entrada do repositório

O `README.md` SHALL apontar para o portfólio publicado, mapear os quatro
entregáveis finais, dizer como subir a demo e onde estão os changes.

#### Scenario: Avaliador abre o repositório
- **WHEN** alguém abre a página inicial do repositório
- **THEN** encontra o link do portfólio e o caminho de cada entregável final
