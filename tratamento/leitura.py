"""Contrato de leitura dos derivados PT-BR e EN — capability `normalizacao-rotulos`.

O requirement "Contrato de leitura do corpus" manda ler o corpus com o
delimitador e o quoting corretos e conferir a contagem obtida contra a
declarada. Divergência é erro de leitura: interrompe, e nenhum derivado é
gerado a partir dela.

O catálogo abaixo é a resposta da task 1.2 — o formato **real** de cada arquivo,
medido, não inferido do nome. Dois arquivos desmentem a extensão `.csv`:
`factcenter_subset_saude.csv` é separado por `;`, e o `pubhealth_pool_fewshot.csv`
carrega aspas escapadas em excesso na origem.
"""
from __future__ import annotations

import dataclasses
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[1]
DIRETORIO_DERIVADOS = RAIZ / "datasets" / "derivados"


class ErroDeLeitura(RuntimeError):
    """Arquivo não satisfaz o contrato. Nenhum derivado é gerado a partir dele."""


@dataclasses.dataclass(frozen=True)
class FormatoDerivado:
    """Formato medido de um derivado, e a contagem que o `datasets/README.md` declara."""

    separador: str
    registros_declarados: int
    colunas: tuple[str, ...]
    colunas_com_newline_interno: tuple[str, ...] = ()
    # Texto que a fonte já entregou alterado (lematizado, sem caixa, sem
    # stopwords). Muda o laudo de integridade: a classe de caractere ausente é
    # consequência declarada da transformação, não perda no nosso pipeline.
    texto_transformado_na_origem: bool = False
    observacao: str = ""


CATALOGO: dict[str, FormatoDerivado] = {
    "factcenter_subset_saude.csv": FormatoDerivado(
        separador=";",
        registros_declarados=4063,
        colunas=("url", "source_name", "title", "subtitle", "publication_date",
                 "text_news", "image_link", "video_link", "authors",
                 "categories", "tags", "obtained_at", "rating"),
        colunas_com_newline_interno=("text_news",),
        observacao="Único derivado separado por ';'. Lido no default de "
                   "read_csv levanta ParserError; com on_bad_lines='skip' "
                   "produz 25.670 registros de uma coluna só, silenciosamente.",
    ),
    "factckbr_normalizado.csv": FormatoDerivado(
        separador=",",
        registros_declarados=1313,
        colunas=("URL", "Author", "datePublished", "claimReviewed", "reviewBody",
                 "title", "ratingValue", "bestRating", "alternativeName",
                 "rotulo_norm"),
        observacao="Reprovado para citação pela capability `integridade-textual`: "
                   "perdeu toda maiúscula acentuada. Ver tratamento.integridade.",
    ),
    "fakehealth_criterios_long.csv": FormatoDerivado(
        separador=",",
        registros_declarados=22959,
        colunas=("dataset", "news_id", "rating", "title", "original_title",
                 "news_source", "source_link", "review_link", "criterio_idx",
                 "pergunta", "resposta", "explicacao"),
        colunas_com_newline_interno=("explicacao",),
        observacao="Um critério por linha. A coluna `dataset` separa os dois "
                   "conjuntos de 10 critérios (HealthStory e HealthRelease).",
    ),
    "fakehealth_matriz_10_criterios.csv": FormatoDerivado(
        separador=",",
        registros_declarados=20,
        colunas=("pergunta", "ocorrencias", "nao_satisfatorio"),
        observacao="O nome do arquivo diz 10 critérios; o conteúdo tem 20 "
                   "perguntas, 10 de cada conjunto. Nome enganoso, mantido "
                   "por estabilidade de referência — ver caveat no README.",
    ),
    "fakehealth_reviews_indice.csv": FormatoDerivado(
        separador=",",
        registros_declarados=2296,
        colunas=("dataset", "news_id", "rating", "title", "original_title",
                 "news_source", "source_link", "review_link"),
    ),
    "fakerecogna2_subset_saude_ciencia.csv": FormatoDerivado(
        separador=",",
        registros_declarados=26436,
        colunas=("Titulo", "Subtitulo", "Noticia", "Categoria", "Data", "Autor",
                 "URL", "Label"),
        colunas_com_newline_interno=("Noticia",),
        texto_transformado_na_origem=True,
        observacao="FakeRecogna 2.0 extrativa, filtrada por termo de saúde "
                   "sobre o texto — o filtro por `Categoria` da v1 não vale "
                   "aqui, porque a classe real tem cinco categorias e a falsa "
                   "tem 69. A notícia real vem sumarizada na origem e a falsa "
                   "vem crua: só o comprimento do texto classifica 80,5%.",
    ),
    "fakerecogna2_amostra_estimulos_300.csv": FormatoDerivado(
        separador=",",
        registros_declarados=300,
        colunas=("Titulo", "Subtitulo", "Noticia", "Categoria", "Data", "Autor",
                 "URL", "Label"),
        colunas_com_newline_interno=("Noticia",),
        texto_transformado_na_origem=True,
        observacao="Amostra estratificada com random_state=42 sobre o subset "
                   "da 2.0. Substitui a amostra da v1, que saiu em 19/09/2026.",
    ),
    "exagero_pares_abstract_vs_release.csv": FormatoDerivado(
        separador=",",
        registros_declarados=663,
        colunas=("original_file_id", "press_release_conclusion",
                 "press_release_strength", "abstract_conclusion",
                 "abstract_strength", "exaggeration_label"),
        observacao="Instrumento em inglês. Atravessa como definição operacional "
                   "de força da afirmação, nunca como texto exibido.",
    ),
    "pubhealth_pool_fewshot.csv": FormatoDerivado(
        separador=",",
        registros_declarados=60,
        colunas=("claim_id", "claim", "explanation", "sources", "label",
                 "subjects"),
        observacao="Aspas escapadas em excesso na origem: `\"\"\"\"\"\"\"texto\"\"\"`. "
                   "O conteúdo lido carrega as aspas redundantes, que precisam "
                   "ser removidas antes de qualquer uso do texto.",
    ),
}


