"""Testa a exportação e a correlação de argumentos/retornos sem modelo."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from desafio_frameworks import gravar_registro_langchain, gravar_registro_crewai


class RegistroFrameworks(unittest.TestCase):
    def test_langchain_correlaciona_ids_fora_de_ordem(self):
        resultado = {'messages': [
            SimpleNamespace(type='ai', tool_calls=[{'id':'a', 'name':'consultar_chamado', 'args':{'numero':'2026009012'}}, {'id':'b', 'name':'consultar_servico', 'args':{'servico':'rede'}}]),
            SimpleNamespace(type='tool', tool_call_id='b', content='prazo: 3', status='success'),
            SimpleNamespace(type='tool', tool_call_id='a', content='data: 2026-11-13', status='success'),
            SimpleNamespace(type='ai', content='Resposta final', tool_calls=[])]}
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta)/'registro.json'
            registro = gravar_registro_langchain(resultado, caminho)
            self.assertEqual(json.loads(caminho.read_text()), registro)
        self.assertEqual(registro['ferramentas'][0]['retorno'], 'data: 2026-11-13')
        self.assertEqual(registro['ferramentas'][1]['retorno'], 'prazo: 3')
        self.assertEqual(registro['ferramentas'][0]['argumentos']['numero'], '2026009012')

    def test_crewai_argumentos_json_e_retorno_ausente(self):
        resultado = SimpleNamespace(raw='Resposta', tasks_output=[SimpleNamespace(messages=[
            {'role':'assistant', 'tool_calls':[{'id':'a','function':{'name':'consultar_chamado','arguments':'{"numero":"2026009012"}'}}, {'id':'b','function':{'name':'calcular_prazo','arguments':'{"data_inicial":"2026-11-13","dias":5}'}}]},
            {'role':'tool','tool_call_id':'a','content':'data: 2026-11-13'}])])
        with tempfile.TemporaryDirectory() as pasta:
            registro = gravar_registro_crewai(resultado, Path(pasta)/'registro.json')
        self.assertEqual(registro['ferramentas'][1]['argumentos']['data_inicial'], '2026-11-13')
        self.assertTrue(registro['ferramentas'][0]['retorno_observado'])
        self.assertFalse(registro['ferramentas'][1]['retorno_observado'])
        self.assertIsNone(registro['ferramentas'][1]['retorno'])

    def test_sem_ferramentas_nao_inventa_consulta(self):
        with tempfile.TemporaryDirectory() as pasta:
            registro = gravar_registro_langchain({'messages':[{'role':'assistant','content':'Preciso do número.'}]}, Path(pasta)/'registro.json')
        self.assertEqual(registro['ferramentas'], [])


if __name__ == '__main__':
    unittest.main()
