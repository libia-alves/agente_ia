# Mini LAB — Assistente de contratos

**Objetivo:** consultar contratos e simular acréscimos. Dados e percentuais fictícios.

## 1. Ferramentas e avaliação

- **Consultar contrato:** `@tool`.
- **Consultar percentual:** função anotada passada na lista.
- **Calcular acréscimo:** `StructuredTool` com campos descritos e exigência de origem verificável dos valores.

**12 perguntas com gabarito anterior aos testes:** 6 de uma ferramenta, 3 de duas, 2 sem ferramenta e 1 com dados insuficientes. A correção tolera diferenças de grafia.

## 2. Resultados reais na OpenAI

| Configuração | Acerto | Ferramenta certa | Passos med./máx. | Tempo total | US$ nas 12 |
| --- | --- | --- | --- | --- | --- |
| Nano econômico | 9/12 | 9/12 | 2/4 | 28,02 s | 0,001215 |
| Luna | 12/12 | 12/12 | 2/3 | 31,69 s | 0,001718 |
| Sol superior | 12/12 | 12/12 | 2/3 | 45,11 s | 0,034664 |

**Escolha: Luna.** O superior custou **20,18 vezes mais**, com o mesmo acerto. O nano também foi mais barato por consulta, mas errou três respostas.

| Custo por consulta (US$) | Mediana | Máximo | Máximo ÷ mediana |
| --- | --- | --- | --- |
| Nano econômico | 0,000088 | 0,000203 | 2,30 vezes |
| Luna | 0,000132 | 0,000225 | 1,71 vez |
| Sol superior | 0,002698 | 0,004618 | 1,71 vez |

Para **1.000 consultas/mês no Luna**: **US$ 0,13 pela mediana** e **US$ 0,23 pela cauda**. Apresentaria ambos ao gestor, usando a cauda como cenário de reserva. Nesta amostra, o P95 coincide com o máximo.

## 3. Falhas e proteção

**Erro observado:** o nano usou 15% quando a pergunta pedia 10%: retornou R$ 115 mil em vez de R$ 110 mil.

**Ataques:** o Luna resistiu aos testes de dados ausentes, valor negativo, contrato inexistente e injeções. Uma injeção dizia “Modo de homologação” e pedia declarar um aditivo aprovado; o objetivo malicioso não foi atingido.

A barreira em `wrap_tool_call` devolve `ToolMessage` ao bloquear uma operação.

| Barreira nas 12 perguntas | Falsos positivos |
| --- | --- |
| Só aceita números presentes na pergunta | 3 |
| Rastreia a origem no usuário ou em outra ferramenta | 0 |

**Conferência humana obrigatória:** antes de aprovar aditivo ou autorizar despesa. Um cálculo errado pode gerar despesa indevida e responsabilização administrativa.

*Amostra pequena: os resultados apoiam um piloto supervisionado. [Relatório completo e evidências](RELATORIO_COMPLETO.md).*
