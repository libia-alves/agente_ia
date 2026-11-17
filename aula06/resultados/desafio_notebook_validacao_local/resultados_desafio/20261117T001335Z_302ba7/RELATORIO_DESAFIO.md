# Aula 06 — Desafio opcional

Setor: TI da SEFAZ-MT. Dados e prazos fictícios.
Ambiente: Validação local. Modelo: gpt-4o-mini.

| Framework | Pergunta | Status | Ferramentas | Retornos observados | Tempo (s) |
|---|---|---|---|---:|---:|
| langchain | Q01 | concluido | consultar_chamado | 1 | 2.56 |
| langchain | Q02 | concluido | consultar_chamado | 1 | 2.453 |
| langchain | Q03 | concluido | consultar_servico | 1 | 2.145 |
| langchain | Q04 | concluido | consultar_servico | 1 | 2.856 |
| langchain | Q05 | concluido | consultar_servico | 1 | 1.842 |
| langchain | Q06 | concluido | consultar_canal | 1 | 1.943 |
| langchain | Q07 | concluido | consultar_chamado, calcular_prazo | 2 | 3.366 |
| langchain | Q08 | concluido | consultar_chamado | 1 | 1.805 |
| crewai | Q01 | concluido | consultar_chamado | 1 | 1.968 |
| crewai | Q02 | concluido | consultar_chamado | 1 | 1.899 |
| crewai | Q03 | concluido | consultar_servico | 1 | 1.74 |
| crewai | Q04 | concluido | consultar_servico | 1 | 2.005 |
| crewai | Q05 | concluido | consultar_servico | 1 | 1.886 |
| crewai | Q06 | concluido | consultar_canal | 1 | 1.528 |
| crewai | Q07 | concluido | consultar_chamado, calcular_prazo | 2 | 2.755 |
| crewai | Q08 | concluido | consultar_chamado | 1 | 1.381 |

## Onde se encontra o registro

- LangChain: `resultado["messages"]`, pedidos em `AIMessage.tool_calls`, retornos em `ToolMessage`.
- CrewAI: `resultado.tasks_output[i].messages`, pedidos em `assistant.tool_calls`, retornos em `role=tool`.
- Funções de gravação: `gravar_registro_langchain` e `gravar_registro_crewai`, em `desafio_frameworks.py`.

## Consulta encadeada

[
  {
    "framework": "langchain",
    "datas_entregues_ao_calculo": [
      "2026-11-13"
    ],
    "data_correta": true,
    "consulta_antes_do_calculo_no_registro": true
  },
  {
    "framework": "crewai",
    "datas_entregues_ao_calculo": [
      "2026-11-13"
    ],
    "data_correta": true,
    "consulta_antes_do_calculo_no_registro": true
  }
]

## Minha análise

[Preencha após ler as respostas: houve consulta correta às fontes? O que variou entre os frameworks?]
