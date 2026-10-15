# Arquitetura

Arquitetura da Dona Checa em diagramas, do contexto ao código. Cada diagrama
cita os arquivos de onde saiu; número ou limiar que aparece nele está no
código citado. Change `add-arquitetura-diagramas`. Estado do código em
15/10/2026.

!!! tip "Mapa interativo"
    Para navegar pela arquitetura inteira, com fluxos guiados e as decisões
    de projeto, abra o [mapa da Dona Checa](mapa/arquitetura.html). Arraste
    para mover, role para aproximar e clique em qualquer card.

Legenda de cores usada em todos os diagramas:

```mermaid
flowchart LR
    P([Pessoa]):::pessoa
    S[Componente nosso]:::nosso
    L[Chamada ao modelo de linguagem]:::llm
    E[Sistema externo]:::externo
    D[(Dado ou índice)]:::dado
    classDef pessoa fill:#fde68a,stroke:#92400e,color:#1f2937
    classDef nosso fill:#dbeafe,stroke:#1e40af,color:#1f2937
    classDef llm fill:#fce7f3,stroke:#9d174d,color:#1f2937
    classDef externo fill:#e5e7eb,stroke:#374151,color:#1f2937,stroke-dasharray:4 3
    classDef dado fill:#dcfce7,stroke:#166534,color:#1f2937
```

## 1. Contexto

Quem usa a Dona Checa e com quais sistemas ela conversa (nível 1 do modelo
C4).

```mermaid
flowchart LR
    pessoa([Pessoa que recebeu<br/>mensagem de saúde]):::pessoa
    dona[Dona Checa<br/>copiloto de verificação]:::nosso
    deepseek[API DeepSeek<br/>deepseek-v4-pro]:::externo
    ollama[Ollama local<br/>gemma4:12b-it-qat]:::externo
    sites[Sites de notícia<br/>link colado pela pessoa]:::externo
    hub[Hugging Face Hub<br/>multilingual-e5-base]:::externo
    agencias[Agências de checagem<br/>Lupa, Boatos.org, Aos Fatos,<br/>Fato ou Fake, Estadão Verifica,<br/>Comprova, Pública]:::externo
    corpus[(FactCenter e FACTCK.BR<br/>checagens publicadas)]:::dado

    pessoa -- "mensagem ou link" --> dona
    dona -- "veredito + critério + fonte" --> pessoa
    dona -- "texto minimizado, com consentimento" --> deepseek
    dona -. "modo piloto ou recusa do termo" .-> ollama
    dona -- "busca a página, guarda contra SSRF" --> sites
    dona -. "baixa o modelo na 1ª consulta" .-> hub
    agencias -- "publicam" --> corpus
    corpus -- "índice construído offline" --> dona

    classDef pessoa fill:#fde68a,stroke:#92400e,color:#1f2937
    classDef nosso fill:#dbeafe,stroke:#1e40af,color:#1f2937
    classDef externo fill:#e5e7eb,stroke:#374151,color:#1f2937,stroke-dasharray:4 3
    classDef dado fill:#dcfce7,stroke:#166534,color:#1f2937
```

Origem: `interface/config.py`, `prototipo/verificacao/modelo.py`,
`prototipo/entrada/rede.py`, `prototipo/rag/densa.py`,
`prototipo/resposta/agencias.py`.

## 2. Contêineres

O que roda e onde (nível 2 do C4). Um único processo Python serve a página e
roda o fluxo; o índice fica inteiro em memória, sem banco vetorial.

