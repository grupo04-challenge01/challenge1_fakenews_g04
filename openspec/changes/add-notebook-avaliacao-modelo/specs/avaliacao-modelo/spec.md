# Delta para avaliacao-modelo

## ADDED Requirements

### Requirement: Avaliação reprodutível da recuperação

O repositório SHALL ter um notebook que carrega o índice de recuperação e
recalcula Recall@1, Recall@3, Recall@5, Recall@10, MRR e latência mediana das
configurações léxica, densa e híbrida sobre o conjunto de aferição, usando as
mesmas funções da CLI. O notebook MUST NOT sobrescrever as medições versionadas.

#### Scenario: Índice presente
- **GIVEN** o índice construído por `python -m prototipo.rag construir`
- **WHEN** o notebook é executado do início ao fim
- **THEN** as métricas recalculadas aparecem ao lado das versionadas
- **AND** nenhum arquivo versionado é modificado

#### Scenario: Índice ausente
- **GIVEN** uma máquina sem `densa.npy`
- **WHEN** a célula de carga roda
- **THEN** a execução para com a instrução de construir o índice

### Requirement: Consolidação das métricas de entrega

O notebook SHALL reunir, a partir de arquivos versionados, as métricas de
preparação de dados, das sondas do gerador e do estudo piloto, cada uma com o
arquivo de origem indicado.

#### Scenario: Leitura das sondas
- **WHEN** a seção de sondas roda
- **THEN** cada sonda mostra tentativas aprovadas sobre tentativas totais e o arquivo de origem
