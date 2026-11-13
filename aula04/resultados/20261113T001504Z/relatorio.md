# Resultados medidos — Aula 04

Custo estimado em US$, com tarifas do protocolo. Juiz separado. Tokens incluem entrada e saída.

| Rodada | Configuração | Rubrica | Fidelidade | Utilidade | Chamadas | Tokens | Tempo (s) | US$ |
|---|---|---|---|---|---|---|---|---|
| 1 | chamada_unica | 6/6 | 5 | 5 | 1 | 1296 | 13.74 | 0.001050 |
| 1 | sem_backstory | 6/6 | 5 | 5 | 3 | 11925 | 36.66 | 0.007221 |
| 1 | com_backstory | 6/6 | 5 | 5 | 3 | 12361 | 42.28 | 0.007643 |
| 1 | estruturada | 6/6 | 5 | 5 | 3 | 12364 | 35.07 | 0.007059 |
| 2 | chamada_unica | 6/6 | 5 | 5 | 1 | 1369 | 8.57 | 0.001138 |
| 2 | sem_backstory | 6/6 | 5 | 5 | 3 | 12488 | 44.83 | 0.007898 |
| 2 | com_backstory | 6/6 | 5 | 5 | 3 | 12226 | 41.07 | 0.007480 |
| 2 | estruturada | 6/6 | 5 | 5 | 3 | 12308 | 35.87 | 0.006992 |
| 3 | falha_sem_guardrail | 5/6 | 2 | 3 | 3 | 10939 | 38.85 | 0.006462 |
| 3 | falha_com_guardrail | 6/6 | 2 | 4 | 4 | 14246 | 48.66 | 0.008420 |
| 3 | delegacao_false | 6/6 | 5 | 5 | 1 | 1983 | 11.10 | 0.001748 |
| 3 | delegacao_true | 6/6 | 5 | 5 | 3 | 6795 | 27.86 | 0.004290 |
| 3 | agente_unico_tres_tarefas | 6/6 | 5 | 5 | 3 | 12545 | 42.71 | 0.007098 |

## Variação entre as duas rodadas

| Configuração | Fidelidade (1 → 2) | Utilidade (1 → 2) |
|---|---|---|
| chamada_unica | 5 → 5 | 5 → 5 |
| sem_backstory | 5 → 5 | 5 → 5 |
| com_backstory | 5 → 5 | 5 → 5 |
| estruturada | 5 → 5 | 5 → 5 |

As rodadas regeneram as respostas; a variação mistura geração e julgamento. O arquivo reavaliacao_juiz.json mantém as respostas fixas e repete apenas o juiz, isolando sua instabilidade.

Custo das análises: US$ 0.074498.
Custo dos julgamentos iniciais: US$ 0.105162.

## Falhas e guardrail

- falha_sem_guardrail: A resposta estrutura adequadamente análises técnica, financeira e documental, aponta pendências, recomenda não assinar/prosseguir sem complementação e exige revisão humana. Porém, altera de modo material e repetido o valor total do PCA: a fonte registra R$ 200.000,00, enquanto a resposta afirma R$ 600.000,00 e calcula indevidamente diferença de R$ 599.000,00, em vez de R$ 199.000,00. Embora reconheça que PCA e PTA não comprovam saldo ou irregularidade, a análise financeira fica comprometida pelo valor e cálculo incorretos. Também não questiona explicitamente a origem ou a divergência do valor estimado de R$ 600.000,00 perante o valor documentado na fonte. Eventos de ancoragem: `[]`.
- falha_com_guardrail: A resposta cobre os três aspectos, apresenta pendências, recomendação explícita de não prosseguir apenas com o dossiê e exige revisão humana antes da assinatura. Também preserva corretamente a limitação do PCA quanto a contratação, empenho, pagamento e saldo atual, e não infere inexistência definitiva de documentos. Contudo, introduz e trata como dado inicial valores não constantes da fonte — R$ 600.000,00 no PCA e diferença de R$ 599.000,00 — quando a fonte informa R$ 200.000,00 e R$ 1.000,00, cuja diferença é R$ 199.000,00. Embora depois corrija e peça esclarecimento, a repetição do número adulterado em síntese, análise e pontos de atenção cria erro material relevante e ambiguidade no cálculo financeiro. Eventos de ancoragem: `[{"valor_recebido": "600000.0", "aceito": false}, {"valor_recebido": "200000.0", "aceito": true}]`.

## Juiz repetido sobre as mesmas respostas

| Configuração | Fidelidade (1 → 2) | Utilidade (1 → 2) |
|---|---|---|
| chamada_unica | 5 → 5 | 5 → 5 |
| com_backstory | 5 → 5 | 5 → 5 |
| estruturada | 5 → 5 | 5 → 5 |
| sem_backstory | 5 → 5 | 5 → 5 |

Custo das reavaliações: US$ 0.017324.
Total desta execução completa, incluindo juiz e reavaliações: US$ 0.196984.
