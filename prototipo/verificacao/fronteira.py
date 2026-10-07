"""Classificador da fronteira de saúde — task 4.1 de mvp-copiloto-verificacao.

Contrato da task 4.2, em `specs/fronteira-orientacao-saude/spec.md`: o
classificador roda antes do LLM de checagem. Em risco imediato e em sofrimento
psíquico, a checagem é pulada e a resposta padrão sai em menos de 500 ms.

Duas camadas:

1. **Regras** (léxico em PT-BR). Rodam em microssegundos. Se acharem risco
   imediato ou sofrimento psíquico, o resultado sai sem chamar o modelo. Para
   não disparar em pedido de checagem ("recebi que dor no peito se cura com..."),
   o sintoma de risco só conta com marca de que está acontecendo com alguém
   ("estou com", "meu pai", "desde", "agora").
2. **Modelo** (Gemma, mesmo prompt JSON dos outros módulos). Pega o que o léxico
   não pega: pedido indireto de conduta ("o que você acha?") e sofrimento dito
   sem as palavras fortes. Conduta achada pelas regras se soma ao modelo; saída
   inválida do modelo deixa só as regras.

A sonda T2 de 18/09 mostrou que o prompt de checagem sozinho não segura a
fronteira. Por isso esta decisão fica fora dele. Ver decisão 15 do design.md.

As respostas padrão são lidas da própria spec, para que texto e código não
divirjam.
"""
import pathlib
import re
import unicodedata
from dataclasses import dataclass

from prototipo.verificacao.modelo import chat_ollama, ler_json

CATEGORIAS = ("risco_imediato", "sofrimento_psiquico", "conduta_individual", "checagem")
BYPASS = {"risco_imediato", "sofrimento_psiquico"}
CANAIS = ("web", "whatsapp")

RAIZ = pathlib.Path(__file__).parents[2]
SPEC = [RAIZ / "openspec/changes/mvp-copiloto-verificacao/specs/fronteira-orientacao-saude/spec.md",
        RAIZ / "openspec/specs/fronteira-orientacao-saude/spec.md"]
# Respostas na voz da Dona Checa, por cima da base enquanto o change não é arquivado.
SOBREPOSICAO = [RAIZ / "openspec/changes/add-identidade-dona-checa/specs/"
                       "fronteira-orientacao-saude/spec.md"]
REQUISITOS = {  # começo do título do requirement na spec -> chave
    "Recusa de orientação clínica": "conduta_individual",
    "Prioridade e bypass em sinal de risco": "risco_imediato",
    "Veredito sem prescrição": "veredito_sem_prescricao",
    "Salvaguarda de sofrimento psíquico": "sofrimento_psiquico",
}

# Léxico aplicado ao texto em minúsculas e sem acento.
SINTOMA = re.compile(
    r"dor (forte )?no peito|aperto no peito|falta de ar|nao consig\w* respirar"
    r"|dificuldade (pra|para|de) respirar|desmai|convuls|perdeu (a )?consciencia|desacordad"
    r"|nao acorda\b|labios? roxo|boca torta|braco dormente|fala enrolada|garganta fechando"
    r"|inchac\w* (na|da) (garganta|lingua|boca)|sangramento (forte|intenso|que nao para)"
    r"|vomitando sangue|febre (alta )?(ha|faz) (\d+|dois|tres|quatro|cinco) dias|febre de 4\d"
    r"|picad[ao] de (cobra|escorpiao)|engoliu (remedio|veneno|produto)|overdose")
ACONTECENDO = re.compile(
    r"\b(estou|to|tou|estava|sinto|senti|sentindo|tive|agora|desde|de repente"
    r"|esta (com|sentindo|passando mal)"
    r"|comecou|ha \d+|nao para)\b"
    r"|\b(meu|minha)s? (pai|mae|filh[oa]|avo|marido|esposa|mulher|irma|irmao|bebe|net[oa]"
    r"|ti[oa]|sogr[oa]|amig[oa]|vizinh[oa])\b|\b(ele|ela)\b")
PSIQUICO = re.compile(
    r"quero morrer|vou me matar|me matar|tirar (a )?minha (propria )?vida"
    r"|acabar com (a )?minha vida|nao quero mais viver|nao aguento mais viver"
    r"|melhor (nao acordar|morrer|sumir)|nao acordar mais"
    r"|(penso|pensando|pensei) em (suicid|me matar)|vou me cortar|me machucar de proposito"
    r"|(cartela|vidro|caixa) (inteir[oa] )?(de remedio )?(pra|para) (acabar com tudo|morrer|nao acordar)")
CONDUTA = re.compile(
    r"\b(posso|pode|podem|devo|deve|devemos|preciso|precisa|da pra|da para|e seguro)\b(\s+\w+){0,4}?\s+"
    r"(parar|tomar|trocar|substituir|suspender|largar|interromper|diminuir|aumentar|dobrar"
    r"|misturar|comecar|usar|vacinar)\b"
    r"|\b(qual|quanto|quantos|quantas)( a| o)? (dose|mg|miligramas|gotas|comprimidos)\b"
    r"|\b(meu|minha|o meu|a minha) (exame|resultado|glicemia|pressao)\b.*\b(deu|mostrou|esta|veio)\b"
    r"|\b(o que|que) (significa|quer dizer) (o |meu |esse )?(exame|resultado)"
    r"|\bsera que (eu |ele |ela )?(tenho|tem|estou|esta com)")
OBJETO_CLINICO = re.compile(
    r"remedio|medicament|medicac|tratamento|dose|comprimid|insulina|quimio|antibiotic|vacin"
    r"|capsula|pressao|anticoncepcional|antidepressiv|\bmg\b|gotas|chas?\b|cha de|exame|glicemia"
    r"|diabet|ivermectina|cloroquina|dipirona|paracetamol")

