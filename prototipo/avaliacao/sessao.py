"""Registro de sessão: leitura do conjunto de casos e validação — task 6.5.

Mesmo arranjo do esquema de indexação (`prototipo/rag/esquema.py`): a forma de
cada registro pelo JSON Schema em `registro_sessao.json`; as invariantes S1 a
S9 de `x-invariantes`, que dependem do conjunto de casos ou cruzam campos, por
código. Erro invalida o registro e ele fica fora das métricas. Aviso não
invalida, mas sai no laudo: hoje, item-armadilha em que a ferramenta não errou.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
from dataclasses import dataclass, field

from .metricas import COM, TRANSF, _instante, erro_ia

RAIZ = pathlib.Path(__file__).resolve().parents[2]
ESQUEMA = pathlib.Path(__file__).with_name("registro_sessao.json")
CASOS = RAIZ / "datasets" / "casos_mvp_copiloto" / "mvp_copiloto_casos.json"


@dataclass
class Laudo:
    erros: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    @property
    def valido(self) -> bool:
        return not self.erros


def carregar_casos(caminho: pathlib.Path = CASOS) -> tuple[dict, str]:
    """Casos indexados por id e o SHA-256 do arquivo."""
    bruto = pathlib.Path(caminho).read_bytes()
    casos = {c["id"]: c for c in json.loads(bruto)}
    return casos, hashlib.sha256(bruto).hexdigest()


def _esquema() -> dict:
    return json.loads(ESQUEMA.read_text(encoding="utf-8"))


def _forma(registro: dict) -> list[str]:
    from jsonschema import Draft7Validator, FormatChecker
    validador = Draft7Validator(_esquema(), format_checker=FormatChecker())
    erros = []
    for e in sorted(validador.iter_errors(registro), key=lambda e: list(e.absolute_path)):
        caminho = "/".join(str(p) for p in e.absolute_path) or "(raiz)"
        erros.append(f"forma {caminho}: {e.message}")
    return erros


def _data_hora(texto: str | None) -> dt.datetime | None:
    try:
        return _instante(texto) if texto else None
    except ValueError:
        return None


def validar(registro: dict, casos: dict, casos_sha256: str | None = None) -> Laudo:
    laudo = Laudo(erros=_forma(registro))
    if laudo.erros:
        # Invariantes supõem a forma; com ela quebrada, só a forma vai no laudo.
        return laudo
    erros, avisos = laudo.erros, laudo.avisos

    registrado = registro.get("casos_sha256")
    if registrado and casos_sha256 and registrado != casos_sha256:
        erros.append(f"S1: casos_sha256 do registro ({registrado[:12]}…) difere do conjunto de "
                     f"casos usado na validação ({casos_sha256[:12]}…)")
    if not registro["tcle_assinado"]:
        erros.append("S7: tcle_assinado falso; sem TCLE não há sessão a registrar")
    if not registro["debriefing_realizado"]:
        erros.append("S8: debriefing_realizado falso; o debriefing vale também para sessão abandonada")
    if registro["abandono_sessao"] is None and registro["confianca_fontes"]["fim"] is None:
        erros.append("S9: confianca_fontes.fim vazia em sessão que não foi abandonada")

    vistos = set()
    for n, item in enumerate(registro["itens"], start=1):
        cid, bloco = item["caso_id"], item["bloco"]
        rotulo = f"item {n} ({cid})"
        if cid not in casos:
            erros.append(f"S1: {rotulo} não existe no conjunto de casos")
            continue
        if cid in vistos:
            erros.append(f"S2: {rotulo} repetido na sessão")
        vistos.add(cid)
        caso = casos[cid]
        abandonado = item["abandono"] is not None

        if bloco == TRANSF and (item["rotulo_exibido"] is not None or item["expressou_duvida"] is not None
                                or item["abriu_detalhe"]):
            erros.append(f"S3: {rotulo} na transferência com saída da ferramenta registrada")
        if bloco == COM and not abandonado and (item["rotulo_exibido"] is None or item["expressou_duvida"] is None):
            erros.append(f"S4: {rotulo} com ferramenta sem rotulo_exibido ou expressou_duvida")
        if caso.get("armadilha") and bloco != COM:
            erros.append(f"S5: {rotulo} é item-armadilha fora do bloco com_ferramenta")

        if abandonado != (item["julgamento"] is None) or abandonado != (item["decisao"] is None):
            erros.append(f"S6: {rotulo}: julgamento e decisao devem ser nulos só quando o item é abandonado")
        inicio, decisao = _data_hora(item["inicio"]), _data_hora(item["decisao"])
        if inicio is None or (item["decisao"] and decisao is None):
            erros.append(f"S6: {rotulo} com data-hora ilegível")
        elif decisao and decisao < inicio:
            erros.append(f"S6: {rotulo} com decisao anterior a inicio")

        if caso.get("armadilha") and bloco == COM and not abandonado and not erro_ia(item, casos):
            avisos.append(f"{rotulo}: item-armadilha em que a ferramenta exibiu "
                          f"'{item['rotulo_exibido']}', sem contradizer o gabarito; não entra na aceitação cega")
    return laudo
