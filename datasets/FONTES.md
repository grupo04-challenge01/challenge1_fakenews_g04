# Fontes, licenças e atribuição

Este diretório contém dados de terceiros. Cada base abaixo tem fonte primária,
licença e citação próprias. **Atribuição é condição de uso** — em especial para
as bases sob CC BY, cuja licença exige crédito na redistribuição.

Coleta feita em 08/09/2026. As contagens estão em [`relatorio.json`](relatorio.json)
e a descrição de uso de cada base, em [`README.md`](README.md).

## O que está versionado e o que não está

O repositório é público e versiona apenas os **derivados** (tabelas prontas para
uso no projeto), a documentação, as licenças e os arquivos pequenos. Os corpora
brutos ficam fora do git — são 181 MB e nenhum deles é nosso.

| Caminho | Estado | Tamanho |
| --- | --- | --- |
| `derivados/` | versionado | 47 MB |
| `01_nucleo_metodologico/factckbr/` | versionado (dataset completo, 721 KB) | 725 KB |
| `02_comparacao_exagero/scientific_exaggeration/` | versionado (dataset completo) | 600 KB |
| `03_banco_estimulos/med_mmhl/` | versionado (só docs, licença e script) | 965 KB |
| `01_nucleo_metodologico/factcenter/central_de_fatos.csv` | **fora do git** | 54 MB |
| `01_nucleo_metodologico/pubhealth/*.csv` | **fora do git** | 65 MB |
| `01_nucleo_metodologico/fakehealth/{reviews,content,engagements}/` | **fora do git** | 53 MB |
| `03_banco_estimulos/fakerecogna2/fakerecogna_extrativo.csv` | **fora do git** | 42 MB |
| `01_nucleo_metodologico/whavax/WhaVax_dataset.csv` | **fora do git** (texto de mensagem e remetente) | 567 KB |
| `04_acervo_circulacao/telegram_antivacina_br/*.jsonl` | **fora do git** | 3,6 GB |

As exclusões estão no `.gitignore` da raiz. Para reconstituir o pacote completo,
baixe de cada fonte primária abaixo e confira contra os checksums da última seção.

## Bases

### PUBHEALTH

- **Citação:** Kotonya, N. & Toni, F. *Explainable Automated Fact-Checking for
  Public Health Claims.* EMNLP 2020.
- **Origem do arquivo baixado:** release original dos autores (TSV), não o loader
  do HuggingFace. Espelho conhecido: `bigbio/pubhealth` no HF Hub.
- **Motivo da escolha:** o loader do HF mapeia rótulos por índice; no TSV original
  os rótulos vêm como texto (`true/false/mixture/unproven`), o que elimina a
  fragilidade apontada no portfólio.
- **Licença:** não declarada no pacote baixado. **Verificar no release dos autores
  antes de qualquer redistribuição** — ver "Pendências" abaixo.
- **Derivado versionado:** `derivados/pubhealth_pool_fewshot.csv` (casos com
  explicação > 300 caracteres, 15 por classe).

### FakeHealth (HealthStory + HealthRelease)

- **Citação:** Dai, E., Sun, Y. & Wang, S. *Ginger Cannot Cure Cancer: Battling
  Fake Health News with a Comprehensive Data Repository.* arXiv:2002.00837.
- **Origem:** repositório dos autores, `EnyanDai/FakeHealth`. Conferido contra o
  ZIP do Zenodo, **DOI 10.5281/zenodo.3606757** — mesmo snapshot.
- **Licença: CC BY 4.0** — conferida em 20/09/2026 no registro do Zenodo
  (`10.5281/zenodo.3606757`, acesso aberto), não no repositório do GitHub, que
  não declara licença. Atribuição é condição de uso.
- **Nota do dataset:** os `engagements/` trazem apenas IDs de tweets, por política
  de privacidade do Twitter/X; o conteúdo não é redistribuível.
- **Caveat:** são **20** perguntas em dois conjuntos de 10 (HealthStory e
  HealthRelease), não 10. O nome do derivado
  `fakehealth_matriz_10_criterios.csv` está errado e foi mantido por
  estabilidade de referência.
- **Derivados versionados:** `derivados/fakehealth_criterios_long.csv`,
  `fakehealth_matriz_10_criterios.csv`, `fakehealth_reviews_indice.csv`.

### FactCenter / Central de Fatos

- **Licença: CC BY 4.0** — redistribuição permitida **com atribuição**.
- **Origem:** Zenodo, **DOI 10.5281/zenodo.5191798**. O link de dados não consta
  do artigo publicado no JIDM.
