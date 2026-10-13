# Proposal: Robustez para a demonstração

**Fase do CBL:** Showcase. Change aberto em 13/10/2026, a partir da revisão
de prontidão da entrega final. Corrige código do Act antes da tag
`showcase-demo` (decisão D5 de `add-portfolio-showcase`).

## Why

A revisão de 13/10 achou quatro defeitos que podem aparecer ao vivo:

1. **Veredito nu.** Quando a saída do modelo não é JSON (texto livre, ou JSON
   cortado no teto de 1200 tokens), `_montar` pula a ancoragem. A resposta
   sai só com a abertura («Falso.») e os blocos 1 e 2 vazios. A nova tentativa
   por defeito pode repetir o erro, e a conferência de sustentação não age
   porque não há frase para conferir. Fere a restrição central do projeto:
   veredito nunca nu.
2. **Fila travada.** `chat_ollama` não passa tempo-limite ao cliente. Uma
   chamada presa segura a vez do servidor (`vez`), e todo pedido seguinte
   falha por tempo até reiniciar.
3. **`.env.example` que não sobe.** As linhas opcionais vêm vazias, e
   `DONA_CHECA_GERADOR=` vazio é recusado na subida.
4. **Agência malformada.** O índice traz nomes como `https:apublica.org` e
   `https:piaui.folha.uol.com.brlupa`, que aparecem como título do cartão de
   fonte.

## What Changes

- **MODIFICADO (código)** `prototipo/resposta/estrutura.py`: saída que não é
  JSON na forma com evidência conta como falha de ancoragem. Uma nova
  tentativa com aviso e, falhando, rebaixamento para a forma sem evidência
  (D1).
- **MODIFICADO (código)** `prototipo/verificacao/modelo.py`: cliente Ollama
  com tempo-limite; estouro vira `ErroGerador` e libera a vez (D2).
- **MODIFICADO (config)** `.env.example` com as linhas opcionais comentadas
  (D3).
- **MODIFICADO (código)** nome de agência legível no detalhe da resposta e no
  pedido ao modelo; o índice não muda (D4).

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `resposta-formativa`: novos requirements «Veredito só com blocos de
  critério» e «Agência com nome legível».
- `interface-chat-web`: novo requirement «Gerador local com tempo-limite».

Ordem de arquivamento: depois de `mvp-copiloto-verificacao`,
`add-interface-chat-web`, `add-gerador-api-deepseek` e `fix-limitacoes-mvp`.

## Impact

- Resposta não-JSON custa uma chamada a mais antes do rebaixamento.
- Gravações da bancada com nome de agência no detalhe podem mudar de texto.
- Sem mudança no índice, na guarda nem no limiar.
