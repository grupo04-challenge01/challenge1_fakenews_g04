"""Conjunto de casos e sessões fictícias para os testes da task 6.5.

Nada aqui vem de participante real. Os casos imitam a forma de
`datasets/casos_mvp_copiloto/mvp_copiloto_casos.json` (task 6.1 e 6.2).
"""
import copy

import pytest

CASOS = {
    "F1": {"id": "F1", "veredito": "falso", "contra_intuitivo": False, "armadilha": False},
    "F2": {"id": "F2", "veredito": "falso", "contra_intuitivo": False, "armadilha": False},
    "F3": {"id": "F3", "veredito": "falso", "contra_intuitivo": False, "armadilha": False},
    "A1": {"id": "A1", "veredito": "falso", "contra_intuitivo": False, "armadilha": True},
    "A2": {"id": "A2", "veredito": "falso", "contra_intuitivo": False, "armadilha": True},
    "V1": {"id": "V1", "veredito": "verdadeiro", "contra_intuitivo": True, "armadilha": False},
    "V2": {"id": "V2", "veredito": "verdadeiro", "contra_intuitivo": True, "armadilha": False},
}


def item(caso_id, bloco="com_ferramenta", inicio="14:00:00", decisao="14:01:00", **campos):
    base = {
        "caso_id": caso_id,
        "bloco": bloco,
        "inicio": f"2026-10-20T{inicio}-03:00",
        "decisao": f"2026-10-20T{decisao}-03:00" if decisao else None,
        "julgamento": "nao_confiavel",
        "criterios_citados": [],
        "consultou_fonte_externa": False,
        "abandono": None,
        "observacao": "",
    }
    if bloco == "com_ferramenta":
        base.update(rotulo_exibido="falso", expressou_duvida=False, abriu_detalhe=False)
    else:
        base.update(rotulo_exibido=None, expressou_duvida=None, abriu_detalhe=False)
    base.update(campos)
    return base


def sessao(itens, **campos):
    base = {
        "versao_instrumento": "1.0.0",
        "participante": "P-01",
        "tipo": "piloto",
        "data": "2026-10-20",
        "faixa_etaria": "60+",
        "casos_sha256": None,
        "tcle_assinado": True,
        "confianca_fontes": {
            "inicio": {"ministerio_saude": 4, "fiocruz": 4, "anvisa": 4},
            "fim": {"ministerio_saude": 4, "fiocruz": 4, "anvisa": 4},
        },
        "itens": itens,
        "abandono_sessao": None,
        "debriefing_realizado": True,
    }
    base.update(campos)
    return base


@pytest.fixture
def casos():
    return copy.deepcopy(CASOS)