def caminho(nome: str) -> pathlib.Path:
    """Caminho do derivado no repositório."""
    return DIRETORIO_DERIVADOS / nome


def formato(nome: str) -> FormatoDerivado:
    """Formato catalogado do derivado. Arquivo fora do catálogo não é lido."""
    try:
        return CATALOGO[nome]
    except KeyError:
        raise ErroDeLeitura(
            f"{nome} não consta do catálogo de formatos. Medir o formato real "
            "e registrá-lo em CATALOGO antes de ler.") from None


def ler_derivado(nome: str, caminho: pathlib.Path | None = None,
                 sep: str | None = None):
    """Lê o derivado sob o contrato declarado e confere a contagem de registros.

    `caminho` e `sep` existem para os testes exercitarem violação do contrato.
    Em uso normal ambos vêm do catálogo.
    """
    import pandas as pd

    declarado = formato(nome)
    arquivo = caminho if caminho is not None else DIRETORIO_DERIVADOS / nome
    separador = sep if sep is not None else declarado.separador

    try:
        df = pd.read_csv(arquivo, sep=separador, dtype=str, keep_default_na=False)
    except Exception as erro:  # pragma: no cover - depende da versão do pandas
        raise ErroDeLeitura(
            f"{nome}: leitura falhou com separador {separador!r} — {erro}") from erro

    faltando = [c for c in declarado.colunas if c not in df.columns]
    if faltando:
        raise ErroDeLeitura(
            f"{nome}: colunas ausentes {faltando} sob separador {separador!r}. "
            "Leitura inválida — conferir delimitador e quoting.")

    if len(df) != declarado.registros_declarados:
        raise ErroDeLeitura(
            f"{nome}: {len(df)} registros lidos contra "
            f"{declarado.registros_declarados} declarados. Divergência é erro "
            "de leitura, nunca corrigida por normalização posterior. Nenhum "
            "derivado é gerado a partir desta leitura.")

    return df


def ler_corpus():
    """Atalho para o corpus de checagens PT-BR, que sustenta a recuperação."""
    return ler_derivado("factcenter_subset_saude.csv")


# --------------------------------------------------------------------------
# Leitura em streaming — task 9.5 de `add-ampliacao-corpus-ptbr`.
#
# O acervo de circulação tem 3,6 GB e 3.998.633 linhas. Carregá-lo inteiro não
# é opção, e o contrato de leitura precisa valer igual: linha ilegível
# interrompe, e a contagem obtida é conferida contra a declarada.
# --------------------------------------------------------------------------

def ler_jsonl(caminho: pathlib.Path, registros_declarados: int | None = None):
    """Gera um registro por linha de um `.jsonl`, sem carregar o arquivo.

    Linha em branco é ignorada; linha ilegível interrompe com o número da
    linha, porque num arquivo de milhões de registros «falhou em algum lugar»
    não é diagnóstico. A conferência de contagem só acontece ao fim do arquivo,
    e só se `registros_declarados` for informado.
    """
    import json

    lidos = 0
    with open(caminho, encoding="utf-8") as arquivo:
        for numero, linha in enumerate(arquivo, start=1):
            linha = linha.strip()
            if not linha:
                continue
            try:
                registro = json.loads(linha)
            except ValueError as erro:
                raise ErroDeLeitura(
                    f"{pathlib.Path(caminho).name}: linha {numero} ilegível "
                    f"— {erro}. Nenhum derivado é gerado a partir desta "
                    "leitura.") from None
            lidos += 1
            yield registro

    if registros_declarados is not None and lidos != registros_declarados:
        raise ErroDeLeitura(
            f"{pathlib.Path(caminho).name}: {lidos} registros lidos contra "
            f"{registros_declarados} declarados. Divergência é erro de "
            "leitura, nunca corrigida por normalização posterior.")
