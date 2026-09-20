# Acervo de circulação — Telegram antivacina brasileiro (2020–2025)

Camada `04_acervo_circulacao`, criada em **19/09/2026** pelo change
`add-ampliacao-corpus-ptbr`, bloco 6. É um nível próprio do acervo, **não um
quarto corpus citável**: aqui está o que circulou, não o que foi verificado.

## Citação e licença

- **Citação:** Cardenuto, João Phillipe; Monari, Ana Carolina Pontalti; Lopes,
  Michelle Diniz; Lusquino Filho, Leopoldo Andre Dutra; Rocha, Anderson de
  Rezende (2025). *Brazilian Social Media Anti-vaccine Information Disorder
  Dataset — Telegram.* REDU, Unicamp.
- **DOI:** `10.25824/redu/5JIVDT`
- **Artigo:** arXiv:2601.18622
- **Licença:** **CC BY-NC 4.0** — atribuição obrigatória e **uso não
  comercial**. Conferida no depósito do REDU em 19/09/2026, não no arXiv.

### A cláusula não comercial propaga (task 6.7)

Todo derivado gerado a partir desta base herda CC BY-NC 4.0 e a exigência de
atribuição. Os derivados em `datasets/derivados/telegram_*.json` carregam a
cláusula no próprio arquivo; qualquer derivado novo MUST fazer o mesmo.

## Arquivos e condição de acesso

| Arquivo | Tamanho | Acesso | Está aqui? |
| --- | --- | --- | --- |
| `telegram-vaccine-info-disorder-dataset-2020-2025.jsonl` | 3.608.168.366 bytes (3,608 GB) | **público** | sim, **fora do git** |
| `readme.pdf` | 35 KB | público | sim, versionado |
| Mídia (imagem, vídeo, áudio) | **5,5 TB** | **restrito**, exige acordo assinado | **não, e não deve ser baixada** |

SHA-256 do `.jsonl`:
`bc8223d59dcfcbc4ed9d5b6e0bfa1bde0116df14660096d32c38a18d1daa9abe`

A assimetria de acesso é do próprio depósito: o texto é aberto, a mídia é
restrita. O projeto baixa só o texto, e isso é decisão de escopo, não limitação.

## Escala declarada pelos autores

| Medida | Valor |
| --- | --- |
| Posts | 3.998.633 |
| Canais | 119 |
| Usuários anonimizados | 71.672 |
| Mensagens com texto | 3.345.088 (83,6%) |
| Posts relacionados a vacina | 407.723 (10,2%) |
| Janela | janeiro/2020 a junho/2025 |
| Itens de mídia | 1,44 milhão |

A medição própria, feita em streaming sobre o arquivo baixado, está em
`datasets/derivados/telegram_agregados.json`.

## `is_vaccine_related` é rótulo derivado, não classificação verificada (task 6.2)

| Item | Valor |
| --- | --- |
| Método | prompt sobre modelo de linguagem |
| Modelo | **Sabiá-3** |
| Desempenho | **F1 de 0,90** contra anotadores humanos |
| Critério | menção a vacina/imunização, discussão de eficácia ou segurança, discussão de política, teoria conspiratória, hesitação |

Um em cada dez rótulos está errado, e o erro não é aleatório: modelo de
linguagem erra mais nos casos ambíguos, que são exatamente os interessantes.
**O campo MUST ser tratado como filtro de busca, nunca como verdade sobre o
post.** Nenhuma afirmação do projeto pode depender só dele.

## Critério de seleção dos canais e o viés que ele produz (task 6.3)

Os 119 canais foram selecionados por serem **públicos, com pelo menos 1.000
membros**, monitorados a partir de palavras-chave antivacina — entre elas
`mRNA`, `Nova Ordem Mundial` e `Efeitos adversos`.

Três consequências, todas restritivas:

1. **A amostra é de comunidade antivacina, por construção.** Não é amostra do
   Telegram brasileiro, nem da população, nem do debate sobre vacinação.
2. **Só canais grandes e públicos.** Grupo pequeno, privado ou familiar — que é
   onde a desinformação em saúde mais circula no Brasil — está ausente.
3. **Leitura de prevalência é VEDADA.** Dizer "X% dos brasileiros acredita em Y"
   ou "a alegação Z cresceu na população" a partir desta base é erro de
   inferência, e a vedação é explícita.

O que a base **pode** sustentar é comparação **interna**: o que cresceu dentro
desses canais, quando, e em que ordem.

## Usos permitidos e vedados (task 6.6)

**Vedado:**

- **Fonte de citação sobre o mérito.** Post de usuário não é evidência sobre a
  alegação ser verdadeira ou falsa. A base não tem veredito.
- **Veredito por proxy de canal.** «Apareceu em canal antivacina, logo é falso»
  é raciocínio de procedência, não de evidência, e viola o princípio de
  auditabilidade até a fonte.
- **Estimativa de prevalência**, pelo motivo acima.
- **Re-identificação** de qualquer usuário, tentativa de reverter os hashes, ou
  cruzamento com outra base para esse fim.

**Permitido:**

- Medir **o que circulou, em que canal e quando** — o único insumo que nenhuma
  base de checagem fornece, porque agência publica o desmentido, não a difusão.
- Caracterizar formato e técnica retórica, de forma agregada.
- Datar o aparecimento de uma pauta, para a declaração de cobertura.

## Privacidade e o que não é versionado (task 6.5)

Os autores aplicaram: hash SHA-256 com sal privado nos identificadores de
usuário e canal, remoção de PII do texto com Microsoft Presidio, e remoção dos
eventos de entrada e saída de canal, para impedir re-identificação por padrão
temporal.

O projeto acrescenta uma camada: **nenhum texto de post e nenhum `user_id` é
versionado**, nem mesmo como exemplo dentro de documentação. Os derivados
gerados contêm apenas contagens.

## Limitações declaradas pelos autores

1. **Reações só existem a partir de 30/12/2021** — o recurso não existia no
   Telegram antes disso. Ausência de reação antes dessa data não é desengajamento.
2. **Mídia acima de 50 MB foi excluída** da coleta.
3. **Conteúdo apagado** por administrador de canal ou por decisão do Supremo
   Tribunal Federal durante o período pode estar ausente — o que produz queda
   abrupta em meses específicos, por canal.

As três foram **medidas** sobre o arquivo baixado, não copiadas do artigo; o
resultado está em `datasets/derivados/telegram_agregados.json`, seção
`lacunas_medidas`.

## Reconstituir

```bash
curl -L -o telegram-vaccine-info-disorder-dataset-2020-2025.jsonl \
  https://redu.unicamp.br/api/access/datafile/23436
curl -L -o readme.pdf https://redu.unicamp.br/api/access/datafile/25435
sha256sum -c ../../SHA256SUMS
python datasets/scripts/medir_telegram.py
```
