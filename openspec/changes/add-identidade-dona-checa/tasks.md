# Tasks: Identidade e voz da Dona Checa

TDD em toda task de código: teste falhando primeiro, depois a implementação.

## 1. Textos da persona

- [x] 1.1 Teste: `textos()` devolve abertura, pergunta_confianca,
      opcoes_confianca e chamada idênticos aos blocos da spec
      `identidade-dona-checa`
- [x] 1.2 Criar `prototipo/identidade/` com `textos()` lendo os blocos
      `##### Texto — <chave>` da spec (delta do change, fallback
      `openspec/specs/`)
- [x] 1.3 Teste: `pergunta_confianca(piloto=True)` devolve `None`;
      `piloto=False` devolve pergunta e três opções; chamada sem `piloto` é
      erro
- [x] 1.4 Implementar `pergunta_confianca(*, piloto)`
- [x] 1.5 Teste: nenhum texto da persona tem "meu bem" mais de uma vez nem
      "Dra."/"Doutora"

## 2. Bordão na resposta

- [x] 2.1 Teste: toda resposta (com evidência, sem evidência, lacuna) começa
      com o bordão lido da spec `resposta-formativa` deste change
- [x] 2.2 Teste: blocos com 111 palavras mais o bordão geram defeito de
      legibilidade pelo teto de 120
- [x] 2.3 Implementar o bordão em `prototipo/resposta/estrutura.py`, contado
      na verificação de legibilidade
- [x] 2.4 Rodar a suíte de `prototipo/resposta/tests/` e ajustar testes que
      dependiam da camada visível começar no título do bloco 1

## 3. Respostas padrão na voz da Dona Checa

- [x] 3.1 Teste: `carregar_respostas()` devolve os textos novos de
      `conduta_individual` e `veredito_sem_prescricao` nos dois canais
- [x] 3.2 Teste: `risco_imediato` e `sofrimento_psiquico` continuam idênticos
      aos da spec de `mvp-copiloto-verificacao`
- [x] 3.3 Teste: textos novos mantêm UBS, Disque Saúde 136 (desmentido) e a
      declaração de que só confere informação (conduta)
- [x] 3.4 Implementar a sobreposição em `prototipo/verificacao/fronteira.py`
- [x] 3.5 Rodar `prototipo/verificacao/tests/` inteiro, incluindo a suíte
      adversarial

## 4. Logo e paleta

- [x] 4.1 Exportar `docs/identidade/dona-checa.svg` (marca refinada, fundo
      verde-azulado) e `docs/identidade/dona-checa-original.svg` do canvas
      aprovado em 07/10/2026
- [x] 4.2 Escrever `docs/identidade/paleta.md` com os cinco valores e a razão
      de contraste de cada par de texto usado
- [x] 4.3 Registrar a identidade no site de documentação (`mkdocs.yml`)

## 5. Fechamento

- [x] 5.1 Rodar as suítes de `prototipo/` e registrar o resultado
      — 07/10/2026: `pytest` 456 passando, 2 falhando, ambas em
      `prototipo/rag/tests` sobre o índice real local, anterior ao esquema
      1.0.0 (`KeyError: 'apto_citacao'` e idioma `None`); falham igual sem
      este change, e exigem `python -m prototipo.rag construir`. Resposta,
      identidade, verificação e bancada: 290 passando; bancada offline 17/17
- [x] 5.2 `openspec validate add-identidade-dona-checa --strict` limpo