- **Composição:** 11.647 checagens em português, de 6 agências (boatos, Lupa,
  Aos Fatos, Fato ou Fake, Estadão Verifica, Comprova).
- **Derivado versionado:** `derivados/factcenter_subset_saude.csv` — 4.063
  checagens filtradas por termos de saúde e ciência.

- **Caveats medidos:** ver a seção «Caveats do tratamento» em [`README.md`](README.md).

### FACTCK.BR

- **Licença: MIT** (© 2019 jghm-f) para a estrutura do dataset. O **texto das
  checagens permanece das agências** (Aos Fatos, Lupa, Truco) — a licença MIT
  cobre o código e a organização, não o conteúdo jornalístico de terceiros.
- **Origem:** `thiagorainmaker77/FACTCK.BR`, espelho do original `jghm-f/FACTCK.BR`.
- **Composição:** 1.313 alegações em português, coletadas via schema ClaimReview.
- **Versionado por inteiro** (721 KB), com `LICENSE` e o script `update_factckbr.py`.

- **Caveats medidos:** ver a seção «Caveats do tratamento» em [`README.md`](README.md).

### Scientific Exaggeration (InSciOut)

- **Citação:** Wright, D. & Augenstein, I. *Semi-Supervised Exaggeration Detection
  of Health Science Press Releases.* EMNLP 2021. arXiv:2108.13493.
- **Origem:** repositório dos autores; também em `copenlu/scientific-exaggeration-detection`
  no HF Hub.
- **Anotação de origem:** derivada dos estudos de Sumner et al. 2014 (BMJ 349:g7015)
  e Bratton et al. 2019 — **cite os dois** ao usar os rótulos.
- **Composição:** 663 pares comunicado/abstract com rótulo `same`/`exaggerates`/`downplays`
  e o *strength* dos dois lados.
- **Versionado por inteiro.** Fora ficou só o `unlabelled_pet.jsonl` (18 MB), que
  serve apenas para treinar PET.
- **Licença: não declarada.** Conferido em 20/09/2026 na fonte primária, o
  repositório `copenlu/scientific-exaggeration-detection`, que **não traz
  arquivo de licença** — a API do GitHub devolve licença nula. O artigo é
  EMNLP 2021, Wright & Augenstein. **Verificar com os autores antes de
  qualquer redistribuição** — ver "Pendências" abaixo.
- **Caveat:** atravessa como **instrumento**, não como conteúdo. Nenhum texto
  em inglês do par comunicado/abstract é exibido ao usuário; o que cruza a
  fronteira de idioma é a escala de força da afirmação, renomeada em português.

### FakeRecogna 2.0 — substitui a v1 em 19/09/2026

**Registro da substituição (change `add-ampliacao-corpus-ptbr`, bloco 4).**

| Item | Valor |
| --- | --- |
| Base removida | FakeRecogna v1 — 11.903 itens, 5.951 por classe |
| Base nova | **FakeRecogna 2.0, variante extrativa** — 52.800 itens, 26.400 por classe |
| Data | 19/09/2026 |
| Motivo | a v1 termina em 2021 e tem um décimo do volume; a 2.0 alcança 2023 e vem de nove agências contra as seis do corpus principal |

**O que se perde na substituição.** Apenas a reprodutibilidade da seleção com
semente da v1. A amostra da v1 **não sofreu curadoria nem tratamento** —
confirmado pelo grupo em 10/09/2026 —, então nenhum trabalho manual é jogado
fora. O que sai é o par `random_state=42` sobre aquele arquivo específico.

- **Citação:** Garcia, G. L.; Paiola, P. H.; Jodas, D. S.; Sugi, L. A.; Papa,
  J. P. *Text Summarization and Temporal Learning Models Applied to Portuguese
  Fake News Detection in a Novel Brazilian Corpus Dataset.* PROPOR 2024,
  p. 86–96. `aclanthology.org/2024.propor-1.9`
- **Origem do arquivo baixado:** `recogna-nlp/fakerecogna2-extrativa` no
  HuggingFace — que **é** a organização dos próprios autores, não um agregador
  de terceiro.
- **Licença: MIT**, declarada pelos autores no cartão da 2.0. Caveat: o
  repositório da v1 (`Gabriel-Lino-Garcia/FakeRecogna`) não tem arquivo de
  licença nenhum, e o artigo não repete a declaração. A pendência de licença da
  FakeRecogna fica **baixada** para a 2.0, por declaração expressa dos autores.
