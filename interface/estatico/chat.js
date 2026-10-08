// Chat web da Dona Checa (add-interface-chat-web).
// Estados da conversa: lendo, fronteira, conferindo, resposta, aviso e erro.
// A resposta à pergunta de confiança fica só em memória, nesta página: nunca
// vai ao servidor nem a armazenamento do navegador (requirement Pergunta de
// confiança só no navegador).
// Com gerador remoto, o termo de consentimento vem antes do campo; a escolha
// também fica só nesta página e vai em cada pedido (add-gerador-api-deepseek, D8).

const config = JSON.parse(document.getElementById("config").textContent);
const conversa = document.getElementById("conversa");
const formulario = document.getElementById("envio");
const campo = document.getElementById("mensagem");
const botaoEnviar = formulario.querySelector('button[type="submit"]');
let consentimento = null;
let ultimoId = 0;

document.getElementById("chamada").textContent = config.textos.chamada;
bolhaDona().append(paragrafo(config.textos.abertura));
if (config.termo) {
  bloquear(true);
  termo(config.termo);
}

formulario.addEventListener("submit", (evento) => {
  evento.preventDefault();
  const texto = campo.value;
  if (!texto.trim() || (config.termo && !consentimento)) return;
  campo.value = "";
  verificar(texto);
});

campo.addEventListener("keydown", (evento) => {
  if (evento.key === "Enter" && !evento.shiftKey && !evento.isComposing) {
    evento.preventDefault();
    formulario.requestSubmit();
  }
});

// ---- elementos ----------------------------------------------------------------------

function criar(tag, classe, texto) {
  const el = document.createElement(tag);
  if (classe) el.className = classe;
  if (texto !== undefined) el.textContent = texto;
  return el;
}

// Ids por contador: crypto.randomUUID só existe em contexto seguro, e no celular
// a página abre por http://<ip da rede>. `ultimoId` fica no topo do arquivo.
function novoId(prefixo) {
  ultimoId += 1;
  return `${prefixo}-${ultimoId}`;
}

function paragrafo(texto, classe) {
  return criar("p", classe, texto);
}

function bolhaDona(classe = "") {
  const bolha = criar("div", `bolha dona ${classe}`.trim());
  bolha.tabIndex = -1;
  conversa.append(bolha);
  return bolha;
}

function bolhaPessoa(texto) {
  conversa.append(criar("div", "bolha pessoa", texto));
}

function focar(bolha) {
  bolha.focus({ preventScroll: true });
  bolha.scrollIntoView({ block: "nearest" });
}

// Markdown mínimo das respostas padrão da spec: **negrito**, *itálico* e listas
// com "- ". O texto é escapado antes.
function escapar(texto) {
  return texto.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;",
                                             '"': "&quot;", "'": "&#39;" })[c]);
}

function enfeitar(linha) {
  return escapar(linha)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>");
}

// Telefones citados viram botões grandes de ligar, embaixo do texto, em vez de
// links pequenos no meio da frase.
const TELEFONES = { 192: "Ligar para o SAMU (192)", 188: "Ligar para o CVV (188)",
                    136: "Ligar para o Disque Saúde (136)" };

function ligar(texto) {
  const acoes = criar("div", "acoes ligar");
  for (const [numero, rotulo] of Object.entries(TELEFONES)) {
    if (!new RegExp(`\\b${numero}\\b`).test(texto)) continue;
    const link = criar("a", "botao-ligar", rotulo);
    link.href = `tel:${numero}`;
    acoes.append(link);
  }
  return acoes;
}

function markdown(texto) {
  const destino = document.createDocumentFragment();
  for (const bloco of texto.split(/\n\s*\n/)) {
    const linhas = bloco.split("\n").map((l) => l.trim()).filter(Boolean);
    if (!linhas.length) continue;
    if (linhas.every((l) => l.startsWith("- "))) {
      const lista = criar("ul");
      for (const l of linhas) {
        const item = criar("li");
        item.innerHTML = enfeitar(l.slice(2));
        lista.append(item);
      }
      destino.append(lista);
    } else {
      const p = criar("p");
      p.innerHTML = linhas.map(enfeitar).join("<br>");
      destino.append(p);
    }
  }
  return destino;
}

// ---- termo de consentimento ----------------------------------------------------------

function bloquear(sim) {
  campo.disabled = sim;
  botaoEnviar.disabled = sim;
}

