"""Travessia dos instrumentos em inglês — capability `adaptacao-criterios-en`.

Decisão 1 do `design.md`: o problema de idioma é o inverso do que parecia. Os
três datasets em inglês nunca chegam ao usuário como texto — são instrumento e
definição. O que cruza a fronteira é **vocabulário de critério**, por adaptação
validada contra casos brasileiros, nunca por tradução de texto corrido.

## Decisão de conjunto (task 5.2)

O FakeHealth tem 20 perguntas em dois conjuntos de 10, não 10. Oito perguntas
são o mesmo conceito nos dois; duas são próprias de cada:

| Só em `HealthStory` | Só em `HealthRelease` |
| --- | --- |
| usa fontes independentes e identifica conflito de interesse | identifica financiador e declara conflito de interesse |
| depende apenas de um comunicado de imprensa | usa linguagem sensacionalista, inclusive nas aspas |

**Adotado o conjunto `HealthStory` como base**, com as duas de `HealthRelease`
mapeadas para dentro dele. Motivo: o que chega ao usuário deste projeto é
mensagem que circulou — post, corrente, manchete —, e não comunicado
institucional. A pergunta sobre financiador é a mesma de conflito de interesse
vista pelo outro lado, e entra como nível da rubrica; a de linguagem
sensacionalista não tem correspondente em `HealthStory` e é preservada por
endereçar diretamente o catálogo de técnicas de `resposta-formativa`.

Este mapeamento é o registro que o requirement "Os dois conjuntos de critérios
são distintos" exige: os conjuntos não foram somados, foram reconciliados um a
um, e a origem de cada critério da rubrica fica declarada.

## O que a validação de hoje é, e o que ela não é (task 5.4)

A primeira tentativa de validar a rubrica foi por **cobertura de vocabulário**:
contar em que proporção dos casos brasileiros aparece o vocabulário que cada
critério interroga, e remover o que fica abaixo de um piso. O proxy foi medido
e **reprovado pela própria medição**, que fica registrada por ser o achado:

| Critério | Proporção sobre a alegação | Decisão real |
| --- | --- | --- |
| `conflito_de_interesse` | 0,193 | mantido |
| `beneficio` | 0,141 | mantido |
| `evidencia` | 0,107 | mantido |
| `dano` | 0,100 | mantido |
| `novidade` | 0,063 | **removido** |
| `custo` | 0,051 | **removido** |
| `alarme` | 0,039 | **mantido** |
| `linguagem` | 0,029 | **mantido** |

Sob qualquer piso único, o proxy removeria `alarme` e `linguagem` — os dois
critérios que mais diretamente endereçam desinformação — e manteria `custo` e
`novidade`. A causa é conhecida: estilo (caixa alta, exclamação, pedido de
repasse) não sobrevive à reescrita do título pela agência, enquanto `novo` e
`reais` são palavras comuns que casam por acaso. O proxy mede presença de
palavra, não aplicabilidade do critério.

**O que sustenta as remoções é o argumento de unidade de análise**, não o
número: as cinco perguntas removidas foram escritas para avaliar jornalismo
sobre tecnologia médica, e não têm objeto quando a unidade analisada é a
mensagem que circulou. O motivo de cada uma está em `REMOVIDOS`.

**O que falta.** "Validar contra casos brasileiros" no sentido pleno do
requirement — aplicar a rubrica a casos reais e ver se ela separa — exige
anotação humana dos 20 a 30 casos, que é da capability `avaliacao-instrumento`,
em `mvp-copiloto-verificacao`. Esta task entrega o instrumento e o registro das
remoções; não entrega a validação empírica.
"""
from __future__ import annotations

import collections
import dataclasses
import json

from tratamento import frescor, leitura, relatorios

NIVEIS = ("atende", "atende em parte", "nao atende")

# Abaixo desta proporção de itens do corpus em que o vocabulário do critério
# aparece, o critério não separa caso brasileiro de caso brasileiro.
PISO_DE_DISCRIMINACAO = 0.05


