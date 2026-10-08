# Chat web da Dona Checa

Como subir a interface de conversa do copiloto para demo e para o piloto.
Change `add-interface-chat-web`; spec `interface-chat-web`.

## O que precisa estar pronto

1. **Dependências:** `pip install -r requirements-interface.txt`. Puxa a pilha
   da recuperação (`requirements-rag.txt`, com `sentence-transformers` e torch),
   FastAPI e uvicorn.
2. **Modelo:** Ollama rodando com o modelo do protótipo
   (`ollama pull gemma4:12b-it-qat`). Para usar um Ollama em outra máquina,
   defina `OLLAMA_HOST`.
3. **Índice:** `python -m prototipo.rag construir`, se o índice local for
   anterior ao esquema de indexação 1.0.0.

## Subir

O modo é obrigatório. Sem ele o servidor não sobe.

```bash
# demonstração e uso comum: com a pergunta de confiança
DONA_CHECA_MODO=uso python -m interface

# sessão de piloto ou de coleta: sem a pergunta de confiança, rodapé "modo piloto"
DONA_CHECA_MODO=piloto python -m interface
```

No PowerShell:

```powershell
$env:DONA_CHECA_MODO = "uso"; python -m interface
```

O servidor imprime o endereço (por padrão `http://127.0.0.1:8000`). O índice
carrega em segundo plano: abra o navegador quando `http://127.0.0.1:8000/saude`
responder `{"pronto": true}`.

| Variável | Padrão | Para quê |
|---|---|---|
| `DONA_CHECA_MODO` | obrigatória | `uso` ou `piloto` |
| `DONA_CHECA_HOST` | `127.0.0.1` | `0.0.0.0` para abrir no celular |
| `DONA_CHECA_PORTA` | `8000` | porta do servidor |
| `DONA_CHECA_TEMPO_MAX` | `300` | segundos até a página mostrar erro |
| `OLLAMA_HOST` | do cliente `ollama` | Ollama em outra máquina |

## Abrir no celular

1. Ligue o celular na **mesma rede Wi-Fi** do computador.
2. Suba com `DONA_CHECA_HOST=0.0.0.0`.
3. Descubra o IP do computador na rede (`ipconfig` no Windows, `ip addr` no
   Linux) e abra `http://<ip>:8000` no celular.

!!! warning "Só em rede de confiança"
    Com `0.0.0.0`, qualquer aparelho da rede alcança o servidor, sem senha.
    Não use em Wi-Fi público. Para a demo fora de casa, prefira o roteador do
    próprio celular.

## Durante o piloto

- Confira o rodapé "modo piloto" antes de chamar o participante.
- Uma verificação por vez: a máquina atende uma pessoa de cada vez, e o
  Ollama local é serial.
- Nada é guardado no servidor. Recarregar a página apaga a conversa.
- O log do terminal mostra etapa, tipo de erro e tempo. O texto da pessoa
  nunca vai ao log.

## Testes

```bash
pip install -r requirements-interface-dev.txt
python -m playwright install chromium   # uma vez
python -m pytest interface
```

Os testes do servidor rodam sem Ollama e sem índice. Os da página sobem o
servidor com um fluxo falso e conferem no Chromium: fronteira antes de tudo,
pergunta de confiança só no navegador, detalhe na bolha, fonte de 18px, alvos
de 44px, 320px sem rolagem horizontal e auditoria axe-core sem violações.
