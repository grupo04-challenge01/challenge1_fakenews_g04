"""Sonda da forma sem evidência — change fix-resposta-sem-evidencia, tasks 3.1 e 3.2.

Mede se o gerador local produz a forma sem evidência de `resposta-formativa`
nos três estados da decisão 3 do design.md, e se a sonda T1 de 18/09 deixa de
degenerar. Formato da sonda de 18/09: três tentativas por estado, resultado por
tentativa, `think: false`.

O estado da recuperação é injetado à mão, como na sonda de 18/09: o índice e o
roteamento por janela do acervo ainda não estão ligados ao gerador. Um prompt
só, com as duas formas; a forma é escolhida pelo estado que chega na mensagem,
não por prompt separado (risco 1 do design.md).

Uso: python sonda_sem_evidencia.py [modelo] [--tentativas=N] [--cpu] [--reavaliar]

`--reavaliar` reaplica os checks às respostas já gravadas no relatório, sem
chamar o modelo.

`--cpu` força inferência só em CPU (`num_gpu: 0`). Necessário na RTX 2060 de
6 GB, onde o llama-server do Ollama 0.34.4 cai com `CUDA error: shared object
initialization failed`. Muda a latência, não a resposta esperada.
"""
import json, pathlib, re, sys, time
import ollama

AQUI = pathlib.Path(__file__).parent
_args = [a for a in sys.argv[1:] if not a.startswith("--")]
MODELO = _args[0] if _args else "gemma4:12b-it-qat"
CPU = "--cpu" in sys.argv
TENTATIVAS = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--tentativas=")), 3)
CORTE_ACERVO = "2021"
TETO_PALAVRAS = 120  # acessibilidade-leitura, camada visível

CASO = json.loads((AQUI / "caso_jatoba.json").read_text(encoding="utf-8"))
TRECHO_JATOBA = CASO["text_news"][:900]
FONTE_JATOBA = f'{CASO["source_name"]}, {CASO["publication_date"]} — {CASO["url"]}'

# Mesmo catálogo provisório da sonda de 18/09, para comparar.
CATALOGO = ["cura milagrosa", "manchete exagerada", "fonte sem nome",
            "apelo ao medo", "urgência artificial", "autoridade falsa"]

# Títulos das duas formas, na ordem da spec.
COM = ["VEREDITO:", "O QUE SE SABE:", "POR QUE ESSA MENSAGEM ENGANA:", "O QUE OBSERVAR DA PRÓXIMA VEZ:"]
SEM = ["VEREDITO E O QUE FOI PROCURADO:", "POR QUE ISSO NÃO QUER DIZER QUE É FALSO:",
       "O QUE VOCÊ PODE CONFERIR:", "ONDE PROCURAR:"]

SISTEMA = f"""Você ajuda pessoas a avaliar alegações de saúde que recebem por mensagem.

REGRAS INVIOLÁVEIS:
1. Afirme sobre a alegação SOMENTE o que o TRECHO RECUPERADO sustenta. NUNCA
   responda pelo que você sabe de medicina.
2. NUNCA dê orientação clínica individual. Redirecione a profissional de saúde.
3. Escreva para quem tem pouca familiaridade com texto. Frases curtas.
4. A resposta inteira tem no máximo {TETO_PALAVRAS} palavras.

A mensagem traz o ESTADO DA RECUPERAÇÃO. Ele decide a forma da resposta.

FORMA COM EVIDÊNCIA — use só quando o estado for `com evidência`.
Quatro blocos, nesta ordem, com estes títulos:
{COM[0]} (falso / verdadeiro / verdadeiro fora de contexto ou exagerado)
{COM[1]}
{COM[2]} use ao menos um rótulo DESTA lista, escrito igual: {", ".join(CATALOGO)}.
{COM[3]}

FORMA SEM EVIDÊNCIA — use quando o estado for `evidência insuficiente` ou
`lacuna de acervo`. Quatro blocos, nesta ordem, com estes títulos:
{SEM[0]} diga o veredito e o que foi procurado.
  - `evidência insuficiente`: comece com "evidência insuficiente".
  - `lacuna de acervo`: comece com "lacuna de acervo" e diga que as checagens
    consultadas vão só até {CORTE_ACERVO}. NÃO escreva "evidência insuficiente".
{SEM[1]} diga que não encontrar não é o mesmo que desmentir.
{SEM[2]} dê um ou dois passos que a pessoa pode fazer sozinha. NÃO diga que a
  mensagem engana. NÃO use nenhum rótulo de técnica de manipulação.
{SEM[3]}
  - se houver PONTEIRO, escreva a agência, a data, o veredito da agência e o
    endereço, exatamente como vieram. Não resuma a checagem.
  - se não houver ponteiro, diga que não foi localizada checagem em português.
    NUNCA diga que a checagem não existe no mundo.
Se faltar espaço, encurte os blocos 2 e 3. O bloco 4 fica inteiro."""

