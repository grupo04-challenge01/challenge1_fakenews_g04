# Design: Robustez para a demonstração

## Context

Motivação em `proposal.md`. Os quatro pontos vêm da revisão de prontidão de
13/10/2026. O change entra na `main` antes do ensaio de 15/10 e da tag
`showcase-demo`.

## Goals / Non-Goals

**Goals:**

- Nenhuma resposta com veredito chega à pessoa sem os blocos 1 e 2.
- Chamada presa ao gerador local não trava os pedidos seguintes.
- `cp .env.example .env` seguido de preencher modo e chave sobe o servidor.
- Cartão de fonte com nome de agência legível.

**Non-Goals:**

- Reconstruir o índice com agências normalizadas (cerca de 883 s mais
  revalidação). Fica para depois da apresentação.
- Fallback automático de DeepSeek para Ollama.
- Mudar o teto de 1200 tokens de saída.

## Decisions

### D1. Saída não-JSON na forma com evidência é falha de ancoragem

Em `_montar`, com veredito com evidência e `ler_json` devolvendo `None`, o
motivo vira `"saída não é JSON"`. Daí em diante vale o caminho da decisão 29
do MVP: uma tentativa a mais com o aviso da conferência e, persistindo o
motivo, rebaixamento para a forma sem evidência, com `rebaixada_por`
registrado.

Alternativa descartada: só filtrar no `fluxo` antes de emitir. Deixaria a
bancada e a sonda com o mesmo buraco, e o rebaixamento já existe em
`estrutura`.

Na forma sem evidência, a saída não-JSON continua como defeito
(`"saída não é JSON"`). Não há veredito a proteger.

### D2. Tempo-limite no cliente Ollama

`chat_ollama` usa `ollama.Client(timeout=TEMPO_LIMITE_LOCAL)`, com
`TEMPO_LIMITE_LOCAL = 120` s, e converte o estouro e erro de conexão em
`ErroGerador` com só o tipo da exceção. O erro sobe pela etapa, o `fluxo`
emite a mensagem de erro, e o `finally` de `rodar` libera a vez.

120 s cabe dentro de `DONA_CHECA_TEMPO_MAX` (300 s) e acima da chamada mais
lenta medida com o Gemma local na sonda de resposta.

### D3. `.env.example` com opcionais comentadas

Só `DONA_CHECA_MODO` e `DEEPSEEK_API_KEY` ficam ativas. `DONA_CHECA_GERADOR`
e `DEEPSEEK_MODELO` vão comentadas, com o padrão no comentário. Config de
tooling; entra aqui por estar no mesmo risco de demo.

### D4. Nome legível na saída, índice intacto

`prototipo/resposta/agencias.py` mapeia o valor cru do índice para o nome da
agência: `boatos` → Boatos.org; `lupa` e `https:piaui.folha.uol.com.brlupa` →
Agência Lupa; `COMPROVA` → Projeto Comprova; `aos fatos` e
`https:www.aosfatos.org` → Aos Fatos; `ESTADAO_VERIFICA` → Estadão Verifica;
`fato-ou-fake` → Fato ou Fake; `https:apublica.org` → Agência Pública.
Valor desconhecido passa como veio.

A troca acontece em `_detalhe` (referências mostradas no painel), em
`mensagem` (trechos `[Tn]` do pedido ao modelo) e no pedido da conferência
de sustentação, para os dois modelos verem o mesmo nome. O índice, a guarda e o
rastro da recuperação continuam com o valor cru.

Como o modelo passa a ver o nome legível, ele o cita nas frases. A ancoragem
aceita como fonte da frase tanto o valor cru quanto o nome legível; sem isso,
«Agência Lupa» vira termo fora do trecho e o veredito é rebaixado. A primeira
rodada real da bancada com o change (13/10) mostrou o efeito em F05 e R2.

## Risks / Trade-offs

- [Rebaixamento a mais] → só quando o modelo erra o formato duas vezes; o
  rastro registra o motivo.
- [Gemma local mais lento que 120 s numa máquina fraca] → a etapa falha com
  erro visível em vez de travar; o tempo-limite é constante de módulo.
- [Agência nova no índice sem mapeamento] → aparece como veio, igual a hoje.
