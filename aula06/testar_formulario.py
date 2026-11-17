"""Revisa as três minutas fictícias pelo formulário real do Streamlit (com API)."""
import json
from pathlib import Path
from streamlit.testing.v1 import AppTest
from configuracao import BASE
from minilab import pasta_nova, salvar


def main():
    dados = json.loads((BASE / 'dados_minilab.json').read_text(encoding='utf-8'))
    pasta = pasta_nova('formulario')
    app = AppTest.from_file(str(BASE / 'app_revisor.py'), default_timeout=180).run()
    resultados = []
    for m in dados['minutas']:
        app.text_area[0].input(m['texto'])
        app.selectbox[0].select(m['tipo'])
        app.button[0].click().run(timeout=180)
        if app.exception:
            raise RuntimeError('Formulário apresentou exceção.')
        if 'revisao' in app.session_state:
            original, revisao, medidas = app.session_state['revisao']
            resultados.append({'id': m['id'], 'status': 'completed', 'revisao': revisao.model_dump(), 'medidas': medidas})
        else:
            resultados.append({'id': m['id'], 'status': 'error'})
        salvar(pasta / 'revisoes.json', resultados)
        print(m['id'], resultados[-1]['status'], flush=True)
    conferencia = []
    for m, r in zip(dados['minutas'], resultados):
        conferencia.append({'id': m['id'], 'avisos_agente': r.get('revisao', {}).get('avisos', []),
            'faltas_previas_didaticas': m['faltas_previas'],
            'avaliacao_servidor': [{'falta': f, 'vista_em_avisos': None, 'justificativa': ''} for f in m['faltas_previas']],
            'falsos_positivos': None})
    salvar(pasta / 'conferencia_humana.json', conferencia)
    print('Evidências:', pasta, flush=True)


if __name__ == '__main__':
    main()
