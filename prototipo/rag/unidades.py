"""Construção das unidades de indexação — task 2.2 de add-selecao-modelos-arquitetura-rag.

A capability `arquitetura-recuperacao` fixa três exigências sobre a unidade:

- é a alegação com seu veredito e sua justificativa, carregando agência, data e
  endereço da checagem;
- fragmentação por tamanho fixo que separe a alegação do seu veredito MUST NOT
  ser usada — o cabeçalho com alegação e veredito é repetido em cada fragmento;
- registro que cobre mais de uma alegação gera unidade por alegação, e nenhuma
  unidade recebe veredito de alegação diferente da sua.

A terceira é a difícil. 587 dos 4.063 registros trazem mais de um veredito e o
corpus não marca onde uma alegação termina e a outra começa — os selos eram
elementos visuais da página e não sobreviveram à raspagem. Alinhar por ordem sem
verificação trocaria veredito entre alegações, que é exatamente a proibição.

O que o corpus oferece é um marcador de formato, só na Lupa: cada alegação
aparece como linha inteira entre aspas curvas, seguida da atribuição e da
análise. A regra adotada é aceitar a segmentação **apenas quando o número de
segmentos encontrados é igual ao número de vereditos declarados**. A igualdade
não prova o alinhamento, mas é a evidência disponível, e ela falha ruidosamente:
uma alegação a mais ou a menos derruba o registro para a via conservadora.

Medido sobre o corpus: 221 dos 587 registros multi-alegação segmentam sob essa
regra. Os demais seguem a disposição da tabela em `dispor_registro`.

Desde a task 1.1 de mvp-copiloto-verificacao (29/09/2026), a saída segue o
contrato `prototipo/indice/esquema_indexacao.json` e é validada por
`esquema.validar` antes de ser devolvida. Duas consequências: todo registro
carrega corpus, tipo de fonte, idioma, aptidão a citação e nome da agência; e a
alegação segmentada sem justificativa vai para a quarentena, porque um fragmento
sem trecho não ancora afirmação nenhuma (`recuperacao-evidencia`).

Desde a task 1.2 (01/10/2026, decisão 17), `construir_indice` junta o FACTCK.BR
como fonte auxiliar, depois do FactCenter e sem mexer nele. Ali não há
segmentação a fazer: cada linha do TSV já é uma alegação com seu veredito.
"""
from __future__ import annotations

import ast
import json
import pathlib
import re
import unicodedata

from . import corpus as corpus_mod
from . import esquema as esquema_mod

SAIDA = pathlib.Path(__file__).resolve().parents[1] / "indice"

CORPUS = "factcenter_saude"
CORPUS_FACTCKBR = "factckbr"

# Sem qualquer um destes, a linha do FACTCK.BR não vira unidade: sem alegação
# não há o que verificar, sem justificativa não há o que ancorar, sem veredito
# não há o que contar (x-corpora.factckbr.mapeamento do esquema).
CAMPOS_EXIGIDOS_FACTCKBR = ("claimReviewed", "reviewBody", "alternativeName")

# Alegação como linha inteira entre aspas. O piso de 15 caracteres descarta
# interjeição curta; o teto de 400 descarta parágrafo inteiro entre aspas.
CITACAO_DE_LINHA = re.compile(r'^[ \t]*[“"](?P<alegacao>.{15,400}?)[”"][ \t]*$', re.M)

# Acima disto o registro é compilado periódico de agência, não checagem de uma
# pauta. `normalizacao-rotulos` manda excluí-lo do banco de estímulos; aqui ele
# só entra no índice se a segmentação verificada resolver cada alegação.
TETO_COMPILADO = 20

# Fragmentação. O teto em caracteres é ditado pela janela do modelo de
# recuperação (512 tokens no e5-base, ~1.500 caracteres em português); o valor
# adotado deixa folga para o cabeçalho, que é repetido em todo fragmento.
FRAGMENTO_CARACTERES = 1100
FRAGMENTO_SOBREPOSICAO = 150


def chave_canonica(veredito: str) -> str:
    """Chave normalizada por caixa e acento; a grafia original é preservada.

    `normalizacao-rotulos` exige a chave ao lado do valor textual original, para
    rastreabilidade até a agência. O mapa dos quatro rótulos de
    `verificacao-alegacao` é task 2.3 daquele change e não é feito aqui —
    atribuir rótulo por semelhança de string é vedado em texto expresso.
    """
    return re.sub(r"\s+", " ", corpus_mod.sem_acento(veredito).strip().lower())


