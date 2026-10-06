"""Gravação e reprodução do modelo e da busca, para rodar a bateria sem Ollama.

A chave de cada chamada é o hash do que entrou nela: prompt de sistema e
mensagem para o modelo; consulta, `k`, modo e `alfa` para a busca. Prompt
alterado gera chave nova, e a reprodução falha com `GravacaoAusente` em vez de
devolver uma resposta de outro prompt.
"""
import hashlib
import json
import pathlib

PASTA = pathlib.Path(__file__).parent / "gravacoes"


class GravacaoAusente(KeyError):
    pass


def chave(*partes):
    bruto = json.dumps(partes, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(bruto.encode("utf-8")).hexdigest()[:16]


def vazio():
    return {"chat": {}, "busca": {}}


class _Busca:
    """Recuperador que grava (com `real`) ou reproduz (sem `real`)."""

    def __init__(self, dados, real=None, alfa=None):
        self._dados, self._real = dados, real
        self._alfa = alfa

    @property
    def alfa(self):
        return self._real.alfa if self._real is not None else self._alfa

    @alfa.setter
    def alfa(self, valor):
        if self._real is not None:
            self._real.alfa = valor
        else:
            self._alfa = valor

    def buscar(self, consulta, k=10, modo="hibrida"):
        c = chave(consulta, k, modo, self.alfa)
        if self._real is None:
            if c not in self._dados["busca"]:
                raise GravacaoAusente(f"busca sem gravação: {consulta!r}, k={k}, {modo}, alfa={self.alfa}")
            return self._dados["busca"][c]
        resultado = self._real.buscar(consulta, k=k, modo=modo)
        self._dados["busca"][c] = resultado
        return resultado


    def recuperar(self, consulta, k=10, modo="hibrida"):
        from prototipo.rag.hibrida import Recuperacao
        c = chave("recuperar", consulta, k, modo, self.alfa)
        if self._real is None:
            if c not in self._dados["busca"]:
                raise GravacaoAusente(f"recuperação sem gravação: {consulta!r}, k={k}, {modo}, alfa={self.alfa}")
            d = self._dados["busca"][c]
            return Recuperacao(d["idioma"], d["resultados"], d["coberto"], tuple(d["consultados"]))
        r = self._real.recuperar(consulta, k=k, modo=modo)
        self._dados["busca"][c] = {"idioma": r.idioma, "resultados": r.resultados,
                                   "coberto": r.coberto, "consultados": list(r.consultados)}
        return r


def gravando(dados, chat, recuperador):
    """(chat, recuperador) que repassam ao real e guardam o resultado em `dados`."""
    def chat_gravado(sistema, usuario):
        bruto = chat(sistema, usuario)
        dados["chat"][chave(sistema, usuario)] = bruto
        return bruto
    return chat_gravado, _Busca(dados, real=recuperador)


def reproduzindo(dados, alfa=None):
    """(chat, recuperador) que só devolvem o que está em `dados`."""
    def chat_reproduzido(sistema, usuario):
        c = chave(sistema, usuario)
        if c not in dados["chat"]:
            raise GravacaoAusente("chamada ao modelo sem gravação (prompt mudou?)")
        return dados["chat"][c]
    return chat_reproduzido, _Busca(dados, alfa=alfa)


def ler(caso_id, pasta=PASTA):
    arquivo = pasta / f"{caso_id}.json"
    return json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else vazio()


def gravar(caso_id, dados, pasta=PASTA):
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / f"{caso_id}.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