@dataclasses.dataclass(frozen=True)
class Criterio:
    """Critério adaptado, com a rubrica de três níveis e a origem declarada."""

    id: str
    pergunta_en: str
    pergunta_pt: str
    conjunto_de_origem: str
    niveis: dict[str, str]
    sinais: tuple[str, ...]
    nota: str = ""


@dataclasses.dataclass(frozen=True)
class CriterioRemovido:
    """Critério que saiu da rubrica, com o motivo — exigido pela capability.

    `sinais` existe para o critério removido continuar sendo medido: é o que
    permite reabrir a decisão se o proxy um dia passar a separar.
    """

    id: str
    pergunta_en: str
    conjunto_de_origem: str
    motivo_da_remocao: str
    sinais: tuple[str, ...]


def extrair_conjuntos(df) -> dict[str, list[str]]:
    """As 20 perguntas do FakeHealth, separadas pelos dois conjuntos (task 5.1)."""
    conjuntos: dict[str, list[str]] = {}
    for nome, grupo in df.groupby("dataset"):
        perguntas = [p.strip() for p in
                     collections.Counter(grupo["pergunta"]).keys()]
        conjuntos[nome] = sorted(perguntas)
    return conjuntos


RUBRICA: tuple[Criterio, ...] = (
    Criterio(
        id="evidencia",
        pergunta_en="Does the story seem to grasp the quality of the evidence?",
        pergunta_pt="A mensagem diz de onde veio a informação e que tipo de "
                    "estudo ou fonte a sustenta?",
        conjunto_de_origem="ambos",
        niveis={
            "atende": "nomeia a fonte e o tipo de estudo, e a fonte é "
                      "localizável por quem lê",
            "atende em parte": "menciona estudo, médico ou instituição sem "
                               "nome, data ou link que permita conferir",
            "nao atende": "afirma sem qualquer origem, ou apela a "
                          "«comprovado cientificamente» sem nada mais",
        },
        sinais=("estudo", "pesquisa", "cientista", "revista", "universidade",
                "artigo", "laboratorio", "oms", "anvisa", "ministerio"),
    ),
    Criterio(
        id="beneficio",
        pergunta_en="Does the story adequately quantify the benefits of the "
                    "treatment/test/product/procedure?",
        pergunta_pt="O benefício prometido vem com número, ou só com adjetivo?",
        conjunto_de_origem="ambos",
        niveis={
            "atende": "dá a magnitude do efeito e sobre quantas pessoas foi "
                      "observado",
            "atende em parte": "dá número solto, sem base de comparação nem "
                               "tamanho do grupo",
            "nao atende": "só adjetivo — «poderoso», «eficaz», «cura»",
        },
        sinais=("cura", "trata", "previne", "eficaz", "elimina", "combate",
                "%", "por cento", "vezes mais", "reduz"),
    ),
    Criterio(
        id="dano",
        pergunta_en="Does the story adequately explain/quantify the harms of "
                    "the intervention?",
        pergunta_pt="A mensagem diz o que pode dar errado, ou só o que pode "
                    "dar certo?",
        conjunto_de_origem="ambos",
        niveis={
            "atende": "nomeia efeitos adversos e com que frequência ocorrem",
            "atende em parte": "menciona risco sem dizer qual nem quão comum",
            "nao atende": "não menciona risco algum, ou afirma que não há",
        },
        sinais=("efeito colateral", "risco", "reacao", "adverso", "perigo",
                "seguro", "contraindicacao", "morte", "morreu", "sequela"),
    ),
    Criterio(
        id="alarme",
        pergunta_en="Does the story commit disease-mongering?",
        pergunta_pt="A mensagem aumenta o tamanho do problema para justificar "
                    "a solução que oferece?",
        conjunto_de_origem="ambos",
        niveis={
            "atende": "descreve a gravidade e a frequência do problema como "
                      "a fonte descreve",
            "atende em parte": "usa caso extremo como se fosse o caso comum",
            "nao atende": "inventa epidemia, urgência ou conspiração para "
                          "empurrar a conclusão",
        },
        sinais=("urgente", "epidemia", "surto", "todos estao", "esconderam",
                "a industria", "nao querem que voce saiba", "alerta",
                "compartilhe", "repasse"),
    ),
    Criterio(
        id="conflito_de_interesse",
        pergunta_en="Does the story use independent sources and identify "
                    "conflicts of interest?",
        pergunta_pt="Dá para saber quem publicou e o que essa pessoa ganha se "
                    "você acreditar?",
        conjunto_de_origem="HealthStory",
        niveis={
            "atende": "autor e financiador identificáveis, e o interesse "
                      "declarado quando existe",
            "atende em parte": "autor identificável, interesse não declarado",
            "nao atende": "autoria anônima, ou fonte que vende o que indica",
        },
        sinais=("vende", "compre", "link na bio", "whatsapp", "dr", "dra",
                "medico", "empresa", "patrocin", "fabricante", "laboratorio"),
        nota="Absorve a pergunta de financiador do conjunto HealthRelease. "
             "É também a única cobertura direta da competência «identificar "
             "vieses» hoje — ver a lacuna registrada em docs/estado.md.",
    ),
    Criterio(
        id="linguagem",
        pergunta_en="Does the news release include unjustifiable, sensational "
                    "language, including in the quotes of researchers?",
        pergunta_pt="O texto precisa de letra maiúscula, ponto de exclamação "
                    "ou pedido de repasse para se sustentar?",
        conjunto_de_origem="HealthRelease",
        niveis={
            "atende": "tom informativo, sem apelo emocional para convencer",
            "atende em parte": "tom exaltado em parte do texto",
            "nao atende": "caixa alta, exclamação em série, pedido de "
                          "compartilhamento urgente",
        },
        sinais=("!", "urgente", "chocante", "inacreditavel", "compartilhe",
                "repasse", "atencao", "cuidado", "voce precisa saber"),
        nota="Preservada do conjunto HealthRelease por não ter correspondente "
             "em HealthStory e por endereçar direto o catálogo de técnicas de "
             "`resposta-formativa`.",
    ),
)