- **Nove agências de origem:** Boatos.org (8.654), E-farsas (3.330), Agência
  Lupa (3.147), Aos Fatos (2.720), UOL Confere (2.579), Fato ou Fake (2.270),
  AFP Checamos (1.587), Estadão Verifica (1.405), Projeto Comprova (877).
  Três não estão no corpus principal: **E-farsas, UOL Confere e AFP Checamos**.

#### Caveats medidos em 19/09/2026

**1. Não há vocabulário de veredito.** O rótulo é binário (`Label` 0/1)
atribuído pela coleta, não a etiqueta publicada pela agência. A base entra como
banco de estímulos e **nunca** como fonte de veredito graduado.

**2. A transformação de texto é assimétrica por classe.** A notícia real passou
por sumarização extrativa na origem (mediana 684 caracteres, teto 1.493); a
falsa veio crua (mediana 294, até 12.904). Consequência medida: **um
classificador que só conta caracteres acerta 80,5%** nesta base balanceada,
contra 50% de linha de base. Nenhuma acurácia medida sobre ela sustenta
afirmação sobre detecção de desinformação.

**3. `Categoria` não é vocabulário compartilhado.** A classe real tem cinco
categorias; a falsa tem 69, das quais 64 não existem na real — incluindo 6.870
itens de categoria vazia e nomes de editoria de agência. Por isso o subset
temático **não** é gerado por categoria, e sim por termo de saúde sobre o
texto, aplicado igual às duas classes.

**4. Reprovada para citação.** `integridade-textual` reprova os derivados por
texto transformado na origem — não por perda de caractere. A base serve a
contagem e a estímulo declarado, nunca a trecho citado.

- **Derivados versionados:** `derivados/fakerecogna2_subset_saude_ciencia.csv`
  (26.436 itens: 18.784 reais, 7.652 falsos), `fakerecogna2_amostra_estimulos_300.csv`
  (300 itens, `random_state=42`) e `fakerecogna2_transformacao.json`.
- **Regerado por:** `datasets/scripts/regerar_fakerecogna2.py`.

### WhaVax — WhatsApp Vaccine Discourse

- **Citação:** *WhatsApp Vaccine Discourse (WhaVax): An Expert-Annotated Dataset
  and Benchmark for Health Misinformation Detection.* ICWSM 2026.
  arXiv:2605.12510.
- **Depósito:** Zenodo, registro `18190030`. **Licença: CC BY 4.0**, conferida
  no registro, não no arXiv.
- **O que é:** 950 mensagens de grupos públicos brasileiros do WhatsApp,
  anotadas por **quatro médicos**, maioria de 3 em 4, Fleiss' Kappa 0,621,
  janela 02/03/2020 a 07/11/2023.
- **Caveat de escala:** os 84.640 do artigo são o corpus filtrado; o conjunto
  **anotado por especialista** tem 950. Não são o mesmo número.
- **A faixa de empate é entregável:** 84 mensagens (8,8%) em que os quatro
  médicos empataram 2 a 2. Recuperável porque o pacote publica o voto por
  anotador; os autores as absorveram na classe não-desinformação.
- **Bruto fora do git** — contém texto de mensagem e identificador
  pseudonimizado de remetente. Detalhe em
  `01_nucleo_metodologico/whavax/README.md`.
- **Derivado versionado:** `derivados/whavax_agregados.json`.

### Acervo de circulação — Telegram antivacina (2020–2025)

- **Citação:** Cardenuto, J. P.; Monari, A. C. P.; Lopes, M. D.; Lusquino Filho,
  L. A. D.; Rocha, A. R. (2025). *Brazilian Social Media Anti-vaccine
  Information Disorder Dataset — Telegram.* REDU, Unicamp.
- **DOI:** `10.25824/redu/5JIVDT` · **Artigo:** arXiv:2601.18622
- **Licença: CC BY-NC 4.0** — atribuição e **uso não comercial**. A cláusula
  propaga a todo derivado gerado.
- **O que é:** 3.998.633 posts de 119 canais antivacina, janeiro/2020 a
  junho/2025. Contagem e janela **conferidas sobre o arquivo baixado**, com
  divergência zero.
- **Acesso assimétrico:** o `.jsonl` de texto (3,608 GB) é público; os 5,5 TB de
  mídia são restritos por acordo assinado, e não foram baixados.
- **Bruto fora do git.** Detalhe, usos vedados e viés de amostra em
  `04_acervo_circulacao/telegram_antivacina_br/README.md`.