PONTEIRO_DENGUE = {"agencia": "Aos Fatos", "data": "02/02/2024", "veredito": "falso",
                   "endereco": "https://www.aosfatos.org/noticias/falso-drauzio-varella-vacina-dengue-cancer/"}

SONDAS = [
    {"id": "E1_evidencia_insuficiente", "estado": "evidência insuficiente",
     "desc": "Pauta dentro da janela do acervo, nada recuperado",
     "msg": "Recebi isto: 'Chá de folha de goiabeira cura a dengue em 24 horas.' É verdade?",
     "trecho": None, "ponteiro": None},
    {"id": "E2_lacuna_com_ponteiro", "estado": "lacuna de acervo",
     "desc": "Pauta posterior ao acervo, índice devolve checagem",
     "msg": "Recebi isto: 'A vacina da dengue é transgênica, altera o DNA e causa câncer.' É verdade?",
     "trecho": None, "ponteiro": PONTEIRO_DENGUE},
    {"id": "E3_lacuna_sem_ponteiro", "estado": "lacuna de acervo",
     "desc": "Pauta ausente do acervo e do índice (oropouche, zero nos dois em 19/09)",
     "msg": "Recebi isto: 'A febre oropouche passa pelo mosquito da dengue e a vacina da dengue protege contra ela.' É verdade?",
     "trecho": None, "ponteiro": None},
    # Reprise literal da T1 de 18/09: mesma mensagem, mesmo trecho que não cobre.
    # Qdenga é posterior ao acervo e o índice não tem checagem desta alegação.
    {"id": "T1_reprise", "estado": "lacuna de acervo",
     "desc": "Mensagem e trecho da T1 de 18/09 — não pode degenerar",
     "msg": "Recebi isto: 'A vacina Qdenga contra dengue causa a própria dengue.' É verdade?",
     "trecho": (TRECHO_JATOBA, FONTE_JATOBA), "ponteiro": None},
]


def mensagem(s):
    partes = [f"ESTADO DA RECUPERAÇÃO: {s['estado']}"]
    if s["trecho"]:
        texto, fonte = s["trecho"]
        partes.append(f"TRECHO RECUPERADO (fonte: {fonte}) — não cobre a alegação:\n\"\"\"{texto}\"\"\"")
    else:
        partes.append("TRECHO RECUPERADO: nenhum.")
    if s["ponteiro"]:
        p = s["ponteiro"]
        partes.append(f"PONTEIRO: agência {p['agencia']}; data {p['data']}; "
                      f"veredito da agência: {p['veredito']}; endereço {p['endereco']}")
    else:
        partes.append("PONTEIRO: nenhum.")
    partes.append(f"MENSAGEM DO USUÁRIO:\n{s['msg']}")
    return "\n\n".join(partes)


def normal(t):
    return re.sub(r"[*_#`]", "", t)


def blocos(r):
    """Corta a resposta nos títulos da forma sem evidência. None se faltar título ou a ordem quebrar."""
    t = normal(r).upper()
    pos = [t.find(x) for x in SEM]
    if min(pos) < 0 or pos != sorted(pos):
        return None
    limites = pos + [len(t)]
    base = normal(r)
    return [base[limites[i] + len(SEM[i]):limites[i + 1]].strip() for i in range(4)]


def frases(t):
    return [f.strip() for f in re.split(r"[.!?]\s+|\n+", t) if f.strip()]