REMOVIDOS: tuple[CriterioRemovido, ...] = (
    CriterioRemovido(
        id="custo",
        pergunta_en="Does the story adequately discuss the costs of the "
                    "intervention?",
        conjunto_de_origem="ambos",
        motivo_da_remocao=(
            "Pergunta escrita para jornalismo sobre tecnologia médica nova, "
            "onde preço é dado noticiável. A mensagem que circula em saúde no "
            "Brasil não discute preço: propõe chá, alho, vitamina ou recusa de "
            "vacina. A pergunta não tem objeto, e critério sem objeto não "
            "gradua nada."),
        sinais=("custo", "preco", "r$", "reais", "caro", "barato", "gratuito"),
    ),
    CriterioRemovido(
        id="disponibilidade",
        pergunta_en="Does the story establish the availability of the "
                    "treatment/test/product/procedure?",
        conjunto_de_origem="ambos",
        motivo_da_remocao=(
            "Mesmo motivo do custo. Disponibilidade é dimensão de reportagem "
            "sobre lançamento; a alegação viral não promete acesso futuro, "
            "promete efeito imediato."),
        sinais=("disponivel", "farmacia", "sus", "receita medica", "a venda"),
    ),
    CriterioRemovido(
        id="alternativas",
        pergunta_en="Does the story compare the new approach with existing "
                    "alternatives?",
        conjunto_de_origem="ambos",
        motivo_da_remocao=(
            "Exige que o texto apresente um tratamento comparado a outro. A "
            "desinformação em saúde faz o oposto: apresenta a alternativa "
            "isolada, muitas vezes contra o tratamento estabelecido. O que "
            "importa desse conceito já é capturado por `beneficio` e "
            "`evidencia`."),
        sinais=("em vez de", "alternativa", "comparado", "melhor que", "substitui"),
    ),
    CriterioRemovido(
        id="novidade",
        pergunta_en="Does the story establish the true novelty of the approach?",
        conjunto_de_origem="ambos",
        motivo_da_remocao=(
            "Pergunta sobre ineditismo de achado científico. Não discrimina "
            "mensagem viral, que costuma reciclar alegação antiga sem "
            "qualquer pretensão de novidade — e quando o faz, o sinal já cai "
            "em `alarme`."),
        sinais=("novo", "inedito", "pela primeira vez", "descoberta", "lancamento"),
    ),
    CriterioRemovido(
        id="release",
        pergunta_en="Does the story appear to rely solely or largely on a news "
                    "release?",
        conjunto_de_origem="HealthStory",
        motivo_da_remocao=(
            "Pergunta sobre prática de redação jornalística: se o repórter "
            "copiou o comunicado da assessoria. Não tem objeto quando a "
            "unidade analisada é a mensagem recebida pelo usuário."),
        sinais=("comunicado", "assessoria", "nota a imprensa", "press release"),
    ),
)

