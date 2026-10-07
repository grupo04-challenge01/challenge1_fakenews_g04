"""Textos da persona Dona Checa (change add-identidade-dona-checa).

Os textos fixos são lidos dos blocos `##### Texto — <chave>` da spec, para que
texto e código não divirjam, no mesmo padrão das respostas padrão de
`prototipo/verificacao/fronteira.py` (decisão 15 de mvp-copiloto-verificacao).
"""
import pathlib

RAIZ = pathlib.Path(__file__).parents[2]


def caminhos(capacidade):
    """Delta do change, depois a spec principal, já arquivada."""
    return [RAIZ / f"openspec/changes/add-identidade-dona-checa/specs/{capacidade}/spec.md",
            RAIZ / f"openspec/specs/{capacidade}/spec.md"]


def ler_textos(spec):
    """{chave: texto} dos blocos `##### Texto — <chave>` de uma spec."""
    textos_, chave, linhas = {}, None, None

    def fechar():
        if chave and linhas:
            textos_[chave] = "\n".join(linhas).strip()

    for linha in spec.read_text(encoding="utf-8").splitlines():
        if linha.startswith("##### Texto"):
            fechar()
            chave = linha.split("—", 1)[1].strip()
            linhas = []
        elif linhas is not None and linha.startswith(">"):
            linhas.append(linha[1:].removeprefix(" ").rstrip())
        elif linhas is not None and linhas:
            fechar()
            chave, linhas = None, None
    fechar()
    return textos_


def textos(capacidade="identidade-dona-checa"):
    """Textos fixos de uma capability, do primeiro arquivo de spec que existir."""
    spec = next((p for p in caminhos(capacidade) if p.exists()), None)
    if spec is None:
        raise FileNotFoundError(f"spec {capacidade} não encontrada")
    return ler_textos(spec)


def pergunta_confianca(*, piloto):
    """Pergunta de confiança e opções, ou None em sessão de piloto ou coleta.

    `piloto` não tem padrão: quem chama decide, e o esquecimento vira erro em
    vez de oferecer a pergunta a um participante (decisão 3 do design).
    """
    if piloto:
        return None
    t = textos()
    return {"pergunta": t["pergunta_confianca"], "opcoes": t["opcoes_confianca"].splitlines()}
