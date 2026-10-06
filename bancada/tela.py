"""Tela local da bancada: uma mensagem, o fluxo inteiro, cada etapa aberta.

    .venv/bin/streamlit run bancada/tela.py

Ferramenta interna. Mostra trechos, scores e defeitos que a camada visível do
produto esconde por desenho; não serve para sessão com participante.
"""
import json
import pathlib
import sys

import streamlit as st

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from bancada import gravacao  # noqa: E402
from bancada.__main__ import RELATORIOS, carregar_casos  # noqa: E402
from bancada.avaliacao import avaliar  # noqa: E402
from bancada.pipeline import ETAPAS, executar  # noqa: E402
from prototipo.rag.hibrida import LIMIAR_EVIDENCIA  # noqa: E402

st.set_page_config(page_title="Bancada do copiloto", layout="wide")


@st.cache_resource(show_spinner="Carregando índice (fragmentos, matriz densa, BM25)...")
def recuperador():
    from prototipo.rag.__main__ import carregar
    return carregar()


def chat_real():
    from prototipo.verificacao.modelo import chat_ollama
    return chat_ollama


# ---- barra lateral: parâmetros -------------------------------------------------

casos = {c["id"]: c for c in carregar_casos()}
with st.sidebar:
    st.header("Parâmetros")
    offline = st.toggle("Offline (gravações)", help="Reproduz bancada/gravacoes; só casos da bateria")
    canal = st.radio("Canal", ("web", "whatsapp"), horizontal=True)
    modo = st.selectbox("Modo de busca", ("hibrida", "lexica", "densa"))
    k = st.slider("k (trechos para a guarda)", 1, 10, 5)
    alfa = st.slider("alfa (peso denso)", 0.0, 1.0, 0.9, 0.05, disabled=modo != "hibrida")
    idioma = st.checkbox("Prioridade de idioma (1.4)", value=True,
                         help="Desligado: ranking cru, sem esgotar o português antes do inglês")
    usar_limiar = st.checkbox("Aplicar limiar", value=True,
                              help=f"Piso calibrado na task 1.5: {LIMIAR_EVIDENCIA}")
    limiar = st.slider("limiar de score", 0.0, 1.0, LIMIAR_EVIDENCIA, 0.01,
                       disabled=not usar_limiar)
    st.divider()
    st.caption("Ainda não ligado no fluxo:")
    from bancada.pipeline import NAO_LIGADO
    for item in NAO_LIGADO:
        st.caption(f"• {item}")

aba_uma, aba_bateria = st.tabs(["Uma mensagem", "Relatórios da bateria"])

# ---- uma mensagem --------------------------------------------------------------