def _id_registro(url: str) -> str:
    # Prefixo vazio para o FactCenter: a chave é a mesma da aferição (esquema, I1).
    return esquema_mod.registro_id(CORPUS, url)


def _limpar(texto: str) -> str:
    return re.sub(r"[ \t]+", " ", (texto or "").strip())


def segmentar(texto: str, vereditos: list[str]) -> list[dict] | None:
    """Devolve uma alegação por veredito, ou None se a contagem não fechar."""
    marcas = list(CITACAO_DE_LINHA.finditer(texto))
    if len(marcas) != len(vereditos):
        return None
    segmentos = []
    for i, marca in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        segmentos.append({"alegacao": _limpar(marca.group("alegacao")),
                          "justificativa": texto[marca.end():fim].strip()})
    return segmentos


def dispor_registro(registro: dict) -> tuple[str, list[dict] | None]:
    """Decide o destino do registro e devolve (disposição, segmentos)."""
    vereditos = registro["vereditos"]
    if len(vereditos) == 1:
        return "unica", None

    segmentos = segmentar(registro["text_news"], vereditos)
    if segmentos is not None:
        return "segmentada", segmentos

    # Sem segmentação verificada, o registro só pode virar unidade se todos os
    # vereditos coincidirem: aí não existe veredito alheio a atribuir. A unidade
    # fica mais grossa que o ideal e é marcada como tal.
    if len({chave_canonica(v) for v in vereditos}) == 1:
        if len(vereditos) > TETO_COMPILADO:
            return "quarentena_compilado", None
        return "nao_segmentada", None

    # Vereditos divergentes sem segmentação: qualquer unidade única receberia
    # veredito que não é da alegação. Vai para a quarentena como `misto`, que é
    # o conjunto de casos de teste reservado por `normalizacao-rotulos`.
    return "quarentena_misto", None


def _fragmentar(justificativa: str) -> list[str]:
    """Corta a justificativa em pedaços, preferindo quebra de parágrafo/frase."""
    texto = justificativa.strip()
    if len(texto) <= FRAGMENTO_CARACTERES:
        return [texto] if texto else [""]
    pedacos, inicio = [], 0
    while inicio < len(texto):
        fim = min(inicio + FRAGMENTO_CARACTERES, len(texto))
        if fim < len(texto):
            janela = texto[inicio:fim]
            corte = max(janela.rfind("\n"), janela.rfind(". "))
            if corte > FRAGMENTO_CARACTERES // 2:
                fim = inicio + corte + 1
        pedacos.append(texto[inicio:fim].strip())
        if fim >= len(texto):
            break
        inicio = max(fim - FRAGMENTO_SOBREPOSICAO, inicio + 1)
    return [p for p in pedacos if p]


def _cabecalho(unidade: dict, agencia: str | None = None) -> str:
    """Alegação e veredito, repetidos em todo fragmento por exigência da spec.

    O FactCenter mantém a grafia original da agência no cabeçalho, para a matriz
    densa já calculada continuar valendo. O FACTCK.BR passa o nome exibível: a
    grafia dele é um pedaço de URL (`https:apublica.org`), que só poluiria os
    braços léxico e denso.
    """
    return (f'Alegação: {unidade["alegacao"]}\n'
            f'Veredito de {agencia or unidade["agencia"]} em {unidade["data_publicacao"]}: '
            f'{unidade["veredito_original"]}')


