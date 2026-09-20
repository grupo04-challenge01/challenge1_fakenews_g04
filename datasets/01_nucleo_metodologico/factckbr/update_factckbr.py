# Auto Upload Fact-Check Dataset
# Feeds:
# https://aosfatos.org/noticias/feed/
# https://apublica.org/feed/
# https://piaui.folha.uol.com.br/lupa/feed/
#
# ---------------------------------------------------------------------------
# REPARO — change `add-tratamento-datasets-ptbr`, tasks 3.4 e 4.5 (19/09/2026)
#
# Código de terceiro (licença MIT, ver LICENSE). Três defeitos corrigidos, todos
# exigidos em texto expresso pelas capabilities do change:
#
# 1. `re_char()` filtrava por allowlist que continha apenas as acentuadas
#    MINÚSCULAS. Toda maiúscula acentuada e o `ü` eram descartados em silêncio —
#    é a causa raiz do `Sistema nico de Saúde` em `factckbr_normalizado.csv`.
#    Substituída por normalização Unicode que não descarta caractere de texto:
#    só caracteres de controle saem. (`integridade-textual`, requirement
#    "Correção da causa a montante".)
#
# 2. `text_pre_proc()` aplicava a mesma allowlist ao bloco JSON-LD antes de
#    `ast.literal_eval`. Além de mutilar o texto, `literal_eval` não é parser de
#    JSON: `true`, `false` e `null` quebram. Passou a usar `json.loads`.
#
# 3. `update_dataset()` usava `DataFrame.append`, removido no pandas 2.0.
#    Substituído por `pd.concat`. (`frescor-corpus`, requirement "Caminho de
#    atualização com cobertura declarada": o script MUST ser reparado antes do uso.)
#
# ATENÇÃO — o reparo vale para coleta FUTURA. O `FACTCKBR.tsv` distribuído já
# vem com as maiúsculas acentuadas perdidas na origem, e nenhuma reexecução
# deste script recupera o que não está no arquivo. Ver `docs/investigate/
# tratamento-datasets.md`, seção "O que não dá para reparar".
#
# COBERTURA — três feeds (Aos Fatos, Agência Pública/Truco, Lupa) contra as seis
# agências do corpus principal. Não é atualização do corpus completo.
# ---------------------------------------------------------------------------

import ast  # noqa: F401  (mantido: parte da API original do script)
import json
import re  # noqa: F401  (mantido: parte da API original do script)
import unicodedata
import xml.sax.saxutils as saxutils

import pandas as pd

# Caracteres de controle que não são quebra de linha nem tabulação. Nada mais
# é descartado: acento, cedilha, trema e maiúscula acentuada são texto.
CONTROLE_PRESERVADO = {"\n", "\r", "\t"}


# Get links list from websites feed
def get_articles_url(url):
    import feedparser

    d = feedparser.parse(url)
    linksList = []
    for post in d.entries: linksList.append(post.link)
    return linksList

# Save dataset to tsv file
def save_tsv_pandas(data, file_name):
    data.to_csv("./" + file_name + ".tsv", sep='\t', index=True, encoding='utf-8')

# Load dataset from tsv file
def load_tsv_pandas(file_name):
    return pd.read_csv(file_name+".tsv", sep='\t', index_col=0)

# Update dataset. URL is primary key.
def update_dataset(dataset, new_entries):
    temp_df = pd.concat([dataset, new_entries])
    temp_df = temp_df[~temp_df.index.duplicated(keep='first')]
    return temp_df

def re_char(str):
    """Normaliza sem descartar caractere de texto.

    A allowlist original removia toda maiúscula acentuada. Aqui só saem os
    caracteres de controle, e a forma composta (NFC) é fixada para que `ç` e
    `Ç` tenham uma única representação no arquivo.
    """
    normalizado = unicodedata.normalize('NFC', str)
    return ''.join(c for c in normalizado
                   if c in CONTROLE_PRESERVADO
                   or unicodedata.category(c) not in ('Cc', 'Cf', 'Co', 'Cs'))

# Text Preprocessing
def text_pre_proc(str):
    aux = saxutils.unescape(str.replace('&quot;', ''))
    aux = re_char(aux)
    # JSON-LD é JSON, não literal Python: `true`/`false`/`null` quebram
    # `ast.literal_eval`, que era o que o script original usava aqui.
    return json.loads(aux)

# Get ClaimReview
def get_claimReview(url):
    from bs4 import BeautifulSoup
    import requests

    response = requests.get(url, timeout=30)
    content = BeautifulSoup(response.content, "html.parser")
    claimList = []
    for claimR in content.findAll('script', attrs={"type": "application/ld+json"}):
        linha = []
        try:
            my_dict = text_pre_proc(claimR.get_text(strip=True))
            linha.append(url)
            linha.append(my_dict['author']['url'])
            linha.append(my_dict['datePublished'])
            linha.append(my_dict['claimReviewed'])
            try: linha.append(my_dict['reviewBody'])
            except:
                try:
                    linha.append(my_dict['description'])
                except:
                    linha.append('Empty')
            linha.append(re_char(content.title.get_text().replace('<title>','').replace('</title>','')))
            linha.append(my_dict['reviewRating']['ratingValue'])
            linha.append(my_dict['reviewRating']['bestRating'])
            linha.append(my_dict['reviewRating']['alternateName'])
            linha.append(my_dict['itemReviewed']['@type'])
            claimList.append(linha)
        except Exception:
            pass
    return claimList

# Main Function
def main():
    websites = ["https://aosfatos.org/noticias/feed/", "https://apublica.org/tag/truco/feed/", "https://piaui.folha.uol.com.br/lupa/feed/"]
    toprow = ['URL', 'Author', 'datePublished', 'claimReviewed', 'reviewBody', 'title', 'ratingValue', 'bestRating', 'alternativeName', 'contentType']
    # Step 1 - Get links list of the last articles
    linksList = []
    for url in websites: linksList.extend(get_articles_url(url))
    print ("Numero de links: {}".format(len(linksList)))
    # Step 2 - Get Claim Review
    claimList = []
    count = 0
    for url in linksList:
        count = count + 1
        print ("{} de {} > ".format(count,len(linksList)) + url)
        lineList = get_claimReview(url)
        for line in lineList: claimList.append(line)
    # Step 3 - Create pandas DataFrame with the new entries
    new_entries = pd.DataFrame(claimList, columns=toprow)
    new_entries = new_entries.set_index('URL')
    # Step 4 - Load the old version of the dataset, update and save
    dataset = load_tsv_pandas('factCkBr')
    factCkBr = update_dataset(dataset, new_entries)
    save_tsv_pandas(factCkBr, 'new_factCkBR')


if __name__ == "__main__":
    main()