```mermaid
flowchart TB
    pessoa([Pessoa]):::pessoa

    subgraph nav["Navegador"]
        pagina["Página do chat<br/>HTML, CSS e JS puros, sem build<br/>interface/estatico/"]:::nosso
    end

    subgraph proc["Processo Python único · uvicorn · python -m interface"]
        api["FastAPI<br/>GET / · GET /saude · POST /verificar<br/>streaming SSE · 1 verificação por vez · 300 s"]:::nosso
        fluxo["Fluxo do copiloto<br/>bancada/pipeline.py · 7 etapas"]:::nosso
        rec["Recuperador híbrido em memória<br/>BM25 + e5 · prototipo/rag/"]:::nosso
        textos["Textos da persona e da interface<br/>lidos das specs do OpenSpec"]:::dado
    end

    subgraph disco["Disco · prototipo/indice/"]
        direction LR
        frag[("fragmentos.jsonl<br/>23.655 fragmentos · 57 MB")]:::dado
        unid[("unidades.jsonl<br/>6.279 checagens · 23 MB")]:::dado
        densa[("densa.npy<br/>23.655 × 768 float32 · 69 MB")]:::dado
    end

    deepseek["API DeepSeek"]:::externo
    ollama["Ollama · localhost:11434"]:::externo

    pessoa --> pagina
    pagina -- "POST /verificar" --> api
    api -- "eventos SSE" --> pagina
    api --> fluxo
    fluxo --> rec
    fluxo --> textos
    rec -- "carga única em thread<br/>/saude = 503 até terminar" --> disco
    fluxo -- "modo uso" --> deepseek
    fluxo -. "modo piloto" .-> ollama

    classDef pessoa fill:#fde68a,stroke:#92400e,color:#1f2937
    classDef nosso fill:#dbeafe,stroke:#1e40af,color:#1f2937
    classDef externo fill:#e5e7eb,stroke:#374151,color:#1f2937,stroke-dasharray:4 3
    classDef dado fill:#dcfce7,stroke:#166534,color:#1f2937
```

Origem: `interface/app.py`, `interface/__main__.py`, `interface/fluxo.py`,
`prototipo/rag/__main__.py` (`carregar`), `prototipo/indice/manifesto.json`.

## 3. Fluxo das sete etapas

O caminho de uma mensagem. Em rosa, as etapas que chamam o modelo de
linguagem. Cada losango é uma saída antecipada: o fluxo para ali e a página
recebe o motivo.

```mermaid
flowchart TD
    entrada([Mensagem ou link]):::pessoa --> separar["Separa links do texto<br/>entrada/link.py"]:::nosso
    separar --> F["1 · Fronteira<br/>regras PT-BR, depois modelo"]:::llm
    F --> Fq{"Urgência ou<br/>sofrimento psíquico?"}
    Fq -- sim --> Fsai([Resposta padrão<br/>de orientação]):::saida
    Fq -- "conduta ou diagnóstico" --> Fred["Anexa redirecionamento<br/>e segue"]:::nosso
    Fq -- não --> Lq
    Fred --> Lq{"Link e menos de<br/>30 palavras da pessoa?"}
    Lq -- sim --> L["2 · Leitura da página<br/>trafilatura · até 800 palavras"]:::nosso
    Lq -- não --> X
    L --> Lf{"Página abriu?"}
    Lf -- "não: fechada, vídeo,<br/>vazia, não abriu" --> Lsai([Aviso com a causa]):::saida
    Lf -- sim --> X["3 · Extração<br/>escolhe a alegação de saúde<br/>de maior risco"]:::llm
    X --> Xq{"Alegação<br/>verificável?"}
    Xq -- não --> Xsai([Aviso: sem alegação<br/>verificável de saúde]):::saida
    Xq -- sim --> D["4 · Decomposição<br/>fato, evidência, opinião"]:::llm
    D --> R["5 · Recuperação híbrida<br/>top 5 checagens"]:::nosso
    R --> G["6 · Guarda<br/>classifica só com trecho citável"]:::llm
    G --> RS["7 · Resposta em 4 blocos<br/>+ conferência de sustentação"]:::llm
    RS --> fim([Veredito + critério + fonte]):::pessoa

    classDef pessoa fill:#fde68a,stroke:#92400e,color:#1f2937
    classDef nosso fill:#dbeafe,stroke:#1e40af,color:#1f2937
    classDef llm fill:#fce7f3,stroke:#9d174d,color:#1f2937
    classDef saida fill:#fee2e2,stroke:#991b1b,color:#1f2937
```

Origem: `bancada/pipeline.py` (`executar`, `ETAPAS`, `PALAVRAS_TEXTO_CURTO`),
`prototipo/verificacao/fronteira.py`, `prototipo/entrada/leitura.py`,
`prototipo/verificacao/extracao.py`.

## 4. Sequência de uma verificação

O que acontece entre o clique em «Verificar» e a resposta na tela. A página
recebe um evento por etapa, então a pessoa vê o andamento.

