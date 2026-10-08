"""Chamada ao gerador local e leitura de JSON, comum aos prompts de verificação.

Mesma configuração das sondas de 18/09 e 28/09: Gemma 4 12B QAT, `think: false`,
temperatura 0.2. Os prompts recebem `chat` como parâmetro para que os testes
troquem o modelo por uma função que devolve texto fixo.

`ChatDeepSeek` é o gerador remoto (add-gerador-api-deepseek): objeto chamável
com a mesma assinatura de `chat_ollama`, mesma temperatura e mesmo teto de
saída, raciocínio desligado (D1). Uma nova tentativa só em falha passageira
(D5). Chave fora do `repr` e de log e erro (D4).
"""
import json
import logging
import os
import re
import time

MODELO = "gemma4:12b-it-qat"
OPCOES = {"temperature": 0.2, "num_ctx": 8192, "num_predict": 1200}


def chat_ollama(sistema, usuario, modelo=MODELO, cpu=False):
    """Texto da resposta do modelo, pedido em modo JSON."""
    import ollama
    resp = ollama.chat(model=modelo, think=False, format="json", messages=[
        {"role": "system", "content": sistema},
        {"role": "user", "content": usuario},
    ], options={**OPCOES, **({"num_gpu": 0} if cpu else {})})
    return resp["message"].get("content") or ""


URL_DEEPSEEK = "https://api.deepseek.com/chat/completions"
MODELO_REMOTO = "deepseek-v4-pro"
PASSAGEIRO = {429, 500, 502, 503}
ESPERA = 1.0
TEMPO_LIMITE = 60.0

log = logging.getLogger(__name__)


class ErroGerador(RuntimeError):
    """Falha do gerador remoto. A mensagem só tem tipo e status, nunca texto nem chave."""


class _Passageira(Exception):
    pass


class ChatDeepSeek:
    """Gerador remoto. `modelo_servido` guarda o `model` da última resposta e `uso`
    soma os tokens que a API informa, para a bancada registrar o custo (D7)."""

    def __init__(self, chave=None, modelo=None, cliente=None):
        self.chave = chave or (os.environ.get("DEEPSEEK_API_KEY") or "").strip() or None
        if self.chave is None:
            raise ErroGerador("DEEPSEEK_API_KEY ausente")
        self.modelo = modelo or os.environ.get("DEEPSEEK_MODELO") or MODELO_REMOTO
        self.cliente = cliente or httpx_cliente()
        self.modelo_servido = None
        self.uso = {"chamadas": 0, "entrada": 0, "entrada_cache": 0, "saida": 0}

    def __repr__(self):
        return f"ChatDeepSeek(modelo={self.modelo!r})"

    def __call__(self, sistema, usuario):
        corpo = {"model": self.modelo,
                 "messages": [{"role": "system", "content": sistema},
                              {"role": "user", "content": usuario}],
                 "response_format": {"type": "json_object"},
                 "thinking": {"type": "disabled"},
                 "temperature": OPCOES["temperature"],
                 "max_tokens": OPCOES["num_predict"]}
        for tentativa in (1, 2):
            try:
                return self._pedir(corpo)
            except _Passageira as e:
                log.warning("deepseek: falha passageira (%s), tentativa %d", e, tentativa)
                if tentativa == 2:
                    raise ErroGerador(f"DeepSeek falhou duas vezes: {e}") from None
                time.sleep(ESPERA)

    def _pedir(self, corpo):
        import httpx
        try:
            resp = self.cliente.post(URL_DEEPSEEK, json=corpo, timeout=TEMPO_LIMITE,
                                     headers={"Authorization": f"Bearer {self.chave}"})
        except httpx.HTTPError as e:
            log.error("deepseek: %s", type(e).__name__)
            raise ErroGerador(f"DeepSeek sem resposta: {type(e).__name__}") from None
        if resp.status_code in PASSAGEIRO:
            raise _Passageira(f"status {resp.status_code}")
        if resp.status_code != 200:
            log.error("deepseek: status %d", resp.status_code)
            raise ErroGerador(f"DeepSeek respondeu {resp.status_code}")
        dados = resp.json()
        self.modelo_servido = dados.get("model")
        uso = dados.get("usage") or {}
        self.uso["chamadas"] += 1
        self.uso["entrada"] += uso.get("prompt_tokens", 0)
        self.uso["entrada_cache"] += uso.get("prompt_cache_hit_tokens", 0)
        self.uso["saida"] += uso.get("completion_tokens", 0)
        escolha = dados["choices"][0]
        if escolha.get("finish_reason") == "length":
            log.warning("deepseek: saída cortada no limite de tokens (%d)", OPCOES["num_predict"])
        conteudo = escolha["message"].get("content")
        if not conteudo:
            raise _Passageira("content vazio")
        return conteudo


def httpx_cliente():
    """Cliente único por processo: reaproveita a conexão TLS entre etapas (D1)."""
    global _CLIENTE
    if _CLIENTE is None:
        import httpx
        _CLIENTE = httpx.Client()
    return _CLIENTE


_CLIENTE = None


def ler_json(bruto):
    """Objeto JSON da saída, aceitando bloco de código em volta. None se não for objeto."""
    texto = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", bruto or "")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError:
        return None
    return dados if isinstance(dados, dict) else None
