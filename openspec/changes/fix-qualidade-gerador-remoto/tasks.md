# Tasks: Qualidade com gerador remoto

TDD em toda task de código: teste falhando primeiro, depois a implementação.

## 1. Verificador de mito

- [x] 1.1 Testes da tabela de D1 em `prototipo/resposta/tests/test_mito.py`,
      positivos e negativos
- [x] 1.2 Ampliar `MARCA` em `prototipo/resposta/mito.py`; os testes existentes
      de mito continuam verdes

## 2. Decomposição

- [x] 2.1 Teste e implementação da nova tentativa (D2): primeira saída com
      defeito e segunda sem; duas com defeito levantam `ValueError`; o rastro
      guarda as duas saídas
- [x] 2.2 Frases de D3 no `SISTEMA` da decomposição; teste de que estão no prompt

## 3. Resposta

- [x] 3.1 Teste e implementação de D5: defeito de forma pede de novo uma vez;
      segunda saída com mais defeitos mantém a primeira; ancoragem que já
      gastou a tentativa não pede outra

- [x] 3.2 Teste e implementação de D6 na extração: teto de 8 no prompt, nova
      tentativa com defeito informado, segunda saída com defeito levanta
- [x] 3.3 Teste e implementação do log de `finish_reason` `length` em
      `ChatDeepSeek`, sem texto

- [x] 3.4 Teste e implementação de D7: alvo de 80 palavras nos blocos no
      prompt, aviso com as palavras a cortar, marcas "retratado" e "fora/tira
      de contexto" com os negativos da tabela de D1

## 4. Bancada

- [x] 4.1 Regravar `bancada/gravacoes/` com o gerador padrão (D4) e conferir
      `pytest bancada` verde
- [x] 4.2 Bancada real com `deepseek-v4-pro`: nos casos das tabelas de `add-gerador-api-deepseek`, nenhuma falha coberta por D1, D2 ou D5 se repete; anotar
      casos, mediana e tokens em `add-gerador-api-deepseek/design.md`
- [x] 4.3 Suíte inteira verde: `pytest interface prototipo bancada`
- [x] 4.4 `openspec validate fix-qualidade-gerador-remoto --strict` limpo
