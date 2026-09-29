"""Sonda da classificação e da guarda — tasks 2.2 e 2.3 de mvp-copiloto-verificacao.

Formato das sondas anteriores: Gemma 4 12B QAT, `think: false`, três tentativas
por caso. Os trechos são fragmentos reais do índice (`prototipo/indice/`),
escolhidos à mão por `fragmento_id`. A recuperação não roda aqui, porque o que se
mede é o que o modelo faz com o trecho que chega, e não se o trecho chega.

Casos C: um por rótulo com evidência, incluindo o verdadeiro contra-intuitivo da
spec. Casos G: a guarda. A alegação é conhecida do modelo, e o trecho não a cobre
ou nem existe. O rótulo final tem de ser `evidência insuficiente`. O relatório
separa quando foi o modelo que disse isso e quando a guarda teve de rebaixar.

Uso: python -m prototipo.sonda_classificacao_guarda [modelo] [--tentativas=N] [--cpu]
"""
import json, pathlib, sys, time

from prototipo.verificacao.guarda import INSUFICIENTE, verificar
from prototipo.verificacao.modelo import MODELO as PADRAO, chat_ollama

AQUI = pathlib.Path(__file__).parent
_args = [a for a in sys.argv[1:] if not a.startswith("--")]
MODELO = _args[0] if _args else PADRAO
CPU = "--cpu" in sys.argv
TENTATIVAS = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--tentativas=")), 3)
DESTINO = AQUI / "relatorio_sonda_classificacao_guarda.json"

JATOBA = "c7a4591df5-00-00"      # aos fatos, 2021: casca do jatobá não cura câncer
CAIXAO = "beff276238-00-00"      # Comprova, 2020: verdadeiro, criança em caixão lacrado testou negativo
CLOROQ = "cd575dcaa4-00-00"      # Comprova, 2020: enganoso, vídeo de abril postado como atual
CLOROQ_DATA = "cd575dcaa4-00-01"  # mesmo registro: gravação de 9 de abril, post de 30 de julho

SONDAS = [
    {"id": "C1_falso", "esperado": "falso", "fragmentos": [JATOBA],
     "alegacao": "A casca triturada do fruto do jatobá cura o câncer."},
    {"id": "C2_verdadeiro_contraintuitivo", "esperado": "verdadeiro", "fragmentos": [CAIXAO],
     "alegacao": "Uma criança com suspeita de covid foi posta em caixão lacrado sem limpeza, "
                 "e depois o exame dela deu negativo."},
    {"id": "C3_fora_de_contexto", "esperado": "verdadeiro fora de contexto ou exagerado",
     "fragmentos": [CLOROQ, CLOROQ_DATA],
     "alegacao": "Vídeo mostra o prefeito Bruno Covas anunciando agora, no fim de julho, "
                 "a cloroquina no protocolo de tratamento da covid em São Paulo."},
    {"id": "G1_sem_trecho", "esperado": INSUFICIENTE, "fragmentos": [],
     "alegacao": "A vacina contra o sarampo causa autismo."},
    {"id": "G2_trecho_de_outro_assunto", "esperado": INSUFICIENTE, "fragmentos": [JATOBA, CAIXAO],
     "alegacao": "A vacina contra o sarampo causa autismo."},
    # O trecho fala de cloroquina, mas da data de um vídeo, não de prevenção.
    {"id": "G3_mesmo_remedio_outra_alegacao", "esperado": INSUFICIENTE, "fragmentos": [CLOROQ],
     "alegacao": "Tomar hidroxicloroquina toda semana previne a covid."},
    # O trecho diz que nenhum alimento cura câncer; a alegação é sobre dengue.
    {"id": "G4_regra_parecida_outra_doenca", "esperado": INSUFICIENTE, "fragmentos": [JATOBA],
     "alegacao": "Chá de folha de goiabeira cura a dengue em 24 horas."},
]


def carregar_trechos(ids):
    """Fragmentos do índice no formato que a recuperação devolve."""
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


def main():
    chamadas = []

    def chat(sistema, usuario):
        chamadas.append(1)
        return chat_ollama(sistema, usuario, modelo=MODELO, cpu=CPU)

    trechos = carregar_trechos({i for s in SONDAS for i in s["fragmentos"]})
    print(f"modelo: {MODELO} | think=False | cpu={CPU} | tentativas={TENTATIVAS}\n" + "=" * 72)
    rel = {"modelo": MODELO, "think": False, "cpu": CPU, "tentativas": TENTATIVAS,
           "gerado_em": time.strftime("%Y-%m-%d %H:%M"), "sondas": []}
    for s in SONDAS:
        registro = {"id": s["id"], "alegacao": s["alegacao"], "esperado": s["esperado"],
                    "fragmentos": s["fragmentos"], "tentativas": []}
        print(f"\n### {s['id']} — esperado: {s['esperado']}")
        for n in range(1, TENTATIVAS + 1):
            antes, t0 = len(chamadas), time.time()
            try:
                v = verificar(s["alegacao"], [trechos[i] for i in s["fragmentos"]], chat=chat)
                erro = None
            except ValueError as e:
                v, erro = None, str(e)
            dt = time.time() - t0
            ok = v is not None and v.rotulo == s["esperado"]
            quem = None if v is None or v.rotulo != INSUFICIENTE else (
                "guarda" if v.rebaixado_por else "modelo")
            print(f"  tentativa {n}: [{'PASSOU' if ok else 'FALHOU'}] {dt:.1f}s "
                  f"{v.rotulo if v else 'ERRO'}{f' (por {quem})' if quem else ''}")
            if erro:
                print(f"    -- {erro}")
            elif v.rebaixado_por:
                print(f"    -- rebaixado: {v.rebaixado_por}")
            registro["tentativas"].append({
                "n": n, "passou": ok, "segundos": round(dt, 1),
                "chamadas_ao_modelo": len(chamadas) - antes, "rotulo": v.rotulo if v else None,
                "insuficiente_por": quem, "rebaixado_por": v.rebaixado_por if v else None,
                "criterio": v.criterio if v else None,
                "trechos_citados": [t["fragmento_id"] for t in v.trechos] if v else None,
                "modelo_disse": v.original if v else None, "erro": erro})
        registro["passou"] = sum(t["passou"] for t in registro["tentativas"])
        rel["sondas"].append(registro)
    DESTINO.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 72)
    for r in rel["sondas"]:
        print(f"{r['id']:34s} {r['passou']}/{TENTATIVAS}")
    print(f"-> {DESTINO.name}")


if __name__ == "__main__":
    main()
