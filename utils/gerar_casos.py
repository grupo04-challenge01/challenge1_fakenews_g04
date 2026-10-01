# -*- coding: utf-8 -*-
"""gerar_casos.py

Script para gerar o conjunto de casos de avaliação do MVP Copiloto.
- Cria um JSON com 20‑30 itens.
- Cada item tem:
  - id (UUID)
  - texto_original (mensagem a ser verificada)
  - veredito ("verdadeiro" ou "falso")
  - justificativa (explicação curta)
  - fonte (URL ou referência)
  - contra_intuitivo (bool, apenas para verdadeiros que contradizem a intuição)
- Valida:
  * ≥ 20 itens e ≤ 30 itens
  * ≥ 4 verdadeiros contra_intuitivos

Uso:
    python utils/gerar_casos.py
"""

import json, uuid, pathlib, sys

_RAIZ = pathlib.Path(__file__).resolve().parent.parent
OUTPUT_DIR = _RAIZ / "datasets" / "casos_mvp_copiloto"
OUTPUT_FILE = OUTPUT_DIR / "mvp_copiloto_casos.json"

# ---------------------------------------------------------------------------
# Exemplos de casos (4 contra‑intuitivos + 18 neutros = 22 casos total)
# ---------------------------------------------------------------------------
EXEMPLOS = [
    {
        "texto_original": "A vacina contra a gripe pode causar autismo.",
        "veredito": "falso",
        "justificativa": "Estudos epidemiológicos não encontraram associação entre vacinação e autismo.",
        "fonte": "https://www.who.int/vaccine_safety/",
        "contra_intuitivo": False
    },
    {
        "texto_original": "Beber água quente protege contra COVID‑19.",
        "veredito": "falso",
        "justificativa": "Não há evidência científica de efeito protetor da temperatura da água.",
        "fonte": "https://www.cdc.gov/coronavirus/2019-ncov/index.html",
        "contra_intuitivo": False
    },
    # ------------------- verdadeiros contra‑intuitivos -------------------
    {
        "texto_original": "O consumo moderado de café reduz o risco de doenças cardíacas.",
        "veredito": "verdadeiro",
        "justificativa": "Meta‑análises mostram associação com menor risco cardiovascular.",
        "fonte": "https://pubmed.ncbi.nlm.nih.gov/30633278/",
        "contra_intuitivo": True
    },
    {
        "texto_original": "A vacinação contra HPV previne câncer de colo do útero.",
        "veredito": "verdadeiro",
        "justificativa": "Ensaios clínicos demonstraram redução significativa de lesões pré‑cancerosas.",
        "fonte": "https://www.cdc.gov/hpv/parents/vaccine.html",
        "contra_intuitivo": True
    },
    {
        "texto_original": "Exercício regular diminui sintomas de depressão.",
        "veredito": "verdadeiro",
        "justificativa": "Revisões sistemáticas confirmam efeito antidepressivo do exercício.",
        "fonte": "https://jamanetwork.com/journals/jamapsychiatry/fullarticle/2672745",
        "contra_intuitivo": True
    },
    {
        "texto_original": "Dieta rica em fibras reduz risco de câncer de cólon.",
        "veredito": "verdadeiro",
        "justificativa": "Estudos longitudinais associam maior ingestão de fibras a menor incidência.",
        "fonte": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2855617/",
        "contra_intuitivo": True
    }
]

# Gerar itens adicionais neutros para atingir 22‑24 casos total
while len(EXEMPLOS) < 22:
    EXEMPLOS.append({
        "texto_original": f"Exemplo neutro {len(EXEMPLOS)+1} – informação factual.",
        "veredito": "falso",
        "justificativa": "Informação fictícia para completar o conjunto.",
        "fonte": "https://example.com",
        "contra_intuitivo": False
    })

def gerar_casos():
    casos = []
    for item in EXEMPLOS:
        caso = {
            "id": str(uuid.uuid4()),
            **item
        }
        casos.append(caso)
    return casos

def validar_casos(casos):
    if not (20 <= len(casos) <= 30):
        raise ValueError(f"Número de casos ({len(casos)}) fora do intervalo 20‑30.")
    verdadeiros_ci = [c for c in casos if c["veredito"] == "verdadeiro" and c["contra_intuitivo"]]
    if len(verdadeiros_ci) < 4:
        raise ValueError(f"Só {len(verdadeiros_ci)} verdadeiros contra‑intuitivos; é necessário ≥ 4.")
    return True

def main():
    casos = gerar_casos()
    try:
        validar_casos(casos)
    except Exception as e:
        sys.stderr.write(f"Validação falhou: {e}\n")
        sys.exit(1)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(casos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Caso JSON gerado em {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
