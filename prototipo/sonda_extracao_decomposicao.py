"""Sonda dos prompts de extração e decomposição — tasks 2.1 e 2.5 de mvp-copiloto-verificacao.

Formato das sondas de 18/09 e 28/09: Gemma 4 12B QAT, `think: false`, três
tentativas por caso, resultado por tentativa. Os prompts são os de
`prototipo/verificacao/`; aqui só se mede o que o modelo faz com eles.

Casos da extração: uma alegação, várias alegações com risco diferente, só opinião.
Casos da decomposição: os dois cenários da spec — mensagem mista e fato verdadeiro
sustentando conclusão que não decorre (forense caso 04, bula da Tripedia).

Uso: python -m prototipo.sonda_extracao_decomposicao [modelo] [--tentativas=N] [--cpu] [--reavaliar]
"""
import json, pathlib, re, sys, time

from prototipo.verificacao import decomposicao, extracao
from prototipo.verificacao.modelo import MODELO as PADRAO, chat_ollama

AQUI = pathlib.Path(__file__).parent
_args = [a for a in sys.argv[1:] if not a.startswith("--")]
MODELO = _args[0] if _args else PADRAO
CPU = "--cpu" in sys.argv
TENTATIVAS = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--tentativas=")), 3)
DESTINO = AQUI / "relatorio_sonda_extracao_decomposicao.json"


def _tem(texto, *termos):
    t = (texto or "").lower()
    return all(x in t for x in termos)


def checar_x1(r):
    return {"verificável": r.verificavel,
            "selecionou a do inhame": r.verificavel and _tem(r.selecionada["texto"], "inhame", "dengue"),
            "risco alto (promete tratar doença)": r.verificavel and r.selecionada["risco"] == "alto"}


def checar_x2(r):
    textos = [a["texto"] for a in r.demais]
    return {"selecionou a do boldo (maior risco)": r.verificavel and _tem(r.selecionada["texto"], "boldo"),
            "ofereceu a do hospital": any(_tem(t, "hospital") for t in textos),
            "ofereceu a do prefeito": any(_tem(t, "prefeito") for t in textos),
            "prefeito marcado fora de saúde": all(not a["saude"] for a in r.demais if _tem(a["texto"], "prefeito"))}


def checar_x3(r):
    return {"não verificável": not r.verificavel,
            "copiou a opinião": bool(r.opiniao)}


def checar_d1(d):
    fatos = " ".join(d.fatos).lower()
    return {"fato: jejum e fígado": "jejum" in fatos and "fígado" in fatos,
            "evidência fraca: médico do YouTube": any(
                _tem(e["texto"], "youtube") and e["forca"] == "fraca" for e in d.evidencias),
            "opinião: remédio de farmácia": any(_tem(o, "farmácia") for o in d.opinioes),
            "opinião fora dos fatos": "farmácia" not in fatos}


def checar_d2(d):
    c = d.conclusao or {}
    return {"fato: bula cita relatos": any(_tem(f, "bula") for f in d.fatos),
            "conclusão: vacina causa autismo": _tem(c.get("texto"), "autismo"),
            "conclusão não decorre": c.get("decorre") is False,
            "salto explicado": bool((c.get("salto") or "").strip()),
            "conclusão não listada como fato": not any(
                _tem(f, "autismo") and not _tem(f, "bula") for f in d.fatos)}


SONDAS = [
    {"id": "X1_uma_alegacao", "prompt": "extracao", "checar": checar_x1,
     "texto": "Estudo da UFMG: suco de inhame cru batido com água corta os efeitos da "
              "dengue em apenas 4 horas. O estudo ainda não foi divulgado. Compartilhem urgente!"},
    {"id": "X2_varias_alegacoes", "prompt": "extracao", "checar": checar_x2,
     "texto": "O hospital de Sorocaba ficou lotado ontem. O prefeito gastou 2 milhões numa "
              "praça. E o chá de boldo cura hepatite, minha tia parou o remédio e melhorou."},
    {"id": "X3_so_opiniao", "prompt": "extracao", "checar": checar_x3,
     "texto": "Esse governo não liga para a saúde de ninguém. Que vergonha, estou cansada de fila."},
    {"id": "D1_caso_misto", "prompt": "decomposicao", "checar": checar_d1,
     "texto": "Um médico no YouTube explicou que o jejum de três dias limpa o fígado. "
              "Eu acho que remédio de farmácia só faz mal."},
    {"id": "D2_salto_fato_conclusao", "prompt": "decomposicao", "checar": checar_d2,
     "texto": "A bula da vacina Tripedia cita relatos de autismo depois da vacina. "
              "Então está provado: vacina causa autismo. Não adianta brigar comigo."},
]
PROMPTS = {"extracao": extracao, "decomposicao": decomposicao}


def avaliar(s, bruto):
    mod = PROMPTS[s["prompt"]]
    achados = mod.defeitos(bruto)
    checks = {"saída bem formada": not achados}
    if not achados:
        checks.update(s["checar"](mod.interpretar(bruto)))
    return checks, achados


def main():
    chat = lambda sistema, usuario: chat_ollama(sistema, usuario, modelo=MODELO, cpu=CPU)
    print(f"modelo: {MODELO} | think=False | cpu={CPU} | tentativas={TENTATIVAS}\n" + "=" * 72)
    rel = {"modelo": MODELO, "think": False, "cpu": CPU, "tentativas": TENTATIVAS,
           "gerado_em": time.strftime("%Y-%m-%d %H:%M"), "sondas": []}
    for s in SONDAS:
        mod = PROMPTS[s["prompt"]]
        registro = {"id": s["id"], "prompt": s["prompt"], "texto": s["texto"], "tentativas": []}
        print(f"\n### {s['id']}")
        for n in range(1, TENTATIVAS + 1):
            t0 = time.time()
            bruto = chat(mod.SISTEMA, mod.mensagem(s["texto"]))
            dt = time.time() - t0
            checks, achados = avaliar(s, bruto)
            ok = all(checks.values())
            print(f"  tentativa {n}: [{'PASSOU' if ok else 'FALHOU'}] {dt:.1f}s")
            for k, x in checks.items():
                if not x:
                    print(f"    XX {k}")
            for a in achados:
                print(f"    -- {a}")
            registro["tentativas"].append({"n": n, "passou": ok, "segundos": round(dt, 1),
                                           "checks": checks, "defeitos": achados,
                                           "resposta": bruto})
        registro["passou"] = sum(t["passou"] for t in registro["tentativas"])
        rel["sondas"].append(registro)
    DESTINO.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 72)
    for r in rel["sondas"]:
        print(f"{r['id']:28s} {r['passou']}/{TENTATIVAS}")
    print(f"-> {DESTINO.name}")


def reavaliar():
    """Reaplica os checks às respostas gravadas, sem chamar o modelo."""
    rel = json.loads(DESTINO.read_text(encoding="utf-8"))
    por_id = {s["id"]: s for s in SONDAS}
    for r in rel["sondas"]:
        for t in r["tentativas"]:
            t["checks"], t["defeitos"] = avaliar(por_id[r["id"]], t["resposta"])
            t["passou"] = all(t["checks"].values())
        r["passou"] = sum(t["passou"] for t in r["tentativas"])
        print(f"{r['id']:28s} {r['passou']}/{len(r['tentativas'])}")
    rel["reavaliado_em"] = time.strftime("%Y-%m-%d %H:%M")
    DESTINO.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    reavaliar() if "--reavaliar" in sys.argv else main()
