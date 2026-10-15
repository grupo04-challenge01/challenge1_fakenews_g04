# Challenge 1 — Desinformação em Saúde (grupo 04)

Repositório do grupo 04 no Challenge 1 da residência em IA do Instituto
Eldorado. O grupo construiu a **Dona Checa**, um copiloto de verificação de
mensagens de saúde em português. Ela recebe a mensagem ou o link que a pessoa
recebeu, procura checagens de agências brasileiras e responde em quatro
blocos. A resposta pode trazer um veredito, mas nunca sozinho: ele vem com o
critério que o sustenta e com a fonte, que a pessoa pode conferir.

- **Repositório:** <https://github.com/grupo04-challenge01/challenge1_fakenews_g04>
- **Portfólio de pesquisa:** <https://grupo04-challenge01.github.io/challenge1_fakenews_g04/>
- **Vídeo explicativo:** pendente

## Entregáveis

| Entregável | Onde está |
| --- | --- |
| Portfólio de pesquisa | o site acima, gerado de [`docs/`](docs/) com MkDocs |
| Estrutura de avaliação de confiança | [matriz de confiança](docs/engage/kit-matriz-confianca.md) e [casos forenses](docs/forense/casos-forense.md) |
| Solução ou protótipo com IA | [`prototipo/`](prototipo/) e [`interface/`](interface/); resumo e resultados em [Protótipo e avaliação](docs/act/prototipo-avaliacao.md) |
| Apresentação e reflexão | change [`add-portfolio-showcase`](openspec/changes/add-portfolio-showcase/), tasks 5.1 e 5.2 |

### Entrega final

| Item pedido | Onde está |
| --- | --- |
| Datasets | [`datasets/`](datasets/), com [fontes](datasets/FONTES.md) e [tratamento](docs/investigate/tratamento-datasets.md) |
| Requisitos funcionais e não funcionais | [`docs/requisitos.md`](docs/requisitos.md) |
| Análise exploratória dos dados (EDA) | [`exploracao/eda_datasets.ipynb`](exploracao/eda_datasets.ipynb) |
| Guiding Questions | [`docs/engage/guiding-questions.md`](docs/engage/guiding-questions.md) |
| Organização, Scrum e papéis | [`docs/showcase/organizacao.md`](docs/showcase/organizacao.md) |
| Modelo de IA | [`prototipo/`](prototipo/) e [`exploracao/avaliacao_modelo.ipynb`](exploracao/avaliacao_modelo.ipynb) |
| Relatório técnico | [`docs/act/relatorio-tecnico.md`](docs/act/relatorio-tecnico.md) |
| Descrição final do produto | [Protótipo e avaliação](docs/act/prototipo-avaliacao.md) e o topo deste README |
| Código | [`prototipo/`](prototipo/), [`interface/`](interface/), [`bancada/`](bancada/), [`tratamento/`](tratamento/) |
| Apresentação para a banca | [`docs/showcase/apresentacao.md`](docs/showcase/apresentacao.md) |
| Vídeo explicativo | [roteiro](docs/showcase/roteiro-video.md); link pendente |

O estado de cada um e o que falta estão em
[Estado do projeto](docs/estado.md) e [Tasks pendentes](docs/pendencias.md).

## Como subir a demo

O guia completo, com todas as variáveis, está em
[Chat web da Dona Checa](docs/interface/chat-web.md). Para a demonstração,
use o commit da tag `showcase-demo` (decisão D5 de `add-portfolio-showcase`).

```bash
git checkout showcase-demo
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-interface.txt

cp .env.example .env     # preencha DONA_CHECA_MODO=uso e DEEPSEEK_API_KEY
set -a; source .env; set +a
python -m interface      # abre em http://127.0.0.1:8000
```

Antes da primeira mensagem, espere `http://127.0.0.1:8000/saude` responder
200. O índice carrega em segundo plano. A primeira consulta também carrega o
modelo de recuperação e demora mais que as outras.

## Como o trabalho é organizado

O projeto segue Spec-Driven Development com [OpenSpec](openspec/). Nada entra
no repositório sem um change que o cubra. As regras estão em
[`CLAUDE.md`](CLAUDE.md), e o contexto do projeto em
[`openspec/project.md`](openspec/project.md).

| Pasta | Conteúdo |
| --- | --- |
| [`openspec/changes/`](openspec/changes/) | um change por trabalho, com proposta, design, specs delta e tasks |
| [`openspec/specs/`](openspec/specs/) | specs promovidas; recebe os changes quando são arquivados |
| [`prototipo/`](prototipo/) | recuperação, verificação, resposta e índice |
| [`interface/`](interface/) | chat web (FastAPI, HTML e JS) |
| [`bancada/`](bancada/) | bancada de casos de ponta a ponta |
| [`datasets/`](datasets/) | corpora tratados, casos e sessões do piloto |
| [`docs/`](docs/) | fonte do portfólio |

Para rodar a suíte: `pip install -r requirements-interface-dev.txt` e depois
`pytest`.
