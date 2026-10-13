"""Sonda da cobertura por alegação mais ampla — D8 de add-cobertura-alegacao-ampla.

Mesmo molde de `sonda_classificacao_guarda.py`: trechos reais do índice,
escolhidos à mão por `fragmento_id`, sem recuperação, rodando a guarda inteira
(classificação, seis travas e verificação de implicação). O que se mede é o que
a guarda faz com o trecho que chega.

Casos A: a alegação é caso particular de uma alegação checada como falsa por
duas agências; o rótulo tem de ser `falso`. Casos N: a guarda tem de chegar a
`evidência insuficiente`. N1 e N2 repetem G4 e G3 da decisão 12 com duas
agências, para que a trava das duas agências não esconda falha da implicação.
N4 usa trechos escritos para a sonda, marcados como sintéticos, porque o acervo
não tem checagem com essa forma.

Aceite: todos os casos passam em todas as tentativas. Basta um falso positivo
para reprovar.

Uso: python -m prototipo.sonda_cobertura_ampla [--gerador=ollama|deepseek] [--tentativas=N] [--cpu]
"""
import json
import pathlib
import sys
import time

from prototipo.verificacao.guarda import INSUFICIENTE, verificar

AQUI = pathlib.Path(__file__).parent

# Fragmentos reais (unidade_id = fragmento_id sem o último sufixo).
DNA_BOATOS = "7a0f573913-00-00"     # boatos, 2020: vacina modifica o DNA e gera seres geneticamente modificados
DNA_AOSFATOS = "0328f83578-00-00"   # aos fatos, 2020: vacina não causa dano irreversível ao DNA
CHIP_CHINA = "f678c48f67-00-00"     # boatos, 2020: nanochip 5G virá na vacina da China
CHIP_LIQUIDO = "185954a72d-00-00"   # fato-ou-fake, 2021: vacina não tem chip líquido para controle
JATOBA = "c7a4591df5-00-00"         # aos fatos, 2021: casca do jatobá não cura câncer
BICARBONATO = "f9eb4e5668-00-00"    # lupa: bicarbonato de sódio não cura câncer
CLOROQ_CURA = "6c68e7c0eb-00-00"    # aos fatos, 2020: médica engana ao dizer que cloroquina cura Covid-19
CLOROQ_100 = "3fe3ac1240-00-00"     # lupa, 2020: cloroquina não é "100% eficiente na cura"
CORONAVAC_ENGANOSO = "9adea6a455-00-00"  # Comprova: enganoso, CoronaVac "protege pela metade"

# Trechos escritos para a sonda (D8): o acervo não tem a checagem do N4.
SINTETICOS = {
    "sintetico-coracao-1": {
        "fragmento_id": "sintetico-coracao-1", "agencia": "agencia sintetica A",
        "url": "https://sintetico/coracao-1", "data_publicacao": "2021-07-01",
        "veredito_original": "falso", "veredito_chave": "falso", "apto_citacao": True,
        "alegacao": "Vacina da covid causa danos graves ao coração de todos que a tomam",
        "trecho": "É falso que a vacina da covid cause danos graves ao coração de todos que a "
                  "tomam. Casos de inflamação no coração são raros e em geral leves."},
    "sintetico-coracao-2": {
        "fragmento_id": "sintetico-coracao-2", "agencia": "agencia sintetica B",
        "url": "https://sintetico/coracao-2", "data_publicacao": "2021-07-02",
        "veredito_original": "falso", "veredito_chave": "falso", "apto_citacao": True,
        "alegacao": "Todo vacinado contra a covid terá problema grave no coração",
        "trecho": "Não é verdade que todo vacinado contra a covid terá problema grave no "
                  "coração. A vacina da covid é segura para a grande maioria."},
}

JACARE = "Vacina de Covid-19 transformam pessoas em jacarés"

SONDAS = [
    {"id": "A1_jacare", "esperado": "falso", "alegacao": JACARE,
     "fragmentos": [DNA_BOATOS, DNA_AOSFATOS]},
    {"id": "A2_chip_chines", "esperado": "falso",
     "alegacao": "Vacinas da COVID-19 têm chips chineses para nos monitorar",
     "fragmentos": [CHIP_CHINA, CHIP_LIQUIDO]},
    {"id": "N1_goiabeira_2ag", "esperado": INSUFICIENTE,
     "alegacao": "Chá de folha de goiabeira cura a dengue em 24 horas.",
     "fragmentos": [JATOBA, BICARBONATO]},
    {"id": "N2_cloroquina_2ag", "esperado": INSUFICIENTE,
     "alegacao": "Tomar hidroxicloroquina toda semana previne a covid.",
     "fragmentos": [CLOROQ_CURA, CLOROQ_100]},
    {"id": "N3_autismo_dna", "esperado": INSUFICIENTE, "alegacao": "Vacinas causam autismo.",
     "fragmentos": [DNA_BOATOS, DNA_AOSFATOS]},
    {"id": "N4_miocardite", "esperado": INSUFICIENTE, "sintetico": True,
     "alegacao": "A vacina da covid pode causar miocardite em alguns jovens.",
     "fragmentos": ["sintetico-coracao-1", "sintetico-coracao-2"]},
    {"id": "N5_uma_agencia", "esperado": INSUFICIENTE, "alegacao": JACARE,
     "fragmentos": [DNA_BOATOS]},
    {"id": "N6_enganoso", "esperado": INSUFICIENTE, "alegacao": JACARE,
     "fragmentos": [DNA_BOATOS, CORONAVAC_ENGANOSO]},
]


