"""Task 3.3 de mvp-copiloto-verificacao: o rótulo usado pertence ao catálogo."""
import json

import pytest

from prototipo.resposta.catalogo import carregar_catalogo, rotulos_marcados, validar_rotulos


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
