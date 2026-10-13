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
