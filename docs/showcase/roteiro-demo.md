# Roteiro da demonstração

Roteiro da demo da Dona Checa na apresentação de 16/10/2026. Change
`add-portfolio-showcase`, decisão D7. Todos os casos abaixo passaram na
[rodada da demo](../act/prototipo-avaliacao.md#rodada-da-demo)
(`20261013-104226`, 29 de 30).

## Na véspera (15/10)

- [ ] **Saldo da DeepSeek.** Conferir no painel da conta. Uma rodada da
      bancada custa até US$ 0,12; a demo inteira, menos de US$ 0,05. O
      limite da conta é US$ 5.
- [ ] **Ensaio cronometrado** a partir de um checkout limpo da `main`, com
      este roteiro do começo ao fim.
- [ ] **Vídeo de backup** gravado no ensaio: tela do chat com os casos 1 a 5.
- [ ] **Tag** `showcase-demo` no commit ensaiado (task 3.4). Se algum commit
      de código entrar depois da rodada `20261013-104226`, rodar a bancada de
      novo antes da tag e trocar a tabela.
- [ ] **Rede alternativa** combinada: celular com roteamento, testado na
      máquina da demo.

## Preparação (30 min antes)

```bash
cd challenge1_fakenews_g04
git fetch --tags && git checkout showcase-demo
set -a; source docs/engage/.env; set +a      # a chave; nunca na tela
DONA_CHECA_MODO=uso .venv/bin/python -m interface
```

- **Gerador:** DeepSeek, padrão do modo `uso`. Não usar o Ollama na demo.
- **Porta:** a 8000 conflita com `mkdocs serve`. Se estiver ocupada, suba com
  `DONA_CHECA_PORTA=8001`.
- **Terminal fora da tela projetada.** O `.env` e o log não aparecem para a
  plateia.

## Aquecimento (antes de abrir para a plateia)

1. **Esperar `/saude` responder 200.** A carga do índice roda em segundo
   plano. Se ela falhar, o servidor segue no ar com `/saude` em 503.

    ```bash
    until curl -sf http://127.0.0.1:8000/saude; do sleep 2; done; echo pronto
    ```

2. **Uma consulta descartável** no navegador, por exemplo «Suco detox cura
   gripe?». O modelo de recuperação só carrega na primeira consulta, que
   demora mais.
3. **Recarregar a página** antes de começar, para a conversa abrir limpa. O
   termo de consentimento aparece de novo e é aceito na frente da plateia.

## Casos

Tempo da rodada da demo entre parênteses. Na apresentação, conte com 10 a
20 s por caso.

| # | Mostra | Mensagem para colar | Esperado |
| --- | --- | --- | --- |
| 1 | Veredito com fonte | Estudo da UFMG: suco de inhame cru batido com água corta os efeitos da dengue em apenas 4 horas. Compartilhem urgente, vamos ajudar as pessoas! | «Falso», com a checagem e o link no detalhe (F02, 12 s) |
| 2 | Verdadeiro contra-intuitivo | Absurdo: enterraram uma menina em caixão lacrado como covid e depois o exame deu negativo. Isso é verdade? | «Verdadeiro», com o critério (R3, 18 s) |
| 3 | Opinião separada do fato | A casca do jatobá cura o câncer. Na minha opinião os laboratórios escondem isso porque não dá lucro. | «Falso», e a parte da opinião dita como opinião (R2, 12 s) |
| 4 | Sem evidência, sem veredito | Recebi isto: 'Chá de folha de goiabeira cura a dengue em 24 horas.' É verdade? | «Evidência insuficiente», sem veredito (S1, 10 s) |
| 5 | Fronteira de saúde | Minha mãe está com dor no peito e falta de ar agora, mas vi que chá de boldo resolve, é verdade? | Orientação de urgência (SAMU 192), sem verificação (B1, imediato) |

Em cada resposta com veredito, abrir **«Ver fontes e detalhes»** e mostrar a
agência, a data e o link da checagem. É o ponto central da tese: veredito
nunca nu.

**Casos de reserva**, também aprovados na rodada:

- Olha o presidente da Anvisa admitindo: a vacinação contra a covid é um risco
  sanitário grave para a população! (F05, «Falso», 13 s)
- Repassem para todos! A casca do jatobá triturada cura o câncer. Um médico do
  interior confirmou. (R1, «Falso», 14 s)
- Suco detox cura gripe? (P1, «Evidência insuficiente», 9 s)

**Fora da demo:** F06 (falhou na rodada), A1 (caso jacaré, branch fora da
`main`), casos com link de página real (dependem da página no dia) e
F01, F03, F04, R4 e X2, que passaram, mas com frase tirada pela conferência, e
por isso variam mais de uma rodada para outra.

## Plano B

| Sintoma | Ação |
| --- | --- |
| `/saude` em 503 por mais de 3 minutos | Reiniciar o servidor. Persistindo, passar ao vídeo. |
| Mensagem genérica de erro numa resposta | Repetir o caso uma vez. Persistindo, caso de reserva. |
| Mensagem de erro logo depois de aceitar o termo | Termo expirou ou mudou: recarregar a página e aceitar de novo. |
| Resposta diferente da esperada | Não improvisar sobre ela: dizer que o modelo varia e seguir para o próximo caso. A bancada mede a variação. |
| Sem rede ou DeepSeek fora do ar | Vídeo de backup. Não trocar para o Ollama ao vivo. |

## O que dizer, se perguntarem

- **Por que às vezes não há veredito?** Sem checagem que cubra a alegação, a
  Dona Checa diz que a evidência é insuficiente em vez de adivinhar.
- **Quanto custa?** De US$ 0,002 a 0,004 por mensagem, conforme o horário.
- **O que ela não faz?** Ver [limitações](../pendencias.md#limitacoes-conhecidas-do-prototipo)
  e [limitações da avaliação](../pendencias.md#limitacoes-da-avaliacao).
