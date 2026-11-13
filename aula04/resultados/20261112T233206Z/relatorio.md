# Resultados medidos — Aula 04

Custo estimado em US$, com tarifas do protocolo. Juiz separado. Tokens incluem entrada e saída.

| Rodada | Configuração | Rubrica | Fidelidade | Utilidade | Chamadas | Tokens | Tempo (s) | US$ |
|---|---|---|---|---|---|---|---|---|
| 1 | chamada_unica | 6/6 | 5 | 5 | 1 | 1221 | 6.96 | 0.000965 |
| 1 | com_backstory | 6/6 | 4 | 5 | 3 | 11903 | 37.76 | 0.007178 |
| 1 | sem_backstory | 6/6 | 4 | 5 | 3 | 11392 | 36.52 | 0.006842 |

## Variação entre as duas rodadas

| Configuração | Fidelidade (1 → 2) | Utilidade (1 → 2) |
|---|---|---|

As rodadas regeneram as respostas; a variação mistura geração e julgamento. O arquivo reavaliacao_juiz.json mantém as respostas fixas e repete apenas o juiz, isolando sua instabilidade.

Custo das análises: US$ 0.014985.
Custo dos julgamentos iniciais: US$ 0.020746.

## Falhas e guardrail

