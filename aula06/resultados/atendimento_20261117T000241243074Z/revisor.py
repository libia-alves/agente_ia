# ============================================================
# Aula 06 – Introdução ao Agno
# Módulo: Agentes Autônomos | Curso: Formação em IA – UNEMAT/RISC
# Apoio: o agente revisor de minutas e suas três ferramentas
# Seção 6 – O agente atrás de um formulário
# Requisitos: pip install agno openai python-dotenv pydantic
# ============================================================
"""O agente que revisa a minuta de resposta ao cidadão.

Este módulo não sabe que existe uma tela. Ele expõe uma única função,
`revisar`, que recebe texto e devolve um objeto validado, e é essa fronteira
que permite trocar o framework sem tocar na interface. O `app_revisor.py`
importa daqui e nada mais.

As três ferramentas são funções Python comuns, no mesmo estilo do
`ferramentas_comuns.py` da Seção 3: nenhuma delas importa framework. Os dados
do manual de redação são hipotéticos.
"""
import pathlib
import json
import re
import time
import warnings

warnings.filterwarnings("ignore")

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run.base import RunStatus
from configuracao import MODELO, PRECO_ENTRADA, PRECO_SAIDA, modelo, MENSAGEM_PADRAO
from registro import extrair
from pydantic import BaseModel, Field

BASE = pathlib.Path(__file__).parent
# Manual didático externo, substituível pelo manual efetivamente usado no setor.
MANUAL_CONFIG = json.loads((BASE / "manual_setor.json").read_text(encoding="utf-8"))
MANUAL = MANUAL_CONFIG["tipos"]

JARGAO = {
    "em sede de": "ao",
    "exordial": "inicial",
    "pleito": "pedido",
    "feito": "processo",
    "s.m.j.": "(suprimir: expressão de uso interno)",
    "smj": "(suprimir: expressão de uso interno)",
    "oportunamente": "(informar a data ou o prazo real)",
    "data vênia": "(suprimir: expressão de uso interno)",
    "alçada": "competência",
    "requerente": "o nome do cidadão, quando conhecido",
    "instrução processual": "análise dos documentos",
    "juntada": "entrega",
}

PADROES_PESSOAIS = {
    "CPF": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|(?i:\bCPF\s*:?\s*\d{11}\b)",
    "telefone": r"\(\d{2}\)\s?\d{4,5}-\d{4}",
    "e-mail": r"\b[\w.\-]+@[\w\-]+\.[a-z]{2,}\b",
    "RG": r"\b\d{2}\.\d{3}\.\d{3}-\d\b",
}


def consultar_manual_redacao(tipo_documento: str) -> str:
    """Consulta as regras do manual de redação oficial para um tipo de documento.

    Use antes de reescrever. Recebe tipo_documento como string: resposta a
    e-mail do cidadão ou despacho. Devolve string com uma regra por linha ou
    mensagem de tipo não encontrado.
    """
    regras = MANUAL.get(tipo_documento.strip().lower())
    if regras is None:
        return (f"Tipo '{tipo_documento}' não consta do manual. "
                f"Tipos disponíveis: {', '.join(MANUAL)}.")
    return "\n".join(f"- {r}" for r in regras)


def verificar_dados_pessoais(texto: str) -> str:
    """Localiza dados pessoais no texto da minuta.

    Use para saber se a minuta expõe CPF, telefone, e-mail ou RG. A ferramenta
    Recebe texto como string livre e devolve string com rótulo e ocorrência
    por linha ou mensagem de nenhum achado. A ferramenta apenas localiza: a decisão de suprimir cada ocorrência cabe ao servidor,
    porque alguns dados são necessários à instrução do processo.
    """
    achados = []
    for rotulo, padrao in PADROES_PESSOAIS.items():
        for ocorrencia in re.findall(padrao, texto):
            achados.append(f"{rotulo}: {ocorrencia}")
    if not achados:
        return "Nenhum dado pessoal localizado no texto."
    return ("Dados pessoais localizados (a supressão depende de decisão do servidor):\n"
            + "\n".join(f"- {a}" for a in achados))


def medir_legibilidade(texto: str) -> str:
    """Mede o tamanho das frases da minuta e aponta as frases longas.

    Recebe texto como string livre; devolve string com contagem, média e
    indicação individual das frases longas. Use para decidir onde dividir o texto. Frases com mais de trinta palavras
    são apontadas uma a uma, porque são o defeito mais comum da redação
    administrativa e o que mais atrapalha o cidadão.
    """
    frases = [f.strip() for f in re.split(r"(?<=[.!?])\s+", texto.strip()) if f.strip()]
    palavras = texto.split()
    if not frases:
        return "Texto vazio."
    media = len(palavras) / len(frases)
    linhas = [f"{len(palavras)} palavras em {len(frases)} frases "
              f"(média de {media:.1f} palavras por frase)."]
    longas = [(i, f) for i, f in enumerate(frases, 1) if len(f.split()) > 30]
    for i, frase in longas:
        linhas.append(f"- frase {i}, com {len(frase.split())} palavras: \"{frase[:60]}...\"")
    if not longas:
        linhas.append("- nenhuma frase acima de trinta palavras.")
    return "\n".join(linhas)


