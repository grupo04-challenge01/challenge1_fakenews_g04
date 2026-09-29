"""Chamada ao gerador local e leitura de JSON, comum aos prompts de verificação.

Mesma configuração das sondas de 18/09 e 28/09: Gemma 4 12B QAT, `think: false`,
temperatura 0.2. Os prompts recebem `chat` como parâmetro para que os testes
troquem o modelo por uma função que devolve texto fixo.
"""
import json
import re

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


def ler_json(bruto):
    """Objeto JSON da saída, aceitando bloco de código em volta. None se não for objeto."""
    texto = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", bruto or "")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError:
        return None
    return dados if isinstance(dados, dict) else None
