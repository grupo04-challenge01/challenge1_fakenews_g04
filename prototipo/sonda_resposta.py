"""Sonda da estrutura de quatro blocos — task 3.2 de mvp-copiloto-verificacao.

Formato das sondas anteriores: Gemma 4 12B QAT, `think: false`, três tentativas
por caso. O veredito entra pronto, montado com fragmentos reais do índice
(`prototipo/indice/`), escolhidos à mão por `fragmento_id`. A classificação não
roda aqui, porque o que se mede é a resposta que sai de um veredito dado, e não
o veredito.

Casos R com evidência: um por rótulo, incluindo o verdadeiro contra-intuitivo da
spec e um caso com opinião na mensagem. Casos S sem evidência: os três estados
da decisão 3 de fix-resposta-sem-evidencia. Uma tentativa passa quando
`Resposta.defeitos` sai vazia.

Uso: python -m prototipo.sonda_resposta [modelo] [--tentativas=N] [--cpu]
"""
import json, pathlib, sys, time

from prototipo.resposta.estrutura import responder
from prototipo.verificacao.guarda import INSUFICIENTE, Veredito
from prototipo.verificacao.modelo import MODELO as PADRAO, chat_ollama

AQUI = pathlib.Path(__file__).parent
_args = [a for a in sys.argv[1:] if not a.startswith("--")]
MODELO = _args[0] if _args else PADRAO
CPU = "--cpu" in sys.argv
TENTATIVAS = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--tentativas=")), 3)
DESTINO = AQUI / "relatorio_sonda_resposta.json"
CORTE_ACERVO = "2021"

JATOBA = "c7a4591df5-00-00"      # aos fatos, 2021: casca do jatobá não cura câncer
CAIXAO = "beff276238-00-00"      # Comprova, 2020: verdadeiro, criança em caixão lacrado testou negativo
CLOROQ = "cd575dcaa4-00-00"      # Comprova, 2020: enganoso, vídeo de abril postado como atual
CLOROQ_DATA = "cd575dcaa4-00-01"  # mesmo registro: gravação de 9 de abril, post de 30 de julho

SONDAS = [
    {"id": "R1_falso", "rotulo": "falso", "fragmentos": [JATOBA],
     "criterio": "O trecho T1 diz que não é verdade que a casca do jatobá trate o câncer.",
     "alegacao": "A casca triturada do fruto do jatobá cura o câncer.",
     "mensagem": "Repassem para todos! A casca do jatobá triturada cura o câncer. "
                 "Um médico do interior confirmou."},
    {"id": "R2_falso_com_opiniao", "rotulo": "falso", "fragmentos": [JATOBA],
     "criterio": "O trecho T1 diz que não é verdade que a casca do jatobá trate o câncer.",
     "alegacao": "A casca triturada do fruto do jatobá cura o câncer.",
     "mensagem": "A casca do jatobá cura o câncer. Na minha opinião os laboratórios "
                 "escondem isso porque não dá lucro.",
     "decomposicao": {"fatos": ["A casca do jatobá cura o câncer."], "evidencias": [],
                      "opinioes": ["os laboratórios escondem isso porque não dá lucro"],
                      "conclusao": None}},
    {"id": "R3_verdadeiro_contraintuitivo", "rotulo": "verdadeiro", "fragmentos": [CAIXAO],
     "criterio": "O trecho T1 confirma que a criança foi posta em caixão lacrado e depois testou negativo.",
     "alegacao": "Uma criança com suspeita de covid foi posta em caixão lacrado, "
                 "e depois o exame dela deu negativo.",
     "mensagem": "Absurdo: enterraram uma menina em caixão lacrado como covid e depois "
                 "o exame deu negativo. Isso é verdade?"},
    {"id": "R4_fora_de_contexto", "rotulo": "verdadeiro fora de contexto ou exagerado",
     "fragmentos": [CLOROQ, CLOROQ_DATA],
     "criterio": "Os trechos T1 e T2 mostram que o vídeo é de 9 de abril e foi postado em 30 de julho como se fosse atual.",
     "alegacao": "Vídeo mostra o prefeito Bruno Covas anunciando agora a cloroquina "
                 "no protocolo de tratamento da covid em São Paulo.",
     "mensagem": "Olha o vídeo! O prefeito Bruno Covas acabou de liberar a cloroquina "
                 "para covid em São Paulo."},
    {"id": "S1_evidencia_insuficiente", "rotulo": INSUFICIENTE, "fragmentos": [],
     "alegacao": "Chá de folha de goiabeira cura a dengue em 24 horas.",
     "mensagem": "Recebi isto: 'Chá de folha de goiabeira cura a dengue em 24 horas.' É verdade?"},
    {"id": "S2_lacuna_com_ponteiro", "rotulo": INSUFICIENTE, "fragmentos": [],
     "alegacao": "A vacina da dengue é transgênica, altera o DNA e causa câncer.",
     "mensagem": "Recebi isto: 'A vacina da dengue é transgênica, altera o DNA e causa câncer.' É verdade?",
     "lacuna": {"corte": CORTE_ACERVO, "ponteiro": {
         "agencia": "Aos Fatos", "data": "02/02/2024", "veredito": "falso",
         "endereco": "https://www.aosfatos.org/noticias/falso-drauzio-varella-vacina-dengue-cancer/"}}},
    {"id": "S3_lacuna_sem_ponteiro", "rotulo": INSUFICIENTE, "fragmentos": [],
     "alegacao": "A febre oropouche passa pelo mosquito da dengue e a vacina da dengue protege contra ela.",
     "mensagem": "Recebi isto: 'A febre oropouche passa pelo mosquito da dengue e a vacina "
                 "da dengue protege contra ela.' É verdade?",
     "lacuna": {"corte": CORTE_ACERVO}},
]


