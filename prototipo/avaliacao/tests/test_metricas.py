"""Task 6.5: métricas de resultado e de guarda, requirement de
`avaliacao-instrumento` em mvp-copiloto-verificacao.

Cada taxa sai como {"n", "de", "taxa"}: com 2 a 30 participantes a fração
importa mais que o percentual. Definições operacionais na decisão 27 do
design.md e em `specs/avaliacao-instrumento/instrumento-coleta-metricas.md`.
"""
import pytest

from prototipo.avaliacao.metricas import agregar, metricas_sessao, reacao
from prototipo.avaliacao.tests.conftest import item, sessao


def taxa(m):
    return (m["n"], m["de"])


# Resultado ------------------------------------------------------------------

def test_discernimento_conta_acerto_com_ferramenta_fora_das_armadilhas(casos):
    registro = sessao([
        item("F1", julgamento="nao_confiavel"),
        item("V1", rotulo_exibido="verdadeiro", julgamento="confiavel"),
        item("F2", julgamento="nao_sei"),            # não sei não é acerto
        item("A1", rotulo_exibido="verdadeiro", julgamento="confiavel"),  # armadilha: fica fora
    ])
    assert taxa(metricas_sessao(registro, casos)["resultado"]["discernimento"]) == (2, 3)


def test_transferencia_reportada_separada_e_com_criterio(casos):
    registro = sessao([
        item("F1", julgamento="confiavel"),
        item("F2", bloco="transferencia", julgamento="nao_confiavel", criterios_citados=["fonte sem nome"]),
        item("V2", bloco="transferencia", julgamento="nao_confiavel"),
    ])
    r = metricas_sessao(registro, casos)["resultado"]
    assert taxa(r["transferencia"]) == (1, 2)
    assert taxa(r["transferencia_com_criterio"]) == (1, 2)
    assert r["criterios_transferencia"] == {"fonte sem nome": 1}


def test_tempo_ate_decisao_so_conta_decisao_fundamentada(casos):
    registro = sessao([
        item("F1", inicio="14:00:00", decisao="14:01:30", criterios_citados=["cura milagrosa"]),
        item("F2", inicio="14:02:00", decisao="14:02:40", criterios_citados=["fora de contexto"]),
        item("F3", inicio="14:03:00", decisao="14:03:05"),  # sem critério: não é fundamentada
        item("V1", bloco="transferencia", inicio="14:10:00", decisao="14:12:00",
             julgamento="confiavel", criterios_citados=["fonte oficial"]),
    ])
    t = metricas_sessao(registro, casos)["resultado"]["tempo_decisao_fundamentada_s"]
    assert t["com_ferramenta"] == {"mediana": 65.0, "n": 2}
    assert t["transferencia"] == {"mediana": 120.0, "n": 1}


def test_consulta_a_fonte_externa_e_camada_de_detalhe_separadas(casos):
    registro = sessao([
        item("F1", consultou_fonte_externa=True),
        item("F2", abriu_detalhe=True),
        item("F3"),
    ])
    r = metricas_sessao(registro, casos)["resultado"]
    assert taxa(r["consulta_fonte_externa"]["com_ferramenta"]) == (1, 3)
    assert taxa(r["abriu_camada_detalhe"]) == (1, 3)


# Reação à saída: aceitou, questionou, consultou fonte ---------------------------

@pytest.mark.parametrize("campos, esperado", [
    ({}, "aceitou"),
    ({"expressou_duvida": True}, "questionou"),
    ({"abriu_detalhe": True}, "consultou_fonte"),
    ({"expressou_duvida": True, "consultou_fonte_externa": True}, "consultou_fonte"),
])
def test_reacao_derivada_do_comportamento_mais_forte(campos, esperado):
    assert reacao(item("F1", **campos)) == esperado


# Guarda ----------------------------------------------------------------------

def test_aceitacao_cega_quando_a_ia_erra(casos):
    registro = sessao([
        # armadilha, IA erra, participante segue sem questionar: cega
        item("A1", rotulo_exibido="verdadeiro", julgamento="confiavel"),
        # armadilha, IA erra, participante questiona: não cega
        item("A2", rotulo_exibido="verdadeiro", julgamento="confiavel", expressou_duvida=True),
        # fora das armadilhas, IA erra sozinha, participante segue: cega, conta só em todos_erros
        item("F1", rotulo_exibido="verdadeiro", julgamento="confiavel"),
        # IA acerta: não entra no denominador
        item("F2", rotulo_exibido="falso", julgamento="nao_confiavel"),
    ])
    g = metricas_sessao(registro, casos)["guarda"]["aceitacao_cega"]
    assert taxa(g["armadilhas"]) == (1, 2)
    assert taxa(g["todos_erros"]) == (2, 3)