SISTEMA = """Você faz a triagem de mensagens enviadas a um verificador de notícias de saúde.
O verificador só checa informações. Ele não dá conduta médica.

Marque TODAS as categorias que valem para a mensagem:
"risco_imediato": a mensagem conta que alguém está AGORA com sintoma grave (dor no
  peito, falta de ar, desmaio, convulsão, sangramento forte, febre alta há dias,
  reação depois de tomar algo). Pergunta sobre um sintoma em notícia NÃO é risco.
"sofrimento_psiquico": a pessoa mostra desespero, vontade de morrer, de se ferir ou
  de sumir, mesmo com palavras indiretas. Notícia sobre suicídio NÃO é isto.
"conduta_individual": a pessoa pede uma decisão de saúde para ela ou alguém próximo:
  parar, começar, trocar ou dosar remédio ou tratamento, tomar ou não vacina,
  interpretar exame, saber se tem uma doença, ou pede a sua opinião sobre isso.
"checagem": a pessoa quer saber se uma informação é verdadeira. Use só quando
  nenhuma das outras vale.

Responda só com JSON, neste formato:
{"categorias": ["conduta_individual"], "motivo": "uma frase curta"}"""


@dataclass
class Intencao:
    categorias: tuple
    via: str

    @property
    def bypass(self):
        return bool(BYPASS & set(self.categorias))


def _normal(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                   if unicodedata.category(c) != "Mn")


def _ordenar(categorias):
    reais = set(categorias) - {"checagem"}
    return tuple(c for c in CATEGORIAS if c in reais) or ("checagem",)


def por_regras(texto):
    """Categorias que o léxico reconhece; conjunto vazio quando nenhuma."""
    t = _normal(texto)
    achadas = set()
    if SINTOMA.search(t) and ACONTECENDO.search(t):
        achadas.add("risco_imediato")
    if PSIQUICO.search(t):
        achadas.add("sofrimento_psiquico")
    if CONDUTA.search(t) and OBJETO_CLINICO.search(t):
        achadas.add("conduta_individual")
    return achadas


def por_modelo(texto, chat=chat_ollama):
    """Categorias que o modelo marca. ValueError se a saída não servir."""
    dados = ler_json(chat(SISTEMA, f"MENSAGEM:\n\"\"\"{texto}\"\"\""))
    if dados is None or not isinstance(dados.get("categorias"), list) or not dados["categorias"]:
        raise ValueError("saída do modelo sem lista `categorias`")
    fora = [c for c in dados["categorias"] if c not in CATEGORIAS]
    if fora:
        raise ValueError(f"categoria fora das quatro: {fora}")
    return set(dados["categorias"])


def classificar(texto, chat=chat_ollama):
    regras = por_regras(texto)
    if regras & BYPASS:
        return Intencao(_ordenar(regras), "regras")
    try:
        modelo = por_modelo(texto, chat=chat)
    except ValueError:
        return Intencao(_ordenar(regras), "regras (modelo inválido)")
    via = "regras+modelo" if regras - modelo else "modelo"
    return Intencao(_ordenar(regras | modelo), via)


def carregar_respostas():
    """{chave: {canal: texto}} a partir dos blocos "Resposta Padrão" da spec.

    A base é a spec de mvp-copiloto-verificacao ou, arquivada, a principal. Por
    cima vêm as respostas do delta de add-identidade-dona-checa, canal a canal;
    as que o delta não traz (urgência, sofrimento psíquico) ficam as da base.
    Arquivados os dois changes, a sobreposição some e a principal já traz o
    texto novo (decisão 2 do design de add-identidade-dona-checa).
    """
    base = next((p for p in SPEC if p.exists()), None)
    if base is None:
        raise FileNotFoundError("spec fronteira-orientacao-saude não encontrada")
    respostas = ler_respostas(base)
    for spec in SOBREPOSICAO:
        if spec.exists():
            for chave, canais in ler_respostas(spec).items():
                respostas.setdefault(chave, {}).update(canais)
    return respostas


def ler_respostas(spec):
    """{chave: {canal: texto}} dos blocos "Resposta Padrão" de um arquivo de spec."""
    respostas, chave, canais, linhas = {}, None, None, None

    def fechar():
        if chave and canais and linhas:
            texto = "\n".join(linhas).strip()
            for canal in canais:
                respostas.setdefault(chave, {})[canal] = texto

    for linha in spec.read_text(encoding="utf-8").splitlines():
        if linha.startswith("### Requirement:"):
            fechar()
            titulo = linha.removeprefix("### Requirement:").strip()
            chave = next((v for k, v in REQUISITOS.items() if titulo.startswith(k)), None)
            canais, linhas = None, None
        elif linha.startswith("##### Resposta Padrão"):
            fechar()
            rotulo = linha.lower()
            canais = [c for c, nome in (("web", "web"), ("whatsapp", "whatsapp")) if nome in rotulo]
            linhas = []
        elif linhas is not None and linha.startswith(">"):
            linhas.append(linha[1:].removeprefix(" ").rstrip())
        elif linhas is not None and linhas and not linha.startswith(">"):
            fechar()
            canais, linhas = None, None
    fechar()
    return respostas


def responder(intencao, canal):
    """Respostas padrão da intenção, no canal pedido, na ordem de prioridade."""
    if canal not in CANAIS:
        raise ValueError(f"canal desconhecido: {canal!r}; use {CANAIS}")
    respostas = carregar_respostas()
    return [respostas[c][canal] for c in intencao.categorias if c != "checagem"]
