# Chat web da Dona Checa

Como subir a interface de conversa do copiloto para demo e para o piloto.
Changes `add-interface-chat-web` e `add-gerador-api-deepseek`; spec
`interface-chat-web`.

## O que precisa estar pronto

1. **Dependências:** `pip install -r requirements-interface.txt`. Puxa a pilha
   da recuperação (`requirements-rag.txt`, com `sentence-transformers`, torch e
   httpx), FastAPI e uvicorn.
2. **Gerador**, o modelo que escreve as respostas. Há dois:
    - **DeepSeek**, padrão no modo uso. Precisa de uma chave da API em
      `DEEPSEEK_API_KEY`. Responde em cerca de 10 segundos e custa perto de
      US$ 0,003 por mensagem. A conta do grupo tem limite de gasto de US$ 5.
    - **Ollama local**, padrão no modo piloto, e alternativa para quem recusa
      o termo. Precisa do Ollama rodando com o modelo do protótipo
      (`ollama pull gemma4:12b-it-qat`). Responde em 1 a 4 minutos. Para usar
      um Ollama em outra máquina, defina `OLLAMA_HOST`.
3. **Índice:** `python -m prototipo.rag construir`, se o índice local for
   anterior ao esquema de indexação 1.0.0.

## Configurar

O servidor lê tudo de variável de ambiente e **não lê o arquivo `.env`
sozinho**. Copie o modelo, preencha e exporte antes de subir:

```bash
cp .env.example .env        # o .env nunca vai para o repositório
# edite o .env: DONA_CHECA_MODO e DEEPSEEK_API_KEY, no mínimo
set -a; source .env; set +a
```

!!! warning "A chave é segredo"
    Não cole a chave em chat, issue, commit ou print de tela. Se ela vazar,
    apague-a no painel da DeepSeek e gere outra.

| Variável | Padrão | Para quê |
|---|---|---|
| `DONA_CHECA_MODO` | obrigatória | `uso` ou `piloto` |
| `DONA_CHECA_GERADOR` | `deepseek` em uso, `ollama` em piloto | `deepseek` ou `ollama` |
| `DEEPSEEK_API_KEY` | nenhum | obrigatória com o gerador `deepseek` |
| `DEEPSEEK_MODELO` | `deepseek-v4-pro` | outro modelo da DeepSeek, para teste |
| `DONA_CHECA_ALTERNATIVA_LOCAL` | `nao` | `sim`: quem recusa o termo é atendido pelo Ollama local |
| `DONA_CHECA_HOST` | `127.0.0.1` | `0.0.0.0` para abrir no celular |
| `DONA_CHECA_PORTA` | `8000` | porta do servidor |
| `DONA_CHECA_TEMPO_MAX` | `300` | segundos até a página mostrar erro |
| `OLLAMA_HOST` | do cliente `ollama` | Ollama em outra máquina |

## Subir

```bash
# demonstração e uso comum: DeepSeek, com a pergunta de confiança
DONA_CHECA_MODO=uso python -m interface

# o mesmo, só com o modelo local (sem chave, sem envio para fora)
DONA_CHECA_MODO=uso DONA_CHECA_GERADOR=ollama python -m interface

# sessão de piloto: sem a pergunta de confiança, rodapé "modo piloto"
DONA_CHECA_MODO=piloto python -m interface
```

No PowerShell:

```powershell
$env:DONA_CHECA_MODO = "uso"; $env:DEEPSEEK_API_KEY = "<chave>"; python -m interface
```

O servidor imprime o modo, o gerador e o endereço, por padrão
`http://127.0.0.1:8000`. O índice carrega em segundo plano. Abra o navegador
quando `http://127.0.0.1:8000/saude` responder `{"pronto": true}`.

O servidor não sobe, e diz o motivo, quando:

- falta `DONA_CHECA_MODO` ou ele tem outro valor;
- o gerador é `deepseek` e falta `DEEPSEEK_API_KEY`;
- `DONA_CHECA_GERADOR` ou `DONA_CHECA_ALTERNATIVA_LOCAL` têm valor inválido.

## Termo de consentimento

