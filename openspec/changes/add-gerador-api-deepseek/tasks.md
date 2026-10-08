# Tasks: Gerador por API (DeepSeek)

TDD em toda task de código: teste falhando primeiro, depois a implementação.
Nenhum teste acessa a rede; a API entra simulada com `httpx.MockTransport`.

## 0. Fora do código

- [x] 0.1 Registrar em `design.md` (D6) a decisão do grupo sobre usar
      DeepSeek no piloto; se sim, inserir a frase de D6 na seção 5 do TCLE
      antes da submissão ao CEP
- [x] 0.2 Configurar limite de gasto mensal no painel da DeepSeek e anotar o
      valor em `design.md` (Risks)
- [ ] 0.3 **Breno** Submeter a emenda 01 do protocolo (dossiê do CEP, seção 5)
      e registrar o resultado na tabela de emendas antes do piloto com DeepSeek

## 1. Segredo e configuração

- [x] 1.1 Criar `.env.example` com
      `DONA_CHECA_MODO`, `DONA_CHECA_GERADOR`, `DEEPSEEK_API_KEY` e
      `DEEPSEEK_MODELO` vazios; verificar que `git check-ignore .env`
      acusa a regra e `git check-ignore .env.example` não acusa nada
- [x] 1.2 Teste e implementação do campo `gerador` em `interface/config.py`:
      padrão por modo, valor inválido, chave ausente com `deepseek`, chave
      nunca presente na mensagem de erro; verificar com
      `pytest interface/tests/test_config.py`

## 2. `ChatDeepSeek` em `prototipo/verificacao/modelo.py`

- [x] 2.1 Teste e implementação do corpo do pedido (D1) e da leitura de
      `content`; verificar com `pytest prototipo/verificacao/tests/test_modelo.py`
- [x] 2.2 Teste e implementação da nova tentativa (D5): `content` vazio uma
      vez, 503 uma vez, 503 duas vezes, 401 sem nova tentativa
- [x] 2.3 Teste de log: falha registra tipo e status, sem cabeçalho
      `Authorization` e sem o texto da mensagem

## 3. Interface

- [x] 3.1 `interface/__main__.py` escolhe `ChatDeepSeek` ou `chat_ollama` a
      partir de `config.gerador` e passa para `criar_app`
- [x] 3.2 Teste e implementação do aviso `servico-externo` (rodapé, injetado
      pelo servidor, ausente com `ollama`); incluir no teste de acessibilidade
      existente
- [x] 3.3 Suíte inteira verde: `pytest interface prototipo bancada`

## 4. Bancada e aceite

- [x] 4.1 Opção `--gerador` em `python -m bancada rodar`, com `gerador` e
      `modelo` em `parametros`; teste no modo offline
- [x] 4.8 Tipos de falha e resultado do critério em `resumo.por_tipo` e
      `resumo.criterio`, impressos ao fim da rodada
- [x] 4.2 No mesmo dia e na mesma rede, rodar a bancada real com
      `--gerador ollama` e com `--gerador deepseek`; anotar em `design.md` o
      nome dos dois relatórios (`bancada/relatorios/` não é versionado)
- [x] 4.5 Teste inicial do gerador antes do primeiro caso: falha para a
      rodada sem sobrescrever `bancada/gravacoes/`
- [x] 4.3 Comparar: casos que passaram e mediana do tempo total por caso
      completo; registrar a tabela em `design.md`. Se não houver 17/17 ou a
      mediana não cair pela metade, rodar com `DEEPSEEK_MODELO=deepseek-v4-pro`
      antes de qualquer outra mudança
- [x] 4.6 Tokens por rodada em `parametros.uso`, somados do `usage` da API
- [x] 4.7 Rodar a bancada com `deepseek-v4-pro` mais duas vezes e anotar em
      `design.md` casos que passaram, mediana e tokens de cada rodada

## 5. Consentimento e minimização (D8, D9)

- [ ] 5.1 **Vitor** Revisão do termo e de D8 pelo jurídico ou DPO da instituição;
      preencher `CONTATO_DO_GRUPO`
- [ ] 5.2 **Vitor** Ler a política de privacidade e os termos da API da DeepSeek
      (retenção e uso para treino) e ajustar o texto do termo se preciso
- [x] 5.3 Teste e implementação de `prototipo/entrada/minimizar.py` e da
      chamada no fluxo antes da fronteira, só com gerador `deepseek`
- [x] 5.4 Teste e implementação do campo `consentimento` em `POST /verificar`:
      403 sem a versão atual, log da versão sem identificador, `recusado` com
      alternativa local usando `chat_ollama`
- [x] 5.5 Teste e implementação do termo na página (Playwright): campo
      bloqueado até a escolha, recusa com e sem alternativa, termo de volta ao
      recarregar, axe sem violações
- [x] 5.6 Servidor com gerador `deepseek` não sobe com `CONTATO_DO_GRUPO` no
      termo; testes da regra e da subida
- [x] 5.7 Documento para a revisão jurídica em `docs/interface/revisao-termo-lgpd.md`,
      com o fluxo dos dados, o termo como a pessoa vê, os fundamentos e as
      perguntas da revisão (insumo da 5.1)

## 6. Fechamento

- [x] 6.1 `openspec validate add-gerador-api-deepseek --strict` limpo
