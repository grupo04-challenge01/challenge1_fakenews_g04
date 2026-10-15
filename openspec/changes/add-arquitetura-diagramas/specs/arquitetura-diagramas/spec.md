# Delta para arquitetura-diagramas

## ADDED Requirements

### Requirement: Arquitetura em diagramas versionados

O portfólio SHALL ter a página `docs/arquitetura.md` com diagramas de
contexto, contêineres, fluxo das etapas, sequência da verificação,
recuperação, dados e implantação. Os diagramas MUST ser escritos em Mermaid
dentro do Markdown, não como imagem exportada.

#### Scenario: Leitura da arquitetura
- **WHEN** o leitor abre a página de arquitetura no site publicado
- **THEN** vê os diagramas renderizados
- **AND** cada diagrama tem no máximo um parágrafo curto de legenda

### Requirement: Diagrama conferível contra o código

Cada diagrama SHALL citar os arquivos de onde saiu. Componente, número ou
limiar que aparece no diagrama MUST existir no código ou no manifesto citado.

#### Scenario: Conferência de um limiar
- **GIVEN** o limiar de evidência mostrado no diagrama de recuperação
- **WHEN** alguém abre o arquivo citado abaixo do diagrama
- **THEN** encontra o mesmo valor no código

### Requirement: Slides com diagrama

Os slides de solução, de IA e de resultados em
`docs/showcase/apresentacao.md` SHALL ter um diagrama como conteúdo principal
e MUST NOT passar de três frases de apoio.

#### Scenario: Slide de IA
- **WHEN** o grupo monta o slide «Como a IA trabalha»
- **THEN** o conteúdo principal é o diagrama do fluxo
- **AND** o texto de apoio tem no máximo três frases
