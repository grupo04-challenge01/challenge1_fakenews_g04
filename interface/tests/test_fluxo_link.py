"""Tasks 7.2 a 7.4 de add-entrada-por-link: mensagem com link nos eventos.

Requirement Mensagem com link, de `interface-chat-web` no delta de
add-entrada-por-link. Roda o `executar` de verdade, com modelo, recuperador e
busca falsos.
"""
from bancada.tests.test_pipeline_link import (
    LONGO_SEM_ALEGACAO, PAGINA_JATOBA, PAGINA_PARCIAL_JATOBA, PAGINA_PARCIAL_SEM_SAUDE,
    buscar_fixo, chat_por_conteudo)
from bancada.tests.test_bancada import Recuperador
from interface import fluxo
from interface.fluxo import verificar
from prototipo.entrada.leitura import AVISO_PARCIAL
from prototipo.entrada.rede import Recusa


def _eventos(texto, buscar=None):
    eventos = []
    verificar(texto, eventos.append, chat=chat_por_conteudo(), recuperador=Recuperador(),
              buscar=buscar or buscar_fixo())
    return eventos


def _andamentos(eventos):
    return [e["etapa"] for e in eventos if e["tipo"] == "andamento"]


def test_textos_de_link_vem_do_delta():
    t = fluxo.textos()
    assert t["andamento"]["leitura"] == "Abrindo o link…"
    assert t["nao_abriu"].startswith("Meu bem, tentei abrir esse link")
    assert t["fechada"].startswith("Meu bem, essa página só abre")
    assert t["video"].startswith("Meu bem, isso é vídeo")
    assert t["vazia"].startswith("Meu bem, abri a página")
    assert t["origem"] == "Li esta página:"


# 7.2 andamento

def test_link_mostra_abrindo_o_link_antes_da_extracao():
    eventos = _eventos("Olha isso: https://blog.exemplo/cura")
    assert _andamentos(eventos) == ["leitura", "extracao", "decomposicao", "recuperacao",
                                    "guarda", "resposta"]
    leitura = next(e for e in eventos if e.get("etapa") == "leitura")
    assert leitura["frase"] == "Abrindo o link…"


def test_sem_link_nao_mostra_abrindo_o_link():
    eventos = _eventos("A casca do jatobá cura o câncer!")
    assert _andamentos(eventos) == ["extracao", "decomposicao", "recuperacao", "guarda",
                                    "resposta"]


def test_texto_longo_sem_alegacao_abre_o_link_depois_da_extracao():
    eventos = _eventos(f"{LONGO_SEM_ALEGACAO} https://blog.exemplo/cura")
    assert _andamentos(eventos)[:3] == ["extracao", "leitura", "extracao"]
    assert eventos[-1]["tipo"] == "resposta"


# 7.3 falhas de leitura

def test_cada_causa_vira_aviso_com_o_texto_da_spec():
    casos = {
        "nao_abriu": ("https://exemplo.com.br/x", buscar_fixo(Recusa("status"))),
        "video": ("https://youtu.be/abc", None),
        "vazia": ("https://exemplo.com.br/x", buscar_fixo(PAGINA_PARCIAL_SEM_SAUDE)),
        "fechada": ("https://www.instagram.com/p/x/",
                    buscar_fixo(b"<html><head><title>Instagram</title></head></html>",
                                url_final="https://www.instagram.com/p/x/")),
    }
    for causa, (mensagem, buscar) in casos.items():
        ultimo = _eventos(mensagem, buscar)[-1]
        assert ultimo == {"tipo": "aviso", "chave": causa, "texto": fluxo.textos()[causa]}, causa


def test_falha_de_leitura_nao_e_erro():
    eventos = _eventos("https://exemplo.com.br/x", buscar_fixo(Recusa("tempo")))
    assert all(e["tipo"] != "erro" for e in eventos)


# 7.4 origem na resposta

def test_resposta_de_pagina_traz_a_origem():
    resposta = _eventos("https://blog.exemplo/cura?utm_source=zap",
                        buscar_fixo(PAGINA_JATOBA, url_final="https://blog.exemplo/cura"))[-1]
    assert resposta["origem"] == {"titulo": "Chá de jatobá cura câncer", "veiculo": "Blog Exemplo",
                                  "data": "2026-09-20", "url": "https://blog.exemplo/cura"}


def test_resposta_de_texto_nao_traz_origem():
    assert _eventos("A casca do jatobá cura o câncer!")[-1]["origem"] is None


def test_leitura_parcial_traz_o_aviso_no_texto():
    resposta = _eventos("https://exemplo.com.br/x", buscar_fixo(PAGINA_PARCIAL_JATOBA))[-1]
    assert resposta["texto"].split("\n\n")[1] == AVISO_PARCIAL


# 7.6 nada guardado

def test_buscas_nao_deixam_pagina_url_nem_texto_no_disco_nem_no_log(tmp_path, monkeypatch, caplog):
    monkeypatch.chdir(tmp_path)
    caplog.set_level("DEBUG")
    _eventos("Olha isso: https://blog.exemplo/cura")
    _eventos("https://exemplo.com.br/fora", buscar_fixo(Recusa("status")))
    _eventos("https://exemplo.com.br/parcial", buscar_fixo(PAGINA_PARCIAL_JATOBA))
    assert list(tmp_path.iterdir()) == []
    for vestigio in ("blog.exemplo", "exemplo.com.br", "jatobá", "<html", "frase1"):
        assert vestigio not in caplog.text
