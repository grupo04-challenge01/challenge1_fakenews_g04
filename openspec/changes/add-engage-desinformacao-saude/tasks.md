# Tasks — add-engage-desinformacao-saude

Donos das tasks em aberto: **Jhessica** 4 (bloco 4), **Breno** 3 (2.4, 7.1, 7.2).

Divisão de 24/09/2026, por papel do artigo de MLOps (Kreuzberger et al.,
2023): R1 Breno, R2 Wingrid, R3 modelagem Vitor, R3 avaliação Jhessica,
R4+R6+R7 Samara. O nome em negrito no início de cada task em aberto é o dono
único dela. Task com dois donos é task sem dono.


Vigência: 08/09 a 11/09.

## 1. Preparação

- [x] 1.1 Selecionar 4 a 6 casos brasileiros de desinformação em saúde,
      cobrindo pelo menos 3 tipos distintos de manipulação — seis casos, três
      tipos, em `docs/forense/casos-forense.md`. Todos sobre vacinação, cinco dos
      seis fora do covid. Lacunas registradas: mídia sintética e distorção
      estatística não cobertas (o caso 05 foi reclassificado em 24/09/2026)
- [x] 1.2 Criar o template da ficha de caso conforme
      `specs/pesquisa-investigativa/spec.md` — `docs/forense/ficha-de-caso.md`,
      com os oito campos exigidos e o checklist de fechamento
- [x] 1.3 Preparar o board com os cinco quadros efetivamente usados: Problema,
      Público, Específicas, Solução e Sucesso —
      `docs/engage/board-brainstorming.md`, com as três regras de condução e o
      procedimento de derivação das GQ

## 2. Investigação forense

- [x] 2.1 Distribuir os casos entre os integrantes, um caso por pessoa no mínimo
      — cinco integrantes para seis casos: Samara Letícia (01), Jhessica Evelyn
      (02), Vitor Gonçalves (03), Wingrid Silva (04) e Breno (05 e 06)
- [x] 2.2 Analisar cada caso aplicando leitura lateral, registrando o tempo gasto
      — as seis fichas citam a checagem externa consultada e registram início,
      conclusão e total; tempos de 10, 20, 20, 24, 33 e 43 min
- [x] 2.3 Preencher uma ficha por caso, com fontes rastreáveis — seis fichas em
      `docs/forense/caso-NN-*.md`, oito campos preenchidos em cada, tipo de
      manipulação dentro das cinco categorias da capability
- [ ] 2.4 **Breno** Consolidar os tempos medidos como evidência para o quadro Problema
      — mínimo 10 min, mediana 22 min, máximo 43 min; falta levar os números
      para o quadro Problema em `docs/engage/board-brainstorming.md`

## 3. Sessão de brainstorming (~90 min)

- [x] 3.1 Rodar os quadros Problema e Público em modo privado antes de abrir a
      discussão — Problema (19 notas) e Público (5 notas) transcritos em
      `docs/engage/board-brainstorming.md`, com o modo privado confirmado pelo
      grupo. **Escopo reduzido em 24/09/2026:** o quadro Sucesso saiu da task
      porque nenhuma spec o exige como fonte de notas e as métricas já estão
      fixadas pela restrição de produto e absorvidas por
      `avaliacao-instrumento` — ver a nota de decisão no `design.md`
- [x] 3.2 Preencher o quadro Solução apenas como hipóteses, sem decidir — sete
      notas em `docs/engage/board-brainstorming.md`, quadro Solução (`SO-01` a
      `SO-07`), todas em forma de pergunta ou de lista de suposição. Nenhuma
      decisão registrada no quadro. A única nota que chegou à matriz, `SO-05`,
      chegou como pergunta (GQ-11)
- [x] 3.3 Plotar guiding questions (não soluções) na matriz impacto × incerteza
      — `docs/engage/guiding-questions.md`, seção «Matriz impacto × incerteza»:
      12 GQ plotadas, 4 aberturas (GQ-02, GQ-03, GQ-04, GQ-09) contra o mínimo
      de 3, nenhuma `fechada` ou `descartada` plotada, esforço ausente como eixo

## 4. Matriz de confiança

- [ ] 4.1 **Jhessica** Card sorting dos sinais que cada integrante usa na prática
- [ ] 4.2 **Jhessica** Consolidar em dimensões, cada uma com sinal observável, papel da IA e
      limite
- [ ] 4.3 **Jhessica** Escrever a rubrica de três níveis por dimensão
- [ ] 4.4 **Jhessica** Testar a matriz contra os casos da forense e remover dimensões que não
      discriminam nenhum caso

## 5. Guiding questions

- [x] 5.1 Derivar uma GQ por agrupamento de notas dos quadros
- [x] 5.2 Aplicar o critério de qualidade e descartar as que não passam
- [x] 5.2b Classificar cada GQ em `dados` / `literatura` / `usuario` /
      `fechada` / `descartada`, nomeando o arquivo derivado nas de `dados`
- [x] 5.3 Priorizar e marcar as 3 que abrem a fase Investigate

## 6. Exploração de datasets

- [x] 6.1 Verificar disponibilidade e licença de cada dataset candidato, com o
      link aberto e conferido — as nove bases do pacote têm licença conferida na
      fonte em `FONTES.md`. Duas lacunas fechadas em 20/09/2026: FakeHealth é
      **CC BY 4.0** (Zenodo `10.5281/zenodo.3606757`), e o **InSciOut não
      declara licença** no repositório dos autores, o que o levou às pendências
      junto do PUBHEALTH
- [x] 6.2 Classificar cada dataset por função: raciocínio, comparação
      fonte-manchete, ou banco de estímulos — as quatro seções de
      `datasets/README.md`, uma por função, com cada base sob a sua. **Achado:
      as três funções nomeadas na task não bastam.** O acervo de circulação não
      cabe em nenhuma — ele mede o que circulou, não o mérito —, e virou a
      quarta função, registrada como tal
- [x] 6.3 Registrar caveats por dataset, incluindo os descartados com motivo —
      `FONTES.md` e a seção «Caveats do tratamento» de `datasets/README.md`. Os
      descartados constam com motivo: Med-MMHL (4,0 GB, quase tudo imagem, uso
      condicional), FakeRecogna v1 (substituída), FACTCK.BR e FakeRecogna 2.0
      (reprovadas para citação, por razões diferentes)

## 7. Fechamento

- [ ] 7.1 **Breno** Consolidar o portfólio de pesquisa (fichas + método + datasets)
- [ ] 7.2 **Breno** Consolidar a matriz de confiança versão 1
- [x] 7.3 Rodar `openspec validate add-engage-desinformacao-saude --strict` — limpo em 20/09/2026
- [x] 7.4 ~~Abrir `add-instrumento-avaliacao-ptbr` para a fase Investigate~~ —
      **decidido em 20/09/2026: o change não será aberto.** A capability
      `avaliacao-instrumento` de `mvp-copiloto-verificacao` já cobre o escopo
      inteiro nos seus quatro requirements, e o material de estímulo já foi
      entregue pelo Investigate. Escopo preservado, rastreamento realocado —
      ver a nota de decisão no `design.md`