with aba_uma:
    escolha = st.selectbox("Caso da bateria", ["(mensagem livre)", *casos])
    caso = casos.get(escolha)
    texto = st.text_area("Mensagem recebida", value=caso["mensagem"] if caso else "", height=110,
                         disabled=offline and caso is not None)
    lacuna_txt = st.text_input("Lacuna de acervo (JSON, opcional)",
                               value=json.dumps(caso["lacuna"]) if caso and caso.get("lacuna") else "",
                               placeholder='{"corte": "2021"}')
    if caso:
        st.caption(f"Origem: {caso.get('origem')}  {('· ' + caso['nota']) if caso.get('nota') else ''}")
        st.caption(f"Esperado: {json.dumps(caso['esperado'], ensure_ascii=False)}")

    if st.button("Verificar", type="primary", disabled=not texto.strip()):
        try:
            lacuna = json.loads(lacuna_txt) if lacuna_txt.strip() else None
        except json.JSONDecodeError as e:
            st.error(f"Lacuna não é JSON: {e}")
            st.stop()
        if offline:
            if not caso:
                st.error("Offline só reproduz casos da bateria.")
                st.stop()
            from prototipo.rag.hibrida import ALFA_PADRAO
            chat, rec = gravacao.reproduzindo(gravacao.ler(caso["id"]), alfa=ALFA_PADRAO)
            alfa_usado = None
        else:
            chat, rec = chat_real(), recuperador()
            alfa_usado = alfa
        with st.spinner("Rodando o fluxo..."):
            rastro = executar(texto, rec, chat=chat, canal=canal, k=k, modo=modo, alfa=alfa_usado,
                              limiar=limiar if usar_limiar else None, lacuna=lacuna,
                              idioma=idioma)
        st.session_state["rastro"], st.session_state["caso"] = rastro, caso

    rastro = st.session_state.get("rastro")
    if rastro:
        caso_rodado = st.session_state.get("caso")
        resposta = rastro.get("resposta")
        total = sum(e.get("segundos", 0) for e in rastro["etapas"])
        if rastro["parou_em"]:
            st.warning(f"Parou em **{rastro['parou_em']}**: {rastro['motivo']} · {total:.1f} s")
        else:
            st.success(f"Fluxo completo · {total:.1f} s")

        col_resp, col_checks = st.columns([3, 2])
        with col_resp:
            st.subheader("Camada visível")
            if resposta:
                st.markdown(resposta["texto"].replace("\n", "  \n"))
                if resposta.get("defeitos"):
                    st.error("Defeitos: \n- " + "\n- ".join(resposta["defeitos"]))
            else:
                st.info("Sem resposta.")
            for r in rastro["redirecionamentos"]:
                st.info(r)
        with col_checks:
            if caso_rodado:
                st.subheader("Esperado × obtido")
                for c in avaliar(caso_rodado, rastro):
                    st.markdown(f"{'✅' if c['ok'] else '❌'} **{c['etapa']}** · {c['check']}: "
                                f"`{c['obtido']}`" + ("" if c["ok"] else f" (esperado `{c['esperado']}`)"))

        st.subheader("Etapas")
        por_nome = {e["etapa"]: e for e in rastro["etapas"]}
        for nome in ETAPAS:
            e = por_nome.get(nome)
            if e is None:
                st.markdown(f"<span style='opacity:.45'>○ {nome} — não rodou</span>",
                            unsafe_allow_html=True)
                continue
            marca = "❌" if "erro" in e else "●"
            with st.expander(f"{marca} {nome} · {e['segundos']} s", expanded="erro" in e):
                if "erro" in e:
                    st.error(e["erro"])
                elif nome == "recuperacao":
                    s = e["saida"]
                    st.caption(f"camada: {s['idioma']} · coberto: {s['coberto']} · "
                               f"consultadas: {', '.join(s['consultados']) or '—'}")
                    st.dataframe([{"#": n, "score": round(t["score"], 3),
                                   "lex": round(t["score_lexico"], 2), "den": round(t["score_denso"], 3),
                                   "veredito": t["veredito_original"], "agência": t["agencia"],
                                   "data": t["data_publicacao"], "unidade": t["unidade_id"],
                                   "alegação": t["alegacao"]}
                                  for n, t in enumerate(s["resultados"], 1)],
                                 hide_index=True, width="stretch")
                    for n, t in enumerate(s["resultados"], 1):
                        st.caption(f"T{n} · {t['url']}")
                        st.text(t["trecho"][:600])
                else:
                    st.json(e["saida"])
        with st.expander("Rastro bruto (JSON)"):
            st.json(rastro)

# ---- relatórios ----------------------------------------------------------------

with aba_bateria:
    st.caption("Gere com `python -m bancada rodar` (ou `--offline`).")
    arquivos = sorted(RELATORIOS.glob("*.json"), reverse=True) if RELATORIOS.exists() else []
    if not arquivos:
        st.info("Nenhum relatório ainda.")
    else:
        arq = st.selectbox("Relatório", arquivos, format_func=lambda p: p.name)
        rel = json.loads(arq.read_text(encoding="utf-8"))
        res = rel["resumo"]
        a, b, c = st.columns(3)
        a.metric("Casos que passaram", f"{res['passaram']}/{res['casos']}")
        b.metric("Modo", rel["modo"])
        c.metric("Parâmetros", ", ".join(f"{k}={v}" for k, v in rel["parametros"].items()
                                         if v is not None))
        st.dataframe([{"etapa": e, "checks ok": v} for e, v in res["por_etapa"].items()],
                     hide_index=True)
        linhas = []
        for r in rel["resultados"]:
            falhas = [f"{x['etapa']}: {x['check']}" for x in r["checks"] if not x["ok"]]
            linhas.append({"caso": r["id"], "passou": "✅" if r["passou"] else "❌",
                           "segundos": r.get("segundos"), "falhas": "; ".join(falhas)})
        st.dataframe(linhas, hide_index=True, width="stretch")
