# Proposal: Copiloto de verificação de informação de saúde (MVP)

**Fase do CBL:** Act (semanas 4–5, desenvolvimento). Proposto durante o Engage
para que a especificação anteceda a construção; nenhuma task é executada antes
do encerramento do Investigate.

## Summary

Construir um assistente conversacional com RAG que responde a alegações de saúde
recebidas por mensagem, entregando veredito fundamentado em checagens brasileiras
e, na mesma resposta, o critério que permitiu chegar a esse veredito.

O produto não é um classificador de fake news. É um instrumento de formação de
discernimento cuja saída principal — do ponto de vista da pesquisa — é a
capacidade do usuário de avaliar a próxima alegação **sem** a ferramenta.

## Motivation

Verificar bem custa 10 a 15 minutos; decidir acreditar custa 3 segundos. As
ferramentas existentes dão veredito e não ensinam, e o alerta repetido gera
dessensibilização. O resultado é que quem mais precisa verificar é quem menos
verifica.

O recorte é saúde, onde o dano é imediato (substância ineficaz, abandono de
tratamento) e onde existe corpus brasileiro de checagem disponível.

Público: geral. Pessoa idosa com baixo letramento digital entra como **restrição
de projeto**, não como público-alvo — a interface e o texto precisam funcionar
para ela, mas as conclusões da pesquisa não se limitam a esse grupo.

## What Changes

Seis capacidades novas. Nada é modificado ou removido (projeto greenfield).

| Capacidade | O que entrega | MVP |
|---|---|---|
| `verificacao-alegacao` | Extração da alegação e emissão de veredito com incerteza explícita | Sim |
| `recuperacao-evidencia` | RAG sobre checagens PT-BR e fontes oficiais, com rastreabilidade | Sim |
| `resposta-formativa` | Resposta em quatro blocos e catálogo fechado de técnicas de manipulação | Sim |
| `fronteira-orientacao-saude` | Recusa de orientação clínica individual | Sim |
| `acessibilidade-leitura` | Legibilidade e requisitos de interface verificáveis | Sim |
| `avaliacao-instrumento` | Conjunto local de 20 a 30 casos, itens-armadilha e protocolo ético | Sim |

## Out of Scope

Fora do escopo do MVP:

- entrada por imagem ou OCR;
- entrada por áudio;
- bot de WhatsApp em produção;
- moderação de plataforma;
- detecção multimodal.

## Impact

Entregáveis finais do challenge atingidos:

- **Solução/protótipo com suporte de IA** — alvo direto das seis capacidades.
- **Estrutura de avaliação de confiança** — o catálogo de técnicas e o bloco 4
  da resposta operacionalizam a matriz. O catálogo MUST ser consistente com as
  dimensões da capability `matriz-confianca` (fase Engage), não um segundo
  vocabulário paralelo.
- **Portfólio de pesquisa** — alimentado por `avaliacao-instrumento`.
- **Apresentação e reflexão** — alimentada pelas métricas de resultado e de
  guarda.

Dependências e restrições:

- Corpus já coletado: FactCenter (4.063 checagens de saúde em PT-BR), FACTCK.BR,
  PUBHEALTH, FakeHealth, InSciOut.
- Depende de decisão de canal antes da fase de testes (ver `design.md`).
- Os itens-armadilha exigem TCLE e debriefing obrigatório; com participantes
  idosos, submissão ao CEP.
