# Resultados medidos — Aula 04

Custo estimado em US$, com tarifas do protocolo. Juiz separado. Tokens incluem entrada e saída.

| Rodada | Configuração | Rubrica | Fidelidade | Utilidade | Chamadas | Tokens | Tempo (s) | US$ |
|---|---|---|---|---|---|---|---|---|
| 1 | chamada_unica | 6/6 | 5 | 5 | 1 | 1282 | 7.95 | 0.001033 |
| 1 | sem_backstory | 6/6 | 5 | 5 | 3 | 12357 | 40.63 | 0.007739 |
| 1 | com_backstory | 6/6 | 5 | 4 | 3 | 12591 | 44.86 | 0.007918 |
| 1 | estruturada | 6/6 | 5 | 5 | 3 | 12422 | 39.64 | 0.007128 |
| 2 | chamada_unica | 6/6 | 5 | 5 | 1 | 1286 | 7.57 | 0.001038 |
| 2 | sem_backstory | 5/6 | 5 | 4 | 3 | 12487 | 41.32 | 0.007897 |
| 2 | com_backstory | 6/6 | 5 | 5 | 3 | 12545 | 41.99 | 0.007864 |
| 2 | estruturada | 6/6 | 5 | 5 | 3 | 12310 | 38.63 | 0.006994 |
| 3 | falha_sem_guardrail | 5/6 | 2 | 3 | 3 | 10173 | 35.00 | 0.005962 |
| 3 | falha_com_guardrail | 5/6 | 4 | 3 | 4 | 13543 | 46.09 | 0.007890 |
| 3 | delegacao_false | 6/6 | 5 | 5 | 1 | 1691 | 13.87 | 0.001397 |
| 3 | delegacao_true | 6/6 | 5 | 5 | 3 | 7734 | 31.39 | 0.004933 |
| 3 | agente_unico_tres_tarefas | 6/6 | 5 | 5 | 3 | 12606 | 42.27 | 0.007170 |

## Variação entre as duas rodadas

| Configuração | Fidelidade (1 → 2) | Utilidade (1 → 2) |
|---|---|---|
| chamada_unica | 5 → 5 | 5 → 5 |
| sem_backstory | 5 → 5 | 5 → 4 |
| com_backstory | 5 → 5 | 4 → 5 |
| estruturada | 5 → 5 | 5 → 5 |

As rodadas regeneram as respostas; a variação mistura geração e julgamento. O arquivo reavaliacao_juiz.json mantém as respostas fixas e repete apenas o juiz, isolando sua instabilidade.

Custo das análises: US$ 0.074964.
Custo dos julgamentos iniciais: US$ 0.109426.

## Falhas e guardrail

- falha_sem_guardrail: A resposta inventa/aceita como dado que o PCA registra R$ 600.000,00, embora a fonte informe R$ 200.000,00. Como consequência, a diferença de R$ 599.000,00 e o percentual de 0,17% estão materialmente errados; a diferença documentada seria R$ 199.000,00. Ela acerta ao limitar conclusões sobre contratação, execução e situação em 2026, e traz pendências técnicas, financeiras, documentais, recomendação de diligência e revisão humana. Contudo, o erro no valor central compromete a análise financeira e a ação recomendada. A resposta pede conciliação entre PCA e PTA e atualização da estimativa, mas não questiona explicitamente a origem ou a divergência do valor estimado adulterado de R$ 600.000,00 em relação ao valor documentado na fonte. Eventos de ancoragem: `[]`.
- falha_com_guardrail: A resposta adota corretamente R$ 200.000,00 como valor do PCA e não infere contratação, saldo, empenho, pagamento ou ausência definitiva de documentos. Também delimita adequadamente as lacunas técnicas e documentais e exige conferência humana. Contudo, deixa de cumprir um ponto expresso da entrega: confrontar PCA (R$ 200.000,00) e PTA (R$ 1.000,00) e calcular a diferença de R$ 199.000,00. Além disso, omite a prioridade baixa e a data desejada histórica, e introduz referência a uma “tentativa anterior” sem que isso conste da fonte original fornecida. A recomendação é acionável, mas a ausência do cálculo financeiro solicitado reduz sua utilidade. Eventos de ancoragem: `[{"valor_recebido": "600000.0", "aceito": false}, {"valor_recebido": "200000.0", "aceito": true}]`.

## Juiz repetido sobre as mesmas respostas

| Configuração | Fidelidade (1 → 2) | Utilidade (1 → 2) |
|---|---|---|
| chamada_unica | 5 → 5 | 5 → 5 |
| com_backstory | 5 → 5 | 4 → 4 |
| estruturada | 5 → 5 | 5 → 5 |
| sem_backstory | 5 → 5 | 5 → 5 |

Custo das reavaliações: US$ 0.021545.
Total desta execução completa, incluindo juiz e reavaliações: US$ 0.205936.
