# ============================================================
# Aula 06 – Introdução ao Agno
# Módulo: Agentes Autônomos | Curso: Formação em IA – UNEMAT/RISC
# Exemplo 04: Verificações antes de entregar o assistente ao cidadão
# Seção 5 – Verificações antes da entrega ao cidadão
# Requisitos: pip install agno openai python-dotenv
# ============================================================
"""Provoca, de propósito, as três falhas que o setor precisa conhecer.

[1] A docstring: oito perguntas diretas são respondidas com as funções
    documentadas e sem documentação; depois, duas perguntas cujo prazo conta
    da última movimentação são feitas com três versões da docstring de
    `consultar_protocolo`.
[2] O modo de depuração: uma pergunta com CPF fictício é feita com
    `debug_mode=True`, e o registro produzido é examinado. Em seguida, a mesma
    pergunta passa por um filtro de dados pessoais, primeiro com os padrões de
    fábrica e depois configurado para o CPF.
[3] O erro da API: o agente é montado com uma configuração que a API recusa,
    e o exemplo mostra o que chega em `resposta.content` e em `resposta.status`.
"""
import json
import logging
import pathlib
import re
import types
import warnings

warnings.filterwarnings("ignore")

from agno.agent import Agent
from agno.guardrails import PIIDetectionGuardrail
from agno.models.openai import OpenAIChat
from agno.run.base import RunStatus
from dotenv import load_dotenv

from ferramentas_comuns import (INSTRUCAO, buscar_legislacao_mt, calcular_atualizacao_debito,
                                calcular_prazo, consultar_protocolo)

BASE = pathlib.Path(__file__).parent
load_dotenv(BASE.parents[2] / ".env")

MODELO = "gpt-5.6-luna"
CPF = "123.456.789-00"  # fictício
PERGUNTA_COM_CPF = f"Qual a situação do protocolo 2026005678? Meu CPF é {CPF}."


def com_docstring(funcao, docstring):
    """Devolve uma cópia exata da função, trocando apenas a docstring.

    A cópia reaproveita o código compilado da original, de modo que o nome, os
    parâmetros, os valores padrão e as anotações de tipo permanecem idênticos.
    A única diferença entre as versões é a documentação.
    """
    copia = types.FunctionType(funcao.__code__, funcao.__globals__, funcao.__name__,
                               funcao.__defaults__, funcao.__closure__)
    copia.__annotations__ = dict(funcao.__annotations__)
    copia.__doc__ = docstring
    return copia


# Três versões da documentação de `consultar_protocolo`, da mais pobre à atual.
SO_QUANDO_USAR = """Consulta a situação de um processo administrativo pelo número de protocolo.

    Use quando o cidadão informar um número de protocolo e quiser saber em que
    etapa o processo se encontra.
    """
VERSOES = [
    ("sem docstring", None),
    ("diz só quando usar", SO_QUANDO_USAR),
    ("diz também o que devolve", consultar_protocolo.__doc__),
]

# Perguntas em que o prazo conta da última movimentação, que só o sistema de
# protocolo informa. A pergunta não diz que é preciso consultá-lo.
DEPENDENTES = [
    {"pergunta": "O protocolo 2026001234 tem prazo de resposta de 20 dias corridos, contados "
                 "da última movimentação. Em que data esse prazo vence?",
     "vencimento": ("2026-04-03", "03/04/2026")},
    {"pergunta": "Tenho 15 dias úteis, contados da última movimentação do protocolo "
                 "2026009012, para enviar a prestação de contas. Até quando posso enviar?",
     "vencimento": ("2026-08-11", "11/08/2026")},
]
REPETICOES = 3


def agente(ferramentas, debug: bool = False, filtros=None) -> Agent:
    return Agent(model=OpenAIChat(id=MODELO, reasoning_effort="none"),
                 tools=ferramentas, instructions=INSTRUCAO, markdown=False,
                 tool_call_limit=6, debug_mode=debug, pre_hooks=filtros,
                 telemetry=False)


def normalizar(texto: str) -> str:
    t = str(texto).lower().replace("**", "").replace(".", "").replace(",", "")
    return re.sub(r"\b(\d{2})/(\d{2})/(\d{4})\b", r"\3-\2-\1", t)


def medir_diretas(ferramentas, consultas: list[dict], rotulo: str) -> None:
    acertos = ferramenta_certa = 0
    for consulta in consultas:
        resposta = agente(ferramentas).run(consulta["pergunta"])
        if all(normalizar(a) in normalizar(resposta.content) for a in consulta["deve_conter"]):
            acertos += 1
        usadas = {t.tool_name for t in (resposta.tools or [])}
        if set(consulta["ferramentas"]) & usadas:
            ferramenta_certa += 1
    print(f"    {rotulo:28} acerto {acertos}/{len(consultas)} · "
          f"ferramenta certa {ferramenta_certa}/{len(consultas)}")


