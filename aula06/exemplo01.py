# ============================================================
# Aula 06 – Introdução ao Agno
# Módulo: Agentes Autônomos | Curso: Formação em IA – UNEMAT/RISC
# Exemplo 01: O assistente de atendimento e o registro de cada resposta
# Seção 4 – Agentes no Agno
# Requisitos: pip install agno openai python-dotenv
# ============================================================
"""Monta o assistente de atendimento da SECITECI e responde a quatro perguntas.

As perguntas são as que chegam ao balcão em um dia comum: a situação de um
protocolo, um prazo que depende da última movimentação, o prazo legal de um
pedido de acesso à informação e o valor atualizado de uma bolsa a devolver.
Para cada uma, o exemplo imprime a resposta, as ferramentas que o agente
consultou com os argumentos usados e o consumo da execução, que é o que o
setor precisa registrar para saber em que se baseou cada resposta.
"""
import pathlib
import warnings

warnings.filterwarnings("ignore")

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

from ferramentas_comuns import FUNCOES, INSTRUCAO

BASE = pathlib.Path(__file__).parent
load_dotenv(BASE.parents[2] / ".env")

MODELO = "gpt-5.6-luna"
PRECO_ENTRADA, PRECO_SAIDA = 0.20, 1.20  # US$ por milhão de tokens

PERGUNTAS = [
    ("bolsista",
     "Meu pedido de prorrogação de bolsa, protocolo 2026005678, já foi analisado?"),
    ("pesquisador",
     "Qual a situação do protocolo 2026009012? Se eu tiver 15 dias úteis a partir da "
     "última movimentação para entregar os documentos, até quando posso entregar?"),
    ("cidadão",
     "Fiz um pedido de acesso à informação em 2026-09-01. Qual o prazo legal de "
     "resposta e em que data ele vence, em dias corridos?"),
    ("ex-bolsista",
     "Preciso devolver R$ 4.800,00 de bolsa não utilizada, com 5 meses de atraso. "
     "Quanto devo pagar com a atualização?"),
]


def construir_agente() -> Agent:
    """Monta o agente uma vez; ele atende todas as perguntas da fila."""
    return Agent(
        # `reasoning_effort="none"` não é preferência: com ferramentas declaradas,
        # a família GPT-5.6 recusa o endpoint de Chat Completions se o raciocínio
        # estiver ativo, conforme a Aula 03, Seção 3.2.
        model=OpenAIChat(id=MODELO, reasoning_effort="none"),
        tools=FUNCOES,
        instructions=INSTRUCAO,
        markdown=False,
        # Teto de chamadas de ferramenta por execução: uma pergunta mal
        # formulada não pode prender o agente em consultas sem fim.
        tool_call_limit=6,
        # Desliga o envio de dados de uso ao fornecedor do Agno (Seção 5.4).
        telemetry=False,
    )


def main() -> None:
    agente = construir_agente()
    custo_total = 0.0

    for perfil, pergunta in PERGUNTAS:
        resposta = agente.run(pergunta)

        print("=" * 76)
        print(f"[{perfil}] {pergunta}")
        print("-" * 76)
        print(str(resposta.content).strip())
        print()
        # `resposta.tools` lista as ferramentas efetivamente chamadas, com os
        # argumentos que o modelo preencheu. É a fundamentação da resposta.
        for chamada in (resposta.tools or []):
            print(f"  consultou: {chamada.tool_name}({chamada.tool_args})")
        if not resposta.tools:
            print("  consultou: nenhuma ferramenta")

        # `resposta.metrics` soma todas as chamadas ao modelo feitas na execução;
        # cada mensagem do assistente traz a parcela da própria chamada.
        por_chamada = [msg.metrics.input_tokens for msg in (resposta.messages or [])
                       if msg.role == "assistant" and msg.metrics]
        m = resposta.metrics
        custo = m.input_tokens / 1e6 * PRECO_ENTRADA + m.output_tokens / 1e6 * PRECO_SAIDA
        custo_total += custo
        print(f"  chamadas ao modelo: {len(por_chamada)}  ·  entrada por chamada: "
              f"{' + '.join(map(str, por_chamada))} = {m.input_tokens} tokens")
        print(f"  saída: {m.output_tokens} tokens  ·  custo: US$ {custo:.5f}")

    print("=" * 76)
    print(f"Custo das {len(PERGUNTAS)} respostas: US$ {custo_total:.5f}")
    print(f"Custo médio por resposta: US$ {custo_total / len(PERGUNTAS):.5f}")


if __name__ == "__main__":
    main()
