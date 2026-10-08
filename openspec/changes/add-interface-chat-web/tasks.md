# Tasks: Interface de chat web da Dona Checa

TDD em toda task de código: teste falhando primeiro, depois a implementação.
Pré-requisito: `add-identidade-dona-checa` aplicado antes da seção 4.

## 1. Base do servidor

- [x] 1.1 Criar `requirements-interface.txt` (`-r requirements-rag.txt`,
      `fastapi`, `uvicorn`) e `requirements-interface-dev.txt` (`playwright`,
      `pytest-playwright`)
- [x] 1.2 Teste e implementação de `interface/config.py`: `DONA_CHECA_MODO`
      obrigatória (`uso`|`piloto`), demais variáveis com padrão, erro que
      nomeia a variável
- [x] 1.3 Teste e implementação de `criar_app` com `GET /` (página estática) e
      `GET /saude` (`503` antes da carga, `200` depois)

## 2. Fluxo com andamento

- [x] 2.1 Teste: `executar(..., ao_etapa=f)` chama `f` uma vez por etapa, na
      ordem; sem `ao_etapa`, a suíte de `bancada/tests/` passa sem mudança
- [x] 2.2 Implementar `ao_etapa` em `bancada/pipeline.py`
- [x] 2.3 Teste e implementação de `interface/fluxo.py`: eventos `fronteira`,
      `andamento`, `resposta`, `aviso`, `erro` conforme a decisão 3 do design,
      com fronteira sempre primeiro
- [x] 2.4 Teste e implementação do mapeamento de desfecho da fronteira
      (urgência, sofrimento, conduta, segue)
- [x] 2.5 Teste e implementação de `POST /verificar` em streaming, com
      semáforo de 1 e tempo máximo
- [x] 2.6 Teste e implementação da mensagem só com link (fluxo não chamado) e
      de `sem_alegacao`
- [x] 2.7 Teste: falha do modelo gera evento `erro` e o log tem etapa e tipo,
      sem o texto da mensagem

## 3. Página

- [x] 3.1 `estatico/index.html` com cabeçalho, chamada, área da conversa
      (`aria-live`), campo com `<label>` e botão Enviar; `estilo.css` com
      tokens da paleta, base 18px em `rem`, alvos de 44px,
      `prefers-reduced-motion`
- [x] 3.2 Fontes Bricolage Grotesque e DM Sans em `estatico/fontes/` com as
      licenças OFL
- [x] 3.3 `chat.js`: envio por `fetch`, leitura do streaming, estados lendo,
      fronteira, conferindo, resposta, aviso e erro com "Tentar de novo"
- [x] 3.4 `chat.js`: pergunta de confiança durante a espera, só em memória,
      ignorável; ausente quando a configuração injetada traz `null`
- [x] 3.5 `chat.js`: botão "Ver fontes e detalhes" expandindo cartões na
      bolha, `aria-expanded`, foco na resposta que chega
- [x] 3.6 Urgência e sofrimento com destaque, anúncio prioritário e telefones
      como links `tel:`

## 4. Textos e identidade

- [x] 4.1 Teste e implementação da leitura dos blocos `##### Texto` desta spec
      e de `identidade-dona-checa`, injetados em `index.html` com o modo
- [x] 4.2 Teste: em modo piloto a configuração injetada traz a pergunta de
      confiança como `null` e o rodapé mostra "modo piloto"
- [x] 4.3 Avatar e favicon a partir de `docs/identidade/dona-checa.svg`

## 5. Testes da página (Playwright)

- [x] 5.1 Fixture que sobe o servidor de teste com fluxo falso; axe-core em
      `interface/tests/vendor/` com a licença
- [x] 5.2 Teste: urgência aparece antes de qualquer bordão; `tel:192` presente
- [x] 5.3 Teste: modo piloto sem pergunta; modo uso com pergunta, e a escolha
      não aparece em requisição nem em armazenamento do navegador
- [x] 5.4 Teste: detalhe abre e fecha na bolha; recarregar mostra só a abertura
- [x] 5.5 Teste: fonte ≥ 18px, alvos ≥ 44px, axe sem violação, 320px com
      fonte em 200% sem rolagem horizontal, fluxo completo só pelo teclado

## 6. Uso e fechamento

- [x] 6.1 Página em `docs/` com como subir em modo uso e em modo piloto, como
      abrir no celular da mesma rede e o aviso sobre `0.0.0.0`
- [x] 6.2 Verificação manual pela checklist de
      `mvp-copiloto-verificacao/specs/acessibilidade-leitura/checklist.md` num
      celular real, com resultado registrado
      — 07/10/2026, iPhone 11 com Safari, servidor com o fluxo falso dos
      testes: leitura sem zoom (e sem óculos), contraste, botões, teclado sem
      esconder o envio e rolagem lateral só com zoom: ok. Dois achados
      corrigidos com teste: `crypto.randomUUID` não existe fora de contexto
      seguro (`http://<ip>`) e derrubava pergunta e detalhe; a fonte não
      seguia o tamanho de texto do iOS, agora segue (`-apple-system-body`),
      conferido no aparelho
- [x] 6.3 Rodar as suítes de `interface/`, `bancada/` e `prototipo/` e
      registrar o resultado
      — 07/10/2026, sobre o conteúdo exato do commit: `pytest` 523 passando,
      2 pulados (testes do índice real, que não vai ao git); interface 65
      passando, entre eles 26 no Chromium com axe-core; bancada offline 17/17
- [x] 6.4 `openspec validate add-interface-chat-web --strict` limpo

## 7. Ajustes depois da entrega

- [x] 7.1 Texto `sem_alegacao` deixa claro que assunto fora da saúde não tem
      resposta, por sugestão do grupo na revisão das telas; teste da página
      confere a frase nova
      — 08/10/2026: interface 83 passando; `openspec validate
      add-interface-chat-web --strict` limpo