Com o gerador `deepseek`, a página mostra o termo antes de liberar o campo de
mensagem. O termo diz que o texto vai para a DeepSeek, na China; que a
DeepSeek pode guardá-lo e usá-lo para aprimorar seus sistemas; que telefone,
CPF e e-mail são apagados antes do envio, mas nomes não; e quem mantém o
serviço, com o contato `donacheca@checatudo.com`.

- **Aceito:** o campo libera. Cada mensagem vai ao servidor com a versão do
  termo (hoje, 3), e o servidor confere antes de chamar a DeepSeek.
- **Não aceito:** sem alternativa local, a página indica agências de
  checagem e o campo continua bloqueado. Com
  `DONA_CHECA_ALTERNATIVA_LOCAL=sim`, a página avisa que vai checar no
  computador do projeto, e as mensagens usam o Ollama.
- Recarregar a página mostra o termo de novo.
- O rodapé lembra o envio, pede para não digitar dados pessoais, avisa que o
  serviço é para maiores de 18 anos e traz o contato.

Textos, parecer jurídico e fundamentos: [revisão do termo](revisao-termo-lgpd.md)
e [parecer](parecer-termo-lgpd.md).

## Abrir no celular

1. Ligue o celular na **mesma rede Wi-Fi** do computador.
2. Suba com `DONA_CHECA_HOST=0.0.0.0`.
3. Descubra o IP do computador na rede e abra `http://<ip>:8000` no celular.
    - **macOS:** `ipconfig getifaddr en0`
    - **Windows:** `ipconfig`
    - **Linux:** `ip addr`

!!! warning "Só em rede de confiança"
    Com `0.0.0.0`, qualquer aparelho da rede alcança o servidor, sem senha.
    Não use em Wi-Fi público. Para a demo fora de casa, prefira o roteador do
    próprio celular.

## Durante o piloto

- Confira o rodapé "modo piloto" antes de chamar o participante.
- **Gerador:** o padrão do piloto é o Ollama local. A emenda 01 ao protocolo,
  aprovada em 08/10/2026, permite usar a DeepSeek. Para isso, suba com
  `DONA_CHECA_GERADOR=deepseek`. O TCLE assinado e o termo da página valem
  juntos.
- Use só as mensagens do banco de estímulos da pesquisa. A emenda não
  autoriza enviar à DeepSeek dados pessoais do participante.
- Uma verificação por vez: o servidor atende uma pessoa de cada vez.
- Nada é guardado no servidor. Recarregar a página apaga a conversa.
- O log do terminal mostra etapa, tipo de erro, tempo e a versão do termo
  aceita. O texto da pessoa nunca vai ao log.

## Problemas comuns

| Sintoma | Causa provável |
|---|---|
| "Dona Checa não subiu: DEEPSEEK_API_KEY é obrigatória…" | a chave não foi exportada: rode `set -a; source .env; set +a` na mesma janela |
| A página mostra o erro, e o log tem `deepseek: status 401` | chave errada ou apagada no painel da DeepSeek |
| O log tem `deepseek: status 402` | saldo ou limite de gasto da conta esgotado |
| O log tem `pedido sem consentimento válido` | página antiga aberta depois de mudar a versão do termo: recarregue |
| A resposta demora minutos | o gerador é o Ollama: confira o gerador na linha que o servidor imprime ao subir |

## Testes

```bash
pip install -r requirements-interface-dev.txt
python -m playwright install chromium   # uma vez
python -m pytest interface
```

Os testes do servidor rodam sem modelo, sem chave e sem índice. Os da página
sobem o servidor com um fluxo falso e conferem no Chromium:

- fronteira antes de tudo;
- pergunta de confiança só no navegador;
- detalhe na bolha;
- termo de consentimento (aceite, recusa com e sem alternativa, termo de novo
  ao recarregar);
- fonte de 18px, alvos de 44px e 320px sem rolagem horizontal;
- auditoria axe-core sem violações.

Para medir a qualidade e o tempo com o modelo real, use a bancada. Ela
imprime o critério de aceite e os tokens gastos, cerca de US$ 0,05 por rodada:

```bash
python -m bancada rodar --gerador deepseek
```