function termo({ versao, texto, recusa, alternativa }) {
  const bolha = bolhaDona("termo");
  const grupo = criar("div", "pergunta");
  grupo.setAttribute("role", "group");
  const rotulo = paragrafo(texto);
  rotulo.id = novoId("termo");
  grupo.setAttribute("aria-labelledby", rotulo.id);
  const botoes = criar("div", "opcoes");
  const aceito = criar("button", "opcao", "Aceito");
  const naoAceito = criar("button", "opcao", "Não aceito");
  for (const botao of [aceito, naoAceito]) {
    botao.type = "button";
    botoes.append(botao);
  }
  aceito.addEventListener("click", () => {
    consentimento = versao;
    botoes.replaceWith(paragrafo("Combinado. Pode mandar a mensagem.", "anotado"));
    bloquear(false);
    campo.focus();
  });
  naoAceito.addEventListener("click", () => {
    botoes.remove();
    const resposta = bolhaDona();
    resposta.append(paragrafo(recusa));
    if (alternativa) {
      consentimento = "recusado";
      bloquear(false);
    }
    focar(resposta);
  });
  grupo.append(rotulo, botoes);
  bolha.append(grupo);
}

// ---- verificação --------------------------------------------------------------------

async function verificar(texto) {
  bolhaPessoa(texto);
  const bolha = bolhaDona();
  const andamento = paragrafo(config.textos.lendo, "andamento");
  bolha.append(andamento);
  const estado = { bolha, andamento, texto, terminou: false };
  try {
    const resposta = await fetch("/verificar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(consentimento ? { texto, consentimento } : { texto }),
    });
    if (!resposta.ok || !resposta.body) throw new Error(`HTTP ${resposta.status}`);
    const leitor = resposta.body.pipeThrough(new TextDecoderStream()).getReader();
    let resto = "";
    for (;;) {
      const { value, done } = await leitor.read();
      if (done) break;
      resto += value;
      const partes = resto.split("\n\n");
      resto = partes.pop();
      for (const parte of partes) {
        if (parte.startsWith("data: ")) tratar(estado, JSON.parse(parte.slice(6)));
      }
    }
  } catch (erro) {
    if (!estado.terminou) tratar(estado, { tipo: "erro", texto: config.textos.erro });
    return;
  }
  if (!estado.terminou) tratar(estado, { tipo: "erro", texto: config.textos.erro });
}

function tratar(estado, evento) {
  const { bolha } = estado;
  switch (evento.tipo) {
    case "fronteira":
      if (evento.desfecho === "urgencia" || evento.desfecho === "sofrimento") {
        alerta(estado, evento.texto);
      } else {
        conferindo(estado, evento.desfecho === "conduta");
      }
      break;
    case "andamento":
      if (estado.andamento) estado.andamento.textContent = evento.frase;
      break;
    case "resposta":
      responder(estado, evento);
      break;
    case "aviso":
      terminar(estado, () => bolha.replaceChildren(paragrafo(evento.texto)));
      break;
    case "erro":
      terminar(estado, () => erro(estado, evento.texto));
      break;
  }
}

function terminar(estado, montar) {
  estado.terminou = true;
  estado.andamento?.remove();
  estado.andamento = null;
  montar();
  focar(estado.bolha);
}

// Urgência e sofrimento: na hora, sem bordão nem pergunta, anunciados com prioridade.
function alerta(estado, texto) {
  estado.terminou = true;
  estado.bolha.remove();
  const bolha = bolhaDona("alerta");
  bolha.setAttribute("role", "alert");
  bolha.append(markdown(texto), ligar(texto));
  estado.bolha = bolha;
  focar(bolha);
}

function conferindo(estado, conduta) {
  const { bolha } = estado;
  bolha.replaceChildren(paragrafo(config.textos.bordao, "bordao"));
  if (config.pergunta && !conduta) bolha.append(pergunta(config.pergunta));
  estado.andamento = paragrafo(config.textos.lendo, "andamento");
  bolha.append(estado.andamento);
}

