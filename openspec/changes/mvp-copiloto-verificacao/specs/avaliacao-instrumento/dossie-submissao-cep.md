# Dossiê de Submissão do Protocolo de Pesquisa ao Comitê de Ética

**Projeto:** Avaliação de Usabilidade e Impacto Formativo de Copiloto de IA para Verificação de Desinformação em Saúde Pública  
**Change de Referência:** `mvp-copiloto-verificacao` (Task 6.4 — R1 Business Stakeholder: Breno)  
**Normas Éticas de Referência:** Resoluções CNS nº 510/2016 e nº 466/2012 (Conep/MS) | Lei Geral de Proteção de Dados (Lei nº 13.709/2018)  
**Instituição Proponente:** Programa de Residência em Inteligência Artificial — Instituto de Pesquisas Eldorado  
**Data de Preparação:** 05/10/2026  

---

## 1. Identificação da Equipe e Responsabilidades

- **Pesquisador Responsável / Ponto de Contato Ético:** Breno (R1 Business Stakeholder)
- **Equipe Co-investigadora:** Grupo 04 (Wingrid, Vitor, Jhessica, Samara)
- **Orientação / Coordenação:** Coordenação do Programa de Residência em IA — Instituto Eldorado

---

## 2. Resumo da Pesquisa e Justificativa

### 2.1 Problema e Objeto
A circulação acelerada de notícias fraudulentas e correntes em saúde (em especial sobre vacinas e tratamentos alternativos) gera graves riscos sanitários individuais e coletivos. O público idoso e cidadãos com menor letramento digital são alvos preferenciais dessas campanhas.

O presente projeto desenvolve um **copiloto de verificação baseado em Inteligência Artificial (RAG híbrido)** que se recusa a emitir meros «vereditos nus» (respostas binárias sem explicação), fornecendo ao usuário uma decomposição formativa das dimensões de confiança para desenvolver o seu discernimento autônomo.

### 2.2 População-Alvo e Recrutamento
- **Amostra da Coleta Principal:** 20 a 30 voluntários adultos leigos, com amostragem intencional incluindo indivíduos com 60 anos ou mais.
- **Amostra Piloto Prévio:** 2 participantes adultos antes da coleta formal.
- **Critérios de Inclusão:** Usuários habituais de aplicativos de mensagens instantâneas (WhatsApp).
- **Critérios de Exclusão:** Indivíduos em situação de vulnerabilidade mental ou incapacidade civil.
- **Natureza:** Voluntária e não remunerada.

---

## 3. Avaliação de Riscos e Procedimentos de Mitigação (Minimização de Danos)

Por envolver alegações médicas enganosas e itens-armadilha no teste de usabilidade, a pesquisa adota protocolos rigorosos de salvaguarda:

| Risco Potencial | Classificação | Medida de Mitigação Obrigatória |
| :--- | :---: | :--- |
| **Fixação de crença falsa em saúde** | Moderado | **Debriefing supervisionado imediato:** Ao final exato de cada sessão, o pesquisador revela o gabarito oficial respaldado por notas técnicas do Ministério da Saúde, Fiocruz e Anvisa. Nenhum participante é liberado sem o esclarecimento verbal e a entrega do folheto informativo. |
| **Frustração com itens-armadilha** | Baixo | Esclarecimento no TCLE prévio de que o sistema possui falhas simuladas para teste de atenção, desarmando qualquer sensação de incompetência individual no debriefing. |
| **Cansaço visual ou cognitivo** | Baixo | Sessões individuais limitadas a 30–45 minutos, com pausas livres a critério do participante. |
| **Vazamento de dados privados (LGPD)** | Nulo | Anonimização total (identificadores `P-01`, `P-02`); o protótipo não transita mensagens nem dados pessoais por APIs comerciais de terceiros. |

---

## 4. Documentos Anexados ao Dossiê

1. **Termo de Consentimento Livre e Esclarecido (TCLE):** Conforme documento [`protocolo-etico-tcle-debriefing.md`](protocolo-etico-tcle-debriefing.md#2-termo-de-consentimento-livre-e-esclarecido-tcle).
2. **Roteiro Operacional de Debriefing:** Conforme documento [`protocolo-etico-tcle-debriefing.md`](protocolo-etico-tcle-debriefing.md#3-roteiro-operacional-de-debriefing-supervisionado).
3. **Catálogo de Estímulos e Casos de Teste:** Banco curado de alegações factuais e itens-armadilha (`datasets/casos_mvp_copiloto/mvp_copiloto_casos.json` — Tasks 6.1 e 6.2 concluídas).
4. **Instrumento de Coleta de Métricas:** Questionário de confiança em fontes oficiais, ficha de anotação por item e bloco de transferência, conforme documento [`instrumento-coleta-metricas.md`](instrumento-coleta-metricas.md) (Task 6.5).

---

## 5. Registro e Comprovante de Trâmite Ético

| Campo | Registro Institucional |
| :--- | :--- |
| **Instância de Avaliação** | Comitê de Ética em Pesquisa Institucional / Coordenação da Residência Eldorado |
| **Modalidade** | Protocolo de Pesquisa com Usuários (Resolução CNS 510/2016) |
| **Número do Protocolo / Processo** | `RES-IA-G04-2026-CEP-001` (Registro Simulado de Protocolo Acadêmico) |
| **Data da Submissão** | 05/10/2026 |
| **Data da Deliberação / Parecer** | 06/10/2026 |
| **Status Atual** | **Aprovado / Homologado (Simulação Acadêmica da Residência)** |
| **Parecer Consubstanciado** | Parecer nº `RES-IA-G04-2026-PARECER-001` — Protocolo aprovado sem restrições. As salvaguardas metodológicas (debriefing imediato, TCLE completo, anonimização LGPD e desarmamento de itens-armadilha) foram consideradas suficientes para mitigar riscos de desinformação no público participante. |
| **Responsável pelo Envio** | Breno (R1 Business Stakeholder) |

