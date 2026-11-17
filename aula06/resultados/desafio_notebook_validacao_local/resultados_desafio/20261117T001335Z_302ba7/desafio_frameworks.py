"""Desafio opcional: mesmas funções em LangChain/CrewAI, com rastros exportáveis."""
import json
from pathlib import Path
import time

from atendimento import FUNCOES, INSTRUCAO


def _campo(objeto, nome, padrao=None):
    return objeto.get(nome, padrao) if isinstance(objeto, dict) else getattr(objeto, nome, padrao)


def _argumentos(valor):
    if isinstance(valor, str):
        try:
            return json.loads(valor)
        except json.JSONDecodeError:
            return {'argumentos_brutos': valor}
    return valor if valor is not None else {}


def _extrair_mensagens(mensagens):
    """Relaciona cada pedido do modelo ao retorno pelo ID da chamada."""
    chamadas, retornos = [], {}
    for mensagem in mensagens:
        papel = _campo(mensagem, 'type') or _campo(mensagem, 'role')
        if papel == 'tool':
            retornos[_campo(mensagem, 'tool_call_id')] = {
                'retorno': _campo(mensagem, 'content'),
                'status_ferramenta': _campo(mensagem, 'status'),
            }
        for chamada in (_campo(mensagem, 'tool_calls', []) or []):
            funcao = _campo(chamada, 'function')
            chamadas.append({
                'id': _campo(chamada, 'id'),
                'nome': _campo(funcao, 'name') if funcao else _campo(chamada, 'name'),
                'argumentos': _argumentos(_campo(funcao, 'arguments') if funcao else _campo(chamada, 'args')),
            })
    for chamada in chamadas:
        retorno = retornos.get(chamada['id'])
        chamada['retorno_observado'] = retorno is not None
        chamada.update(retorno or {'retorno': None, 'status_ferramenta': None})
    return chamadas


def _gravar(destino: str | Path, registro: dict) -> dict:
    caminho = Path(destino)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(registro, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')
    return registro


def gravar_registro_langchain(resultado: dict, destino: str | Path) -> dict:
    """Grava consultas do estado retornado por create_agent.invoke.

    Recebe resultado como dicionário com messages e destino como caminho JSON.
    Lê AIMessage.tool_calls (nome/args/id), correlaciona ToolMessage.tool_call_id
    com content e devolve o mesmo dicionário gravado. Não deduz consultas da resposta.
    """
    mensagens = resultado['messages']
    return _gravar(destino, {
        'framework': 'LangChain', 'campo_do_resultado': 'resultado["messages"]',
        'ferramentas': _extrair_mensagens(mensagens),
        'resposta': _campo(mensagens[-1], 'content') if mensagens else None,
    })


def gravar_registro_crewai(resultado, destino: str | Path) -> dict:
    """Grava consultas do CrewOutput na versão fixada neste laboratório.

    Recebe objeto de Crew.kickoff e destino como caminho JSON. Percorre
    resultado.tasks_output[i].messages: assistant.tool_calls contém nome e
    arguments JSON; role=tool contém tool_call_id e content. Devolve o registro.
    """
    ferramentas = []
    for indice, tarefa in enumerate(resultado.tasks_output):
        if not hasattr(tarefa, 'messages'):
            raise ValueError('Esta versão não expõe TaskOutput.messages. Use as versões do notebook.')
        for chamada in _extrair_mensagens(tarefa.messages):
            ferramentas.append({'tarefa': indice, **chamada})
    return _gravar(destino, {
        'framework': 'CrewAI', 'campo_do_resultado': 'resultado.tasks_output[i].messages',
        'ferramentas': ferramentas, 'resposta': resultado.raw,
    })


def executar_langchain(pergunta: str, modelo: str):
    from langchain.agents import create_agent
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI

    agente = create_agent(
        model=ChatOpenAI(model=modelo, temperature=0, timeout=45, max_retries=0),
        tools=[tool(f) for f in FUNCOES], system_prompt=INSTRUCAO,
    )
    inicio = time.perf_counter()
    resultado = agente.invoke({'messages': [{'role': 'user', 'content': pergunta}]},
                              config={'recursion_limit': 16})
    return resultado, round(time.perf_counter() - inicio, 3)


def executar_crewai(pergunta: str, modelo: str):
    from crewai import Agent, Crew, LLM, Process, Task
    from crewai.tools import tool

    agente = Agent(
        role='Assistente de atendimento de TI da SEFAZ-MT',
        goal='Responder consultas usando exclusivamente as fontes hipotéticas das ferramentas.',
        backstory=INSTRUCAO,
        llm=LLM(model=f'openai/{modelo}', temperature=0, timeout=45, max_retries=0),
        tools=[tool(f.__name__)(f) for f in FUNCOES],
        allow_delegation=False, max_iter=6, max_retry_limit=0, verbose=False,
    )
    tarefa = Task(description=pergunta, expected_output='Resposta objetiva em português, sem inventar dados.', agent=agente)
    equipe = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential,
                  verbose=False, tracing=False, memory=False, cache=False)
    inicio = time.perf_counter()
    resultado = equipe.kickoff()
    return resultado, round(time.perf_counter() - inicio, 3)