function pergunta({ pergunta: texto, opcoes }) {
  const grupo = criar("div", "pergunta");
  grupo.setAttribute("role", "group");
  const rotulo = paragrafo(texto);
  rotulo.id = novoId("pergunta");
  grupo.setAttribute("aria-labelledby", rotulo.id);
  const botoes = criar("div", "opcoes");
  const anotado = criar("p", "anotado");
  anotado.setAttribute("aria-live", "polite");
  for (const opcao of opcoes) {
    const botao = criar("button", "opcao", opcao);
    botao.type = "button";
    botao.setAttribute("aria-pressed", "false");
    botao.addEventListener("click", () => {
      for (const b of botoes.children) b.setAttribute("aria-pressed", String(b === botao));
      anotado.textContent = "Anotado. Vamos ver o que as fontes dizem.";
    });
    botoes.append(botao);
  }
  grupo.append(rotulo, botoes, anotado);
  return grupo;
}

function titulo(texto) {
  const minusculo = texto.toLocaleLowerCase("pt-BR");
  return minusculo.charAt(0).toLocaleUpperCase("pt-BR") + minusculo.slice(1);
}

function responder(estado, evento) {
  terminar(estado, () => {
    const { bolha } = estado;
    for (const recusa of evento.redirecionamentos) {
      const aviso = criar("div", "bolha dona");
      aviso.append(markdown(recusa));
      conversa.insertBefore(aviso, bolha);
    }
    const [primeiro, ...blocos] = evento.texto.split("\n\n");
    if (!bolha.querySelector(".bordao")) bolha.prepend(paragrafo(primeiro, "bordao"));
    for (const bloco of blocos) {
      const casa = bloco.match(/^([A-ZÁÉÍÓÚÂÊÔÃÕÇ ?]+:)\s*([\s\S]*)$/u);
      const p = criar("p", "bloco");
      if (casa) {
        p.append(criar("strong", "", titulo(casa[1])), ` ${casa[2]}`);
      } else {
        p.textContent = bloco;
      }
      bolha.append(p);
    }
    if (evento.detalhe.length || evento.origem) detalhe(bolha, evento.detalhe, evento.origem);
  });
}

function data(iso) {
  const casa = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso ?? "");
  return casa ? `${casa[3]}/${casa[2]}/${casa[1]}` : "data não informada";
}

// Cartão de origem: a página que a Dona Checa leu, para a pessoa conferir que foi
// lido o que ela mandou (add-entrada-por-link, requirement Mensagem com link).
function cartaoOrigem(origem) {
  const cartao = criar("article", "origem");
  cartao.append(paragrafo(config.textos.origem, "rotulo"));
  cartao.append(criar("h2", "", origem.titulo || origem.url));
  const meta = [origem.veiculo, origem.data ? data(origem.data) : null].filter(Boolean);
  if (meta.length) cartao.append(paragrafo(meta.join(" · "), "meta"));
  const link = criar("a", "", "Abrir a página lida");
  link.href = origem.url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  cartao.append(link);
  return cartao;
}

function detalhe(bolha, fontes, origem) {
  const painel = criar("div", "detalhe");
  painel.id = novoId("detalhe");
  painel.hidden = true;
  if (origem) painel.append(cartaoOrigem(origem));
  for (const fonte of fontes) {
    const cartao = criar("article", "fonte");
    cartao.append(criar("h2", "", fonte.agencia || "Fonte"));
    cartao.append(paragrafo(
      `${data(fonte.data_publicacao)} · veredito da agência: ${fonte.veredito_original || "não informado"}`,
      "meta"));
    if (fonte.trecho) {
      cartao.append(criar("blockquote", "", fonte.trecho));
    } else {
      cartao.append(paragrafo("Trecho não exibido: esta fonte não permite citação."));
    }
    if (fonte.url) {
      const link = criar("a", "", "Abrir a checagem original");
      link.href = fonte.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      cartao.append(link);
    }
    painel.append(cartao);
  }
  const botao = criar("button", "secundario", "Ver fontes e detalhes");
  botao.type = "button";
  botao.setAttribute("aria-expanded", "false");
  botao.setAttribute("aria-controls", painel.id);
  botao.addEventListener("click", () => {
    const abrir = painel.hidden;
    painel.hidden = !abrir;
    botao.setAttribute("aria-expanded", String(abrir));
  });
  const acoes = criar("div", "acoes");
  acoes.append(botao);
  bolha.append(acoes, painel);
}

function erro(estado, texto) {
  const { bolha } = estado;
  bolha.append(paragrafo(texto));
  const botao = criar("button", "secundario", "Tentar de novo");
  botao.type = "button";
  botao.addEventListener("click", () => {
    botao.disabled = true;
    verificar(estado.texto);
  });
  const acoes = criar("div", "acoes");
  acoes.append(botao);
  bolha.append(acoes);
}
