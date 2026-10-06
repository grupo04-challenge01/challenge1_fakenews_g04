"""Calibração do limiar de `evidência insuficiente` — task 1.5 de mvp-copiloto-verificacao.

Spec `verificacao-alegacao`: o sistema MUST usar `evidência insuficiente` quando a
recuperação não retornar fonte que cubra a alegação. O limiar decide quando um
trecho recuperado conta como não recuperado. Ver decisão 27 do design.md.

A sonda mede o limiar junto com o modelo, porque é o par que decide. Três
famílias de caso, todas tiradas de `rag/consultas_afericao.json`:

- `pos`: as 20 consultas de aferição, com a checagem correta no índice. O
  limiar não pode cortar o trecho dela.
- `vizinho`: as mesmas 20, com o registro correto mascarado. É a lacuna de
  acervo com trecho recuperado: o que sobra é de assunto parecido. Às vezes
  outra checagem cobre a mesma alegação, e aí o veredito é legítimo. A
  adjudicação está em `ADJUDICACAO`, feita lendo o trecho citado.
- `ausente`: as 8 consultas sem alvo (pauta posterior ao acervo ou fora de saúde).

Cada caso vai à guarda com `limiar=None`, e o relatório guarda o rótulo do
modelo e os scores. A grade de limiares é calculada depois, sobre o relatório:
um trecho abaixo do limiar sai antes do modelo, então o caso cai para
`evidência insuficiente` quando todos os trechos que o modelo citou ficam abaixo.

Uso: python -m prototipo.sonda_limiar [modelo] [--reavaliar]

`--reavaliar` recalcula a grade sobre o relatório gravado, sem índice nem modelo.
"""
import json
import pathlib
import sys
import time

AQUI = pathlib.Path(__file__).parent
RELATORIO = AQUI / "relatorio_sonda_limiar.json"
_args = [a for a in sys.argv[1:] if not a.startswith("--")]
MODELO = _args[0] if _args else "gemma4:12b-it-qat"
K = 5   # trechos que vão à guarda, como na bancada
GRADE = [round(0.50 + 0.005 * i, 3) for i in range(61)]   # 0,50 a 0,80

# Vizinho com veredito: a outra checagem cobre a mesma alegação? Lido no trecho
# citado em 06/10/2026. Vizinho com `evidência insuficiente` não precisa: o
# modelo já não usou o trecho.
ADJUDICACAO = {
    "a01": (False, "trecho diz que a vacina protege a vida toda; não fala de mutação"),
    "a02": (True, "duas listas do Boatos.org desmentem a mesma 'vacina da gripe é veneno mortal'"),
    "a03": (True, "Lupa desmente a mesma ligação entre vacina H1N1 e narcolepsia"),
    "a04": (True, "Boatos.org diz que quem tomou na infância não precisa tomar de novo"),
    "a05": (True, "lista de boatos da febre amarela traz '50% de letalidade'"),
    "a06": (True, "lista de boatos da febre amarela traz a cegueira"),
    "a07": (False, "trechos falam de 'veneno mortal', não de mercúrio; o critério inventa o mercúrio"),
    "a10": (True, "Lupa desmente que chá de erva-doce tem as propriedades do Tamiflu"),
    "a11": (True, "lista de boatos da febre amarela traz o médico de Sorocaba e o fígado"),
    "a12": (True, "Boatos.org chama de bobagem que o governo inventou a febre amarela para vender vacina"),
    "a13": (False, "trecho fala do estudo retratado sobre autismo, não da bula"),
    "a14": (True, "Aos Fatos desmente a mesma decisão do STF sobre imigrantes venezuelanos"),
    "a15": (True, "Lupa diz que a vacina vale dez anos, que responde à pergunta"),
    "a16": (True, "Boatos.org desmente o mesmo veto de Lula à vacina da meningite"),
    "a17": (False, "patente do coronavírus, não do zika nem dos Rockefeller"),
    "a19": (True, "Lupa desmente o mesmo estudo da UFMG sobre suco de inhame"),
    "a20": (False, "vacina da covid baixando imunidade; a alegação é a da H1N1 e câncer"),
}


def _registro(unidade):
    return unidade.get("registro_id") or unidade["unidade_id"].split("-")[0]


def coletar():
    import numpy as np

    from prototipo.rag import afericao
    from prototipo.rag.__main__ import carregar
    from prototipo.verificacao import guarda
    from prototipo.verificacao.modelo import chat_ollama

    def chat(sistema, usuario):
        return chat_ollama(sistema, usuario, modelo=MODELO)

    r = carregar()
    registro_do_fragmento = np.array([_registro(r.unidades[f["unidade_id"]])
                                      for f in r.fragmentos], dtype=object)
    corpus_da_unidade = {f["unidade_id"]: f.get("corpus") for f in r.fragmentos}

    dados = afericao.carregar_consultas()
    casos = []
    for c in dados["consultas"]:
        casos.append(("pos", c, None))
        casos.append(("vizinho", c, c["registro_id"]))
    for c in dados["consultas_sem_alvo"]["consultas"]:
        casos.append(("ausente", c, None))

    saida = []
    for tipo, c, mascarar in casos:
        score, s_lex, s_den = r._pontuar(c["consulta"], "hibrida", "score")
        mascara = None if mascarar is None else registro_do_fragmento != mascarar
        trechos = r._reduzir(score, s_lex, s_den, K, mascara)
        inicio = time.perf_counter()
        v = guarda.verificar(c["consulta"], trechos, chat=chat, limiar=None)
        registros = [_registro(t) for t in trechos]
        alvo = c.get("registro_id")
        caso = {
            "tipo": tipo, "id": c["id"], "familia": c.get("familia", ""),
            "consulta": c["consulta"],
            "posicao_do_alvo": (registros.index(alvo) + 1
                                if tipo == "pos" and alvo in registros else None),
            "trechos": [{"score": round(t["score"], 4), "cosseno": round(t["score_denso"], 4),
                         "corpus": corpus_da_unidade.get(t["unidade_id"]),
                         "agencia": t["agencia"], "veredito_original": t["veredito_original"],
                         "alegacao": t["alegacao"][:140]} for t in trechos],
            "rotulo": v.rotulo,
            "citados": [trechos.index(t) + 1 for t in v.trechos],
            "criterio": v.criterio,
            "segundos": round(time.perf_counter() - inicio, 1),
        }
        saida.append(caso)
        print(f"{tipo:8} {c['id']} top={trechos[0]['score']:.3f} -> {v.rotulo} "
              f"{caso['citados']}", flush=True)
    return saida


