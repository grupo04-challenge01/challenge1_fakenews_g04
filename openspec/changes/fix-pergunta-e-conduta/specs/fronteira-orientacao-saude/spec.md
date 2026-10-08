# Delta para fronteira-orientacao-saude

## MODIFIED Requirements

### Requirement: Prioridade e bypass em sinal de risco imediato / urgência médica

Quando a mensagem relatar sintomas agudos ou sinais de alerta de emergência (ex.: dor precordial, dispneia grave, reações anafiláticas, perda de consciência, febre alta persistente) ou ferimento recente (ex.: corte, queimadura, queda com batida na cabeça, osso quebrado, mordida de animal, pisar em prego), o sistema MUST interromper imediatamente o fluxo habitual de checagem/RAG e SHALL responder de imediato com encaminhamento para atendimento de emergência do SUS.

#### Scenario: Sintoma de risco imediato
- **WHEN** a mensagem descreve sintoma agudo ou situação de urgência
- **THEN** o sistema suspende a checagem da alegação antes do socorro
- **AND** instrui a buscar atendimento emergencial imediatamente
- **AND** fornece explicitamente os contatos do SAMU (192) e UPA / Pronto-Socorro

#### Scenario: Ferimento recente
- **GIVEN** a mensagem "Cortei o pé com uma enxada, o que devo fazer?"
- **WHEN** a fronteira classifica a mensagem
- **THEN** a categoria é risco imediato, pelas regras, sem depender do modelo
- **AND** a resposta é a de urgência, com o SAMU (192)

#### Scenario: Ferimento citado em notícia
- **GIVEN** a mensagem "Recebi que corte de enxada se cura com borra de café, é verdade?"
- **WHEN** a fronteira classifica a mensagem
- **THEN** a categoria não é risco imediato pelas regras

##### Resposta Padrão — Web
> 🚨 **Atenção:** Você descreveu sintomas que precisam de avaliação médica urgente.
> 
> **Antes de qualquer checagem**, procure imediatamente uma **UPA** ou **Pronto-Socorro**, ou ligue para o **SAMU (192)**. Não espere nem tente receitas caseiras para sintomas graves.

##### Resposta Padrão — WhatsApp
> 🚨 *ATENÇÃO URGENTE* 🚨
> 
> Você descreveu sintomas que precisam de **avaliação médica imediata**.
> 
> 🔴 **Antes de qualquer checagem de notícia:**
> - Procure imediatamente uma **UPA** ou **Pronto-Socorro** mais próximo.
> - Ou ligue agora para o **SAMU (192)**.
> 
> ⚠️ *Não espere nem tente receitas caseiras para sintomas graves.*

---
