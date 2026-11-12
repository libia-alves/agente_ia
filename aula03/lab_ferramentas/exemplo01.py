"""Parte 1: impressão e verificação local, sem chamadas à API."""
import json
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool
from .ferramentas import FERRAMENTAS, Acrescimo

def main():
    esquemas = [convert_to_openai_tool(tool(f) if callable(f) else f) for f in FERRAMENTAS]
    assert all(c.get('description') for c in Acrescimo.model_json_schema()['properties'].values())
    assert 'Não use' in esquemas[2]['function']['description']
    print(json.dumps(esquemas, ensure_ascii=False, indent=2))
    print('Confirmado: todos os argumentos da terceira ferramenta têm descrição.')

if __name__ == '__main__':
    main()
