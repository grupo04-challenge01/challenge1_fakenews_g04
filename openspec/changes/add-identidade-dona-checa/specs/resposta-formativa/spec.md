# Delta para Resposta Formativa

## Purpose

Abrir toda resposta de verificação com o bordão da Dona Checa
(`identidade-dona-checa`), sem tirar espaço de legibilidade além do que o teto
de 120 palavras já admite. Decidido em 07/10/2026: o bordão é posto pelo
código, nunca escrito pelo modelo, e conta no teto.

## MODIFIED Requirements

### Requirement: Estrutura de quatro blocos

Toda resposta de verificação SHALL abrir com o bordão fixo abaixo, posto antes
do bloco 1 pelo código, e SHALL conter quatro blocos, cuja forma depende de
haver ou não evidência recuperada que sustente afirmação sobre a mensagem. O
bordão MUST contar no teto de palavras da camada visível
(`acessibilidade-leitura`) e MUST NOT ser gerado nem reescrito pelo modelo.

##### Texto — bordao
> Peraí, de onde veio isso? Vamos olhar juntos, meu bem.

Quando **há** evidência recuperada, os blocos são, nesta ordem: (1) veredito,
(2) o que se sabe sobre o assunto, (3) por que aquela mensagem engana e (4) o
que observar da próxima vez. Os blocos 3 e 4 MUST estar presentes mesmo quando o
veredito for `verdadeiro`.

Quando **não há** evidência recuperada — veredito `evidência insuficiente` ou
resposta de lacuna de acervo — os blocos são, nesta ordem: (1) veredito e o que
foi procurado, (2) por que isso não equivale a dizer que a mensagem é falsa,
(3) o que a pessoa pode conferir por conta própria e (4) onde procurar. O bloco
3 MUST NOT afirmar que a mensagem engana, e o bloco 4 MUST estar presente mesmo
quando não houver ponteiro a oferecer, declarando que não há.

#### Scenario: Alegação falsa
- **GIVEN** uma resposta com evidência recuperada
- **WHEN** o veredito é `falso`
- **THEN** a resposta abre com o bordão e traz os quatro blocos na ordem definida
- **AND** o bloco 3 nomeia os sinais concretos presentes naquela mensagem

#### Scenario: Alegação verdadeira
- **GIVEN** uma resposta com evidência recuperada
- **WHEN** o veredito é `verdadeiro`
- **THEN** a resposta abre com o bordão
- **AND** o bloco 3 explica por que a mensagem era difícil de avaliar
- **AND** o bloco 4 indica o que sustentou a confirmação

#### Scenario: Sem evidência ou lacuna de acervo
- **GIVEN** veredito `evidência insuficiente` ou lacuna de acervo
- **WHEN** a resposta é montada
- **THEN** a resposta abre com o bordão e traz os quatro blocos da forma sem evidência

#### Scenario: Bordão no teto
- **GIVEN** quatro blocos que somam 111 palavras com os títulos
- **WHEN** o bordão é acrescentado
- **THEN** a camada visível passa de 120 palavras e é tratada como defeito de legibilidade