```mermaid
sequenceDiagram
    autonumber
    actor P as Pessoa
    participant N as Página
    participant A as FastAPI
    participant F as Fluxo
    participant R as Recuperador
    participant M as DeepSeek

    P->>N: cola a mensagem e aceita o termo v3
    N->>A: POST /verificar {texto, consentimento: "3"}
    alt termo ausente ou versão antiga
        A-->>N: 403 {"erro": "consentimento"}
    else termo aceito
        A->>A: minimizar: e-mail, CPF e telefone viram marcadores
        A->>A: semáforo: 1 verificação por vez
        A->>F: verificar em thread, prazo de 300 s
        F->>M: fronteira
        F-->>N: data: {tipo: fronteira}
        F-->>N: data: {tipo: andamento, etapa: extracao}
        F->>M: extração e decomposição
        F-->>N: data: {tipo: andamento, etapa: recuperacao}
        F->>R: recuperar(alegação, k=5)
        R-->>F: trechos com escore
        F->>M: guarda: rótulo + critério + ids dos trechos
        F->>M: resposta em 4 blocos + conferência
        F-->>N: data: {tipo: resposta, texto, detalhe, origem}
    end
    N-->>P: 4 blocos + «Ver fontes e detalhes»
```

Origem: `interface/app.py` (`gerador_do_pedido`, `Semaphore(1)`,
`TERMO_VERSAO`), `interface/fluxo.py` (`verificar`),
`prototipo/entrada/minimizar.py`.

## 5. Recuperação híbrida

Como a alegação vira as cinco checagens que a guarda vai ler. Dois braços
pontuam em paralelo; cada escore é normalizado contra a própria distribuição
da consulta antes da fusão.

```mermaid
flowchart LR
    q([Alegação extraída]):::pessoa
    q --> lex["BM25 Okapi<br/>sem acento · mantém «não»"]:::nosso
    q --> den["e5-base<br/>prefixo query: · vetor normalizado"]:::nosso
    den --> prod["Produto escalar contra<br/>densa.npy 23.655 × 768"]:::nosso
    lex --> nl["Normaliza<br/>p50 a p99 da consulta"]:::nosso
    prod --> nd["Normaliza<br/>p50 a p99 da consulta"]:::nosso
    nl -- "× 0,1" --> fus["Fusão<br/>α·denso + 1−α·léxico<br/>α = 0,9"]:::nosso
    nd -- "× 0,9" --> fus
    fus --> uni["1 fragmento por checagem<br/>entre os 200 melhores"]:::nosso
    uni --> idi{"Algum trecho pt-BR<br/>com escore ≥ 0,55?"}
    idi -- sim --> top["Top 5 em pt-BR<br/>coberto = sim"]:::dado
    idi -- "não: tenta en" --> nc["Top 5 da 1ª camada<br/>não vazia · coberto = não"]:::dado

    classDef pessoa fill:#fde68a,stroke:#92400e,color:#1f2937
    classDef nosso fill:#dbeafe,stroke:#1e40af,color:#1f2937
    classDef dado fill:#dcfce7,stroke:#166534,color:#1f2937
```

Na aferição com 20 consultas reais, a fusão teve Recall@5 de 1,00 e MRR de
0,897, contra 0,725 de MRR do BM25 sozinho.

Origem: `prototipo/rag/hibrida.py` (`ALFA_PADRAO`, `LIMIAR_EVIDENCIA`,
`PRIORIDADE_IDIOMA`, `recuperar`), `prototipo/rag/lexica.py`,
`prototipo/rag/densa.py`; números em
[Protótipo e avaliação](act/prototipo-avaliacao.md).

## 6. Guarda e resposta: veredito nunca nu

Onde o código impede veredito sem fonte. O modelo propõe o rótulo; o código
decide se ele sobrevive.

