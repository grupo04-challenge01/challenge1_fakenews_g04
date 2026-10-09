# Tasks: Limitações do MVP

TDD em toda task de código: teste falhando primeiro, depois a implementação.

## 1. Conferência de sustentação (D1)

- [x] 1.1 Testes e implementação de `prototipo/resposta/conferencia.py`: prompt,
      leitura da saída, frases apontadas saem e vão para `sem_base`
- [x] 1.2 Integração em `estrutura.responder`: rebaixamento quando bloco 1 ou 2
      fica sem frase, bloco 3 mantém a primeira, falha da chamada registrada
- [x] 1.3 Bancada conta casos com frase tirada pela conferência

## 2. Termo em parágrafos (D2)

- [x] 2.1 Spec com o termo em seis parágrafos; servidor mantém os parágrafos;
      página monta um `<p>` por parágrafo; testes de página e axe

## 3. Corte no bloco 2 (D3)

- [x] 3.1 Testes e implementação do corte no bloco 2 depois dos blocos 3 e 4

## 4. Verificação

- [x] 4.1 Rodada real da bancada, que regrava as gravações e cumpre D10
- [ ] 4.2 Teste de ponta a ponta nos modos uso e piloto
- [x] 4.3 Suíte verde e `openspec validate fix-limitacoes-mvp --strict`
