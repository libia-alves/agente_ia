# ============================================================
# Aula 06 – Introdução ao Agno
# Módulo: Agentes Autônomos | Curso: Formação em IA – UNEMAT/RISC
# Apoio: as quatro ferramentas do atendimento, em Python puro
# Seção 3 – Ferramentas do atendimento no Agno
# Requisitos: nenhum (biblioteca padrão)
# ============================================================
"""As quatro ferramentas do assistente de atendimento da SEFAZ-MT.

Cada função substitui uma consulta que o servidor do atendimento faz hoje à
mão: o sistema de protocolo, o cálculo de prazos, a base de legislação e a
planilha de atualização de débitos. Os dados são hipotéticos e ficam em
dicionários locais, para que os exemplos não dependam de serviço externo.

Nenhuma função importa framework. O Agno as recebe como estão, e a mesma
neutralidade permite entregá-las ao LangChain e ao CrewAI sem adaptação,
como mostra a Seção 4.4.
"""
from datetime import date, timedelta

# Base local de protocolos, com dados hipotéticos do atendimento da SEFAZ-MT.
PROTOCOLOS = {
    "2026001234": ("Requerimento de licença-prêmio", "Em análise na Gerência de RH", "2026-03-14"),
    "2026005678": ("Pedido de prorrogação de bolsa de pesquisa", "Deferido", "2026-05-02"),
    "2026009012": ("Prestação de contas de auxílio à pesquisa", "Aguardando documentação", "2026-07-21"),
}

# Base local de normas. As leis federais citadas existem; o decreto estadual
# sobre débitos é hipotético, como os demais dados do exemplo.
NORMAS = {
    "licitação": ("Lei nº 14.133/2021", "Art. 125: acréscimos e supressões de até 25% do valor inicial."),
    "processo administrativo": ("Lei nº 9.784/1999", "Art. 59: prazo de dez dias para recurso administrativo."),
    "dados pessoais": ("Lei nº 13.709/2018", "Art. 18: o titular tem direito à eliminação dos dados."),
    "débito": ("Decreto Estadual nº 987/2023", "Art. 3: juros de mora de 1% ao mês sobre o valor atualizado."),
    "acesso à informação": ("Lei nº 12.527/2011", "Art. 11: resposta em até vinte dias, prorrogável por dez."),
}

IPCA_MENSAL, JUROS_MENSAL, MULTA = 0.0042, 0.01, 0.02


def _reais(valor: float) -> str:
    """Formata um valor no padrão brasileiro, como em R$ 10.515,81."""
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def consultar_protocolo(numero: str) -> str:
    """Consulta a situação de um processo administrativo pelo número de protocolo.

    Devolve o assunto, a situação atual e a data da última movimentação. Use
    quando o cidadão informar um número de protocolo e quiser saber em que
    etapa o processo se encontra, ou quando um prazo for contado a partir da
    última movimentação.
    """
    registro = PROTOCOLOS.get(numero.strip())
    if registro is None:
        return f"Protocolo {numero} não localizado na base."
    assunto, situacao, data = registro
    return f"Protocolo {numero}: {assunto}. Situação: {situacao}. Última movimentação: {data}."


def calcular_prazo(data_inicial: str, dias: int, uteis: bool = True) -> str:
    """Calcula a data final de um prazo em dias úteis ou corridos.

    A data inicial deve vir no formato AAAA-MM-DD. Use uteis=True para prazos
    processuais e uteis=False para prazos contratuais em dias corridos.
    """
    try:
        inicio = date.fromisoformat(data_inicial)
    except ValueError:
        return f"Data inválida: '{data_inicial}'. Use o formato AAAA-MM-DD."
    if not uteis:
        return (f"Prazo de {dias} dias corridos a partir de {data_inicial}: "
                f"vence em {(inicio + timedelta(days=dias)).isoformat()}.")
    atual, restantes = inicio, dias
    while restantes > 0:
        atual += timedelta(days=1)
        if atual.weekday() < 5:
            restantes -= 1
    return (f"Prazo de {dias} dias úteis a partir de {data_inicial}: vence em "
            f"{atual.isoformat()} (feriados não considerados).")


def buscar_legislacao_mt(assunto: str) -> str:
    """Busca a norma aplicável a um assunto na base da Procuradoria estadual.

    Use para localizar a lei ou o decreto que disciplina um tema, como
    licitação, processo administrativo, dados pessoais ou atualização de débito.
    """
    termo = assunto.lower().strip()
    for chave, (norma, artigo) in NORMAS.items():
        # Palavras de até duas letras, como "à", não servem de critério de busca.
        if any(palavra in termo for palavra in chave.split() if len(palavra) > 2):
            return f"{norma} — {artigo}"
    return f"Nenhuma norma localizada para o assunto '{assunto}'."


def calcular_atualizacao_debito(valor_principal: float, meses_atraso: int,
                                aplicar_multa: bool = True) -> str:
    """Calcula a atualização monetária de um débito com a Fazenda Estadual.

    Aplica IPCA, juros de mora de 1% ao mês e multa de 2%. Use apenas quando o
    valor principal e o número de meses de atraso forem informados
    explicitamente pelo usuário.
    """
    if valor_principal <= 0 or meses_atraso < 0:
        return "Valores inválidos: o principal deve ser positivo e o atraso não negativo."
    corrigido = valor_principal * ((1 + IPCA_MENSAL) ** meses_atraso)
    juros = corrigido * JUROS_MENSAL * meses_atraso
    multa = corrigido * MULTA if aplicar_multa else 0.0
    return (f"Principal {_reais(valor_principal)} · corrigido {_reais(corrigido)} · "
            f"juros {_reais(juros)} · multa {_reais(multa)} · "
            f"TOTAL {_reais(corrigido + juros + multa)}")


FUNCOES = [consultar_protocolo, calcular_prazo, buscar_legislacao_mt,
           calcular_atualizacao_debito]

INSTRUCAO = (
    "Você é o assistente de atendimento da Secretaria de Estado de Fazenda de "
    "Mato Grosso (SEFAZ-MT), em um laboratório com dados hipotéticos. "
    "Responda em português, com linguagem simples e orientação objetiva. "
    "Fundamente as respostas nas ferramentas e informe quais dados faltam. "
    "Se um cálculo depender de outra consulta, aguarde o resultado antes de calcular. "
    "Não invente protocolos, prazos, contatos ou fundamentos. Não solicite senhas "
    "nem dados pessoais desnecessários. Não apresente as simulações como valores "
    "oficiais de tributos, normas validadas ou decisões da SEFAZ-MT. "
    "Encaminhe dúvidas fora das fontes disponíveis à conferência do servidor."
)


if __name__ == "__main__":
    # As funções são executáveis sem agente e sem chave de API. Conferir cada
    # uma isoladamente é o primeiro teste antes de entregá-las a um framework.
    print("Ferramentas e a primeira linha da docstring de cada uma:")
    for funcao in FUNCOES:
        print(f"  {funcao.__name__:30} {funcao.__doc__.splitlines()[0]}")
    print()
    print(consultar_protocolo("2026005678"))
    print(calcular_prazo("2026-07-21", 15, uteis=True))
    print(buscar_legislacao_mt("acesso à informação"))
    print(calcular_atualizacao_debito(4800, 5))
