# Matriz de Confiança (Versão 1)

Este documento consolida as dimensões de confiança, validadas empiricamente contra os casos da forense, cumprindo as exigências das tasks 4.1 a 4.4. 

---

## Dimensão 1: Falsa Autoridade ou Fonte Inexistente
*   **Sinal observável:** A mensagem atribui a afirmação a uma autoridade genérica/sem nome (ex: "um médico", "marido da Simone") ou cita uma instituição real, mas a pesquisa ou estudo não existe.
*   **Papel da IA:** Buscar o estudo nos repositórios públicos da instituição citada ou verificar se a autoridade nomeada existe e fez publicamente a declaração.
*   **Limite:** A IA não pode afirmar categoricamente que o médico não existe, mas sim que não há registo público do estudo/declaração vinculada a ele.
*   **Rubrica:**
    *   **Sinal Forte:** Cita instituição/autoridade nominal, mas a verificação nos repositórios oficiais confirma a inexistência do estudo ou da declaração.
    *   **Sinal Fraco:** Cita uma autoridade de forma vaga ("um médico de Sorocaba"), impossibilitando a verificação de autoria.
    *   **Sinal Ausente:** Não invoca autoridade técnica ou a fonte citada é localizável e corrobora a afirmação.

## Dimensão 2: Recontextualização e Edição de Mídia
*   **Sinal observável:** A data do vídeo/imagem não corresponde à data do evento alegado, ou existem cortes abruptlys que removem palavras que mudam o sentido da fala.
*   **Papel da IA:** Realizar busca reversa para encontrar a data de publicação original da imagem/vídeo ou localizar o vídeo original completo para comparar a transcrição.
*   **Limite:** A IA apenas aponta a divergência temporal ou a omissão de trechos entre os vídeos; não julga a "intenção" de quem fez o corte.
*   **Rubrica:**
    *   **Sinal Forte:** O vídeo/foto original é localizado e possui data anterior ao evento alegado, ou a transcrição original revela uma pergunta/ressalva cortada.
    *   **Sinal Fraco:** Vídeo ou imagem apresentados sem contexto temporal ou espacial claro, dificultando o rastreio.
    *   **Sinal Ausente:** A mídia condiz perfeitamente com o evento, data e contexto relatados.

## Dimensão 3: Distorção de Documento Real
*   **Sinal observável:** Um documento real é citado (ex: bula de remédio), mas a mensagem omite uma ressalva crucial ou afirma que o documento diz mais do que realmente diz.
*   **Papel da IA:** Localizar o documento real citado na base de dados (ex: Anvisa, FDA) e comparar o trecho original completo com a alegação da mensagem.
*   **Limite:** A IA mostra o texto do documento original lado a lado com a alegação para evidenciar o exagero, mas não julga a validade científica do documento em si.
*   **Rubrica:**
    *   **Sinal Forte:** Documento original localizado e o texto contradiz a alegação ou contém uma ressalva explicitamente omitida na mensagem.
    *   **Sinal Fraco:** O documento é citado de forma muito genérica ("tá na bula"), sem especificar a marca ou a versão.
    *   **Sinal Ausente:** A alegação reproduz fielmente as conclusões e ressalvas do documento original.

## Dimensão 4: Enquadramento Conspiratório (Vaga do Catálogo)
*   **Sinal observável:** A mensagem atribui uma motivação secreta, deliberada e maligna a autoridades públicas ou instituições (ex: "o governo quer matar a população com isso").
*   **Papel da IA:** Identificar o padrão de linguagem de conspiração, separar o fato narrado da acusação de intenção oculta, e buscar se há evidências documentais anexas que provem a acusação.
*   **Limite:** O limite explícito é que a existência de uma conspiração real não pode ser sumariamente descartada pela IA; a IA marca o texto que faz alegações extraordinárias de intenção oculta sem apresentar provas correspondentes, deixando o julgamento final para o usuário.
*   **Rubrica:**
    *   **Sinal Forte:** Acusação direta de plano maligno/secreto institucional sem apresentação de nenhuma evidência ou fonte documental.
    *   **Sinal Fraco:** Insinuação de que informações cruciais estão a ser ocultadas propositadamente ("o estudo ainda não foi divulgado por eles").
    *   **Sinal Ausente:** A mensagem foca-se apenas no relato dos factos, sem atribuir intenções ocultas ou motivações secretas a terceiros.

---

## Task 4.4 — Registro de Remoções (Variância Zero)
Ao testar os sinais candidatos contra os 6 casos forenses da área da saúde, as seguintes dimensões foram descartadas da versão 1:
1. **Ausência genérica de link/fonte:** Removida por variância zero. 100% dos casos de fabricação e correntes apresentaram falta de links verificáveis, não servindo para discriminar as nuances entre as peças.
2. **Polaridade Emocional / Linguagem Alarmista (ex: "Pede repasse urgente"):** Removida por determinação de arquitetura. O tom técnico e sóbrio também é muito usado em desinformação. Usar a polaridade emocional como detector violaria a Decisão 7 (add-selecao-modelos-arquitetura-rag), pois emoção não é evidência de falsidade.
3. **Tema "Saúde/Medicina":** Removida por variância zero, pois todos os 6 casos pertenciam a este domínio.