def test_seguir_a_ia_errada_exige_julgamento_igual_ao_rotulo(casos):
    # Não questionou nem consultou, mas julgou contra a IA: não é aceitação cega.
    registro = sessao([item("A1", rotulo_exibido="verdadeiro", julgamento="nao_confiavel")])
    assert taxa(metricas_sessao(registro, casos)["guarda"]["aceitacao_cega"]["armadilhas"]) == (0, 1)


def test_evidencia_insuficiente_nao_e_erro_da_ia(casos):
    registro = sessao([item("A1", rotulo_exibido="evidência insuficiente", julgamento="nao_sei")])
    assert taxa(metricas_sessao(registro, casos)["guarda"]["aceitacao_cega"]["todos_erros"]) == (0, 0)


def test_falso_positivo_em_conteudo_legitimo_do_participante_e_do_sistema(casos):
    registro = sessao([
        item("V1", rotulo_exibido="verdadeiro", julgamento="nao_confiavel"),
        item("V2", rotulo_exibido="falso", julgamento="nao_confiavel"),
        item("F1"),
    ])
    g = metricas_sessao(registro, casos)["guarda"]["falso_positivo_legitimo"]
    assert taxa(g["participante_com_ferramenta"]) == (2, 2)
    assert taxa(g["sistema"]) == (1, 2)


def test_fora_de_contexto_conta_como_nao_confiavel(casos):
    registro = sessao([item("V1", rotulo_exibido="verdadeiro fora de contexto ou exagerado",
                            julgamento="nao_confiavel")])
    assert taxa(metricas_sessao(registro, casos)["guarda"]["falso_positivo_legitimo"]["sistema"]) == (1, 1)


def test_queda_de_confianca_em_fonte_confiavel(casos):
    registro = sessao([item("F1")])
    registro["confianca_fontes"]["fim"] = {"ministerio_saude": 3, "fiocruz": 4, "anvisa": 2}
    g = metricas_sessao(registro, casos)["guarda"]["confianca_fontes"]
    assert g["delta_medio"] == -1.0
    assert g["queda"] is True


def test_abandono_por_atrito_separado_de_outro_motivo(casos):
    registro = sessao([
        item("F1", rotulo_exibido=None, expressou_duvida=None, julgamento=None, decisao=None,
             abandono={"motivo": "atrito", "detalhe": "não achou o botão"}),
        item("F2", rotulo_exibido=None, expressou_duvida=None, julgamento=None, decisao=None,
             abandono={"motivo": "outro", "detalhe": "telefonema"}),
        item("F3"),
    ])
    g = metricas_sessao(registro, casos)["guarda"]["abandono_atrito"]
    assert taxa(g["itens"]) == (1, 3)
    assert g["sessao"] is False


def test_item_abandonado_fica_fora_do_discernimento(casos):
    registro = sessao([
        item("F1", rotulo_exibido=None, expressou_duvida=None, julgamento=None, decisao=None,
             abandono={"motivo": "atrito", "detalhe": ""}),
        item("F2"),
    ])
    assert taxa(metricas_sessao(registro, casos)["resultado"]["discernimento"]) == (1, 1)


# Agregação -------------------------------------------------------------------

def test_agregado_soma_fracoes_e_nao_mistura_piloto_com_coleta(casos):
    p1 = sessao([item("F1"), item("F2", julgamento="confiavel")], participante="P-01")
    p2 = sessao([item("F1"), item("F2")], participante="P-02",
                abandono_sessao={"bloco": "transferencia", "motivo": "atrito", "detalhe": ""})
    p2["confianca_fontes"]["fim"] = {"ministerio_saude": 3, "fiocruz": 3, "anvisa": 3}
    c1 = sessao([item("F1")], participante="P-03", tipo="coleta")
    ag = agregar([p1, p2, c1], casos)
    assert set(ag) == {"piloto", "coleta"}
    piloto = ag["piloto"]
    assert piloto["sessoes"] == 2
    assert taxa(piloto["resultado"]["discernimento"]) == (3, 4)
    assert taxa(piloto["guarda"]["confianca_fontes"]["sessoes_com_queda"]) == (1, 2)
    assert taxa(piloto["guarda"]["abandono_atrito"]["sessoes"]) == (1, 2)
    assert ag["coleta"]["sessoes"] == 1


def test_taxa_com_denominador_zero_e_nula(casos):
    registro = sessao([item("F1")])
    assert metricas_sessao(registro, casos)["guarda"]["aceitacao_cega"]["armadilhas"] == \
        {"n": 0, "de": 0, "taxa": None}
