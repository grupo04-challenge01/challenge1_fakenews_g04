"""Task 6.5: o registro de sessão é recusado quando não sustenta as métricas.

Forma pelo JSON Schema de `registro_sessao.json`; as invariantes S1 a S9 de
`x-invariantes` pelo código, porque dependem do conjunto de casos ou de mais
de um campo. Erro invalida o registro; aviso não invalida, mas sai no laudo.
"""
from prototipo.avaliacao.sessao import validar
from prototipo.avaliacao.tests.conftest import item, sessao


def _erros(registro, casos, sha=None):
    return validar(registro, casos, casos_sha256=sha).erros


def test_registro_completo_e_valido(casos):
    registro = sessao([item("F1"), item("V1", rotulo_exibido="verdadeiro", julgamento="confiavel"),
                       item("F2", bloco="transferencia")])
    laudo = validar(registro, casos)
    assert laudo.erros == []
    assert laudo.valido


def test_forma_errada_sai_pelo_esquema(casos):
    registro = sessao([item("F1", julgamento="talvez")])
    assert any("julgamento" in e for e in _erros(registro, casos))


def test_s1_caso_fora_do_conjunto(casos):
    assert any("S1" in e for e in _erros(sessao([item("X9")]), casos))


def test_s1_hash_do_conjunto_diferente_do_registrado(casos):
    registro = sessao([item("F1")], casos_sha256="a" * 64)
    assert any("S1" in e for e in _erros(registro, casos, sha="b" * 64))


def test_s2_caso_repetido_na_sessao(casos):
    registro = sessao([item("F1"), item("F1", bloco="transferencia")])
    assert any("S2" in e for e in _erros(registro, casos))


def test_s3_transferencia_nao_tem_saida_da_ferramenta(casos):
    registro = sessao([item("F1", bloco="transferencia", rotulo_exibido="falso")])
    assert any("S3" in e for e in _erros(registro, casos))


def test_s4_com_ferramenta_exige_rotulo_e_reacao(casos):
    registro = sessao([item("F1", rotulo_exibido=None)])
    assert any("S4" in e for e in _erros(registro, casos))


def test_s4_item_abandonado_dispensa_rotulo_e_julgamento(casos):
    registro = sessao([item("F1", rotulo_exibido=None, expressou_duvida=None, julgamento=None,
                            decisao=None, abandono={"motivo": "atrito", "detalhe": "texto longo"})])
    assert _erros(registro, casos) == []


def test_s5_armadilha_so_no_bloco_com_ferramenta(casos):
    registro = sessao([item("A1", bloco="transferencia")])
    assert any("S5" in e for e in _erros(registro, casos))


def test_s6_decisao_antes_do_inicio(casos):
    registro = sessao([item("F1", inicio="14:05:00", decisao="14:01:00")])
    assert any("S6" in e for e in _erros(registro, casos))


def test_s6_julgamento_sem_decisao(casos):
    registro = sessao([item("F1", decisao=None)])
    assert any("S6" in e for e in _erros(registro, casos))


def test_s7_sem_tcle_o_registro_nao_existe(casos):
    registro = sessao([item("F1")], tcle_assinado=False)
    assert any("S7" in e for e in _erros(registro, casos))


def test_s8_debriefing_vale_ate_para_sessao_abandonada(casos):
    registro = sessao([item("F1")], debriefing_realizado=False,
                      abandono_sessao={"bloco": "com_ferramenta", "motivo": "cansaco", "detalhe": ""})
    assert any("S8" in e for e in _erros(registro, casos))


def test_s9_confianca_final_exigida_quando_a_sessao_termina(casos):
    registro = sessao([item("F1")])
    registro["confianca_fontes"]["fim"] = None
    assert any("S9" in e for e in _erros(registro, casos))


def test_s9_sessao_abandonada_dispensa_confianca_final(casos):
    registro = sessao([item("F1")], abandono_sessao={"bloco": "com_ferramenta", "motivo": "atrito",
                                                      "detalhe": "desistiu"})
    registro["confianca_fontes"]["fim"] = None
    assert _erros(registro, casos) == []


def test_armadilha_que_nao_exibiu_erro_e_aviso_nao_erro(casos):
    # A IA acertou o item-armadilha: ele não mede aceitação cega, mas o registro vale.
    registro = sessao([item("A1", rotulo_exibido="falso")])
    laudo = validar(registro, casos)
    assert laudo.erros == []
    assert any("A1" in a and "armadilha" in a for a in laudo.avisos)