# InSciOut — força da afirmação. Escala 0 a 3 medida no derivado
# `exagero_pares_abstract_vs_release.csv`. Os nomes são portugueses e a escala
# atravessa como definição operacional; os pares em inglês MUST NOT ser
# exibidos ao usuário (`adaptacao-criterios-en`).
FORCA_DA_AFIRMACAO: dict[str, str] = {
    "0": "sem afirmação de relação",
    "1": "associação observada",
    "2": "relação condicional",
    "3": "relação causal afirmada",
}

# Comparação entre a força do estudo e a força da manchete. O rótulo `exagera`
# é o que liga ao rótulo `verdadeiro fora de contexto ou exagerado` de
# `verificacao-alegacao` e à técnica `manchete exagerada` do catálogo.
COMPARACAO_DE_FORCA: dict[str, dict[str, str]] = {
    "same": {
        "rotulo_pt": "mesma força",
        "tecnica": "",
        "explicacao": "a manchete afirma o que o estudo conclui",
    },
    "exaggerates": {
        "rotulo_pt": "afirma mais que o estudo",
        "tecnica": "manchete exagerada",
        "explicacao": "o estudo observou associação e a manchete afirma causa",
    },
    "downplays": {
        "rotulo_pt": "afirma menos que o estudo",
        "tecnica": "",
        "explicacao": "a manchete enfraquece o que o estudo concluiu; não é "
                      "desinformação de promessa, mas distorce igual",
    },
}


def _alegacoes(df) -> list[str]:
    """A alegação checada, que é o objeto certo da medição.

    Medir sobre `text_news` mede a análise escrita pela agência, não a mensagem
    que circulou: lá `custo` aparece em 36% dos registros e `novidade` em 49%,
    números que não dizem nada sobre o caso. Título e subtítulo são o mais
    próximo da alegação que o corpus oferece.
    """
    return [frescor.sem_acento(f"{t} {s}").lower()
            for t, s in zip(df["title"], df["subtitle"])]


def _medir(alegacoes: list[str], sinais: tuple[str, ...]) -> dict:
    termos = [frescor.sem_acento(s).lower() for s in sinais]
    acertos = sum(1 for a in alegacoes if any(t in a for t in termos))
    return {"casos_com_sinal": acertos,
            "proporcao": acertos / max(len(alegacoes), 1)}


