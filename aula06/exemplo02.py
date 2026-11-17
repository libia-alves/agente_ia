# ============================================================
# Aula 06 – Introdução ao Agno
# Módulo: Agentes Autônomos | Curso: Formação em IA – UNEMAT/RISC
# Exemplo 02: Consultas encadeadas e a ordem das ferramentas
# Seção 4.3 – Consultas encadeadas no Agno
# Requisitos: pip install agno openai python-dotenv
# ============================================================
"""Verifica se o agente espera o resultado de uma ferramenta antes de calcular.

Algumas perguntas do atendimento exigem duas consultas em sequência: primeiro
o sistema de protocolo, que informa a data da última movimentação, e depois o
cálculo do prazo, que precisa dessa data. O modelo pode pedir as duas
ferramentas na mesma chamada, e nesse caso o cálculo parte de uma data que ele
ainda não conhece.

O exemplo faz duas perguntas desse tipo, três vezes cada, em três
configurações do agente, e confere em cada execução se a data entregue ao
cálculo é a do protocolo e se a resposta traz o vencimento correto.
"""
import pathlib
import warnings

warnings.filterwarnings("ignore")

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run.base import RunStatus
from dotenv import load_dotenv

from ferramentas_comuns import FUNCOES, INSTRUCAO

BASE = pathlib.Path(__file__).parent
load_dotenv(BASE.parents[2] / ".env")

MODELO = "gpt-5.6-luna"
REPETICOES = 3

# Cada pergunta traz a data que deveria chegar ao cálculo e o vencimento certo,
# nos dois formatos em que a resposta pode escrevê-lo.
PERGUNTAS = [
    {"rotulo": "P1",
     "texto": ("Qual a situação do protocolo 2026009012? Se eu tiver 15 dias úteis a partir "
               "da última movimentação para entregar os documentos, até quando posso entregar?"),
     "data_protocolo": "2026-07-21", "vencimento": ("2026-08-11", "11/08/2026")},
    {"rotulo": "P2",
     "texto": ("O protocolo 2026001234 tem prazo de resposta de 20 dias corridos, contados "
               "da última movimentação. Em que data esse prazo vence?"),
     "data_protocolo": "2026-03-14", "vencimento": ("2026-04-03", "03/04/2026")},
]

REGRA_DE_ORDEM = (" Quando um cálculo depender de um dado que outra ferramenta fornece, "
                  "consulte primeiro essa ferramenta e só faça o cálculo depois de receber "
                  "o resultado.")

CONFIGURACOES = [
    ("instrução original", INSTRUCAO, None),
    ("instrução com regra de ordem", INSTRUCAO + REGRA_DE_ORDEM, None),
    ("chamadas paralelas desligadas", INSTRUCAO, {"parallel_tool_calls": False}),
]


def construir(instrucao: str, parametros: dict | None) -> Agent:
    # `request_params` repassa parâmetros diretamente à API da OpenAI. O
    # `parallel_tool_calls=False` impede o modelo de pedir mais de uma
    # ferramenta na mesma resposta.
    return Agent(model=OpenAIChat(id=MODELO, reasoning_effort="none",
                                  request_params=parametros),
                 tools=FUNCOES, instructions=instrucao, markdown=False,
                 tool_call_limit=6, telemetry=False)


def examinar(resposta, pergunta: dict) -> tuple[int, str, bool]:
    """Devolve o maior número de ferramentas pedidas em uma única chamada ao
    modelo, a data entregue ao cálculo e se a resposta traz o vencimento certo."""
    simultaneas = max((len(m.tool_calls or []) for m in (resposta.messages or [])
                       if m.role == "assistant"), default=0)
    datas = [str(t.tool_args.get("data_inicial", "")) for t in (resposta.tools or [])
             if t.tool_name == "calcular_prazo"]
    data_usada = datas[0] if datas else "(sem cálculo)"
    correta = any(v in str(resposta.content) for v in pergunta["vencimento"])
    return simultaneas, data_usada, correta


def main() -> None:
    print(f"{'configuração':31} {'perg.':>5} {'simult.':>8} {'data no cálculo':>16} "
          f"{'vencimento':>11}")
    print("-" * 76)
    resumo = {}
    for nome, instrucao, parametros in CONFIGURACOES:
        data_certa = resposta_certa = 0
        for pergunta in PERGUNTAS:
            for _ in range(REPETICOES):
                resposta = construir(instrucao, parametros).run(pergunta["texto"])
                if resposta.status == RunStatus.error:
                    # Falha de rede ou da API: o Agno devolve o erro como conteúdo
                    # (Seção 5.3), e a execução não entra na contagem.
                    print(f"{nome:31} {pergunta['rotulo']:>5} {'erro da API, execução descartada':>38}")
                    continue
                simultaneas, data_usada, correta = examinar(resposta, pergunta)
                data_certa += data_usada == pergunta["data_protocolo"]
                resposta_certa += correta
                print(f"{nome:31} {pergunta['rotulo']:>5} {simultaneas:>8} "
                      f"{data_usada or '(vazia)':>16} {'certo' if correta else 'errado':>11}")
        resumo[nome] = (data_certa, resposta_certa)
        print()

    total = len(PERGUNTAS) * REPETICOES
    print("Resumo")
    for nome, (data_certa, resposta_certa) in resumo.items():
        print(f"  {nome:31} data do protocolo no cálculo {data_certa}/{total}"
              f" · vencimento correto {resposta_certa}/{total}")


if __name__ == "__main__":
    main()
