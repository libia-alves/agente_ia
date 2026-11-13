# Resultados medidos — Aula 04

Custo estimado em US$, com tarifas do protocolo. Juiz separado. Tokens incluem entrada e saída.

| Rodada | Configuração | Rubrica | Fidelidade | Utilidade | Chamadas | Tokens | Tempo (s) | US$ |
|---|---|---|---|---|---|---|---|---|
| 1 | chamada_unica | 6/6 | 5 | 5 | 1 | 1294 | 7.57 | 0.001053 |
| 1 | sem_backstory | 6/6 | 5 | 5 | 3 | 11902 | 38.12 | 0.007236 |
| 1 | com_backstory | 6/6 | 4 | 5 | 3 | 11838 | 36.73 | 0.007082 |
| 1 | estruturada | 6/6 | 4 | 5 | 3 | 12168 | 37.49 | 0.006889 |
| 2 | chamada_unica | 6/6 | 5 | 5 | 1 | 1195 | 6.59 | 0.000934 |
| 2 | sem_backstory | 6/6 | 4 | 5 | 3 | 11669 | 37.08 | 0.007033 |
| 2 | com_backstory | 6/6 | 4 | 5 | 3 | 11944 | 39.71 | 0.007223 |
| 2 | estruturada | 6/6 | 4 | 5 | 3 | 12098 | 35.32 | 0.006805 |
| 3 | falha_sem_guardrail | 5/6 | 2 | 3 | 3 | 10251 | 35.94 | 0.006083 |
| 3 | falha_com_guardrail | 6/6 | 5 | 5 | 4 | 11463 | 35.23 | 0.006419 |
| 3 | delegacao_false | 6/6 | 5 | 5 | 1 | 1521 | 7.67 | 0.001205 |
| 3 | delegacao_true | 6/6 | 5 | 5 | 3 | 5924 | 24.48 | 0.003622 |
| 3 | agente_unico_tres_tarefas | 6/6 | 4 | 5 | 3 | 10374 | 29.78 | 0.005794 |

## Variação entre as duas rodadas

| Configuração | Fidelidade (1 → 2) | Utilidade (1 → 2) |
|---|---|---|
| chamada_unica | 5 → 5 | 5 → 5 |
| sem_backstory | 5 → 4 | 5 → 5 |
| com_backstory | 4 → 4 | 5 → 5 |
| estruturada | 4 → 4 | 5 → 5 |

As rodadas regeneram as respostas; a variação mistura geração e julgamento. O arquivo reavaliacao_juiz.json mantém as respostas fixas e repete apenas o juiz, isolando sua instabilidade.

Custo das análises: US$ 0.067376.
Custo dos julgamentos iniciais: US$ 0.084206.

## Falhas e guardrail

- falha_sem_guardrail: A resposta preserva adequadamente as limitações do recorte documental, evita afirmar ausência de ETP ou parecer jurídico e traz recomendações técnicas, financeiras e documentais em geral acionáveis. Contudo, altera de forma material o valor estimado documentado: a fonte informa R$ 541.080,47, enquanto a resposta adota repetidamente R$ 941.080,47. Isso compromete a análise financeira, os pontos de atenção e a recomendação de revisão. Embora questione corretamente a divergência entre a URL e a identificação do pregão, não questiona nem pede confirmação da origem da divergência numérica do valor estimado; ao contrário, trata o valor adulterado como referência para validação e revisão. Eventos de ancoragem: `[]`.
- falha_com_guardrail: A resposta preserva corretamente o valor estimado de R$ 541.080,47 e sua natureza não executada, distingue estimativa de dotação, empenho ou pagamento, e não conclui sobre suficiência orçamentária, aptidão técnica ou regularidade jurídica com base no resumo. Também trata as lacunas como limites da fonte, não como irregularidades. Entrega os três aspectos solicitados, pendências, recomendação explícita e revisão humana. As verificações adicionais sugeridas são apresentadas como pontos a confirmar, sem serem afirmadas como fatos ausentes no processo. Eventos de ancoragem: `[{"valor_recebido": "941080.47", "aceito": false}, {"valor_recebido": "541080.47", "aceito": true}]`.

## Juiz repetido sobre as mesmas respostas

| Configuração | Fidelidade (1 → 2) | Utilidade (1 → 2) |
|---|---|---|
| chamada_unica | 5 → 5 | 5 → 5 |
| com_backstory | 4 → 5 | 5 → 5 |
| estruturada | 4 → 4 | 5 → 5 |
| sem_backstory | 5 → 5 | 5 → 5 |

Custo das reavaliações: US$ 0.017212.
Total desta execução completa, incluindo juiz e reavaliações: US$ 0.168794.

## Análise — itens 13 a 15

Nas duas rodadas, a chamada única e as equipes cobriram 6/6; todas tiveram utilidade 5, sem vantagem de qualidade demonstrada pela equipe.  
A chamada única custou em média US$ 0,000993 e levou 7,08 s; a equipe estruturada custou US$ 0,006847 e levou 36,41 s: cerca de 6,9 vezes o custo e 5,1 vezes o tempo.  
A equipe oferece etapas separadas e um ponto de validação estruturada, mas esses recursos também podem ser implementados com um único agente; não justificam, por si, três agentes.  
Entre os elementos adicionados à definição, o esquema de saída teve o efeito mais concreto: campos tipados e custo médio 4,3% menor que a equipe com biografia, embora os tokens totais tenham aumentado 2,0%.  
Esse efeito foi pequeno e não reproduziu a forte economia da Seção 5.2; a biografia também não elevou a utilidade neste caso, que já estava no teto da escala.  
Com o mesmo texto, a fidelidade da equipe com biografia mudou de 4 para 5 na reavaliação; diferenças de um ponto não sustentam um ranking, e duas rodadas não permitem generalização.  
O erro de R$ 941.080,47 atravessou a cadeia sem questionamento da estimativa; o guardrail rejeitou esse valor e aceitou R$ 541.080,47, com quatro chamadas em vez de três.  
Antes da assinatura, a conferência humana deve obrigatoriamente confrontar estimativa, dotação, requisitos técnicos e instrução com os documentos originais; neste recorte, a chamada única é a opção de menor custo sem perda de utilidade observada.  

## Desafio opcional

Um único agente nas três tarefas obteve 6/6, fidelidade 4 e utilidade 5, com três chamadas, 10.374 tokens, 29,78 s e US$ 0,005794. Ficou próximo da equipe estruturada em qualidade, com menor consumo nesta única medição. Isso sugere que o encadeamento pesa mais que a separação de identidades, mas o perfil combinado é uma variável adicional e o ensaio não foi repetido.

## Histórico e custos

A tentativa preliminar 20261112T233206Z parou por incompatibilidade do esquema Decimal. Suas três medições concluídas somam US$ 0.014985 de produção e US$ 0.020746 de juiz. O consumo da configuração interrompida não foi recuperado; portanto, o total do relatório é somente da execução completa, não o gasto integral da sessão. A correção de esquema precedeu o reinício integral com o mesmo dossiê e rubrica.
