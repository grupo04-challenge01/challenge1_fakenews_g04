# Tasks: Entrada por link

TDD em toda task de código: teste falhando primeiro, depois a implementação.
Nenhum teste acessa a rede.

## 0. Prioridade fora do código

- [x] 0.1 Inserir a frase de D9 na seção 5 do TCLE
      (`mvp-copiloto-verificacao/specs/avaliacao-instrumento/protocolo-etico-tcle-debriefing.md`)
      e avisar o responsável pela 6.4 antes da submissão ao CEP; verificar
      com `grep -n "servidor do projeto abre" ` no arquivo

## 1. Dependências

- [x] 1.1 Instalar `trafilatura` e `httpx` no Python 3.14.6 do lock e rodar
      `python -c "import trafilatura, httpx; print(trafilatura.__version__)"`;
      se falhar, parar e reabrir D3
- [x] 1.2 Adicionar `httpx` e `trafilatura` a `requirements-rag.txt` com
      comentário de origem, regenerar `requirements-rag.lock.txt` e verificar
      que `pip install -r requirements-rag.lock.txt` instala limpo

## 2. `prototipo/entrada/link.py`

- [x] 2.1 Teste e implementação de `separar`: texto sem URL, uma URL, duas
      URLs (ordem preservada), URL com pontuação colada (`…/noticia).`),
      URL no meio do texto; verificar com `pytest prototipo/entrada/tests/test_link.py`
- [x] 2.2 Teste e implementação de `limpar`: cada parâmetro da lista de D5
      removido, parâmetros legítimos mantidos na ordem, fragmento removido
- [x] 2.3 Teste e implementação de `classificar_antes`: um caso por host e
      caminho de D5 para `video` e `nao_abriu`, e notícia comum devolvendo
      `None`

## 3. `prototipo/entrada/rede.py`

- [x] 3.1 Teste e implementação das regras de URL: esquema `ftp`/`file`,
      porta 8080, `user:pass@host` recusados com `Recusa`
- [x] 3.2 Teste e implementação do backend de conexão de D4 com resolvedor
      falso: `127.0.0.1`, `10.0.0.1`, `192.168.0.1`, `169.254.169.254`,
      `::1`, `::ffff:127.0.0.1`, `fc00::1`, e nome com um IP público e um
      privado, todos recusados sem abrir socket
- [x] 3.3 Teste de DNS rebinding: resolvedor que responde público na
      primeira chamada e privado na segunda; verificar que a conexão usa o
      endereço validado ou é recusada
- [x] 3.4 Teste e implementação do laço de redirecionamento com
      `httpx.MockTransport`: 2 saltos seguidos e URL final registrada,
      salto para IP interno recusado, 6 saltos recusados, `Location` relativa
      resolvida
- [x] 3.5 Teste e implementação dos limites: corpo de 3 MB, gzip de 100 KB
      que vira 50 MB, `application/pdf`, resposta 503 e tempo esgotado, todos
      com `Recusa`; User-Agent e ausência de cookie conferidos na requisição

## 4. `prototipo/entrada/leitura.py`

- [x] 4.1 Gravar em `prototipo/entrada/tests/paginas/` HTML de: blog de
      saúde brasileiro, jornal com paywall que entrega o texto no HTML,
      página com só título e lead, página só-JS, página com `JSON-LD`
      `isAccessibleForFree: false`, post de rede social com login, e página
      com tentativa de injeção (D8); registrar URL e data de coleta em
      `paginas/README.md`
- [x] 4.2 Teste e implementação de `ler` para leitura completa: título,
      veículo e data extraídos do blog e do jornal; corte em 800 palavras
      marca `cortado`
- [x] 4.3 Teste e implementação de leitura parcial e fallback de metadados
      (`articleBody`, `og:description`) com os limiares de D6
- [x] 4.4 Teste e implementação das falhas: `fechada` para `JSON-LD` e rede
      social, `vazia` para página só-JS, `nao_abriu` para `Recusa`, `video`
      sem chamar `buscar` (verificado com `buscar` falso que falha se chamado)

## 5. Pipeline

- [x] 5.1 Teste: fronteira recebe a mensagem sem URL; página que fala de
      infarto não dispara urgência; relato de urgência com link para antes de
      qualquer chamada a `buscar`
- [x] 5.2 Teste: regra de escolha de D2 (curto → página; longo verificável →
      texto sem chamar `buscar`; longo não verificável → página com segunda
      extração; dois links → só o primeiro, segundo em `origem.ignorados`)
- [x] 5.3 Implementar etapa `leitura` e `buscar` injetável em
      `bancada/pipeline.py` e verificar 5.1 e 5.2 verdes e
      `pytest bancada/tests` sem regressão
- [x] 5.4 Teste e implementação: falha de leitura gera
      `resposta = {"forma": "leitura", "causa": ...}` sem chamar `chat`;
      leitura parcial sem alegação para em `leitura` com `vazia`
- [x] 5.5 Teste e implementação de `rastro["origem"]` com todos os campos de
      D2, para texto e para página
- [x] 5.6 Teste e implementação de D7: `estrutura.responder(aviso=...)` põe
      `leitura_parcial` entre bordão e bloco 1 e conta no teto de 120
- [x] 5.7 Teste e implementação de D8: texto de página chega aos prompts de
      extração e decomposição entre delimitadores

## 6. Bancada

- [x] 6.1 Adicionar a `bancada/casos.json` casos com link (blog completo,
      paywall mole, parcial, só-JS, vídeo, IP interno, injeção) com `buscar`
      gravado, e gravações de modelo em `bancada/gravacoes/`; verificar com
      `python -m bancada` que todos rodam offline
- [x] 6.2 Rodar a bancada com modelo real nos casos de 6.1 e registrar em
      `docs/` a taxa de leitura completa, parcial e `vazia`; se algum limiar
      de D6 precisar mudar, atualizar spec e design antes do código

## 7. Interface

Depende de `interface/` existir em `main` (`add-interface-chat-web`).

- [x] 7.1 Remover o tratamento `so_link` e verificar que mensagem só com link
      roda o fluxo
- [x] 7.2 Teste e implementação: evento SSE da etapa `leitura` mostra
      "Abrindo o link…" na linha de andamento
- [x] 7.3 Teste e implementação: cada causa de falha mostra seu texto da
      spec, sem bordão, pergunta de confiança nem "Tentar de novo"
- [x] 7.4 Teste e implementação: cartão de origem abre a camada de detalhe
      quando `origem.tipo == "pagina"`, com link para a URL limpa
- [x] 7.5 Teste e implementação: aviso de leitura parcial aparece entre o
      bordão e o bloco 1; auditoria axe-core e teste de 320px continuam
      passando com o cartão de origem aberto
- [x] 7.6 Teste: depois de três buscas, nenhum HTML, URL ou texto extraído
      no diretório de trabalho nem no log do servidor

## 8. Fechamento

- [x] 8.1 Atualizar `docs/estado.md` e `docs/pendencias.md` com a entrada por
      link e a ordem de arquivamento de D10
- [x] 8.2 Rodar `pytest prototipo bancada interface` e verificar suíte verde
- [x] 8.3 Rodar `openspec validate add-entrada-por-link --strict` e verificar
      saída limpa
