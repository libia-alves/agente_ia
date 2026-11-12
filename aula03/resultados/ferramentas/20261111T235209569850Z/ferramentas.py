"""Base inteiramente fictícia: nenhuma taxa constitui orientação jurídica."""
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal
from langchain_core.tools import StructuredTool, tool
from pydantic import BaseModel, Field, ConfigDict

CONTRATOS = {
    'LAB-001': {'fornecedor': 'Pantanal Serviços', 'valor': 100000.0, 'situacao': 'ativo'},
    'LAB-002': {'fornecedor': 'Cerrado Tecnologia', 'valor': 80000.0, 'situacao': 'ativo'},
    'LAB-003': {'fornecedor': 'Araguaia Engenharia', 'valor': 250000.0, 'situacao': 'encerrado'},
}
REGRAS = {'material': 10.0, 'servico': 15.0, 'obra': 20.0}

@tool
def consultar_contrato(numero: str) -> dict:
    """Consulta fornecedor, valor em reais e situação de um contrato fictício pelo número LAB-001 etc."""
    return {'numero': numero, **CONTRATOS[numero]} if numero in CONTRATOS else {'erro': 'contrato inexistente'}

# Segunda forma: função anotada entregue diretamente na lista a create_agent.
def consultar_regra(tipo: Literal['material', 'servico', 'obra']) -> dict:
    """Consulta o percentual didático de acréscimo para material, servico ou obra; não é regra legal."""
    return {'tipo': tipo, 'percentual': REGRAS[tipo], 'natureza': 'regra fictícia de laboratório'}

class Acrescimo(BaseModel):
    """Argumentos de uma simulação financeira, sem autorização de despesa."""
    model_config = ConfigDict(extra='forbid')
    valor_base: float = Field(gt=0, allow_inf_nan=False, description='Valor original do contrato em reais, informado pelo usuário ou retornado por consultar_contrato; nunca estimar.')
    percentual: float = Field(gt=0, le=100, allow_inf_nan=False, description='Percentual de acréscimo, em pontos percentuais: 10 significa 10%, informado pelo usuário ou retornado por consultar_regra.')

def calcular_acrescimo(valor_base: float, percentual: float) -> dict:
    base, taxa = Decimal(str(valor_base)), Decimal(str(percentual))
    adicional = (base * taxa / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return {'acrescimo': float(adicional), 'total': float(base + adicional), 'simulacao': True}

simular_acrescimo = StructuredTool.from_function(
    func=calcular_acrescimo, name='simular_acrescimo', args_schema=Acrescimo,
    description='Simula acréscimo financeiro e devolve acréscimo e total em reais. Não use esta ferramenta quando faltar valor_base ou percentual com origem verificável, nem para autorizar despesa ou aprovar aditivo.')
FERRAMENTAS = [consultar_contrato, consultar_regra, simular_acrescimo]
