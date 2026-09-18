"""Busca léxica sobre os fragmentos — task 2.3 de add-selecao-modelos-arquitetura-rag.

Existe por exigência de spec, não como reforço opcional: `arquitetura-recuperacao`
determina que versão apenas densa MUST NOT ser tratada como linha de base, e o
cenário que a sustenta é o do nome próprio de baixa frequência — `qdenga`,
`oropouche`, `semaglutida`, lote de vacina, dosagem. São os termos pelos quais
uma alegação de saúde é identificada, e são os que o denso trata pior.

BM25 Okapi, implementação `rank_bm25`, sobre o texto do fragmento (cabeçalho com
alegação e veredito + trecho da justificativa).
"""
from __future__ import annotations

import re

from .corpus import sem_acento

# O índice léxico dobra acento e caixa porque quem consulta digita "duvida" e
# "QDENGA". A dobra vale para o token indexado, nunca para o texto citado —
# `integridade-textual` exige o trecho idêntico ao da fonte, e o fragmento
# guarda esse trecho intacto em `trecho`.
TOKEN = re.compile(r"[0-9a-z]+")

# Lista curta e deliberada. Stopword demais apaga negação, e "não" é o que separa
# "vacina causa autismo" de "vacina não causa autismo".
VAZIAS = frozenset("""a o as os um uma uns umas de do da dos das em no na nos nas
por para com sem sob sobre entre e ou que se ao aos à às pelo pela pelos pelas
este esta estes estas esse essa esses essas isso aquilo ser e' eh foi sao e
ha ter tem tinha seu sua seus suas meu minha como mais menos ja ainda tambem
""".split())

MIN_TOKEN = 2


def tokenizar(texto: str) -> list[str]:
    bruto = TOKEN.findall(sem_acento(texto).lower())
    return [t for t in bruto if len(t) >= MIN_TOKEN and t not in VAZIAS]


class IndiceLexico:
    def __init__(self, fragmentos: list[dict]):
        from rank_bm25 import BM25Okapi

        self.fragmentos = fragmentos
        self.bm25 = BM25Okapi([tokenizar(f["texto"]) for f in fragmentos])

    def pontuar(self, consulta: str):
        """Score BM25 de todos os fragmentos, na ordem do índice."""
        import numpy as np

        return np.asarray(self.bm25.get_scores(tokenizar(consulta)), dtype="float32")

    def buscar(self, consulta: str, k: int = 20) -> list[tuple[int, float]]:
        import numpy as np

        scores = self.pontuar(consulta)
        topo = np.argpartition(-scores, min(k, len(scores) - 1))[:k]
        topo = topo[np.argsort(-scores[topo])]
        return [(int(i), float(scores[i])) for i in topo if scores[i] > 0]
