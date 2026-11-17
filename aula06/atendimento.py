"""Compatibilidade com o minilab: funções e diretrizes ficam em ferramentas.py."""
from ferramentas import (
    CHAMADOS, SERVICOS, FUNCOES, INSTRUCAO, NOME_AGENTE,
    consultar_chamado, consultar_servico, calcular_prazo, consultar_canal,
)

if __name__ == '__main__':
    import runpy
    from pathlib import Path
    runpy.run_path(str(Path(__file__).with_name('ferramentas.py')), run_name='__main__')
