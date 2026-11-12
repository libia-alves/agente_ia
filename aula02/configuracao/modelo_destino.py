"""Parte 3, item 9: altere apenas a linha DESTINO e preserve as outras opções.

Exemplo alternativo OpenAI (permitido no enunciado):
DESTINO = dict(modelo="gpt-4.1-mini", provedor="openai", chave="OPENAI_API_KEY", base_url=None, entrada=0.40, cache=0.10, saida=1.60)
Para Groq/HF, preencha as tarifas vigentes e a variável de chave apropriada.
"""
DESTINO = dict(modelo="gpt-5.6-luna", provedor="openai", chave="OPENAI_API_KEY", base_url=None, entrada=0.20, cache=0.02, saida=1.20)
