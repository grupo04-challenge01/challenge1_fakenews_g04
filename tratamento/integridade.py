"""Verificação de integridade textual — capability `integridade-textual`.

Duas garantias, e a segunda é a que chega ao usuário:

1. **Perda sistemática de caractere.** Arquivo que perdeu uma classe inteira de
   caractere MUST NOT ser aprovado para recuperação nem citação.
2. **Fidelidade do trecho.** Todo trecho citado SHALL ser idêntico ao texto
   correspondente no corpus — sem reescrita, sem remoção de acento e sem
   normalização silenciosa.

## Por que ausência total não basta como critério

A leitura literal do requirement ("zero ocorrência é corrupção") reprova corpus
íntegro. `factcenter_subset_saude.csv` tem zero `Ü` em 21,5 milhões de
caracteres, e não por defeito: o trema foi abolido pelo Acordo Ortográfico de
1990 e o corpus cobre 2013 a 2021. O `ü` minúsculo aparece 57 vezes, em nomes
estrangeiros, o que prova que o pipeline não descarta o caractere.

O que separa os dois casos observados é a **maiúscula com zero ocorrências e a
minúscula correspondente frequente**. Em `factckbr_normalizado.csv` sete letras
batem nisso (`ã` 3.625 contra `Ã` 0; `ç` 2.312 contra `Ç` 0); no corpus de
checagens, nenhuma. A precisão nasceu em `prototipo/rag/corpus.py` (task 2.2b de
`add-selecao-modelos-arquitetura-rag`) e este módulo é a implementação
definitiva que a capability pedia.
"""
from __future__ import annotations

import collections
import json
import pathlib

from tratamento import leitura

# Pares maiúscula/minúscula acentuadas do português, mais o `ü` da capability.
PARES_ACENTUADOS: tuple[tuple[str, str], ...] = (
    ("Á", "á"), ("À", "à"), ("Â", "â"), ("Ã", "ã"),
    ("É", "é"), ("Ê", "ê"), ("Í", "í"), ("Ó", "ó"),
    ("Ô", "ô"), ("Õ", "õ"), ("Ú", "ú"), ("Ü", "ü"),
    ("Ç", "ç"),
)

# Piso de ocorrências da minúscula abaixo do qual a ausência da maiúscula não
# sustenta acusação de corrupção — ver o cabeçalho deste módulo.
PISO_EVIDENCIA_MINUSCULA = 500

# Derivados em português. Os três em inglês (PUBHEALTH, FakeHealth, InSciOut)
# ficam fora: não têm classe de caractere acentuado a perder.
ARQUIVOS_PT_BR: tuple[str, ...] = (
    "factcenter_subset_saude.csv",
    "factckbr_normalizado.csv",
    "fakerecogna_subset_saude_ciencia.csv",
    "fakerecogna_amostra_estimulos_300.csv",
)


ASCII_MAIUSCULAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ASCII_MINUSCULAS = "abcdefghijklmnopqrstuvwxyz"

CAUSA_APROVADO = "sem perda detectada"
CAUSA_PERDA = "perda seletiva de caractere"
CAUSA_TRANSFORMACAO = "texto transformado na origem"


class ErroDeIntegridade(RuntimeError):
    """Arquivo reprovado. MUST NOT ser usado em recuperação nem em citação."""


def _causa_provavel(nome: str, corrompidos: list[dict]) -> str:
    """Diz por que o arquivo reprovou, que não é a mesma coisa em todo arquivo.

    `factckbr_normalizado.csv` perdeu caractere por allowlist no script de
    atualização a montante: o texto conserva a caixa, e só as maiúsculas
    acentuadas sumiram. Os derivados da FakeRecogna reprovam por outra razão —
    a base entrega a coluna de texto lematizada e sem caixa. O efeito no gate é
    o mesmo (nenhum dos dois serve de trecho citado), mas a acusação não é, e
    registrar `perda de caractere` contra a FakeRecogna seria erro de portfólio.
    """
    if not corrompidos:
        return CAUSA_APROVADO
    try:
        declarado = leitura.formato(nome)
    except leitura.ErroDeLeitura:
        return CAUSA_PERDA
    return CAUSA_TRANSFORMACAO if declarado.texto_transformado_na_origem else CAUSA_PERDA