def medir_dependentes(versao: str, docstring) -> None:
    ferramentas = [com_docstring(consultar_protocolo, docstring), calcular_prazo,
                   buscar_legislacao_mt, calcular_atualizacao_debito]
    consultou = certos = 0
    for item in DEPENDENTES:
        for _ in range(REPETICOES):
            resposta = agente(ferramentas).run(item["pergunta"])
            usadas = {t.tool_name for t in (resposta.tools or [])}
            consultou += "consultar_protocolo" in usadas
            certos += any(v in str(resposta.content) for v in item["vencimento"])
    total = len(DEPENDENTES) * REPETICOES
    print(f"    {versao:28} consultou o protocolo {consultou}/{total} · "
          f"vencimento correto {certos}/{total}")


def falha_docstring() -> None:
    print("\n[1] A docstring das ferramentas")
    consultas = json.loads((BASE / "consultas.json").read_text(encoding="utf-8"))["consultas"]
    diretas = [c for c in consultas if c["ferramentas"]][:8]  # Q01 a Q08
    originais = [consultar_protocolo, calcular_prazo, buscar_legislacao_mt,
                 calcular_atualizacao_debito]
    print("  Oito perguntas diretas, com as quatro ferramentas documentadas ou não:")
    medir_diretas(originais, diretas, "com docstring")
    medir_diretas([com_docstring(f, None) for f in originais], diretas, "sem docstring")
    print("  Prazos contados da última movimentação, com três versões de consultar_protocolo:")
    for versao, docstring in VERSOES:
        medir_dependentes(versao, docstring)


def registro_de_depuracao(filtros=None) -> tuple[str, Agent]:
    """Executa a pergunta com `debug_mode=True` e devolve o que foi registrado.

    O Agno escreve a depuração pelo próprio registrador, e não pela saída
    padrão; por isso o coletor é acoplado ao registrador da biblioteca, como
    faria um serviço de observabilidade.
    """
    acumulado = []

    class Coletor(logging.Handler):
        def emit(self, registro):
            acumulado.append(self.format(registro))

    coletor = Coletor()
    for nome in ("agno", "httpx", "openai"):
        logging.getLogger(nome).addHandler(coletor)
        logging.getLogger(nome).setLevel(logging.DEBUG)
    resposta = agente([consultar_protocolo], debug=True, filtros=filtros).run(PERGUNTA_COM_CPF)
    for nome in ("agno", "httpx", "openai"):
        logging.getLogger(nome).removeHandler(coletor)
    return "\n".join(acumulado), resposta


def falha_debug_vaza() -> None:
    print("\n[2] O que debug_mode=True registra")
    log, _ = registro_de_depuracao()
    print(f"    linhas registradas: {len(log.splitlines())}")
    print(f"    o registro contém o CPF informado?         {'SIM' if CPF in log else 'não'}")
    print(f"    o registro contém o número do protocolo?   "
          f"{'sim' if '2026005678' in log else 'não'}")

    print("\n    Filtro de dados pessoais com os padrões de fábrica")
    fabrica = PIIDetectionGuardrail(mask_pii=True)
    log, resposta = registro_de_depuracao([fabrica])
    print(f"    pergunta entregue ao modelo: {resposta.input.input_content}")
    print(f"    o registro contém o CPF informado?         {'SIM' if CPF in log else 'não'}")
    print(f"    argumento da ferramenta: {resposta.tools[0].tool_args if resposta.tools else '-'}")

    print("\n    Filtro configurado para o CPF")
    para_cpf = PIIDetectionGuardrail(
        mask_pii=True,
        # Os padrões de fábrica são norte-americanos. O de telefone casa com
        # qualquer sequência de dez algarismos, inclusive o número do protocolo.
        enable_ssn_check=False, enable_credit_card_check=False, enable_phone_check=False,
        custom_patterns={"CPF": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"},
    )
    log, resposta = registro_de_depuracao([para_cpf])
    print(f"    pergunta entregue ao modelo: {resposta.input.input_content}")
    print(f"    o registro contém o CPF informado?         {'SIM' if CPF in log else 'não'}")
    print(f"    argumento da ferramenta: {resposta.tools[0].tool_args if resposta.tools else '-'}")


def falha_erro_silencioso() -> None:
    print("\n[3] O erro que chega como resposta")
    # Sem `reasoning_effort="none"`, a API recusa ferramentas na família GPT-5.6
    # pelo endpoint de Chat Completions (Aula 03, Seção 3.2).
    ag = Agent(model=OpenAIChat(id=MODELO), tools=[consultar_protocolo],
               instructions=INSTRUCAO, markdown=False, telemetry=False)
    try:
        resposta = ag.run("Qual a situação do protocolo 2026005678?")
    except Exception as erro:
        print(f"    levantou exceção: {type(erro).__name__}")
        return
    print("    levantou exceção? não")
    print(f"    resposta.status : {resposta.status}")
    print(f"    resposta.content: {str(resposta.content)[:120]}")

    # A verificação que impede o erro de chegar ao cidadão.
    if resposta.status == RunStatus.error:
        print("    verificação: execução com erro; o atendimento recebe a mensagem padrão")


if __name__ == "__main__":
    print("=" * 72)
    print("Verificações antes da entrega ao cidadão")
    print("=" * 72)
    for funcao in (falha_docstring, falha_debug_vaza, falha_erro_silencioso):
        try:
            funcao()
        except Exception as erro:
            print(f"    interrompida: {type(erro).__name__} — {str(erro)[:110]}")
    print()
