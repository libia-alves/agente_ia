# ============================================================
# Aula 06 – Introdução ao Agno
# Módulo: Agentes Autônomos | Curso: Formação em IA – UNEMAT/RISC
# Mini LAB, Parte 4: esqueleto do agente revisor do seu setor
# Seção 6 – O agente atrás de um formulário
# Requisitos: pip install streamlit agno openai python-dotenv pydantic
# ============================================================
"""Esqueleto para a Parte 4 do Mini LAB.

Renomeie este arquivo para `revisor.py` no seu projeto: o `app_revisor.py`
importa com esse nome e não deve ser alterado. A tela já está pronta, e o
contrato com ela também. O que falta é o agente.

Onde há `TODO` existe trabalho seu. Nada mais precisa mudar.
"""
import pathlib
import time
import warnings

warnings.filterwarnings("ignore")

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
from pydantic import BaseModel, Field

BASE = pathlib.Path(__file__).parent
load_dotenv(BASE / ".env")

MODELO = "gpt-5.6-luna"
PRECO_ENTRADA, PRECO_SAIDA = 0.20, 1.20  # US$ por milhão de tokens

# ------------------------------------------------------------------
# TODO 1: o manual do seu órgão.
# Troque as regras abaixo pelas do manual de redação que o seu setor
# usa de fato, e mantenha pelo menos dois tipos de documento.
# ------------------------------------------------------------------
MANUAL = {
    "resposta a e-mail do cidadão": [
        "TODO: regra de tratamento do seu órgão",
        "TODO: regra de fechamento do seu órgão",
    ],
    "despacho": [
        "TODO: o que o despacho do seu setor precisa conter",
    ],
}


def consultar_manual_redacao(tipo_documento: str) -> str:
    """Consulta as regras do manual de redação oficial para um tipo de documento.

    Use sempre antes de reescrever, para saber qual tratamento e qual fechamento
    o tipo exige.
    """
    regras = MANUAL.get(tipo_documento.strip().lower())
    if regras is None:
        return (f"Tipo '{tipo_documento}' não consta do manual. "
                f"Tipos disponíveis: {', '.join(MANUAL)}.")
    return "\n".join(f"- {r}" for r in regras)


def verificar_dados_pessoais(texto: str) -> str:
    """TODO 2: localize dados pessoais no texto da minuta.

    Escreva a docstring de verdade, dizendo quando usar a ferramenta e o que
    ela devolve, porque é isso que o modelo lê para decidir chamá-la, conforme
    a Seção 5.1. A função deve apenas localizar: a decisão de suprimir cada
    ocorrência é do servidor, e o que a ferramenta devolve vai para `avisos`.

    Sugestão: expressões regulares para CPF, telefone, e-mail e RG.
    """
    raise NotImplementedError("TODO 2")


def medir_legibilidade(texto: str) -> str:
    """TODO 3: meça o tamanho das frases e aponte as longas, uma a uma.

    Devolva texto, não número solto: o modelo precisa saber qual frase dividir,
    e não apenas que a média está alta.
    """
    raise NotImplementedError("TODO 3")


FERRAMENTAS = [consultar_manual_redacao, verificar_dados_pessoais, medir_legibilidade]

# ------------------------------------------------------------------
# O contrato com a tela, já pronto. Não altere os nomes dos campos:
# o `app_revisor.py` desenha a interface a partir deles.
# ------------------------------------------------------------------


class Alteracao(BaseModel):
    trecho_original: str = Field(description="Trecho da minuta como o servidor escreveu")
    trecho_novo: str = Field(description="Trecho como ficou depois da revisão")
    motivo: str = Field(description="Regra do manual ou defeito de redação que justifica a troca")


class Revisao(BaseModel):
    texto_revisado: str = Field(description="A minuta inteira reescrita, pronta para conferência")
    alteracoes: list[Alteracao] = Field(description="Uma entrada por alteração feita")
    avisos: list[str] = Field(
        description="O que o agente não corrigiu porque exige decisão ou informação do servidor")


# ------------------------------------------------------------------
# TODO 4: a instrução do agente.
# Ela precisa dizer, no mínimo: em que ordem consultar as ferramentas;
# que a forma se corrige e o mérito não; que informação ausente se
# registra em `avisos` em vez de ser inventada; e que dado pessoal não
# se suprime por conta própria.
# ------------------------------------------------------------------
INSTRUCAO = """TODO 4: escreva a instrução do seu agente revisor."""


def construir_agente() -> Agent:
    """TODO 5: monte o agente.

    Precisa declarar o modelo com `reasoning_effort="none"`, as `FERRAMENTAS`,
    a `INSTRUCAO`, `output_schema=Revisao`, um `tool_call_limit` e
    `telemetry=False`. O limite não é detalhe: na tela, cada chamada a mais é
    espera do servidor.
    """
    raise NotImplementedError("TODO 5")


def revisar(
    minuta: str,
    tipo: str,
    agente: Agent | None = None,
    ao_chamar_ferramenta=None,
) -> tuple[Revisao, dict]:
    """Revisa uma minuta e devolve o resultado validado e as medidas da execução.

    Esta função já está pronta e é a fronteira com a tela. Leia-a antes de
    escrever o resto: é aqui que se vê por que a interface não precisa saber
    qual framework está atrás.
    """
    agente = agente or construir_agente()
    pedido = f"Tipo de documento: {tipo}\n\nMinuta a revisar:\n{minuta}"

    inicio = time.perf_counter()
    ferramentas: list[str] = []

    if ao_chamar_ferramenta is None:
        resultado = agente.run(pedido)
        ferramentas = [c.tool_name for c in (resultado.tools or [])]
        chamadas = [m.role for m in (resultado.messages or [])].count("assistant")
    else:
        resultado, chamadas = None, 0
        for evento in agente.run(pedido, stream=True, stream_events=True):
            nome = type(evento).__name__
            if nome == "ModelRequestStartedEvent":
                chamadas += 1
            elif nome == "ToolCallStartedEvent":
                ferramentas.append(evento.tool.tool_name)
                ao_chamar_ferramenta(evento.tool.tool_name)
            elif nome == "RunCompletedEvent":
                resultado = evento

    duracao = time.perf_counter() - inicio
    m = resultado.metrics
    return resultado.content, {
        "segundos": round(duracao, 1),
        "chamadas": chamadas,
        "tokens_entrada": m.input_tokens,
        "tokens_saida": m.output_tokens,
        "ferramentas": ferramentas,
        "custo": m.input_tokens / 1e6 * PRECO_ENTRADA + m.output_tokens / 1e6 * PRECO_SAIDA,
    }
