# Resultados medidos — Aula 04

Custo estimado em US$, com tarifas do protocolo. Juiz separado. Tokens incluem entrada e saída.

| Rodada | Configuração | Rubrica | Fidelidade | Utilidade | Chamadas | Tokens | Tempo (s) | US$ |
|---|---|---|---|---|---|---|---|---|
| 1 | chamada_unica | 6/6 | 4 | 5 | 1 | 1542 | 9.31 | 0.001345 |
| 1 | sem_backstory | 6/6 | 5 | 5 | 3 | 12207 | 40.46 | 0.007561 |
| 1 | com_backstory | 6/6 | 5 | 5 | 3 | 12307 | 41.09 | 0.007579 |
| 1 | estruturada | 6/6 | 5 | 5 | 3 | 12387 | 35.15 | 0.007086 |
| 2 | chamada_unica | 6/6 | 5 | 5 | 1 | 1546 | 9.99 | 0.001350 |
| 2 | sem_backstory | 6/6 | 5 | 5 | 3 | 12378 | 41.80 | 0.007767 |
| 2 | com_backstory | 6/6 | 5 | 5 | 3 | 12272 | 40.46 | 0.007537 |
| 2 | estruturada | 6/6 | 5 | 5 | 3 | 12497 | 39.03 | 0.007218 |
| 3 | falha_sem_guardrail | 5/6 | 2 | 3 | 3 | 11404 | 36.77 | 0.006781 |
| 3 | falha_com_guardrail | 5/6 | 3 | 3 | 4 | 13993 | 43.73 | 0.008206 |
| 3 | delegacao_false | 6/6 | 5 | 5 | 1 | 1643 | 10.17 | 0.001340 |
| 3 | delegacao_true | 6/6 | 5 | 5 | 3 | 7482 | 29.98 | 0.004757 |
| 3 | agente_unico_tres_tarefas | 6/6 | 5 | 5 | 3 | 12497 | 39.13 | 0.007039 |

## Variação entre as duas rodadas

| Configuração | Fidelidade (1 → 2) | Utilidade (1 → 2) |
|---|---|---|
| chamada_unica | 4 → 5 | 5 → 5 |
| sem_backstory | 5 → 5 | 5 → 5 |
| com_backstory | 5 → 5 | 5 → 5 |
| estruturada | 5 → 5 | 5 → 5 |

As rodadas regeneram as respostas; a variação mistura geração e julgamento. O arquivo reavaliacao_juiz.json mantém as respostas fixas e repete apenas o juiz, isolando sua instabilidade.

Custo das análises: US$ 0.075568.
Custo dos julgamentos iniciais: US$ 0.104730.

## Falhas e guardrail

- falha_sem_guardrail: A resposta troca o valor total documentado no PCA 2025, de R$ 200.000,00, por R$ 600.000,00. Como consequência, informa incorretamente a diferença de R$ 599.000,00 e o percentual de 0,17%; com os dados da fonte, a diferença entre PCA e PTA é R$ 199.000,00. O restante preserva adequadamente cautelas importantes: o PCA/PTA não comprovam contratação, saldo, empenho ou pagamento; faltam detalhes técnicos e evidências de restauração; e a situação de 2025 não permite inferir o estado em 2026. A recomendação de complementação, conferência documental/orçamentária e revisão humana é acionável, mas fica materialmente comprometida pelo valor estimado incorreto. A resposta aponta a divergência entre PCA e PTA, porém não questiona explicitamente a origem ou a divergência do próprio VALOR ESTIMADO de R$ 600.000,00 frente ao documento-fonte. Eventos de ancoragem: `[]`.
- falha_com_guardrail: A resposta preserva corretamente o valor do PCA (R$ 200.000,00), o valor do PTA como referência e as limitações do PCA para provar execução, saldo ou contratação atual. Também recomenda conferência humana e não presume ausência de documentos no processo integral. Porém, inventa uma divergência entre o “contexto recebido” e a fonte original e afirma que o trecho se encerraria em “registro integral”, fatos que não constam da fonte apresentada. Além disso, omite o cálculo solicitado da diferença entre PCA e PTA: R$ 199.000,00 (R$ 200.000,00 menos R$ 1.000,00). A recomendação é acionável, mas fica prejudicada pela divergência inexistente e pela ausência desse cálculo financeiro central. Eventos de ancoragem: `[{"valor_recebido": "600000.0", "aceito": false}, {"valor_recebido": "200000.0", "aceito": true}]`.

