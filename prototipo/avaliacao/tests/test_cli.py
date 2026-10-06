"""Task 6.5: do modelo ao relatório, pela CLI, com o conjunto de casos real."""
import json

from prototipo.avaliacao.__main__ import main
from prototipo.avaliacao.sessao import carregar_casos


def test_modelo_preenchido_vira_relatorio(tmp_path, capsys):
    casos, sha = carregar_casos()
    armadilha = next(c for c in casos.values() if c.get("armadilha"))
    verdadeiro = next(c for c in casos.values() if c["veredito"] == "verdadeiro")
    falso = next(c for c in casos.values() if c["veredito"] == "falso" and not c.get("armadilha"))
    pasta = tmp_path / "sessoes"
    registro = pasta / "P-01.json"
    assert main(["modelo", "--participante", "P-01", "--tipo", "piloto",
                 "--com", f"{armadilha['id'][:8]},{falso['id'][:8]}", "--transf", verdadeiro["id"][:8],
                 "--saida", str(registro), "--data", "2026-10-20"]) == 0

    # O esqueleto não passa: o pesquisador ainda não preencheu.
    assert main(["validar", str(registro)]) == 1

    r = json.loads(registro.read_text(encoding="utf-8"))
    assert r["casos_sha256"] == sha
    r.update(faixa_etaria="60+", tcle_assinado=True, debriefing_realizado=True)
    r["confianca_fontes"] = {"inicio": {"ministerio_saude": 5, "fiocruz": 5, "anvisa": 4},
                             "fim": {"ministerio_saude": 5, "fiocruz": 4, "anvisa": 4}}
    preenchido = [
        dict(rotulo_exibido="verdadeiro", julgamento="confiavel"),          # armadilha aceita
        dict(rotulo_exibido="falso", julgamento="nao_confiavel", criterios_citados=["cura milagrosa"]),
        dict(julgamento="confiavel", criterios_citados=["fonte oficial"]),
    ]
    for n, (item, campos) in enumerate(zip(r["itens"], preenchido)):
        item.update(inicio=f"2026-10-20T14:0{n}:00-03:00", decisao=f"2026-10-20T14:0{n}:45-03:00", **campos)
    registro.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")

    saida = tmp_path / "relatorio.json"
    assert main(["metricas", str(pasta), "--saida", str(saida)]) == 0
    rel = json.loads(saida.read_text(encoding="utf-8"))
    piloto = rel["agregado"]["piloto"]
    assert rel["casos"]["sha256"] == sha
    assert piloto["guarda"]["aceitacao_cega"]["armadilhas"] == {"n": 1, "de": 1, "taxa": 1.0}
    assert piloto["resultado"]["discernimento"] == {"n": 1, "de": 1, "taxa": 1.0}
    assert piloto["resultado"]["transferencia"] == {"n": 1, "de": 1, "taxa": 1.0}
    assert piloto["resultado"]["tempo_decisao_fundamentada_s"]["com_ferramenta"] == {"mediana": 45.0, "n": 1}
    assert rel["excluidos"] == []


def test_modelo_nao_sobrescreve_registro(tmp_path):
    casos, _ = carregar_casos()
    um = next(iter(casos))[:8]
    destino = tmp_path / "P-02.json"
    destino.write_text("{}")
    try:
        main(["modelo", "--participante", "P-02", "--tipo", "piloto", "--com", um, "--transf", "",
              "--saida", str(destino)])
    except SystemExit as e:
        assert "não sobrescrevo" in str(e)
    else:
        raise AssertionError("sobrescreveu")
    assert destino.read_text() == "{}"


def test_pasta_inexistente_da_mensagem_e_nao_traceback(tmp_path):
    try:
        main(["validar", str(tmp_path / "nada")])
    except SystemExit as e:
        assert "não existe" in str(e)
    else:
        raise AssertionError("não parou")