def carregar_trechos(ids):
    """Fragmentos do índice no formato que a guarda devolve no veredito."""
    por_id = {}
    with open(AQUI / "indice" / "fragmentos.jsonl", encoding="utf-8") as f:
        for linha in f:
            frag = json.loads(linha)
            if frag["fragmento_id"] in ids:
                por_id[frag["fragmento_id"]] = {k: frag[k] for k in (
                    "fragmento_id", "agencia", "url", "data_publicacao",
                    "veredito_original", "trecho")}
    faltam = set(ids) - set(por_id)
    if faltam:
        sys.exit(f"fragmentos ausentes do índice: {sorted(faltam)}")
    return por_id


def veredito(s, trechos):
    if not s["fragmentos"]:
        return Veredito(INSUFICIENTE, "Nenhum trecho recuperado cobre a alegação.",
                        rebaixado_por="nenhum trecho recuperado")
    return Veredito(s["rotulo"], s["criterio"], [trechos[i] for i in s["fragmentos"]])


def main():
    def chat(sistema, usuario):
        return chat_ollama(sistema, usuario, modelo=MODELO, cpu=CPU)

    trechos = carregar_trechos({i for s in SONDAS for i in s["fragmentos"]})
    print(f"modelo: {MODELO} | think=False | cpu={CPU} | tentativas={TENTATIVAS}\n" + "=" * 72)
    rel = {"modelo": MODELO, "think": False, "cpu": CPU, "tentativas": TENTATIVAS,
           "corte_acervo": CORTE_ACERVO, "gerado_em": time.strftime("%Y-%m-%d %H:%M"),
           "sondas": []}
    for s in SONDAS:
        registro = {"id": s["id"], "rotulo": s["rotulo"], "alegacao": s["alegacao"],
                    "fragmentos": s["fragmentos"], "tentativas": []}
        print(f"\n### {s['id']}")
        for n in range(1, TENTATIVAS + 1):
            t0 = time.time()
            r = responder(s["mensagem"], s["alegacao"], veredito(s, trechos),
                          decomposicao=s.get("decomposicao"), lacuna=s.get("lacuna"), chat=chat)
            dt = time.time() - t0
            ok = not r.defeitos
            palavras = len(r.texto.split())
            print(f"  tentativa {n}: [{'PASSOU' if ok else 'FALHOU'}] {dt:.1f}s, {palavras} palavras")
            for d in r.defeitos:
                print(f"    XX {d}")
            registro["tentativas"].append({
                "n": n, "passou": ok, "segundos": round(dt, 1), "forma": r.forma,
                "palavras": palavras, "palavras_por_bloco": [len(b.split()) for b in r.blocos],
                "defeitos": r.defeitos, "resposta": r.texto})
        registro["passou"] = sum(t["passou"] for t in registro["tentativas"])
        rel["sondas"].append(registro)
    DESTINO.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 72)
    for r in rel["sondas"]:
        print(f"{r['id']:34s} {r['passou']}/{TENTATIVAS}")
    print(f"-> {DESTINO.name}")


if __name__ == "__main__":
    main()
