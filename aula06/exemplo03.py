# ============================================================
# Aula 06 – Introdução ao Agno
# Módulo: Agentes Autônomos | Curso: Formação em IA – UNEMAT/RISC
# Exemplo 03: As mesmas ferramentas em LangChain, CrewAI e Agno
# Seção 4.4 – Portabilidade das ferramentas
# Requisitos: pip install agno langchain langchain-openai crewai openai python-dotenv
# ============================================================
"""Entrega as mesmas quatro ferramentas do atendimento a três frameworks.

As funções de `ferramentas_comuns.py` não importam framework algum, e por
isso o LangChain, o CrewAI e o Agno as recebem sem adaptação. O exemplo
resolve as quinze perguntas de `consultas.json` com cada um deles, usando o
mesmo modelo e a mesma instrução, e confere se as respostas continuam
corretas e se o resultado informa quais ferramentas foram consultadas.
"""
import json
import pathlib
import re
import statistics
import time
import warnings

warnings.filterwarnings("ignore")

from dotenv import load_dotenv

from ferramentas_comuns import FUNCOES, INSTRUCAO

BASE = pathlib.Path(__file__).parent
load_dotenv(BASE.parents[2] / ".env")

MODELO = "gpt-5.6-luna"
USD_ENTRADA, USD_SAIDA = 0.20, 1.20

EXTENSO = {"dez": "10", "quinze": "15", "vinte": "20", "trinta": "30"}


def normalizar(texto: str) -> str:
    """Aproxima grafias equivalentes, conforme a Aula 03, Seção 5.2."""
    t = str(texto).lower().replace("**", "").replace(".", "").replace(",", "")
    for palavra, algarismo in EXTENSO.items():
        t = t.replace(palavra, algarismo)
    return re.sub(r"\b(\d{2})/(\d{2})/(\d{4})\b", r"\3-\2-\1", t)


def acertou(resposta: str, consulta: dict) -> bool:
    texto = normalizar(resposta)
    return all(normalizar(a) in texto for a in consulta["deve_conter"])


# ---------------------------------------------------------------
# LangChain
# ---------------------------------------------------------------
def rodar_langchain(consulta: dict) -> dict:
    from langchain.agents import create_agent
    from langchain.agents.middleware import wrap_model_call
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI

    estado = {"passos": 0, "entrada": 0, "saida": 0}

    @wrap_model_call
    def contar(request, handler):
        estado["passos"] += 1
        resposta = handler(request)
        msg = getattr(resposta, "result", None) or getattr(resposta, "message", None)
        if isinstance(msg, list) and msg:
            msg = msg[0]
        uso = getattr(msg, "usage_metadata", None) or {}
        estado["entrada"] += uso.get("input_tokens", 0)
        estado["saida"] += uso.get("output_tokens", 0)
        return resposta

    inicio = time.perf_counter()
    agente = create_agent(model=ChatOpenAI(model=MODELO, reasoning_effort="none"),
                          tools=[tool(f) for f in FUNCOES],
                          system_prompt=INSTRUCAO, middleware=[contar])
    instanciacao = time.perf_counter() - inicio

    inicio = time.perf_counter()
    saida = agente.invoke({"messages": [{"role": "user", "content": consulta["pergunta"]}]})
    final = saida["messages"][-1].content
    usadas = [m.name for m in saida["messages"] if getattr(m, "type", "") == "tool"]
    return montar(final, usadas, estado["passos"], estado["entrada"], estado["saida"],
                  time.perf_counter() - inicio, instanciacao, consulta)


# ---------------------------------------------------------------
# CrewAI
# ---------------------------------------------------------------
def rodar_crewai(consulta: dict) -> dict:
    from crewai import Agent, Crew, LLM, Process, Task
    from crewai.tools import tool as crew_tool

    ferramentas = [crew_tool(f.__name__)(f) for f in FUNCOES]

    inicio = time.perf_counter()
    agente = Agent(role="Assistente de Atendimento",
                   goal="Responder consultas de servidores e cidadãos",
                   backstory=INSTRUCAO,
                   llm=LLM(model=f"openai/{MODELO}", reasoning_effort="none"),
                   tools=ferramentas, verbose=False, max_iter=6,
                   allow_delegation=False)
    instanciacao = time.perf_counter() - inicio

    tarefa = Task(description=consulta["pergunta"],
                  expected_output="Resposta objetiva, fundamentada nas ferramentas.",
                  agent=agente)
    inicio = time.perf_counter()
    resultado = Crew(agents=[agente], tasks=[tarefa],
                     process=Process.sequential, verbose=False).kickoff()
    uso = resultado.token_usage
    # O CrewAI registra a conversa de cada tarefa em `tasks_output[i].messages`,
    # e as chamadas de ferramenta aparecem nas mensagens do assistente, no
    # campo `tool_calls`, no mesmo formato da API da OpenAI.
    usadas = [chamada["function"]["name"]
              for saida in resultado.tasks_output
              for mensagem in (saida.messages or [])
              for chamada in (mensagem.get("tool_calls") or [])]
    return montar(str(resultado), usadas, uso.successful_requests, uso.prompt_tokens,
                  uso.completion_tokens, time.perf_counter() - inicio,
                  instanciacao, consulta)