def verificar(nome: str, caminho: pathlib.Path | None = None) -> dict:
    """Laudo de perda sistemática de caractere de um arquivo, sem levantar erro."""
    arquivo = caminho if caminho is not None else leitura.DIRETORIO_DERIVADOS / nome
    texto = arquivo.read_text(encoding="utf-8")
    contagem = collections.Counter(texto)

    # Razão de caixa do próprio arquivo, para estimar quantas maiúsculas
    # acentuadas seriam esperadas. Corrobora o piso fixo sem depender dele.
    maiusculas_ascii = sum(contagem[c] for c in ASCII_MAIUSCULAS)
    minusculas_ascii = sum(contagem[c] for c in ASCII_MINUSCULAS)
    razao_de_caixa = maiusculas_ascii / max(minusculas_ascii, 1)

    ausentes: list[str] = []
    corrompidos: list[dict] = []
    for maiuscula, minuscula in PARES_ACENTUADOS:
        if contagem[maiuscula]:
            continue
        ausentes.append(maiuscula)
        if contagem[minuscula] >= PISO_EVIDENCIA_MINUSCULA:
            corrompidos.append({
                "maiuscula": maiuscula,
                "ocorrencias_maiuscula": 0,
                "minuscula": minuscula,
                "ocorrencias_minuscula": int(contagem[minuscula]),
                "ocorrencias_esperadas": round(contagem[minuscula] * razao_de_caixa, 1),
            })

    return {
        "arquivo": nome,
        "caracteres": len(texto),
        "ausentes": ausentes,
        "corrompidos": corrompidos,
        "aprovado": not corrompidos,
        "razao_de_caixa": round(razao_de_caixa, 4),
        "causa_provavel": _causa_provavel(nome, corrompidos),
        "criterio": ("maiúscula com zero ocorrências e minúscula correspondente "
                     f"com pelo menos {PISO_EVIDENCIA_MINUSCULA} ocorrências"),
        "contagem_por_letra": {m: int(contagem[m]) for m, _ in PARES_ACENTUADOS},
        "contagem_por_letra_minuscula": {m: int(contagem[m]) for _, m in PARES_ACENTUADOS},
    }


def exigir_aprovado(nome: str, caminho: pathlib.Path | None = None) -> dict:
    """Verifica e interrompe se o arquivo estiver reprovado."""
    laudo = verificar(nome, caminho)
    if not laudo["aprovado"]:
        perdidos = [c["maiuscula"] for c in laudo["corrompidos"]]
        raise ErroDeIntegridade(
            f"{nome} reprovado por perda sistemática de caractere: {perdidos}. "
            "O arquivo MUST NOT ser usado em recuperação nem em citação; "
            "permanece utilizável apenas para contagem de rótulo.")
    return laudo


def verificar_todos() -> dict[str, dict]:
    """Laudo de cada derivado em português, para registro por arquivo (task 3.2)."""
    return {nome: verificar(nome) for nome in ARQUIVOS_PT_BR}


def trecho_e_fiel(trecho: str, origem: str) -> bool:
    """Fidelidade é igualdade literal: o trecho é subcadeia exata da origem.

    Nenhuma tolerância é concedida — comparar sem acento ou com espaço
    colapsado é exatamente a normalização silenciosa que a capability proíbe.
    """
    return bool(trecho) and trecho in origem


def verificar_fidelidade_dos_trechos(df) -> dict:
    """Confere que todo fragmento indexável é subcadeia exata do texto de origem.

    Roda contra o construtor de unidades da prova de conceito de recuperação,
    que é quem produz o trecho exibido ao usuário.
    """
    import hashlib

    from prototipo.rag import unidades

    _, fragmentos, _, _ = unidades.construir(df)

    origem_por_registro = {
        hashlib.sha1(registro.url.encode()).hexdigest()[:10]: registro.text_news
        for registro in df.itertuples(index=False)
    }

    infieis: list[dict] = []
    for fragmento in fragmentos:
        registro_id = fragmento["unidade_id"].split("-")[0]
        origem = origem_por_registro.get(registro_id, "")
        if not trecho_e_fiel(fragmento["trecho"], origem):
            infieis.append({
                "fragmento_id": fragmento["fragmento_id"],
                "trecho": fragmento["trecho"][:120],
            })

    return {
        "registros": int(len(df)),
        "fragmentos": len(fragmentos),
        "fieis": len(fragmentos) - len(infieis),
        "infieis": len(infieis),
        "exemplos_infieis": infieis[:5],
    }


def gravar_laudo(caminho: pathlib.Path | None = None) -> dict:
    """Grava o laudo por arquivo como artefato reexecutável (task 3.2)."""
    destino = caminho or (leitura.DIRETORIO_DERIVADOS / "relatorio_integridade.json")
    laudos = verificar_todos()
    destino.write_text(json.dumps(laudos, ensure_ascii=False, indent=2),
                       encoding="utf-8")
    return laudos
