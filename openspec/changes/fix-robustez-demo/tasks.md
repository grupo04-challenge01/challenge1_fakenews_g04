# Tasks: Robustez para a demonstração

TDD em toda task de código: teste falhando primeiro, depois a implementação.

## 1. Veredito só com blocos de critério (D1)

- [x] 1.1 Teste: saída não-JSON duas vezes na forma com evidência sai
      rebaixada, sem abertura de veredito
- [x] 1.2 Teste: saída não-JSON na primeira e JSON ancorado na segunda mantém
      o veredito
- [x] 1.3 Implementação em `estrutura._montar`

## 2. Gerador local com tempo-limite (D2)

- [x] 2.1 Teste: `chat_ollama` passa o tempo-limite ao cliente e converte o
      estouro em `ErroGerador`
- [x] 2.2 Teste: verificação que falha por erro do gerador libera a vez do
      servidor para o pedido seguinte
- [x] 2.3 Implementação em `prototipo/verificacao/modelo.py`

## 3. Configuração de exemplo (D3)

- [x] 3.1 Teste: `.env.example` com os valores de modo e chave preenchidos
      carrega sem `ErroConfig`
- [x] 3.2 `.env.example` com as linhas opcionais comentadas

## 4. Agência com nome legível (D4)

- [x] 4.1 Testes de `agencias.nome` e do detalhe da resposta
- [x] 4.2 Implementação em `prototipo/resposta/agencias.py`, `_detalhe` e
      `mensagem`
- [x] 4.3 Teste e implementação: a ancoragem aceita o nome legível da agência
      como fonte da frase, e a conferência de sustentação vê o mesmo nome

## 5. Verificação

- [x] 5.1 Suíte verde
- [x] 5.2 `openspec validate fix-robustez-demo --strict`
- [ ] 5.3 Rodada real da bancada com o gerador remoto, sem regressão contra a
      rodada anterior