# ---------------------------------------------------------------
# Agno
# ---------------------------------------------------------------
def rodar_agno(consulta: dict) -> dict:
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat

    inicio = time.perf_counter()
    agente = Agent(model=OpenAIChat(id=MODELO, reasoning_effort="none"),
                   tools=FUNCOES, instructions=INSTRUCAO, markdown=False,
                   tool_call_limit=6)
    instanciacao = time.perf_counter() - inicio

    inicio = time.perf_counter()
    resposta = agente.run(consulta["pergunta"])
    metricas = resposta.metrics
    usadas = [t.tool_name for t in (resposta.tools or [])]
    passos = sum(1 for m in (resposta.messages or []) if getattr(m, "role", "") == "assistant")
    return montar(resposta.content, usadas, passos, metricas.input_tokens,
                  metricas.output_tokens, time.perf_counter() - inicio,
                  instanciacao, consulta)


def montar(final, usadas, passos, entrada, saida, tempo, instanciacao, consulta) -> dict:
    """Monta a linha de resultado. `usadas=None` significa não observável."""
    if usadas is None:
        ferramenta_ok = None
    else:
        esperadas, obtidas = set(consulta["ferramentas"]), set(usadas)
        ferramenta_ok = bool(esperadas & obtidas) if esperadas else not obtidas
    return {"acertou": acertou(str(final), consulta), "ferramenta_ok": ferramenta_ok,
            "passos": passos, "entrada": entrada, "saida": saida,
            "tempo": tempo, "instanciacao": instanciacao}


FRAMEWORKS = [("LangChain 1.4", rodar_langchain), ("CrewAI 1.15", rodar_crewai),
              ("Agno 3.0", rodar_agno)]


def main() -> None:
    consultas = json.loads((BASE / "consultas.json").read_text(encoding="utf-8"))["consultas"]
    print(f"{len(consultas)} consultas · mesmas 4 ferramentas · mesmo modelo {MODELO}\n")

    resumo = []
    for nome, funcao in FRAMEWORKS:
        print(f"[{nome}] executando...")
        linhas, falhas = [], 0
        for consulta in consultas:
            try:
                linhas.append(funcao(consulta))
            except Exception as erro:
                print(f"    {consulta['id']}: {type(erro).__name__} — {str(erro)[:70]}")
                falhas += 1
        if not linhas:
            continue
        resumo.append({
            "framework": nome,
            "acertos": sum(l["acertou"] for l in linhas),
            "ferramenta_ok": (None if linhas[0]["ferramenta_ok"] is None
                              else sum(bool(l["ferramenta_ok"]) for l in linhas)),
            "ferramentas_observaveis": linhas[0]["ferramenta_ok"] is not None,
            "passos_mediana": statistics.median(l["passos"] for l in linhas),
            "entrada_mediana": statistics.median(l["entrada"] for l in linhas),
            "tempo_mediano": statistics.median(l["tempo"] for l in linhas),
            "instanciacao_mediana": statistics.median(l["instanciacao"] for l in linhas),
            "custo": sum(l["entrada"] for l in linhas) / 1e6 * USD_ENTRADA
                     + sum(l["saida"] for l in linhas) / 1e6 * USD_SAIDA,
            "falhas": falhas, "n": len(linhas),
        })

    print(f"\n{'Framework':16} {'Acerto':>8} {'Ferr.':>8} {'Passos':>8} {'Entrada':>9} "
          f"{'Instanc.':>10} {'Tempo':>8} {'US$ nas 15':>11}")
    print("-" * 92)
    for r in resumo:
        ferr = (f"{r['ferramenta_ok']:>4}/{r['n']:<3}" if r["ferramenta_ok"] is not None
                else f"{'n/d':>8}")
        print(f"{r['framework']:16} {r['acertos']:>4}/{r['n']:<3} {ferr} "
              f"{r['passos_mediana']:>8.0f} {r['entrada_mediana']:>9.0f} "
              f"{r['instanciacao_mediana']:>9.3f}s {r['tempo_mediano']:>7.1f}s {r['custo']:>11.5f}")

    destino = BASE / "resultado_frameworks.json"
    destino.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResultados em {destino.name}")


if __name__ == "__main__":
    main()