def construir(df, validar_esquema: bool = True) -> tuple[list[dict], list[dict], list[dict], dict]:
    esquema = esquema_mod.carregar_esquema()
    unidades, fragmentos, quarentena = [], [], []
    contagem = {}
    unidades_sem_justificativa = 0

    for linha in df.to_dict("records"):
        try:
            vereditos = [str(v) for v in ast.literal_eval(linha["rating"])]
        except (ValueError, SyntaxError):
            vereditos = []
        if not vereditos:
            quarentena.append({"corpus": CORPUS, "url": linha["url"],
                               "agencia": linha["source_name"],
                               "motivo": "veredito ilegível", "rating": linha["rating"]})
            contagem["quarentena_rating"] = contagem.get("quarentena_rating", 0) + 1
            continue

        registro = {"text_news": linha["text_news"], "vereditos": vereditos}
        disposicao, segmentos = dispor_registro(registro)
        contagem[disposicao] = contagem.get(disposicao, 0) + 1

        if disposicao.startswith("quarentena"):
            quarentena.append({
                "corpus": CORPUS, "url": linha["url"], "agencia": linha["source_name"],
                "titulo": _limpar(linha["title"]), "motivo": disposicao,
                "vereditos_originais": vereditos,
                "vereditos_chave": sorted({chave_canonica(v) for v in vereditos}),
            })
            continue

        rid = _id_registro(linha["url"])
        atributos = esquema_mod.atributos_de_corpus(CORPUS, linha["source_name"], esquema)
        base = {"registro_id": rid, **atributos, "agencia": linha["source_name"],
                "url": linha["url"], "data_publicacao": linha["publication_date"],
                "obtido_em": linha["obtained_at"], "titulo": _limpar(linha["title"]),
                "subtitulo": _limpar(linha["subtitle"]),
                "alegacoes_no_registro": len(vereditos)}

        if disposicao == "segmentada":
            partes = [{"alegacao": s["alegacao"], "justificativa": s["justificativa"],
                       "veredito": v} for s, v in zip(segmentos, vereditos)]
            origem = "citacao_segmentada"
        else:
            # Título é a alegação quando a agência publica uma pauta por página;
            # `subtitle` costuma trazer o resumo do veredito e entra no texto.
            alegacao = _limpar(linha["title"])
            partes = [{"alegacao": alegacao, "justificativa": linha["text_news"],
                       "veredito": vereditos[0]}]
            origem = "titulo"

        for i, parte in enumerate(partes):
            if not parte["justificativa"].strip():
                # O texto raspado terminou antes da justificativa desta alegação.
                # Sem trecho não há o que citar; o índice das irmãs não muda.
                quarentena.append({
                    "corpus": CORPUS, "url": linha["url"], "agencia": linha["source_name"],
                    "unidade_id": f"{rid}-{i:02d}", "motivo": "justificativa_ausente",
                    "alegacao": parte["alegacao"], "veredito_original": parte["veredito"]})
                unidades_sem_justificativa += 1
                continue
            unidade = dict(base)
            unidade.update({
                "unidade_id": f"{rid}-{i:02d}",
                "indice_alegacao": i,
                "alegacao": parte["alegacao"],
                "veredito_original": parte["veredito"],
                "veredito_chave": chave_canonica(parte["veredito"]),
                "justificativa": parte["justificativa"].strip(),
                "origem_alegacao": origem,
                "disposicao": disposicao,
                # A unidade não segmentada cobre mais de uma alegação sob o mesmo
                # veredito. Quem for citar precisa saber disso: a citação tem de
                # sair do fragmento recuperado, não da unidade inteira.
                "cobre_multiplas_alegacoes": disposicao == "nao_segmentada",
            })
            pedacos = _fragmentar(unidade["justificativa"])
            unidade["fragmentos"] = len(pedacos)
            unidades.append(unidade)
            cabecalho = _cabecalho(unidade)
            for j, trecho in enumerate(pedacos):
                fragmentos.append({
                    "fragmento_id": f'{unidade["unidade_id"]}-{j:02d}',
                    "unidade_id": unidade["unidade_id"],
                    **atributos,
                    "agencia": unidade["agencia"], "url": unidade["url"],
                    "data_publicacao": unidade["data_publicacao"],
                    "alegacao": unidade["alegacao"],
                    "veredito_original": unidade["veredito_original"],
                    "posicao": j, "total": len(pedacos),
                    # `trecho` é literal, para citação fiel (integridade-textual).
                    # `texto` é o que vai ao índice, com o cabeçalho repetido.
                    "trecho": trecho,
                    "texto": f"{cabecalho}\n{trecho}",
                })

    manifesto = {
        "esquema": {"arquivo": "prototipo/indice/esquema_indexacao.json",
                    "versao": esquema["x-versao"]},
        "registros_lidos": len(df),
        "unidades_indexadas": len(unidades),
        "fragmentos_indexados": len(fragmentos),
        "registros_em_quarentena": len(quarentena) - unidades_sem_justificativa,
        "unidades_em_quarentena": unidades_sem_justificativa,
        "disposicoes": contagem,
        "busca": "exata, sem índice aproximado e sem banco vetorial "
                 "(design.md, decisão 3)",
        "condicao_de_reabertura": "crescimento do corpus em uma ordem de grandeza "
                                  "(dezenas de milhares de unidades)",
        "fragmento_caracteres": FRAGMENTO_CARACTERES,
        "fragmento_sobreposicao": FRAGMENTO_SOBREPOSICAO,
    }
    if validar_esquema:
        laudo = esquema_mod.validar(unidades, fragmentos, quarentena, esquema)
        esquema_mod.exigir(laudo)
        manifesto["esquema"]["aprovado"] = True
    return unidades, fragmentos, quarentena, manifesto


