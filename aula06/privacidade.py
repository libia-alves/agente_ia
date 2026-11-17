"""Padrões didáticos brasileiros, sem mascarar sequências genéricas de protocolos."""
from agno.guardrails import PIIDetectionGuardrail
from agno.run.agent import RunInput

# CPF/RG sem pontuação exigem rótulo: não é possível distinguir todo identificador
# só pelo comprimento. Nomes, endereços e outros formatos exigem ampliar a política.
PADROES = {
    'CPF': r'(?<!\d)\d{3}\.\d{3}\.\d{3}-\d{2}(?!\d)|(?i:\bCPF\s*:?\s*\d{11}\b)',
    'telefone': r'\(\d{2}\)\s?\d{4,5}-\d{4}|(?i:\b(?:telefone|celular)\s*:?\s*\d{10,11}\b)',
    'RG': r'(?i:\bRG\s*:?\s*[\d.]+-?[\dxX]\b)',
}


def filtro_pii() -> PIIDetectionGuardrail:
    return PIIDetectionGuardrail(mask_pii=True, enable_ssn_check=False,
        enable_credit_card_check=False, enable_phone_check=False,
        enable_email_check=True, custom_patterns=PADROES)


def mascarar_antes_do_agente(texto: str) -> str:
    """Protege também logs anteriores aos pre_hooks do Agno."""
    entrada = RunInput(input_content=texto)
    filtro_pii().check(entrada)
    return entrada.input_content
