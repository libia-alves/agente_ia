"""Extrai rastros e métricas diretamente do RunOutput do Agno."""
from agno.run.base import RunStatus
from configuracao import MENSAGEM_PADRAO, custo_tokens


def resposta_publica(resposta) -> str:
    if resposta.status != RunStatus.completed:
        return MENSAGEM_PADRAO
    return str(resposta.content)


def extrair(resposta) -> dict:
    m = resposta.metrics
    entrada = getattr(m, 'input_tokens', None)
    saida = getattr(m, 'output_tokens', None)
    chamadas = [msg for msg in (resposta.messages or []) if msg.role == 'assistant' and msg.metrics]
    return {
        'status': resposta.status.value,
        'resposta': resposta_publica(resposta),
        'ferramentas': [{'nome': t.tool_name, 'argumentos': t.tool_args, 'retorno': t.result}
                        for t in (resposta.tools or [])],
        'chamadas_modelo': len(chamadas),
        'entrada_por_chamada': [msg.metrics.input_tokens for msg in chamadas],
        'tokens_entrada': entrada, 'tokens_saida': saida,
        'custo_provedor_usd': getattr(m, 'cost', None),
        'custo_estimado_usd': custo_tokens(entrada, saida) if entrada is not None and saida is not None else None,
        'max_ferramentas_por_resposta': max((len(msg.tool_calls or []) for msg in chamadas), default=0),
    }
