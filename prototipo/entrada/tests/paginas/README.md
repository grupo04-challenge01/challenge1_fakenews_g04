# Páginas gravadas para os testes de `leitura`

Task 4.1 de `add-entrada-por-link`. Os testes leem estes arquivos e nunca a
rede. `indice.json` guarda, para cada página real, a URL pedida, a URL final
depois dos redirecionamentos e o `Content-Type` recebido.

## Reais, coletadas em 07/10/2026

Buscadas com `prototipo.entrada.rede.buscar`. Para reduzir tamanho, foram
removidos `<script>` (menos `application/ld+json`), `<style>`, `<svg>` e
comentários HTML. A extração com `trafilatura` deu o mesmo número de
palavras, título e data antes e depois da redução, nas cinco.

| Arquivo | Origem | Caso | Palavras extraídas |
| --- | --- | --- | --- |
| `blog_oglobo_completo.html` | blog de saúde de O Globo | leitura completa | 660 |
| `folha_paywall_mole.html` | blog da Folha | `isAccessibleForFree: false` com texto inteiro no HTML | 491 |
| `valor_titulo_lead.html` | notícia do Valor Econômico | paywall sem sinal no `JSON-LD`, só título e começo | 47 |
| `excalidraw_so_js.html` | Excalidraw | página montada por JavaScript, com resumo em `og:description` (leitura parcial) | 10 |
| `instagram_login.html` | perfil do Ministério da Saúde no Instagram | rede social com login | 32 |

O conteúdo pertence aos veículos de origem e está aqui só como dado de teste.

## Sintéticas, escritas pelo grupo

Não foi achada, na coleta, página real com estes casos.

| Arquivo | Caso |
| --- | --- |
| `fechada_sintetica.html` | `isAccessibleForFree: false` sem o texto da matéria, só aviso de assinatura |
| `injecao_sintetica.html` | blog de desinformação com tentativa de injeção de instrução (decisão D8) |
| `injecao_controle_sintetica.html` | a mesma página sem o parágrafo de injeção, para comparar o veredito |