FERRAMENTAS = [consultar_manual_redacao, verificar_dados_pessoais, medir_legibilidade]

# ------------------------------------------------------------------
# O contrato com a tela. Cada campo existe porque a interface precisa
# desenhá-lo: o texto no campo editável, as alterações na lista com
# justificativa, os avisos no painel de decisões pendentes.
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


INSTRUCAO = """Você revisa minutas de resposta ao cidadão redigidas por servidores
do atendimento de TI da SEFAZ-MT, em laboratório com regras hipotéticas.

Procedimento obrigatório, nesta ordem:
1. Consulte o manual de redação para o tipo de documento informado.
2. Verifique se a minuta contém dados pessoais.
3. Meça a legibilidade para localizar as frases longas.
4. Só então reescreva a minuta.

Regras da reescrita:
- Preserve integralmente o conteúdo decidido pelo servidor. Você corrige a forma,
  não o mérito: não defira, não indefira e não altere situação de processo.
- Nunca invente informação que não esteja na minuta. Se falta o prazo, o nome da
  norma, o setor ou o canal de contato, registre a falta em `avisos` e deixe no
  texto uma marca entre colchetes, como [informar o prazo].
- Não suprima dado pessoal por conta própria: registre a ocorrência em `avisos`
  para que o servidor decida, porque alguns dados instruem o processo.
- Substitua jargão por linguagem simples e divida as frases longas.
- Registre em `alteracoes` uma entrada por troca relevante, com o motivo apoiado
  na regra do manual ou no defeito encontrado."""


def construir_agente() -> Agent:
    """Monta o agente revisor.

    A construção fica em função própria porque a aplicação Streamlit a envolve
    em `@st.cache_resource`: sem isso, cada reexecução do script criaria um
    agente novo a cada interação do usuário.
    """
    return Agent(
        model=modelo(request_params={"parallel_tool_calls": False}),
        tools=FERRAMENTAS,
        instructions=INSTRUCAO,
        output_schema=Revisao,
        tool_call_limit=6,
        markdown=False,
        telemetry=False,
    )


def revisar(
    minuta: str,
    tipo: str,
    agente: Agent | None = None,
    ao_chamar_ferramenta=None,
) -> tuple[Revisao, dict]:
    """Revisa uma minuta e devolve o resultado validado e as medidas da execução.

    A tela consome os dois: o objeto `Revisao` para desenhar os campos e o
    dicionário de medidas para exibir no rodapé o que a revisão custou.

    Quando a interface passa uma função em `ao_chamar_ferramenta`, a execução
    corre em modo de eventos e cada ferramenta é anunciada no momento em que
    começa. É assim que a aplicação mostra progresso: com `output_schema` o
    texto não pode ser exibido aos poucos, e o que se transmite é a ação.
    """
    agente = agente or construir_agente()
    pedido = f"Tipo de documento: {tipo}\n\nMinuta a revisar:\n{minuta}"

    if not minuta.strip() or tipo not in MANUAL:
        raise ValueError("Informe uma minuta e um tipo disponível no manual.")
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
            elif nome == "RunErrorEvent":
                raise RuntimeError(MENSAGEM_PADRAO)

    duracao = time.perf_counter() - inicio
    if resultado is None or getattr(resultado, "status", RunStatus.completed) != RunStatus.completed:
        raise RuntimeError(MENSAGEM_PADRAO)
    conteudo = resultado.content
    if not isinstance(conteudo, Revisao):
        try:
            conteudo = Revisao.model_validate_json(conteudo) if isinstance(conteudo, str) else Revisao.model_validate(conteudo)
        except (ValueError, TypeError):
            raise RuntimeError(MENSAGEM_PADRAO) from None
    if ao_chamar_ferramenta is None:
        registro = extrair(resultado)
        chamadas = registro["chamadas_modelo"]
    else:
        # Eventos não têm o mesmo contrato de mensagens do RunOutput.
        final = agente.get_last_run_output()
        if final is None or final.status != RunStatus.completed:
            raise RuntimeError(MENSAGEM_PADRAO)
        registro = extrair(final)
        chamadas = registro["chamadas_modelo"]
    medidas = {
        "segundos": round(duracao, 2), "chamadas": chamadas,
        "tokens_entrada": registro["tokens_entrada"],
        "tokens_saida": registro["tokens_saida"],
        "ferramentas": ferramentas, "registro_ferramentas": registro["ferramentas"],
        "custo": registro["custo_estimado_usd"],
    }
    return conteudo, medidas
