"""Fusão das duas listas e recuperador — task 2.5 de add-selecao-modelos-arquitetura-rag.

`arquitetura-recuperacao` exige duas coisas que puxam em direções diferentes:
a recuperação combina léxica e densa com fusão de listas, e o limiar de
`evidência insuficiente` é calibrado **sobre o score fundido**.

A segunda exigência descarta Reciprocal Rank Fusion como forma padrão. RRF é a
escolha usual e está implementada aqui, mas o score que ela produz é função da
posição, não da relevância: numa consulta sobre pauta ausente do corpus, o
primeiro colocado recebe exatamente o mesmo score que receberia numa consulta
perfeitamente atendida. Um limiar sobre score de RRF não distingue os dois
casos, e distinguir os dois casos é o que `frescor-corpus` manda fazer.

A forma padrão é a combinação convexa dos dois scores. O que decide a fusão,
porém, não é a combinação — é a escala em que cada braço entra nela. A primeira
versão somava cosseno cru com BM25 saturado e **anulava o braço denso**, o que
só apareceu na medição:

| Consulta | cosseno mediano | cosseno máximo | BM25 máximo |
| --- | --- | --- | --- |
| `chá da casca do jatobá cura câncer` | 0,787 | 0,893 | 35,1 |
| `hidroxicloroquina previne covid-19` | 0,816 | 0,903 | 11,3 |
| `como faço bolo de cenoura` | 0,762 | 0,826 | 13,2 |

O cosseno do e5 não é centrado: a mediana fica perto de 0,79 em qualquer
consulta e o topo raramente passa de 0,90. Todo o sinal vive numa faixa de
cerca de 0,06 muito longe do zero. Somado a um BM25 que varia de 0 a 35, ele
vira constante — contribuía o mesmo para todo candidato, e a ordem final saía
inteira do braço léxico. O sintoma foi concreto: em `hidroxicloroquina previne
covid-19` o braço denso achou a checagem certa, o léxico achou `dexametasona` e
`própolis`, e a fusão premiou o léxico.

Nenhuma constante fixa corrige isso, porque o fundo muda de consulta para
consulta. O que se adota é normalizar cada braço **contra o próprio fundo
daquela consulta**: a mediana sobre os 22.464 fragmentos é o que aquele braço
devolve para qualquer coisa, e a distância até o percentil 99 é a escala em que
ele separa. O resultado entra saturado em [0, 1), então os dois braços chegam à
combinação com variância comparável e sem depender do máximo da consulta — que
é o que normalização min-max faria, e que forçaria o primeiro colocado a 1,0
sempre, apagando a diferença entre achar e não achar.

Fica registrado o que este desenho **não** resolve. Nem cosseno nem BM25
separam bem pauta ausente: `como faço bolo de cenoura` alcança cosseno máximo
de 0,826 contra 0,893 de uma consulta perfeitamente atendida. O realce reduz a
distorção, não a elimina. Fixar o limiar de `evidência insuficiente` é a task
3.5, e a medição acima já diz que ela não sai de similaridade bruta.

`alfa` foi varrido na task 3.1 e deixou de ser provisório. O 0,5 inicial era
um chute, e a medição o reprovou: em 0,5 a fusão perde `a14`, `a16` e `a20` —
os três documentos que o braço denso sozinho recupera nas posições 5, 3 e 1. O
ruído léxico os empurrava para fora do top-10.

O padrão passa a ser **0,9**, e o que o autoriza não é o ótimo, é a forma da
curva e a validação:

| alfa | recall@5 | MRR |
| --- | --- | --- |
| 0,50 | 0,85 | 0,825 |
| 0,84 | 0,95 | 0,856 |
| **0,90** | **1,00** | **0,897** |
| 0,98 | 1,00 | 0,902 |
| 1,00 (só denso) | 1,00 | 0,877 |

Cinco valores, de 0,90 a 0,98, ficam dentro de 0,01 do topo com recall@5 de
1,00: é platô, não pico, e um erro de ±0,08 na calibração não muda o resultado.
Sob leave-one-out — alfa escolhido em 19 consultas, avaliado na vigésima — a
híbrida dá MRR de 0,8975 contra 0,8767 da densa pura. O ganho sobrevive a não
ver a consulta em que é medido.

**O resultado é do `e5-base`, e não se transfere.** No `e5-small` o melhor alfa
é 1,00 e a híbrida *perde* sob leave-one-out (0,8500 contra 0,8625), com a
escolha de alfa oscilando entre 0,74 e 1,00. A leitura que a medição sustenta é
«0,9 com `e5-base`», não «híbrida supera densa»: o braço léxico só corrige na
margem quando o braço denso já é bom. Trocar o modelo de embedding obriga a
revarrer — `python -m prototipo.rag varrer-alfa --modelo NOME`.

**Prioridade de idioma — task 1.4 de mvp-copiloto-verificacao, decisão 23.**
`recuperacao-evidencia` manda esgotar as fontes em português antes de recorrer
às em inglês. `buscar` continua sendo o ranking cru, que a aferição mede;
`recuperar` é a entrada do sistema. A consulta é pontuada **uma vez** sobre o
índice inteiro, e cada camada de idioma é um corte desse mesmo score: separar
em dois índices daria a cada um seu próprio fundo (`_sobre_o_fundo`), e o
limiar da 1.5 deixaria de valer igual nas duas camadas. O inglês só é
consultado quando o critério `cobre` diz que o português não cobre. Nenhum
corpus em inglês está indexado em 01/10/2026, então com o índice de hoje
`recuperar` devolve exatamente o que `buscar` devolve.

**Limiar de `evidência insuficiente` — task 1.5, decisão 27.** O critério
`cobre` padrão é o limiar `LIMIAR_EVIDENCIA`: a camada cobre se ao menos uma
unidade tem score fundido igual ou acima dele. A guarda usa o mesmo valor para
descartar trecho fraco. O valor é um piso, não um separador. Na calibração de
06/10, nenhum corte sobre score separa o trecho que cobre a alegação do trecho
que só fala de alegação parecida, e o modelo já devolve `evidência
insuficiente` nas 8 pautas ausentes do acervo. O piso fica abaixo da positiva
mais fraca (0,5785) e não corta nenhuma evidência que cobre; quem decide a
cobertura é o modelo, e o limite fica registrado na decisão 27. Vale para a
fusão por score com alfa 0,9 e `e5-base`. Em outro modo ou fusão o score muda
de escala, e quem chama passa seu próprio `cobre`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

ALFA_PADRAO = 0.9        # peso do denso; 1.0 = só denso, 0.0 = só léxico
                         # medido na task 3.1 para intfloat/multilingual-e5-base
PERCENTIL_FUNDO = 50     # o que o braço devolve para qualquer coisa
PERCENTIL_TOPO = 99      # escala em que o braço separa
K_RRF = 60
_EPS = 1e-6

# Ordem em que as camadas são esgotadas (recuperacao-evidencia). Os valores são
# os do enum `idioma` do esquema de indexação; o teste confere que batem.
PRIORIDADE_IDIOMA = ("pt-BR", "en")

# Piso do score fundido abaixo do qual o trecho conta como não recuperado.
# Calibrado na task 1.5 (decisão 27) para a fusão por score, alfa 0,9 e e5-base:
# a positiva mais fraca da calibração fica em 0,5785.
LIMIAR_EVIDENCIA = 0.55

# Fragmentos da mesma checagem que acompanham cada trecho citado até a resposta
# (decisão 29). Uma checagem tem mediana de 3 fragmentos e p90 de 8.
TETO_VIZINHOS = 3


def cobertura_padrao(resultados: list[dict], limiar: float = LIMIAR_EVIDENCIA) -> bool:
    """A camada cobre se ao menos uma unidade alcança o limiar (task 1.5).

    É o mesmo corte que a guarda aplica a cada trecho. Camada sem unidade acima
    dele não cobre, e a recuperação passa à camada seguinte de idioma.
    """
    return any(r["score"] >= limiar for r in resultados)


@dataclass(frozen=True)
class Recuperacao:
    """O que a recuperação entrega à verificação.

    `idioma` é a camada de onde vêm os `resultados`; `consultados`, as camadas
    pelas quais a busca passou, na ordem. Camada sem nenhuma fonte indexada não
    é consultada. `coberto` falso quer dizer que nenhuma camada satisfez o
    critério: os resultados são os da primeira camada não vazia. O veredito cai
    para `evidência insuficiente` na guarda, que corta com o mesmo limiar.
    """

    idioma: str | None
    resultados: list[dict]
    coberto: bool
    consultados: tuple[str, ...]


def _sobre_o_fundo(scores):
    """Quanto o score se destaca do que este braço devolve nesta consulta.

    Devolve valores em [0, 1): 0 para tudo que está na mediana ou abaixo, 0,5
    para o que está exatamente no percentil 99, e assintota em 1 para o que o
    ultrapassa com folga.
    """
    import numpy as np

    fundo = np.percentile(scores, PERCENTIL_FUNDO)
    escala = max(float(np.percentile(scores, PERCENTIL_TOPO) - fundo), _EPS)
    destaque = np.clip((scores - fundo) / escala, 0.0, None)
    return (destaque / (destaque + 1.0)).astype("float32")


class Recuperador:
    """Une fragmentos, índice léxico e índice denso numa única consulta."""

    MODOS = ("lexica", "densa", "hibrida")

    def __init__(self, fragmentos, unidades, indice_lexico, indice_denso,
                 alfa: float = ALFA_PADRAO):
        import numpy as np

        self.fragmentos = fragmentos
        self.unidades = {u["unidade_id"]: u for u in unidades}
        self.lexico = indice_lexico
        self.denso = indice_denso
        self.alfa = alfa
        # Fragmento de índice anterior ao esquema 1.0.0 não tem `idioma`; a
        # busca crua segue funcionando, e só `recuperar` o recusa.
        self._idioma = np.array([f.get("idioma") for f in fragmentos], dtype=object)

    # ---- fusão ----------------------------------------------------------

    def _fundir_por_score(self, s_lex, s_den):
        return (self.alfa * _sobre_o_fundo(s_den)
                + (1 - self.alfa) * _sobre_o_fundo(s_lex))

    def _fundir_por_rrf(self, s_lex, s_den):
        """Alternativa por posição, mantida para a comparação da task 3.1."""
        import numpy as np

        fundido = np.zeros(len(s_lex), dtype="float32")
        for scores in (s_lex, s_den):
            ordem = np.argsort(-scores)
            posicao = np.empty(len(scores), dtype="int64")
            posicao[ordem] = np.arange(len(scores))
            fundido += (1.0 / (K_RRF + posicao + 1)).astype("float32")
        return fundido

    # ---- consulta -------------------------------------------------------

    def _pontuar(self, consulta: str, modo: str, fusao: str):
        """Score de todos os fragmentos do índice, mais os brutos de cada braço."""
        import numpy as np

        if modo not in self.MODOS:
            raise ValueError(f"modo desconhecido: {modo!r}; use {self.MODOS}")

        zero = np.zeros(len(self.fragmentos), dtype="float32")
        s_lex = self.lexico.pontuar(consulta) if modo != "densa" else zero
        s_den = self.denso.pontuar(consulta) if modo != "lexica" else zero

        if modo == "lexica":
            score = _sobre_o_fundo(s_lex)
        elif modo == "densa":
            score = _sobre_o_fundo(s_den)
        elif fusao == "rrf":
            score = self._fundir_por_rrf(s_lex, s_den)
        else:
            score = self._fundir_por_score(s_lex, s_den)
        return score, s_lex, s_den

    def _reduzir(self, score, s_lex, s_den, k: int, mascara=None) -> list[dict]:
        """Ordena, reduz a unidade e corta em `k`.

        `mascara` restringe os candidatos sem tocar no score de quem fica: o
        excluído vai para −∞ e é descartado depois da ordenação. Máscara toda
        verdadeira deixa o vetor idêntico, e a ordem — empates inclusive — é a
        mesma da busca sem máscara.
        """
        import numpy as np

        if mascara is not None:
            score = score.copy()
            score[~mascara] = -np.inf

        # Reduz a unidade antes de cortar em k, senão o corte pode gastar as k
        # vagas com fragmentos de uma checagem só.
        melhor: dict[str, int] = {}
        for i in np.argsort(-score)[: max(k * 20, 200)]:
            if mascara is not None and not mascara[i]:
                continue
            uid = self.fragmentos[i]["unidade_id"]
            if uid not in melhor:
                melhor[uid] = int(i)

        ordenadas = sorted(melhor.items(), key=lambda par: -score[par[1]])[:k]
        return [self._resultado(i, score, s_lex, s_den) for _, i in ordenadas]

    def _resultado(self, i: int, score, s_lex, s_den) -> dict:
        """Um fragmento no formato que a busca entrega, com os dados da unidade."""
        fragmento = self.fragmentos[i]
        uid = fragmento["unidade_id"]
        unidade = self.unidades[uid]
        return {
            "unidade_id": uid,
            "fragmento_id": fragmento["fragmento_id"],
            "score": float(score[i]),
            "score_lexico": float(s_lex[i]),
            "score_denso": float(s_den[i]),
            "idioma": fragmento.get("idioma"),
            # Decisão 17: fragmento inapto não serve de âncora. A busca só
            # entrega a marca; ausente (índice anterior ao esquema 1.0.0)
            # sai `None`, e a ancoragem decide — a busca não supõe valor.
            "apto_citacao": fragmento.get("apto_citacao"),
            "agencia": unidade["agencia"],
            "data_publicacao": unidade["data_publicacao"],
            "url": unidade["url"],
            "alegacao": unidade["alegacao"],
            "veredito_original": unidade["veredito_original"],
            "veredito_chave": unidade["veredito_chave"],
            "cobre_multiplas_alegacoes": unidade["cobre_multiplas_alegacoes"],
            # Trecho literal, para citação fiel. A disponibilidade do texto
            # no índice não autoriza reproduzi-lo inteiro ao usuário
            # (arquitetura-recuperacao, cenário "Indexação não autoriza
            # reprodução").
            "trecho": fragmento["trecho"],
        }

    def buscar(self, consulta: str, k: int = 10, modo: str = "hibrida",
               fusao: str = "score") -> list[dict]:
        """Devolve até `k` unidades, cada uma com seu melhor fragmento.

        A busca roda em fragmento e o resultado é reduzido a unidade: cinco
        fragmentos da mesma checagem ocupando o topo é uma checagem recuperada,
        não cinco evidências. A redução usa o melhor fragmento, que é o trecho
        que a resposta deve citar.

        É o ranking cru, sem prioridade de idioma — o que a aferição mede. A
        entrada do sistema é `recuperar`.
        """
        return self._reduzir(*self._pontuar(consulta, modo, fusao), k)

    def recuperar(self, consulta: str, k: int = 10, modo: str = "hibrida",
                  fusao: str = "score",
                  cobre: Callable[[list[dict]], bool] = cobertura_padrao) -> Recuperacao:
        """Esgota o português antes de recorrer ao inglês (recuperacao-evidencia).

        Pontua uma vez e percorre `PRIORIDADE_IDIOMA`. A primeira camada que
        `cobre` aceita é a resposta, e as seguintes nem são cortadas: se o
        português cobre, nenhuma fonte em inglês entra. Se nenhuma cobre,
        devolve a primeira camada não vazia com `coberto=False`.
        """
        import numpy as np

        fora = sorted({str(i) for i in self._idioma} - set(PRIORIDADE_IDIOMA))
        if fora:
            raise ValueError(
                f"fragmento com idioma fora de {PRIORIDADE_IDIOMA}: {fora}. "
                "`None` é índice anterior ao esquema de indexação 1.0.0 — rode "
                "`python -m prototipo.rag construir`; outro valor exige "
                "atualizar o esquema e a prioridade juntos.")

        score, s_lex, s_den = self._pontuar(consulta, modo, fusao)
        consultados: list[str] = []
        reserva: tuple[str, list[dict]] | None = None
        for idioma in PRIORIDADE_IDIOMA:
            mascara = self._idioma == idioma
            if not np.any(mascara):
                continue
            consultados.append(idioma)
            resultados = self._reduzir(score, s_lex, s_den, k, mascara)
            if cobre(resultados):
                return Recuperacao(idioma, resultados, True, tuple(consultados))
            if reserva is None and resultados:
                reserva = (idioma, resultados)

        idioma, resultados = reserva if reserva else (None, [])
        return Recuperacao(idioma, resultados, False, tuple(consultados))

    def expandir(self, consulta: str, trechos: list[dict], teto: int = TETO_VIZINHOS,
                 modo: str = "hibrida", fusao: str = "score") -> list[dict]:
        """Os trechos citados e, depois deles, outros fragmentos das mesmas checagens.

        A busca reduz a unidade e entrega o melhor fragmento de cada checagem,
        mas o fato que decide a resposta pode estar em outro fragmento dela. No
        R4 da bancada, a data do vídeo estava no quarto fragmento, o modelo só
        viu o primeiro e escreveu a data de memória (decisão 29). Cada checagem
        citada ganha até `teto` fragmentos seus, pelos mais próximos da
        consulta. Os citados ficam na frente e na mesma ordem, para que T1..Tn
        continuem sendo os trechos do veredito.
        """
        if not trechos:
            return []
        if not hasattr(self, "_por_unidade"):
            self._por_unidade: dict[str, list[int]] = {}
            for i, f in enumerate(self.fragmentos):
                self._por_unidade.setdefault(f["unidade_id"], []).append(i)

        score, s_lex, s_den = self._pontuar(consulta, modo, fusao)
        saida = list(trechos)
        vistos = {t["fragmento_id"] for t in trechos}
        for t in trechos:
            outros = [i for i in self._por_unidade.get(t["unidade_id"], [])
                      if self.fragmentos[i]["fragmento_id"] not in vistos]
            outros.sort(key=lambda i: -score[i])
            for i in outros[:teto]:
                saida.append(self._resultado(i, score, s_lex, s_den))
                vistos.add(self.fragmentos[i]["fragmento_id"])
        return saida
