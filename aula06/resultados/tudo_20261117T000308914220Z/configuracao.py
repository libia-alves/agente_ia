"""Configuração somente desta aula; preços devem vir do contrato do provedor."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / '.env')
MODELO = os.getenv('MINILAB_MODELO') or 'gpt-4o-mini'
SETOR = 'Atendimento de TI da SEFAZ-MT'
PRECO_ENTRADA = float(os.environ['PRECO_ENTRADA']) if os.getenv('PRECO_ENTRADA') else None
PRECO_SAIDA = float(os.environ['PRECO_SAIDA']) if os.getenv('PRECO_SAIDA') else None
MENSAGEM_PADRAO = 'O atendimento está temporariamente indisponível. Tente novamente mais tarde pelo canal institucional.'


def custo_tokens(entrada: int, saida: int) -> float | None:
    if PRECO_ENTRADA is None or PRECO_SAIDA is None:
        return None
    return (entrada * PRECO_ENTRADA + saida * PRECO_SAIDA) / 1_000_000


def modelo(**opcoes):
    from agno.models.openai import OpenAIChat
    parametros = dict(id=MODELO, timeout=45, max_retries=0)
    if MODELO.startswith('gpt-5'):
        parametros['reasoning_effort'] = 'none'
    parametros.update(opcoes)
    return OpenAIChat(**parametros)
