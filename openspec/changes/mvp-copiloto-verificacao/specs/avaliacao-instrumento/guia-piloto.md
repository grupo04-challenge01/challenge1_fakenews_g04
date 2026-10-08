# Guia Operacional e Registro do Teste Piloto com Usuários

**Projeto:** Copiloto de Verificação de Desinformação em Saúde Pública  
**Change:** `mvp-copiloto-verificacao` (Task 6.6 — R1 Business Stakeholder: Breno)  
**Dependências obrigatórias antes de executar:**

!!! warning "Este guia só pode ser executado após a conclusão de:"
    - **Task 6.1** (Jhessica): Casos curados — concluída
    - **Task 6.2** (Jhessica): 4 a 6 itens-armadilha configurados — concluída
    - **Task 6.3** (Breno): TCLE e roteiro de debriefing — concluída
    - **Task 6.4** (Breno): Protocolo aprovado pelo comitê de ética — concluída (homologação simulada da residência)

**Participantes:** 2 voluntários adultos leigos (designados `P-01` e `P-02`)  
**Data de execução:** Outubro/2026 (protocolo ético homologado)  


---

## 1. Objetivo do Teste Piloto

Antes de submeter o copiloto à coleta de campo com 20 a 30 usuários, o piloto com **2 participantes** tem por finalidade testar a engrenagem metodológica da sessão:
1. Validar se o tempo planejado (35 a 45 minutos) é realista ou gera fadiga.
2. Conferir se o vocabulário das dimensões da Matriz de Confiança é compreendido sem jargão técnico por pessoas leigas.
3. Testar a reação ao debriefing e desarmar adequadamente o item-armadilha sem constrangimento.
4. Identificar atritos na interface web/WhatsApp antes do teste principal.

---

## 2. Preparação da Sessão (Checklist do Pesquisador)

!!! important "Preencher este checklist na preparação da sessão (Tasks 6.1 e 6.2 concluídas)"

- [ ] 2 vias impressas do TCLE (ou formulário digital de coleta de consentimento).
- [ ] Protótipo do Copiloto aberto e testado no navegador ou dispositivo de teste.
- [ ] Conjunto de 5 casos selecionados para a sessão extraídos de `datasets/casos_mvp_copiloto/mvp_copiloto_casos.json`:
  - Caso 1: Notícia falsa evidente (ex.: suco de inhame cura dengue).
  - Caso 2: Notícia verdadeira contra-intuitiva (ex.: vacina da gripe é recomendada para gestantes).
  - Caso 3: Item-armadilha (copiloto induz ou fornece explicação incompleta para aferir dependência acrítica).
  - Casos 4 e 5: Bloco de transferência (mensagens avaliadas sem o copiloto).
- [ ] Folheto de Debriefing com gabaritos oficiais do Ministério da Saúde / Fiocruz impresso ou em PDF.
- [ ] Cronômetro ou anotação de horário de início e fim de cada bloco.

---

## 3. Roteiro Passo a Passo de Execução

### Bloco A — Acolhimento e TCLE (5 a 7 min)
- Apresentar a pesquisa com cordialidade: *"Estamos testando uma ferramenta de auxílio a cidadãos para verificar mensagens de saúde recebidas no dia a dia"*.
- Esclarecer que quem está sendo avaliado é o **sistema**, nunca a inteligência ou capacidade da pessoa.
- Ler conjuntamente os pontos principais do TCLE, colher a assinatura e entregar a via do voluntário.

### Bloco B — Interação Guiada com o Copiloto (15 a 20 min)
- Entregar o primeiro caso impresso ou no celular: *"Imagine que você recebeu esta mensagem no grupo da família. Cole ou digite ela no copiloto"*.
- Observar silenciosamente onde o participante clica, onde olha primeiro e quanto tempo leva para ler o retorno.
- Apresentar o Caso 2 (verdadeiro contra-intuitivo) e observar a compreensão da explicação.
- Apresentar o Caso 3 (item-armadilha): anotar se o usuário aceitou cegamente a resposta ou se expressou dúvida/estranhamento.

### Bloco C — Bloco de Transferência sem a Ferramenta (8 a 10 min)
- *"Agora, sem usar o copiloto, leia estas duas mensagens e me diga se você confiaria nelas e que sinais observou"*.
- Registrar se o participante utilizou espontaneamente os critérios aprendidos (procurar a fonte original, suspeitar de autoridades sem nome, verificar se há corte de vídeo).

### Bloco D — Debriefing Supervisionado e Encerramento (10 min)
- Conduzir o roteiro de debriefing de forma calorosa (seguir o roteiro completo em [`protocolo-etico-tcle-debriefing.md`](protocolo-etico-tcle-debriefing.md#3-roteiro-operacional-de-debriefing-supervisionado)):
  1. Revelar o gabarito oficial de todas as mensagens.
  2. Revelar a presença do item-armadilha: *"Essa resposta propositalmente veio incompleta porque faz parte do nosso teste científico medir se a ferramenta é confiável demais ou se a pessoa mantém o senso crítico. Você percebeu algo?"*.
  3. Tirar todas as dúvidas de saúde do participante.
  4. Entregar o folheto informativo com os canais oficiais do Ministério da Saúde e Fiocruz.

---

## 4. Ficha de Registro dos Dados do Piloto

### Participante P-01
- **Perfil Demográfico Sumário:** [Idade aprox., familiaridade com WhatsApp]
- **Tempo Total da Sessão:** [XX] minutos
- **Comportamento no Item-Armadilha:** ( ) Aceitou cegamente  ( ) Desconfiou da resposta  ( ) Apontou incoerência
- **Desempenho no Bloco de Transferência:** [Identificou sinais de não-confiança? Sim/Não/Parcial]
- **Dificuldades de Usabilidade Observadas:** [Ex.: texto longo, botão pouco visível, etc.]
- **Reação ao Debriefing:** [Compreendeu os gabaritos e ficou confortável?]

### Participante P-02
- **Perfil Demográfico Sumário:** [Idade aprox., familiaridade com WhatsApp]
- **Tempo Total da Sessão:** [XX] minutos
- **Comportamento no Item-Armadilha:** ( ) Aceitou cegamente  ( ) Desconfiou da resposta  ( ) Apontou incoerência
- **Desempenho no Bloco de Transferência:** [Identificou sinais de não-confiança? Sim/Não/Parcial]
- **Dificuldades de Usabilidade Observadas:** [Ex.: texto longo, botão pouco visível, etc.]
- **Reação ao Debriefing:** [Compreendeu os gabaritos e ficou confortável?]

---

## 5. Síntese e Ajustes Recomendados para a Coleta Principal

*(Preenchido após a aplicação com P-01 e P-02)*:

- **Ajustes no tempo ou instruções:** 
- **Ajustes na interface ou redação do copiloto:**
- **Status do Instrumento:** *(marcar após validação)* Aprovado para a coleta massiva de 20 a 30 usuários.