def cobre(caso):
    """Verdade da calibração: a evidência que chegou ao modelo cobre a alegação?"""
    if caso["tipo"] == "pos":
        return True
    if caso["tipo"] == "ausente" or not caso["citados"]:
        return False
    return ADJUDICACAO[caso["id"]][0]


def aplicar(caso, limiar):
    """Rótulo depois do corte: some todo trecho citado abaixo do limiar, cai.

    Para `pos` vale o trecho da checagem correta, não o citado: cortá-lo é perder
    a evidência, mesmo que o modelo ainda achasse outro trecho.
    """
    if caso["tipo"] == "pos":
        alvo = caso["trechos"][caso["posicao_do_alvo"] - 1]["score"]
        return "perde" if alvo < limiar else "mantem"
    if not caso["citados"]:
        return "insuficiente"
    if all(caso["trechos"][i - 1]["score"] < limiar for i in caso["citados"]):
        return "insuficiente"
    return "veredito"


def avaliar(casos):
    pos = [c for c in casos if c["tipo"] == "pos"]
    legitimos = [c for c in casos if c["tipo"] != "pos" and c["citados"] and cobre(c)]
    erros = [c for c in casos if c["tipo"] != "pos" and c["citados"] and not cobre(c)]
    grade = []
    for limiar in GRADE:
        grade.append({
            "limiar": limiar,
            "positivas_perdidas": [c["id"] for c in pos if aplicar(c, limiar) == "perde"],
            "legitimos_perdidos": [c["id"] for c in legitimos
                                   if aplicar(c, limiar) == "insuficiente"],
            "erros_pegos": [c["id"] for c in erros if aplicar(c, limiar) == "insuficiente"],
        })
    sem_perda = [g["limiar"] for g in grade
                 if not g["positivas_perdidas"] and not g["legitimos_perdidos"]]
    alvos = [c["trechos"][c["posicao_do_alvo"] - 1]["score"] for c in pos]
    return {
        "modelo_sozinho": {
            "positivas_com_veredito": sum(c["rotulo"] != "evidência insuficiente" for c in pos),
            "positivas": len(pos),
            "ausentes_insuficiente": sum(c["rotulo"] == "evidência insuficiente"
                                         for c in casos if c["tipo"] == "ausente"),
            "ausentes": sum(c["tipo"] == "ausente" for c in casos),
            "vizinhos_insuficiente": sum(c["rotulo"] == "evidência insuficiente"
                                         for c in casos if c["tipo"] == "vizinho"),
            "vizinhos_legitimos": [c["id"] for c in legitimos],
            "vizinhos_erro": [c["id"] for c in erros],
        },
        "score_do_alvo_nas_positivas": {"minimo": min(alvos), "ordenados": sorted(alvos)},
        "maior_limiar_sem_perda": max(sem_perda),
        "trechos_factckbr_entre_os_k": sum(t["corpus"] == "factckbr"
                                           for c in casos for t in c["trechos"]),
        "grade": grade,
    }


def main():
    if "--reavaliar" in sys.argv:
        relatorio = json.loads(RELATORIO.read_text(encoding="utf-8"))
    else:
        relatorio = {"modelo": MODELO, "think": False, "k": K, "fusao": "score",
                     "gerado_em": time.strftime("%Y-%m-%d %H:%M"), "casos": coletar()}
    relatorio["adjudicacao"] = {i: {"cobre": c, "motivo": m}
                                for i, (c, m) in ADJUDICACAO.items()}
    relatorio["avaliacao"] = avaliar(relatorio["casos"])
    RELATORIO.write_text(json.dumps(relatorio, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")

    a = relatorio["avaliacao"]
    m = a["modelo_sozinho"]
    print(f"modelo sozinho: positivas {m['positivas_com_veredito']}/{m['positivas']} com veredito, "
          f"ausentes {m['ausentes_insuficiente']}/{m['ausentes']} insuficiente, "
          f"vizinhos: {len(m['vizinhos_legitimos'])} legítimos, erros {m['vizinhos_erro']}")
    print(f"score do alvo nas positivas: mínimo {a['score_do_alvo_nas_positivas']['minimo']}")
    print(f"maior limiar sem perder evidência que cobre: {a['maior_limiar_sem_perda']}")
    print(f"trechos do FACTCK.BR entre os {K}: {a['trechos_factckbr_entre_os_k']}")
    print(f"gravado em {RELATORIO}")


if __name__ == "__main__":
    main()
