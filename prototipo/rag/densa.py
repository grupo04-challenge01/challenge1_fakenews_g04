"""Busca densa exata em memória — task 2.4 de add-selecao-modelos-arquitetura-rag.

Sem banco vetorial e sem índice aproximado, por decisão 3 do `design.md`: na
escala de milhares de unidades, produto escalar sobre matriz densa em memória é
mais rápido que o tempo de rede de um serviço externo, e é **exato**. A decisão
reabre se o corpus crescer uma ordem de grandeza.

Modelo: `intfloat/multilingual-e5-base`, multilíngue e treinado para recuperação
— que é o critério da decisão 5 do `design.md`, onde o achado do MTEB-BR é que o
que separa os modelos não é terem sido pré-treinados em português, é terem sido
treinados para buscar. A comparação com um segundo modelo é a task 3.3 e não é
feita aqui; o modelo é parâmetro, não constante embutida.

O e5 exige prefixo assimétrico: `query:` na consulta, `passage:` no que é
indexado. Sem isso a qualidade cai sem erro visível.
"""
from __future__ import annotations

import pathlib

MODELO_PADRAO = "intfloat/multilingual-e5-base"
LOTE = 64


def _dispositivo() -> str:
    import torch

    if torch.backends.mps.is_available():
        return "mps"
    return "cuda" if torch.cuda.is_available() else "cpu"


class IndiceDenso:
    def __init__(self, matriz, modelo_nome: str = MODELO_PADRAO):
        self.matriz = matriz            # (n_fragmentos, dim), linhas normalizadas
        self.modelo_nome = modelo_nome
        self._codificador = None

    @property
    def codificador(self):
        if self._codificador is None:
            from sentence_transformers import SentenceTransformer

            self._codificador = SentenceTransformer(self.modelo_nome,
                                                    device=_dispositivo())
        return self._codificador

    @classmethod
    def construir(cls, fragmentos: list[dict], modelo_nome: str = MODELO_PADRAO,
                  progresso: bool = True) -> "IndiceDenso":
        import numpy as np
        from sentence_transformers import SentenceTransformer

        modelo = SentenceTransformer(modelo_nome, device=_dispositivo())
        textos = [f'passage: {f["texto"]}' for f in fragmentos]
        matriz = modelo.encode(textos, batch_size=LOTE, normalize_embeddings=True,
                               show_progress_bar=progresso,
                               convert_to_numpy=True).astype("float32")
        indice = cls(np.ascontiguousarray(matriz), modelo_nome)
        indice._codificador = modelo
        return indice

    @classmethod
    def carregar(cls, caminho: pathlib.Path,
                 modelo_nome: str = MODELO_PADRAO) -> "IndiceDenso":
        import numpy as np

        return cls(np.load(caminho), modelo_nome)

    def gravar(self, caminho: pathlib.Path) -> None:
        import numpy as np

        np.save(caminho, self.matriz)

    def pontuar(self, consulta: str):
        """Cosseno da consulta contra todos os fragmentos — exato, não aproximado.

        Vetores normalizados, então o produto escalar já é o cosseno, e o valor
        é absoluto: comparável entre consultas, que é o que a task 3.5 precisa
        para calibrar `evidência insuficiente`.
        """
        vetor = self.codificador.encode([f"query: {consulta}"],
                                        normalize_embeddings=True,
                                        convert_to_numpy=True).astype("float32")[0]
        return self.matriz @ vetor

    def buscar(self, consulta: str, k: int = 20) -> list[tuple[int, float]]:
        import numpy as np

        scores = self.pontuar(consulta)
        topo = np.argpartition(-scores, min(k, len(scores) - 1))[:k]
        topo = topo[np.argsort(-scores[topo])]
        return [(int(i), float(scores[i])) for i in topo]