def validar_contra_corpus(df) -> dict:
    """Mede a cobertura de vocabulário de cada critério sobre a alegação.

    O resultado **não** é a justificativa das remoções: ele é a evidência de
    que o proxy não serve como regra de decisão. Ver o cabeçalho do módulo.
    """
    alegacoes = _alegacoes(df)

    por_criterio = {}
    for criterio in RUBRICA:
        medida = _medir(alegacoes, criterio.sinais)
        por_criterio[criterio.id] = {
            "pergunta_pt": criterio.pergunta_pt,
            "conjunto_de_origem": criterio.conjunto_de_origem,
            **medida,
            "acima_do_piso": medida["proporcao"] >= PISO_DE_DISCRIMINACAO,
        }

    removidos_medidos = {
        c.id: {"pergunta_en": c.pergunta_en,
               "conjunto_de_origem": c.conjunto_de_origem,
               "motivo": c.motivo_da_remocao,
               **_medir(alegacoes, c.sinais)}
        for c in REMOVIDOS
    }

    menor_mantido = min(m["proporcao"] for m in por_criterio.values())
    maior_removido = max(m["proporcao"] for m in removidos_medidos.values())
    proxy_separa = menor_mantido > maior_removido

    return {
        "registros_avaliados": int(len(df)),
        "objeto_medido": "title + subtitle (a alegação checada)",
        "piso_de_discriminacao": PISO_DE_DISCRIMINACAO,
        "metodo": ("cobertura de vocabulário sobre a alegação; proxy "
                   "reprodutível, não anotação humana"),
        "por_criterio": por_criterio,
        "removidos_medidos": removidos_medidos,
        "proxy_valido_como_regra": proxy_separa,
        "leitura_do_resultado": (
            "o proxy separa mantidos de removidos e pode ser usado como regra"
            if proxy_separa else
            f"o proxy NÃO separa: o menor mantido ({menor_mantido:.3f}) está "
            f"abaixo do maior removido ({maior_removido:.3f}). As remoções se "
            "sustentam no argumento de unidade de análise, registrado em "
            "`REMOVIDOS`, e a validação empírica da rubrica fica pendente de "
            "anotação humana em `avaliacao-instrumento`."),
        "base_da_decisao": "unidade de análise, não a medição de vocabulário",
    }


def pool_fewshot(df, por_rotulo: int = 5, semente: int = 42):
    """Pool de exemplares em português, tirado do corpus brasileiro (task 5.5).

    `adaptacao-criterios-en` proíbe exemplar traduzido do PUBHEALTH. Entram só
    registros de alegação única, com rótulo consolidado e texto suficiente para
    servir de exemplar — registro misto é caso de teste, não exemplar.
    """
    marcado = relatorios.marcar_registros(df)
    marcado = marcado.assign(
        titulo=df["title"].values,
        texto=df["text_news"].values,
    )

    elegivel = marcado[
        (marcado["n_vereditos"] == 1)
        & (marcado["rotulo_consolidado"] != "")
        & (marcado["rotulo_consolidado"] != "nao_mapeavel")
        & (~marcado["excluido_do_banco_de_estimulos"])
        & (marcado["texto"].str.len() >= 400)
    ]

    partes = []
    for rotulo, grupo in elegivel.groupby("rotulo_consolidado"):
        n = min(por_rotulo, len(grupo))
        partes.append(grupo.sample(n=n, random_state=semente))

    import pandas as pd

    pool = pd.concat(partes).sort_values(["rotulo_consolidado", "url"])
    pool = pool.assign(idioma="pt-BR", origem="factcenter_subset_saude.csv",
                       semente=semente)
    return pool.reset_index(drop=True)


def gravar(caminho_pool=None, caminho_rubrica=None) -> dict:
    """Versiona a rubrica adaptada, a validação e o pool de few-shot."""
    destino_pool = caminho_pool or (
        leitura.DIRETORIO_DERIVADOS / "fewshot_ptbr_pool.csv")
    destino_rubrica = caminho_rubrica or (
        leitura.DIRETORIO_DERIVADOS / "rubrica_criterios_ptbr.json")

    corpus = leitura.ler_corpus()
    pool_fewshot(corpus).to_csv(destino_pool, index=False, encoding="utf-8")

    conteudo = {
        "conjunto_adotado": "HealthStory, com duas perguntas de HealthRelease "
                            "mapeadas para dentro dele",
        "perguntas_do_fakehealth": extrair_conjuntos(
            leitura.ler_derivado("fakehealth_criterios_long.csv")),
        "rubrica": [dataclasses.asdict(c) for c in RUBRICA],
        "removidos": [dataclasses.asdict(c) for c in REMOVIDOS],
        "forca_da_afirmacao": FORCA_DA_AFIRMACAO,
        "comparacao_de_forca": COMPARACAO_DE_FORCA,
        "validacao": validar_contra_corpus(corpus),
    }
    destino_rubrica.write_text(
        json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")
    return conteudo["validacao"]
