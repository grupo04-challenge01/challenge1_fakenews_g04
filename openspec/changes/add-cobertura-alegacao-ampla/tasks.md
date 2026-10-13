# Tasks: Veredito por cobertura de alegação mais ampla

TDD em toda task de código: primeiro o teste falhando, depois a implementação.
Verificação padrão das tasks de código: `pytest` do módulo verde.

## 1. Classificação declara a cobertura (D1)

- [x] 1.1 `classificacao.defeitos` e `interpretar`: `cobertura` obrigatória
      fora de `evidência insuficiente`; `ponte` e `sujeito` obrigatórios com
      `ampla`. `Classificacao` ganha os três campos. Verificar com testes em
      `prototipo/verificacao/tests/test_classificacao.py` para saída válida e
      para cada defeito.
- [x] 1.2 Prompt `SISTEMA` com a regra da alegação mais ampla, a definição de
      `mesma` e G4 como exemplo negativo. Verificar com teste que confere a
      presença das três partes no prompt.

## 2. Travas da guarda (D2, D3)

- [x] 2.1 `Veredito` ganha `cobertura`, `ponte` e `sujeito`; o caminho
      `mesma` não muda. Verificar com os testes atuais de
      `test_guarda.py` verdes, sem alteração.
- [x] 2.2 Travas 1 a 4 (desligada, rótulo, veredito da agência, duas
      agências), com `rebaixado_por` específico. Verificar com um teste por
      trava em `test_guarda.py` e teste da constante de vereditos aceitos
      contra `tratamento/mapa_vereditos.json`.
- [x] 2.3 Trava 5, âncora do sujeito: palavras vazias, `s` final, sujeito vazio
      falha. Verificar com testes: "vacinas da COVID-19" passa no trecho da Lupa
      e falha diante de um trecho de cloroquina.

## 3. Verificação de implicação (D4)

- [x] 3.1 `prototipo/verificacao/implicacao.py` com `confirmar(p, g, chat)`:
      prompt cego (sem ponte, critério ou rótulo); só `sim` confirma; `não`,
      `incerto`, saída inválida e erro do gerador devolvem não confirmado.
      Verificar com `tests/test_implicacao.py` usando chat falso.
- [x] 3.2 Trava 6 na guarda: chama `confirmar` só depois das travas 1 a 5,
      com G = `alegacao` do trecho citado de maior score; registra a resposta
      no `Veredito`. Verificar com teste de que o chat de implicação não é
      chamado quando uma trava de código falha.

## 4. Chave de desligar (D5)

- [x] 4.1 `interface/config.py`: `DONA_CHECA_COBERTURA_AMPLA` (`sim`|`nao`,
      padrão `sim`), valor inválido gera `ErroConfig`. Verificar com testes de
      config.
- [x] 4.2 Parâmetro descendo por `fluxo.verificar` → `executar` →
      `guarda.verificar`, registrado em `rastro["parametros"]`; bancada com
      `--sem-cobertura-ampla`. Verificar com teste de pipeline em que a chave
      desligada rebaixa um veredito `ampla`.

## 5. Resposta (D6)

- [x] 5.1 Texto `abertura_ampla` no delta de `resposta-formativa`, lido da spec
      como o bordão; `_abertura` usa a frase quando `cobertura == "ampla"`.
      Verificar com testes em `test_estrutura.py`: cobertura ampla abre com a
      frase; cobertura `mesma` abre com "Falso."; rebaixamento remove a frase.
- [x] 5.2 `mensagem` informa cobertura e ponte ao modelo; `_detalhe` traz
      `alegacao_checada` literal e a `ponte`. Verificar com testes de
      `estrutura`; teto de 120 palavras com a abertura nova coberto por
      `test_teto.py`.
- [x] 5.3 `interface/estatico/chat.js` mostra a alegação checada e a ponte no
      painel de detalhe. Verificar com o teste de página existente estendido e
      com a checagem axe sem violação nova.

## 6. Avaliação e rastro (D7)

- [x] 6.1 `metricas.py` separa por cobertura discernimento e aceitação cega;
      item sem o campo conta como `mesma`. Verificar com testes de métricas.
- [x] 6.2 Bancada grava a lista de pontes da rodada em `bancada/relatorios/`.
      Verificar com teste da bancada com gravação.

## 7. Sonda e bancada (D8)

- [x] 7.1 `prototipo/sonda_cobertura_ampla.py` com os casos A1, A2 e N1 a N6,
      trechos congelados do índice por `unidade_id` (N4 sintético, marcado, se
      faltar no acervo). Verificar com a sonda rodando com chat falso no teste.
- [ ] 7.2 Rodar a sonda com o Gemma local, 3 rodadas. Aceite: A1 e A2 `falso`
      3/3; N1 a N6 `evidência insuficiente` 3/3. Gravar relatório em
      `prototipo/relatorio_sonda_cobertura_ampla.json` e registrar o resultado
      no `design.md`. Se houver um falso positivo, parar e revisar prompt ou
      travas antes de seguir.
- [ ] 7.3 Repetir 7.2 com o gerador remoto (exige chave DeepSeek válida).
      Mesmo aceite e mesmo registro.
- [ ] 7.4 Casos novos em `bancada/casos.json`: jacaré (`falso`, cobertura
      `ampla`) e autismo vs DNA (sem veredito ampla). Verificar com a rodada
      real da bancada, regravando as gravações, sem regressão nos casos atuais.

## 8. Verificação final

- [ ] 8.1 Ponta a ponta no chat, modos uso e piloto: jacaré mostra a abertura
      ampla, a alegação checada e a ponte; com `DONA_CHECA_COBERTURA_AMPLA=nao`,
      volta a `evidência insuficiente`.
- [ ] 8.2 Suíte inteira verde e `openspec validate add-cobertura-alegacao-ampla
      --strict` limpo.
