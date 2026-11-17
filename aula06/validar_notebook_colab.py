"""Executa células do notebook localmente; não simula uma sessão Google Colab."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / '.env')
notebook = BASE / 'desafio_aula06_colab.ipynb'
nb = json.loads(notebook.read_text(encoding='utf-8'))
pasta = BASE / 'resultados' / 'desafio_notebook_validacao_local'
pasta.mkdir(parents=True, exist_ok=True)
os.chdir(pasta)
sys.path.insert(0, str(pasta))
contexto = {'__name__': '__validacao_notebook__'}
saida = io.StringIO()
with contextlib.redirect_stdout(saida):
    for i, celula in enumerate(nb['cells']):
        if celula['cell_type'] != 'code':
            continue
        fonte = ''.join(celula['source'])
        if '%pip install' in fonte:
            fonte = '\n'.join(l for l in fonte.splitlines() if not l.startswith('%pip '))
        if fonte.startswith('%%writefile '):
            cabecalho, conteudo = fonte.split('\n', 1)
            Path(cabecalho.split(' ', 1)[1]).write_text(conteudo, encoding='utf-8')
            continue
        fonte = fonte.replace('from google.colab import files\nfiles.download(ARQUIVO_ZIP)', 'print("Download exclusivo do Colab; ZIP local gerado.")')
        exec(compile(fonte, f'celula_{i}', 'exec'), contexto)
resumo = contexto['RESUMO']
assert len(resumo) == 16
assert all(r['status'] == 'concluido' for r in resumo)
assert all(r['consultas_com_retorno'] >= 1 for r in resumo)
assert all(r['data_correta'] and r['consulta_antes_do_calculo_no_registro'] for r in contexto['VERIFICACOES'])
(pasta / 'saida.txt').write_text(saida.getvalue(), encoding='utf-8')
(pasta / 'validacao.json').write_text(json.dumps({
    'ambiente': 'local, Python 3.12; não executado no serviço Google Colab',
    'notebook_sha256': hashlib.sha256(notebook.read_bytes()).hexdigest(),
    'execucoes': len(resumo), 'concluidas': sum(r['status'] == 'concluido' for r in resumo),
    'consultas_encadeadas': contexto['VERIFICACOES'],
    'nota': 'Instalação e download da interface Colab não executados; demais células executadas com API real.'
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('16/16 execuções com API concluídas; registros e ZIP gerados. Validação local:', pasta)