def _fragmentos_da_unidade(unidade: dict, atributos: dict, cabecalho: str) -> list[dict]:
    pedacos = _fragmentar(unidade["justificativa"])
    unidade["fragmentos"] = len(pedacos)
    return [{
        "fragmento_id": f'{unidade["unidade_id"]}-{j:02d}',
        "unidade_id": unidade["unidade_id"],
        **atributos,
        "agencia": unidade["agencia"], "url": unidade["url"],
        "data_publicacao": unidade["data_publicacao"],
        "alegacao": unidade["alegacao"],
        "veredito_original": unidade["veredito_original"],
        "posicao": j, "total": len(pedacos),
        "trecho": trecho,
        "texto": f"{cabecalho}\n{trecho}",
    } for j, trecho in enumerate(pedacos)]


def construir_factckbr(df, urls_ja_indexadas: set[str], esquema: dict | None = None
                       ) -> tuple[list[dict], list[dict], list[dict], dict]:
    """Unidades e fragmentos do FACTCK.BR — task 1.2 de mvp-copiloto-verificacao.

    `urls_ja_indexadas` são as URLs normalizadas que outro corpus apto a
    citação já indexou. Pela I10, a checagem fica com ele, e o registro do
    FACTCK.BR vai para a quarentena como `duplicata_factcenter`.

    Não valida o esquema: a I10 e a I12 só fecham sobre o índice inteiro, e
    quem valida é `construir_indice`.
    """
    from tratamento.vereditos import rotular

    esquema = esquema or esquema_mod.carregar_esquema()

    # Portão de normalizacao-rotulos: valor fora do mapa interrompe o corpus
    # inteiro antes de qualquer unidade existir. `rotular` levanta
    # VeredictoDesconhecido; o rótulo devolvido não entra no índice.
    for valor in df["alternativeName"]:
        if valor.strip():
            rotular(valor)

    unidades, fragmentos, quarentena = [], [], []
    contagem: dict[str, int] = {}

    def conta(chave: str) -> None:
        contagem[chave] = contagem.get(chave, 0) + 1

    for url, grupo in df.groupby("URL", sort=False):
        agencia = grupo["Author"].iloc[0]
        if esquema_mod.normalizar_url(url) in urls_ja_indexadas:
            quarentena.append({"corpus": CORPUS_FACTCKBR, "url": url, "agencia": agencia,
                               "motivo": "duplicata_factcenter", "linhas": len(grupo)})
            conta("quarentena_duplicata_factcenter")
            continue

        linhas = grupo.to_dict("records")
        validas = [all(l[c].strip() for c in CAMPOS_EXIGIDOS_FACTCKBR) for l in linhas]
        if not any(validas):
            quarentena.append({"corpus": CORPUS_FACTCKBR, "url": url, "agencia": agencia,
                               "motivo": "campo_vazio", "linhas": len(grupo)})
            conta("quarentena_campo_vazio")
            continue

        rid = esquema_mod.registro_id(CORPUS_FACTCKBR, url, esquema)
        atributos = esquema_mod.atributos_de_corpus(CORPUS_FACTCKBR, agencia, esquema)
        disposicao = "unica" if len(linhas) == 1 else "segmentada"
        conta(disposicao)

        for i, (linha, valida) in enumerate(zip(linhas, validas)):
            # O índice é a ordem da linha dentro da URL, com lacuna quando uma
            # irmã vai para a quarentena: o id das demais não depende dela.
            unidade_id = f"{rid}-{i:02d}"
            if not valida:
                vazios = [c for c in CAMPOS_EXIGIDOS_FACTCKBR if not linha[c].strip()]
                quarentena.append({"corpus": CORPUS_FACTCKBR, "url": url, "agencia": agencia,
                                   "unidade_id": unidade_id, "motivo": "campo_vazio",
                                   "campos_vazios": vazios})
                conta("unidade_em_quarentena")
                continue
            unidade = {
                "registro_id": rid, "unidade_id": unidade_id, "indice_alegacao": i,
                **atributos, "agencia": agencia, "url": url,
                # A Lupa grava data e hora; o esquema guarda só a data.
                "data_publicacao": linha["datePublished"].strip()[:10],
                "obtido_em": None,
                "titulo": _limpar(linha["title"]), "subtitulo": None,
                "alegacoes_no_registro": len(linhas),
                "alegacao": _limpar(linha["claimReviewed"]),
                "veredito_original": linha["alternativeName"].strip(),
                "veredito_chave": chave_canonica(linha["alternativeName"]),
                "justificativa": linha["reviewBody"].strip(),
                "origem_alegacao": "claim_review",
                "disposicao": disposicao,
                "cobre_multiplas_alegacoes": False,
            }
            fragmentos.extend(_fragmentos_da_unidade(
                unidade, atributos, _cabecalho(unidade, atributos["agencia_nome"])))
            unidades.append(unidade)

    return unidades, fragmentos, quarentena, contagem