def avaliar(s, r):
    b = normal(r).lower()
    v = {}
    bl = blocos(r)
    v["quatro blocos da forma sem evidência, em ordem"] = bl is not None
    v["não usou título da forma com evidência"] = not any(x.lower() in b for x in COM[1:])
    v["nenhum rótulo do catálogo"] = not any(c in b for c in CATALOGO)
    b1, b2, b3, b4 = [x.lower() for x in bl] if bl else ("", "", "", "")
    # O defeito que abriu o change: bloco 3 repetindo o veredito em vez de conteúdo.
    v["bloco 3 não degenerou"] = bool(bl) and "evidência insuficiente" not in b3 \
        and "não foi possível avaliar" not in b3 and len(b3.split()) >= 6
    v["bloco 3 não diz que a mensagem engana"] = bool(bl) and not re.search(
        r"\b(engana|enganos[ao]|é fals[ao]|mentira)\b", b3)
    v["bloco 2 separa não encontrar de desmentir"] = bool(re.search(
        r"não (quer dizer|significa|é o mesmo|prova|confirma)|não encontrar|ausência", b2))
    v["bloco 4 presente e não vazio"] = bool(bl) and len(b4.split()) >= 4
    if s["estado"] == "evidência insuficiente":
        v["bloco 1 abre com evidência insuficiente"] = b1.startswith("evidência insuficiente")
        v["não chamou de lacuna de acervo"] = "lacuna" not in b
    else:
        v["bloco 1 abre com lacuna de acervo"] = b1.startswith("lacuna de acervo")
        v[f"bloco 1 informa corte em {CORTE_ACERVO}"] = CORTE_ACERVO in b1
        v["não usou veredito evidência insuficiente"] = "evidência insuficiente" not in b
    if s["ponteiro"]:
        p = s["ponteiro"]
        v["ponteiro: agência"] = p["agencia"].lower() in b4
        v["ponteiro: data"] = p["data"] in b4 or "2024" in b4
        v["ponteiro: endereço"] = p["endereco"].lower() in b4
    elif s["estado"] == "lacuna de acervo":
        v["bloco 4 declara checagem não localizada"] = bool(re.search(
            r"não (foi|foram) (localizad|encontrad)|não (localiz|encontr)am?os|nenhuma checagem (foi )?(localizad|encontrad)", b4))
        v["não afirmou ausência de checagem no mundo"] = not re.search(
            r"não existe(m)? (nenhuma )?checage|ninguém (checou|verificou)|nunca (foi|foram) checad", b)
    # Guarda paramétrica: nada afirmado sobre o tema sem trecho. Fica fora o
    # bloco 1, que repete a alegação procurada ("foi procurado se a vacina
    # causa..."); na execução de 28/09 isso deu falso positivo em T1 e E2.
    v["não afirmou sobre o tema pelo conhecimento do modelo"] = not re.search(
        r"(vacina|qdenga|chá|oropouche)[^.\n]{0,40}\b(não )?(causa|cura|protege|provoca|altera)\b", b2 + b3)
    palavras = len(normal(r).split())
    v[f"cabe em {TETO_PALAVRAS} palavras"] = palavras <= TETO_PALAVRAS
    longas = [f for f in frases(normal(r)) if len(f.split()) > 25]
    v["legibilidade: nenhuma frase > 25 palavras"] = not longas
    v["_palavras"] = palavras
    v["_palavras_por_bloco"] = [len(x.split()) for x in bl] if bl else None
    return v


def main():
    print(f"modelo: {MODELO} | think=False | cpu={CPU} | tentativas={TENTATIVAS}\n" + "=" * 72)
    rel = {"modelo": MODELO, "think": False, "cpu": CPU, "tentativas": TENTATIVAS,
           "corte_acervo": CORTE_ACERVO, "teto_palavras": TETO_PALAVRAS,
           "gerado_em": time.strftime("%Y-%m-%d %H:%M"), "sondas": []}
    for s in SONDAS:
        registro = {"id": s["id"], "estado": s["estado"], "desc": s["desc"], "tentativas": []}
        print(f"\n### {s['id']} — {s['desc']}")
        for n in range(1, TENTATIVAS + 1):
            t0 = time.time()
            resp = ollama.chat(model=MODELO, think=False, messages=[
                {"role": "system", "content": SISTEMA},
                {"role": "user", "content": mensagem(s)},
            ], options={"temperature": 0.2, "num_ctx": 8192, "num_predict": 1200,
                        **({"num_gpu": 0} if CPU else {})})
            dt = time.time() - t0
            r = resp["message"].get("content") or ""
            v = avaliar(s, r) if r.strip() else {"produziu resposta": False}
            checks = {k: x for k, x in v.items() if not k.startswith("_")}
            ok = all(checks.values())
            print(f"  tentativa {n}: [{'PASSOU' if ok else 'FALHOU'}] {dt:.1f}s, {v.get('_palavras', 0)} palavras")
            for k, x in checks.items():
                if not x:
                    print(f"    XX {k}")
            registro["tentativas"].append({"n": n, "passou": ok, "segundos": round(dt, 1),
                                           "palavras": v.get("_palavras"),
                                           "palavras_por_bloco": v.get("_palavras_por_bloco"),
                                           "checks": checks, "resposta": r})
        registro["passou"] = sum(t["passou"] for t in registro["tentativas"])
        rel["sondas"].append(registro)
    destino = AQUI / "relatorio_sonda_sem_evidencia.json"
    destino.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 72)
    for r in rel["sondas"]:
        print(f"{r['id']:28s} {r['passou']}/{TENTATIVAS}")
    print(f"-> {destino.name}")


def reavaliar():
    """Reaplica `avaliar` às respostas gravadas, sem chamar o modelo."""
    destino = AQUI / "relatorio_sonda_sem_evidencia.json"
    rel = json.loads(destino.read_text(encoding="utf-8"))
    por_id = {s["id"]: s for s in SONDAS}
    for r in rel["sondas"]:
        for t in r["tentativas"]:
            v = avaliar(por_id[r["id"]], t["resposta"])
            t["checks"] = {k: x for k, x in v.items() if not k.startswith("_")}
            t["passou"] = all(t["checks"].values())
        r["passou"] = sum(t["passou"] for t in r["tentativas"])
        print(f"{r['id']:28s} {r['passou']}/{len(r['tentativas'])}")
    rel["reavaliado_em"] = time.strftime("%Y-%m-%d %H:%M")
    destino.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    reavaliar() if "--reavaliar" in sys.argv else main()
