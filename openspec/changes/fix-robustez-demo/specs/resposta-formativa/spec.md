# Delta para resposta-formativa

## ADDED Requirements

### Requirement: Veredito só com blocos de critério

Uma resposta com veredito de evidência MUST NOT chegar à pessoa sem frase do
modelo nos blocos 1 e 2. Quando a saída do modelo não puder ser lida como JSON
na forma com evidência, o sistema SHALL pedir uma nova resposta com o aviso da
conferência e, se a falha persistir, SHALL rebaixar a resposta para a forma
sem evidência, registrando o motivo.

#### Scenario: Saída não-JSON nas duas tentativas
- **GIVEN** um veredito «falso» com trechos recuperados
- **AND** um modelo que responde texto livre nas duas chamadas
- **WHEN** a resposta é montada
- **THEN** a resposta sai na forma sem evidência
- **AND** o motivo do rebaixamento registra que a saída não é JSON

#### Scenario: Saída não-JSON corrigida na segunda tentativa
- **GIVEN** um veredito «falso» com trechos recuperados
- **AND** um modelo que responde texto livre na primeira chamada e JSON ancorado na segunda
- **WHEN** a resposta é montada
- **THEN** a resposta sai na forma com evidência, com os blocos 1 e 2 preenchidos

### Requirement: Agência com nome legível

As referências mostradas à pessoa e os trechos enviados ao modelo SHALL trazer
o nome da agência de checagem, não o valor cru do índice. Valor sem nome
conhecido SHALL aparecer como veio.

#### Scenario: Valor do índice com endereço colado
- **GIVEN** um trecho com agência `https:piaui.folha.uol.com.brlupa`
- **WHEN** a resposta monta o detalhe
- **THEN** a referência traz a agência «Agência Lupa»