def construir_indice(df_factcenter, df_factckbr, validar_esquema: bool = True
                     ) -> tuple[list[dict], list[dict], list[dict], dict]:
    """Índice dos dois corpora, FactCenter à frente e intacto.

    A ordem importa: a matriz densa tem uma linha por fragmento, e o FactCenter
    na frente, igual ao que era, permite estender a matriz em vez de refazê-la.
    """
    esquema = esquema_mod.carregar_esquema()
    uni_fc, frag_fc, q_fc, manifesto = construir(df_factcenter, validar_esquema=False)
    ja_indexadas = {esquema_mod.normalizar_url(u["url"]) for u in uni_fc}
    uni_fb, frag_fb, q_fb, contagem_fb = construir_factckbr(df_factckbr, ja_indexadas, esquema)

    unidades, fragmentos, quarentena = uni_fc + uni_fb, frag_fc + frag_fb, q_fc + q_fb
    manifesto["por_corpus"] = {
        CORPUS: {"registros_lidos": len(df_factcenter),
                 "unidades": len(uni_fc), "fragmentos": len(frag_fc),
                 "disposicoes": manifesto["disposicoes"]},
        CORPUS_FACTCKBR: {"linhas_lidas": len(df_factckbr),
                          "registros_lidos": int(df_factckbr["URL"].nunique()),
                          "unidades": len(uni_fb), "fragmentos": len(frag_fb),
                          "disposicoes": contagem_fb,
                          "apto_citacao": esquema["x-corpora"][CORPUS_FACTCKBR]["apto_citacao"]},
    }
    manifesto.update({
        "registros_lidos": len(df_factcenter) + int(df_factckbr["URL"].nunique()),
        "unidades_indexadas": len(unidades),
        "fragmentos_indexados": len(fragmentos),
        "registros_em_quarentena": sum(1 for q in quarentena if not q.get("unidade_id")),
        "unidades_em_quarentena": sum(1 for q in quarentena if q.get("unidade_id")),
    })
    manifesto["esquema"]["versao"] = esquema["x-versao"]
    if validar_esquema:
        laudo = esquema_mod.validar(unidades, fragmentos, quarentena, esquema)
        esquema_mod.exigir(laudo)
        manifesto["esquema"]["aprovado"] = True
    return unidades, fragmentos, quarentena, manifesto


def _gravar(caminho: pathlib.Path, registros) -> None:
    with caminho.open("w", encoding="utf-8") as saida:
        for registro in registros:
            saida.write(json.dumps(registro, ensure_ascii=False) + "\n")


def main() -> None:
    laudo = corpus_mod.verificar_integridade_textual()
    laudo_fb = corpus_mod.verificar_integridade_auxiliar(CORPUS_FACTCKBR)
    unidades, fragmentos, quarentena, manifesto = construir_indice(
        corpus_mod.ler_corpus(), corpus_mod.ler_factckbr())
    manifesto["integridade_textual"] = laudo
    manifesto["integridade_textual_factckbr"] = laudo_fb

    SAIDA.mkdir(parents=True, exist_ok=True)
    _gravar(SAIDA / "unidades.jsonl", unidades)
    _gravar(SAIDA / "fragmentos.jsonl", fragmentos)
    _gravar(SAIDA / "quarentena.jsonl", quarentena)
    (SAIDA / "manifesto.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({k: v for k, v in manifesto.items()
                      if k != "integridade_textual"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
