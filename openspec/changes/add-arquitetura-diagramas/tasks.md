# Tasks: Arquitetura em diagramas

## 1. Configuração

- [x] 1.1 Declarar o fence `mermaid` em `pymdownx.superfences` no `mkdocs.yml` (D1)

## 2. Página de arquitetura

- [x] 2.1 Escrever `docs/arquitetura.md` com os diagramas de contexto,
      contêineres, fluxo, sequência, recuperação, guarda e resposta, dados,
      avaliação, implantação e pacotes (D2, D3)
- [x] 2.2 Incluir a página na nav do `mkdocs.yml`

## 3. Apresentação

- [x] 3.1 Trocar o texto dos slides 4, 5 e 7 por diagramas, com no máximo
      três frases de apoio por slide (D4)

## 5. Mapa interativo

- [x] 5.1 Criar `docs/mapa/arquitetura.html`, mapa navegável com zonas, cards,
      fluxos guiados e decisões, na identidade da Dona Checa (D5)
- [x] 5.2 Ligar o mapa a partir de `docs/arquitetura.md`
- [x] 5.3 Conferir os números do mapa contra o código e o manifesto

## 4. Verificação

- [x] 4.1 Conferir cada componente, número e limiar dos diagramas contra o
      código citado
- [x] 4.2 `mkdocs build --strict` sem `WARNING`, com os diagramas renderizados
- [x] 4.3 `openspec validate add-arquitetura-diagramas --strict`
