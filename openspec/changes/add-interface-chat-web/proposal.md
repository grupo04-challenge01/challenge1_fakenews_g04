# Proposal: Interface de chat web da Dona Checa

**Fase do CBL:** Act. Change aberto em 07/10/2026. Depende de
`add-identidade-dona-checa` (textos, bordão, voz das recusas e logo) e deixa
uma pendência declarada para `add-entrada-por-link`.

## Why

O canal primário do produto é uma aplicação web de chat responsivo (decisão 5
de `mvp-copiloto-verificacao`), e as tasks 5.x daquele change fixaram camadas,
checklist de acessibilidade e fluxo sem cadastro. Nenhuma delas entregou
código: o fluxo inteiro existe (`bancada/pipeline.py`, `executar`), mas a única
tela é a da bancada, em Streamlit, que mostra scores e defeitos e "não serve
para sessão com participante" (cabeçalho de `bancada/tela.py`).

Sem interface não há demo, não há piloto (task 6.6 de `mvp-copiloto-verificacao`)
e não há como medir discernimento com gente de verdade.

## What Changes

- **NOVO** pacote `interface/`: servidor FastAPI que serve uma página de chat em
  HTML, CSS e JS puros, sem etapa de build, e uma rota que roda o fluxo e
  devolve o andamento por SSE.
- **NOVO** comportamento de tela: abertura e chamada da Dona Checa, fronteira
  antes de tudo (urgência e sofrimento psíquico aparecem na hora, sem bordão
  nem pergunta), pergunta de confiança durante a espera e só no navegador,
  resposta em quatro blocos com o detalhe expandindo na própria bolha, erro e
  mensagem só com link na voz da Dona Checa.
- **NOVO** modo de execução obrigatório por variável de ambiente
  (`DONA_CHECA_MODO=piloto|uso`): em `piloto`, a pergunta de confiança some.
- **MODIFICADO (código)** `bancada/pipeline.py`: `executar` ganha um parâmetro
  opcional para avisar cada etapa concluída. Sem o parâmetro, o comportamento
  é o de hoje.
- Roda na máquina de um integrante para demo e piloto, desenhado para ser
  hospedado depois sem reescrita: configuração por ambiente, modelo e índice
  injetáveis, nada guardado no servidor.

## Capabilities

### New Capabilities

- `interface-chat-web`: estados da conversa, ordem fronteira-primeiro, modo
  por ambiente, pergunta de confiança só no navegador, detalhe na bolha,
  mensagem só com link, erro sem vazamento, nada guardado.

### Modified Capabilities

Nenhuma. A interface cumpre `acessibilidade-leitura` e `identidade-dona-checa`
como estão. A entrada por link, exigida em `acessibilidade-leitura` /
"Entrada sem barreira", continua descumprida até `add-entrada-por-link`; a
pendência fica declarada no design.

## Out of Scope

- Busca do conteúdo de link (`add-entrada-por-link`).
- Extensão ou bot de WhatsApp.
- Hospedagem pública, domínio, HTTPS, autenticação e controle de abuso: o
  desenho permite, o change não entrega.
- Histórico de conversa entre visitas, contas ou qualquer persistência.
- Registro de sessão do piloto: continua com `prototipo/avaliacao/`.

## Impact

**Entregáveis finais do desafio atingidos:**

- **Solução/protótipo com suporte de IA:** o protótipo passa a ter uma tela
  utilizável por qualquer pessoa, que é o que a demo e o piloto exigem.
- **Apresentação final (Showcase):** a demo ao vivo roda nesta interface.

**Código afetado:**

- `interface/` (novo): `app.py`, `config.py`, `fluxo.py`, `estatico/`, testes.
- `bancada/pipeline.py`: parâmetro opcional de aviso por etapa.
- `requirements-interface.txt` e `requirements-interface-dev.txt` (novos):
  `fastapi`, `uvicorn`; `playwright`, `pytest-playwright`.
- `docs/`: página de como subir a interface em modo uso e em modo piloto.