- **Derivado versionado:** `derivados/telegram_agregados.json` — só contagens,
  sem texto de post e sem identificador de autor.

### Med-MMHL

- **Licença: CC BY-NC 4.0** — não comercial, compatível com uso acadêmico. Texto
  completo em `03_banco_estimulos/med_mmhl/LICENSE-CC-BY-NC-4.0.md`.
- **Citação:** *Med-MMHL: A Multi-Modal Dataset for Detecting Human- and
  LLM-Generated Misinformation in the Medical Domain.* arXiv:2306.08871.
- **Status: dados não baixados.** São ~4,0 GB num Dropbox, quase tudo imagem. O
  uso previsto é teste de estresse condicional; o comando está pronto em
  `baixar_med_mmhl.sh`, junto do apêndice do artigo e da licença.

## Pendências de licença

**Duas** bases têm derivado versionado neste repositório público sem licença
declarada na fonte:

1. **PUBHEALTH** — `derivados/pubhealth_pool_fewshot.csv`
2. **InSciOut / Scientific Exaggeration** — `derivados/exagero_pares_abstract_vs_release.csv`
   e os quatro arquivos em `02_comparacao_exagero/`

A pendência da **FakeRecogna foi baixada em 19/09/2026**: a 2.0 declara MIT no
cartão dos próprios autores, e a v1 saiu do repositório. A do **FakeHealth foi
baixada em 20/09/2026**: CC BY 4.0 no registro do Zenodo.

Antes da entrega, conferir a licença das duas na fonte primária. Se a
redistribuição não for permitida, mover o arquivo para o `.gitignore` e deixar
apenas o script que o reconstrói. Nenhum uso interno do grupo fica bloqueado por
isso — a pendência é sobre publicar, não sobre usar.


## Checksums dos brutos baixados em 19/09/2026

```
ba70bcf773be0559d75cb6fcbb1757d0686051fa1b6191ed2c787448c0089d84  03_banco_estimulos/fakerecogna2/fakerecogna_extrativo.csv
5f9e9381551f4244882f9586072d557888d391bb491d6e109a2f78ad7b7f52f1  01_nucleo_metodologico/whavax/WhaVax_dataset.csv
bc8223d59dcfcbc4ed9d5b6e0bfa1bde0116df14660096d32c38a18d1daa9abe  04_acervo_circulacao/telegram_antivacina_br/telegram-vaccine-info-disorder-dataset-2020-2025.jsonl
a798984e09ca6b7f20dba8c7ed029b7c5e4586e70cb084fcd18304ca17bb4822  04_acervo_circulacao/telegram_antivacina_br/readme.pdf
```

## Checksums dos brutos não versionados

SHA-256, para conferir um download novo contra o snapshot de 08/09/2026:

```
2ac61adced62eee5cd89d438cc010946e5103161467e999f6f31ccfa316126e5  01_nucleo_metodologico/factcenter/central_de_fatos.csv
12a95e5760500b5f7e3acb5094db250398b627a9a1cef4d1f27497e810f47c28  01_nucleo_metodologico/pubhealth/train_limpo.csv
c715f2ac953626378ef5244318ded58be8843d4fea1815678f49749b5ee614f7  01_nucleo_metodologico/pubhealth/dev_limpo.csv
ba98fbfb64084f9613ac6b3ba7023648bcafd4297178b1d5bf44585eed3ce16c  01_nucleo_metodologico/pubhealth/test_limpo.csv
4d9db2ec053888234313e8ef9a8c999fe9b57cbc3dea8c0181c217827256fd7c  01_nucleo_metodologico/fakehealth/reviews/HealthStory.json
f0c800154e29f1df8599b91c337ae362641083aa44e3c93f3a75186b861dcd1f  01_nucleo_metodologico/fakehealth/reviews/HealthRelease.json
85c87c2462106232da708e7e1707583157ad2a7b82af1387c54cfe990e6dd564  01_nucleo_metodologico/fakehealth/engagements/HealthStory.json
1e369e609814a0ae0bed39d33c8a07c480350a73e2da7c2db7a50ab16e22cb9f  01_nucleo_metodologico/fakehealth/engagements/HealthRelease.json
```

`01_nucleo_metodologico/fakehealth/content/` não entra na lista acima: são 2.237
arquivos JSON (23 MB) do texto das notícias. Os checksums dos arquivos versionados
estão em [`SHA256SUMS`](SHA256SUMS).