```mermaid
flowchart TD
    t([Trechos recuperados]):::dado --> c1{"Algum trecho com<br/>escore ≥ 0,55 e<br/>apto a citação?"}
    c1 -- não --> ins["Rótulo: evidência insuficiente<br/>sem chamar o modelo"]:::nosso
    c1 -- sim --> cls["Classificação<br/>rótulo + critério + ids dos trechos"]:::llm
    cls --> c2{"Ids citados existem<br/>entre os trechos?"}
    c2 -- não --> ins
    c2 -- sim --> ver["Veredito com critério:<br/>falso · verdadeiro ·<br/>fora de contexto ou exagerado"]:::nosso
    ver --> gen["Gera 4 blocos<br/>abertura do bloco 1 escrita pelo código"]:::llm
    ins --> sem["4 blocos da forma sem evidência<br/>o que foi procurado e onde conferir"]:::llm
    gen --> anc{"Blocos 1 e 2 ancorados<br/>em trecho? 1 nova tentativa"}
    anc -- não --> sem
    anc -- sim --> conf["Conferência de sustentação<br/>remove frase sem base"]:::llm
    conf --> chk["Checagens em código:<br/>mito marcado · técnica do catálogo ·<br/>até 120 palavras"]:::nosso
    chk --> out([Resposta + agência, data e link<br/>da checagem citada]):::pessoa
    sem --> out2([Resposta sem veredito]):::pessoa

    classDef pessoa fill:#fde68a,stroke:#92400e,color:#1f2937
    classDef nosso fill:#dbeafe,stroke:#1e40af,color:#1f2937
    classDef llm fill:#fce7f3,stroke:#9d174d,color:#1f2937
    classDef dado fill:#dcfce7,stroke:#166534,color:#1f2937
```

Os quatro blocos com evidência: **veredito**, **o que se sabe**, **por que
essa mensagem engana** e **o que observar da próxima vez**.

Origem: `prototipo/verificacao/guarda.py`,
`prototipo/verificacao/classificacao.py`, `prototipo/resposta/estrutura.py`
(`COM`, `SEM`, `ABERTURA`), `prototipo/resposta/conferencia.py`,
`prototipo/resposta/ancoragem.py`, `prototipo/resposta/mito.py`.

## 7. Pipeline de dados

Como as checagens publicadas viram o índice. Roda offline, uma vez, com
`python -m prototipo.rag construir`.

```mermaid
flowchart LR
    fc[("FactCenter · saúde<br/>4.063 checagens<br/>2013 a 2021 · CC BY 4.0")]:::dado
    fk[("FACTCK.BR<br/>984 checagens<br/>2016 a 2019")]:::dado
    fc & fk --> gate["Portões de integridade<br/>FACTCK.BR perdeu acentos:<br/>só metadado, nunca citado"]:::nosso
    gate --> un["Unidades<br/>alegação + veredito + justificativa<br/>6.279 unidades"]:::nosso
    gate --> qua[("quarentena.jsonl<br/>174 registros")]:::dado
    un --> fr["Fragmentos<br/>1.100 caracteres, 150 de sobreposição<br/>cabeçalho repetido em cada um"]:::nosso
    fr --> esq["Validação contra<br/>esquema_indexacao.json"]:::nosso
    esq --> j1[("unidades.jsonl<br/>fragmentos.jsonl")]:::dado
    esq --> emb["e5-base · prefixo passage:"]:::nosso
    emb --> j2[("densa.npy")]:::dado
    j1 & j2 --> man[("manifesto.json<br/>contagens e custo")]:::dado

    classDef nosso fill:#dbeafe,stroke:#1e40af,color:#1f2937
    classDef dado fill:#dcfce7,stroke:#166534,color:#1f2937
```

Nenhum modelo é treinado: o dataset é acervo para citar, não alvo de
classificador.

Origem: `prototipo/rag/__main__.py` (`construir`), `prototipo/rag/corpus.py`,
`prototipo/rag/unidades.py`, `prototipo/indice/manifesto.json`.

## 8. Avaliação

Como o grupo mede sem gastar API a cada teste. A bancada grava as chamadas ao
modelo e à rede e as repete offline; a mesma função `executar` serve a bancada
e o chat.