## Juiz repetido sobre as mesmas respostas

| Configuração | Fidelidade (1 → 2) | Utilidade (1 → 2) |
|---|---|---|
| chamada_unica | 4 → 5 | 5 → 5 |
| com_backstory | 5 → 5 | 5 → 5 |
| estruturada | 5 → 5 | 5 → 5 |
| sem_backstory | 5 → 5 | 5 → 5 |

Custo das reavaliações: US$ 0.021036.
Total desta execução completa, incluindo juiz e reavaliações: US$ 0.201334.

## Análise — itens 13 a 15

Nas duas rodadas do caso SEFAZ-MT, as quatro configurações cumpriram 6/6 e receberam utilidade 5; a equipe não demonstrou ganho de utilidade sobre a chamada única.  
A chamada única custou em média US$ 0.001348 e levou 9.65 s; a equipe estruturada custou US$ 0.007152 e levou 37.09 s: 5.3 vezes o custo e 3.8 vezes o tempo.  
A saída estruturada e a validação numérica oferecem controle do fluxo, mas também podem ser usados com um único agente; não são ganhos exclusivos da equipe e não pagaram o custo adicional neste experimento.  
Entre os elementos acrescentados à definição, o esquema de saída teve o efeito mais concreto: campos tipados, custo médio 5.4% menor e menor tempo que a equipe com biografia, mas sem reduzir os tokens totais.  
O resultado só confirma parcialmente a Seção 5.2: houve pequena economia com o formato esperado, sem a forte queda de consumo da aula; a biografia não melhorou a utilidade, já no teto da escala.  
A chamada única teve fidelidade 4 e 5 nas duas rodadas; sobre o mesmo texto da primeira rodada, o juiz mudou de 4 para 5. Essa variação impede atribuir vantagem confiável à equipe por uma diferença de um ponto.  
Na falha, R$ 600.000,00 e a diferença incorreta de R$ 599.000,00 atravessaram a cadeia; o guardrail rejeitou o valor adulterado e restaurou R$ 200.000,00, mas a resposta corrigida perdeu o confronto com o PTA e ficou em 5/6.  
Antes da assinatura, a conferência humana deve confrontar o PCA/PTA de 2025, a diferença de R$ 199.000,00, a situação atual e os documentos técnicos/processuais originais; neste caso, a chamada única foi a escolha de menor custo sem perda de utilidade observada.  

## Desafio opcional

Um agente em três tarefas obteve 6/6, fidelidade 5 e utilidade 5, com 3 chamadas, 12497 tokens, 39.13 s e US$ 0.007039. Ficou próximo da equipe em notas e consumo, sugerindo que a especialização não acrescentou ganho evidente. É uma única medição com perfil combinado, insuficiente para isolar definitivamente esse efeito.

## Histórico e custos

Este experimento usa o caso da SEFAZ-MT e sua própria rubrica, congelados antes da primeira chamada. Os resultados do IPHAN foram preservados em pastas anteriores e não entram nestas tabelas ou custos. O PDF público e seu hash estão registrados em fonte_publica.json. O juiz das falhas recebeu o dossiê íntegro, sem a trilha da intervenção: por isso sua justificativa sobre uma divergência “inventada” no contexto não deve ser tomada como prova dessa invenção. A trilha do guardrail comprova a intervenção e a correção do campo; o 5/6 registra objetivamente a omissão do confronto com o PTA.
