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

`alfa` é provisório e é parâmetro explícito para que a task 3.1 possa varrê-lo.
"""
from __future__ import annotations

ALFA_PADRAO = 0.5        # peso do denso; 1.0 = só denso, 0.0 = só léxico
PERCENTIL_FUNDO = 50     # o que o braço devolve para qualquer coisa
PERCENTIL_TOPO = 99      # escala em que o braço separa
K_RRF = 60
_EPS = 1e-6


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
        self.fragmentos = fragmentos
        self.unidades = {u["unidade_id"]: u for u in unidades}
        self.lexico = indice_lexico
        self.denso = indice_denso
        self.alfa = alfa

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

    def buscar(self, consulta: str, k: int = 10, modo: str = "hibrida",
               fusao: str = "score") -> list[dict]:
        """Devolve até `k` unidades, cada uma com seu melhor fragmento.

        A busca roda em fragmento e o resultado é reduzido a unidade: cinco
        fragmentos da mesma checagem ocupando o topo é uma checagem recuperada,
        não cinco evidências. A redução usa o melhor fragmento, que é o trecho
        que a resposta deve citar.
        """
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

        # Reduz a unidade antes de cortar em k, senão o corte pode gastar as k
        # vagas com fragmentos de uma checagem só.
        melhor: dict[str, int] = {}
        for i in np.argsort(-score)[: max(k * 20, 200)]:
            uid = self.fragmentos[i]["unidade_id"]
            if uid not in melhor:
                melhor[uid] = int(i)

        ordenadas = sorted(melhor.items(), key=lambda par: -score[par[1]])[:k]
        resultado = []
        for uid, i in ordenadas:
            fragmento = self.fragmentos[i]
            unidade = self.unidades[uid]
            resultado.append({
                "unidade_id": uid,
                "fragmento_id": fragmento["fragmento_id"],
                "score": float(score[i]),
                "score_lexico": float(s_lex[i]),
                "score_denso": float(s_den[i]),
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
            })
        return resultado
