# Tasks — add-engage-desinformacao-saude

Vigência: 08/09 a 11/09.

## 1. Preparação

- [x] 1.1 Selecionar 4 a 6 casos brasileiros de desinformação em saúde,
      cobrindo pelo menos 3 tipos distintos de manipulação — seis casos, quatro
      tipos, em `docs/engage/casos-forense.md`. Todos sobre vacinação, cinco dos
      seis fora do covid. Lacuna registrada: distorção estatística não coberta
- [x] 1.2 Criar o template da ficha de caso conforme
      `specs/pesquisa-investigativa/spec.md` — `docs/engage/ficha-de-caso.md`,
      com os oito campos exigidos e o checklist de fechamento
- [x] 1.3 Preparar o board com os cinco quadros efetivamente usados: Problema,
      Público, Específicas, Solução e Sucesso —
      `docs/engage/board-brainstorming.md`, com as três regras de condução e o
      procedimento de derivação das GQ

## 2. Investigação forense

- [ ] 2.1 Distribuir os casos entre os integrantes, um caso por pessoa no mínimo
- [ ] 2.2 Analisar cada caso aplicando leitura lateral, registrando o tempo gasto
- [ ] 2.3 Preencher uma ficha por caso, com fontes rastreáveis
- [ ] 2.4 Consolidar os tempos medidos como evidência para o quadro Problema

## 3. Sessão de brainstorming (~90 min)

- [ ] 3.1 Rodar os quadros Problema, Público e Sucesso em modo privado antes de
      abrir a discussão
- [ ] 3.2 Preencher o quadro Solução apenas como hipóteses, sem decidir
- [ ] 3.3 Plotar guiding questions (não soluções) na matriz impacto × incerteza

## 4. Matriz de confiança

- [ ] 4.1 Card sorting dos sinais que cada integrante usa na prática
- [ ] 4.2 Consolidar em dimensões, cada uma com sinal observável, papel da IA e
      limite
- [ ] 4.3 Escrever a rubrica de três níveis por dimensão
- [ ] 4.4 Testar a matriz contra os casos da forense e remover dimensões que não
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

- [ ] 7.1 Consolidar o portfólio de pesquisa (fichas + método + datasets)
- [ ] 7.2 Consolidar a matriz de confiança versão 1
- [x] 7.3 Rodar `openspec validate add-engage-desinformacao-saude --strict` — limpo em 20/09/2026
- [ ] 7.4 Abrir `add-instrumento-avaliacao-ptbr` para a fase Investigate