def carregar_trechos(sondas=SONDAS):
    """Fragmentos do índice no formato da recuperação, com `veredito_chave` da unidade."""
    ids = {i for s in sondas for i in s["fragmentos"] if i not in SINTETICOS}
    unidades = {i.rsplit("-", 1)[0] for i in ids}
    chave = {}
    with open(AQUI / "indice" / "unidades.jsonl", encoding="utf-8") as f:
        for linha in f:
            u = json.loads(linha)
            if u["unidade_id"] in unidades:
                chave[u["unidade_id"]] = u["veredito_chave"]
    por_id = dict(SINTETICOS)
    with open(AQUI / "indice" / "fragmentos.jsonl", encoding="utf-8") as f:
        for linha in f:
            frag = json.loads(linha)
            if frag["fragmento_id"] in ids:
                por_id[frag["fragmento_id"]] = {
                    **{k: frag[k] for k in ("fragmento_id", "agencia", "url", "data_publicacao",
                                            "veredito_original", "alegacao", "trecho",
                                            "apto_citacao")},
                    "veredito_chave": chave.get(frag["unidade_id"])}
    faltam = ids - set(por_id)
    if faltam:
        sys.exit(f"fragmentos ausentes do índice: {sorted(faltam)}")
    return por_id


def montar(sonda, trechos):
    """Trechos do caso, com score decrescente na ordem escrita: a implicação usa o
    de maior score, e a sonda escolhe qual é."""
    return [{**trechos[i], "score": round(0.9 - 0.01 * n, 2)}
            for n, i in enumerate(sonda["fragmentos"])]


def rodar(chat, trechos, tentativas=3, sondas=SONDAS):
    rel = {"tentativas": tentativas, "gerado_em": time.strftime("%Y-%m-%d %H:%M"), "sondas": []}
    for s in sondas:
        registro = {"id": s["id"], "alegacao": s["alegacao"], "esperado": s["esperado"],
                    "fragmentos": s["fragmentos"], "sintetico": bool(s.get("sintetico")),
                    "tentativas": []}
        for n in range(1, tentativas + 1):
            t0 = time.time()
            try:
                # Trechos escolhidos à mão: o piso da recuperação não se aplica.
                v = verificar(s["alegacao"], montar(s, trechos), chat=chat, limiar=None)
                erro = None
            except ValueError as e:
                v, erro = None, str(e)
            original = (v.original or {}) if v else {}
            registro["tentativas"].append({
                "n": n, "passou": v is not None and v.rotulo == s["esperado"],
                "segundos": round(time.time() - t0, 1),
                "rotulo": v.rotulo if v else None,
                "cobertura": v.cobertura if v and v.cobertura else original.get("cobertura"),
                "ponte": (v.ponte if v else "") or original.get("ponte"),
                "implicacao": v.implicacao if v else None,
                "rebaixado_por": v.rebaixado_por if v else None,
                "criterio": v.criterio if v else None,
                "modelo_disse": v.original if v else None, "erro": erro})
        registro["passou"] = sum(t["passou"] for t in registro["tentativas"])
        rel["sondas"].append(registro)
    return rel


def aceite(rel):
    """D8: todos os casos em todas as tentativas."""
    return all(r["passou"] == rel["tentativas"] for r in rel["sondas"])


def main():
    gerador = next((a.split("=")[1] for a in sys.argv if a.startswith("--gerador=")), "ollama")
    tentativas = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--tentativas=")), 3)
    cpu = "--cpu" in sys.argv
    if gerador == "deepseek":
        from prototipo.verificacao.modelo import ChatDeepSeek
        chat, modelo = ChatDeepSeek(), "deepseek"
    else:
        from prototipo.verificacao.modelo import MODELO, chat_ollama
        chat, modelo = (lambda s, u: chat_ollama(s, u, cpu=cpu)), MODELO
    sufixo = "" if gerador == "ollama" else f"_{gerador}"
    destino = AQUI / f"relatorio_sonda_cobertura_ampla{sufixo}.json"

    print(f"gerador: {gerador} ({modelo}) | tentativas={tentativas}\n" + "=" * 72)
    rel = {"gerador": gerador, "modelo": modelo, "cpu": cpu,
           **rodar(chat, carregar_trechos(), tentativas)}
    rel["aceite"] = aceite(rel)
    destino.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
    for r in rel["sondas"]:
        rotulos = ", ".join(f"{t['rotulo']}/{t['cobertura']}" for t in r["tentativas"])
        print(f"{r['id']:20s} {r['passou']}/{tentativas}  [{rotulos}]")
        for t in r["tentativas"]:
            if not t["passou"]:
                print(f"    -- n={t['n']}: {t['rebaixado_por'] or t['erro'] or t['criterio']}")
    print(f"aceite: {'SIM' if rel['aceite'] else 'NÃO'}  -> {destino.name}")


if __name__ == "__main__":
    main()