```mermaid
flowchart LR
    casos[("bancada/casos.json<br/>35 casos com esperado por etapa")]:::dado
    casos --> exe["bancada/pipeline.executar<br/>o mesmo fluxo do chat"]:::nosso
    exe <--> grav["Gravação<br/>chamada indexada por hash"]:::nosso
    grav <-. "rodada ao vivo" .-> api["DeepSeek"]:::externo
    grav <--> dir[("bancada/gravacoes/<br/>replay offline")]:::dado
    exe --> av["Avaliação por etapa<br/>fronteira · alegação · checagem no topo ·<br/>rótulo · forma · leitura"]:::nosso
    av --> rel["Rodada da demo, 13/10<br/>29 de 30 casos · mediana 13,8 s"]:::dado
    pil([Piloto com 2 pessoas<br/>prototipo/avaliacao/]):::pessoa --> disc["Ganho de discernimento<br/>métrica primária"]:::dado

    classDef pessoa fill:#fde68a,stroke:#92400e,color:#1f2937
    classDef nosso fill:#dbeafe,stroke:#1e40af,color:#1f2937
    classDef externo fill:#e5e7eb,stroke:#374151,color:#1f2937,stroke-dasharray:4 3
    classDef dado fill:#dcfce7,stroke:#166534,color:#1f2937
```

Origem: `bancada/gravacao.py`, `bancada/avaliacao.py`, `bancada/casos.json`;
números em [Protótipo e avaliação](act/prototipo-avaliacao.md#rodada-da-demo).

## 9. Implantação

Estado em 15/10/2026: o chat roda na máquina de quem apresenta, e só o
portfólio é publicado. A hospedagem pública do chat é tratada em change
próprio.

```mermaid
flowchart LR
    subgraph gh["GitHub"]
        repo["Repositório<br/>grupo04-challenge01"]:::nosso
        ci["Actions: deploy mkdocs<br/>a cada push na main"]:::nosso
        pages["GitHub Pages<br/>portfólio de pesquisa"]:::nosso
    end
    subgraph mac["MacBook Air M4 · Python 3.14.6"]
        srv["python -m interface<br/>127.0.0.1:8000"]:::nosso
        idx[("prototipo/indice/<br/>gerado localmente,<br/>fora do git")]:::dado
        env[("DEEPSEEK_API_KEY<br/>variável de ambiente")]:::dado
        olla["Ollama · Metal"]:::externo
    end
    repo --> ci --> pages
    repo -- "git checkout showcase-demo" --> srv
    idx --> srv
    env --> srv
    srv -.-> olla
    srv -- HTTPS --> ds["API DeepSeek"]:::externo
    banca([Banca e visitantes]):::pessoa --> pages
    banca -- "navegador da máquina" --> srv

    classDef pessoa fill:#fde68a,stroke:#92400e,color:#1f2937
    classDef nosso fill:#dbeafe,stroke:#1e40af,color:#1f2937
    classDef externo fill:#e5e7eb,stroke:#374151,color:#1f2937,stroke-dasharray:4 3
    classDef dado fill:#dcfce7,stroke:#166534,color:#1f2937
```

Origem: `.github/workflows/deploy.yml`, `interface/config.py`
(`DONA_CHECA_HOST`), `.gitignore`.

## 10. Pacotes

Quem importa quem. O fluxo em `bancada/` é o centro: o chat e a bancada usam
a mesma função.

```mermaid
flowchart TD
    interface["interface/<br/>servidor, config, eventos"]:::nosso --> bancada["bancada/<br/>pipeline.executar"]:::nosso
    bancada --> verif["prototipo/verificacao/<br/>fronteira, extração, decomposição,<br/>classificação, guarda, modelo"]:::nosso
    bancada --> entrada["prototipo/entrada/<br/>link, rede, leitura, minimizar"]:::nosso
    bancada --> rag["prototipo/rag/<br/>léxica, densa, híbrida, construção"]:::nosso
    bancada --> resp["prototipo/resposta/<br/>estrutura, ancoragem, conferência,<br/>mito, catálogo"]:::nosso
    interface --> entrada
    resp --> ident["prototipo/identidade/<br/>textos da persona"]:::nosso
    verif & ident & interface & entrada --> specs[("openspec/changes/*/specs/<br/>textos lidos em execução")]:::dado
    rag --> indice[("prototipo/indice/")]:::dado
    rag -. "só na construção" .-> trat["tratamento/<br/>integridade dos datasets"]:::nosso
    trat --> ds[("datasets/")]:::dado

    classDef nosso fill:#dbeafe,stroke:#1e40af,color:#1f2937
    classDef dado fill:#dcfce7,stroke:#166534,color:#1f2937
```

Origem: imports de `interface/app.py`, `interface/fluxo.py`,
`bancada/pipeline.py`, `prototipo/rag/corpus.py`.
