"""Task 3.3 de mvp-copiloto-verificacao: o rótulo usado pertence ao catálogo."""
import json

import pytest

from prototipo.resposta.catalogo import (
    carregar_catalogo,
    rotulos_marcados,
    validar_rotulos,
    validar_sem_evidencia,
)


@pytest.fixture(scope="module")
def catalogo():
    return carregar_catalogo()


def test_catalogo_versionado_tem_de_6_a_8_rotulos_unicos(catalogo):
    assert 6 <= len(catalogo) <= 8
    assert len(set(catalogo)) == len(catalogo)


def test_catalogo_traz_os_dois_rotulos_fixados_na_spec(catalogo):
    assert "cura milagrosa" in catalogo
    assert "manchete exagerada" in catalogo


def test_catalogo_fora_do_intervalo_e_recusado(tmp_path):
    arquivo = tmp_path / "curto.json"
    arquivo.write_text(json.dumps({"tecnicas": [{"rotulo": f"r{i}"} for i in range(5)]}),
                       encoding="utf-8")
    with pytest.raises(ValueError):
        carregar_catalogo(arquivo)


def test_rotulo_com_e_ou_virgula_e_recusado(tmp_path):
    # A leitura do bloco 3 separa rótulos por vírgula e por " e ".
    tecnicas = [{"rotulo": f"r{i}"} for i in range(6)] + [{"rotulo": "medo e pressa"}]
    arquivo = tmp_path / "ambiguo.json"
    arquivo.write_text(json.dumps({"tecnicas": tecnicas}), encoding="utf-8")
    with pytest.raises(ValueError):
        carregar_catalogo(arquivo)


def test_rotulo_do_catalogo_passa(catalogo):
    assert validar_rotulos("Técnica: cura milagrosa. A mensagem promete cura rápida.", catalogo) == []


def test_dois_rotulos_do_catalogo_passam(catalogo):
    texto = "Técnica: fonte sem nome e urgência fabricada."
    assert rotulos_marcados(texto) == ["fonte sem nome", "urgência fabricada"]
    assert validar_rotulos(texto, catalogo) == []


def test_markdown_e_caixa_nao_mudam_o_rotulo(catalogo):
    assert validar_rotulos("**Técnica:** `Cura Milagrosa`.", catalogo) == []


def test_rotulo_inventado_e_defeito(catalogo):
    # `apelo ao medo` estava no catálogo provisório da sonda de 18/09 e não entrou.
    assert validar_rotulos("Técnica: apelo ao medo.", catalogo) == [
        "rótulo fora do catálogo: apelo ao medo"]


def test_so_o_rotulo_inventado_e_apontado(catalogo):
    assert validar_rotulos("Técnica: cura milagrosa, remédio da vovó.", catalogo) == [
        "rótulo fora do catálogo: remédio da vovó"]


def test_sem_marcador_e_defeito(catalogo):
    # O rótulo aparece no texto, mas sem o marcador não há como separar rótulo
    # de uso comum da palavra; a validação não adivinha.
    assert validar_rotulos("Isso é uma cura milagrosa.", catalogo) == ["nenhum rótulo marcado"]


# --- Task 3.3 de fix-resposta-sem-evidencia: sob evidência insuficiente, técnica é defeito ---


def test_forma_sem_evidencia_sem_tecnica_passa(catalogo):
    texto = (
        "VEREDITO E O QUE FOI PROCURADO: evidência insuficiente.\n"
        "POR QUE ISSO NÃO QUER DIZER QUE É FALSO: não encontrar não é desmentir.\n"
        "O QUE VOCÊ PODE CONFERIR: consulte o portal da Anvisa e fontes oficiais.\n"
        "ONDE PROCURAR: https://www.gov.br/anvisa"
    )
    assert validar_sem_evidencia(texto, catalogo) == []


def test_forma_sem_evidencia_com_tecnica_marcada_e_reprovada(catalogo):
    texto = "VEREDITO: evidência insuficiente. Técnica: cura milagrosa."
    defeitos = validar_sem_evidencia(texto, catalogo)
    assert defeitos == ["técnica nomeada sob evidência insuficiente: cura milagrosa"]


def test_forma_sem_evidencia_com_dois_rotulos_reprova_ambos(catalogo):
    texto = "VEREDITO: evidência insuficiente. Técnica: fonte sem nome e manchete exagerada."
    defeitos = validar_sem_evidencia(texto, catalogo)
    assert defeitos == [
        "técnica nomeada sob evidência insuficiente: fonte sem nome",
        "técnica nomeada sob evidência insuficiente: manchete exagerada",
    ]


def test_forma_sem_evidencia_com_rotulo_inventado_tambem_e_reprovada():
    texto = "VEREDITO: evidência insuficiente. Técnica: apelo ao medo."
    defeitos = validar_sem_evidencia(texto)
    assert defeitos == ["técnica nomeada sob evidência insuficiente: apelo ao medo"]


def test_forma_sem_evidencia_com_mencao_a_tecnica_do_catalogo_e_reprovada(catalogo):
    texto = "VEREDITO: evidência insuficiente. A mensagem aponta cura milagrosa para o sintoma."
    defeitos = validar_sem_evidencia(texto, catalogo)
    assert defeitos == ["técnica do catálogo mencionada sob evidência insuficiente: cura milagrosa"]

