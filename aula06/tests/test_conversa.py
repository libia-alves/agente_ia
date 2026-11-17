import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conversa import Conversa, conversar, MENSAGEM_FALHA


class ConversaTeste(unittest.TestCase):
    def test_contexto_e_fontes_do_turno(self):
        pedidos = []
        def responder(estado, **kwargs):
            pedidos.append(list(estado['messages']))
            if len(pedidos) == 1:
                extras = [{'role':'assistant','tool_calls':[{'id':'a','name':'consultar_chamado','args':{'numero':'2026009012'}}]},
                          {'role':'tool','tool_call_id':'a','content':'Data 2026-11-13'},
                          {'role':'assistant','content':'O chamado aguarda indicação da pasta.'}]
            else:
                extras = [{'role':'assistant','tool_calls':[{'id':'b','name':'calcular_prazo','args':{'data_inicial':'2026-11-13','dias':5}}]},
                          {'role':'tool','tool_call_id':'b','content':'2026-11-20'},
                          {'role':'assistant','content':'Prazo didático: 2026-11-20.'}]
            return {'messages': [*estado['messages'], *extras]}
        sessao = Conversa(nome='Sofia', agente=SimpleNamespace(invoke=responder))
        sessao.perguntar('Consulte o chamado 2026009012.')
        self.assertIn('2026-11-20', sessao.perguntar('E cinco dias úteis depois?'))
        self.assertEqual(pedidos[1][0]['content'], 'Consulte o chamado 2026009012.')
        self.assertEqual([f['nome'] for f in sessao.ultimas_fontes], ['calcular_prazo'])
        with tempfile.TemporaryDirectory() as pasta:
            registro = json.loads(sessao.salvar(pasta).read_text())
        self.assertEqual(registro['agente'], 'Sofia')
        self.assertEqual(len(registro['turnos']), 2)
        sessao.limpar()
        self.assertEqual(sessao.turnos, [])
        self.assertEqual(sessao._mensagens, [])

    def test_falha_nao_corrompe_historico_ou_expoe_erro(self):
        def falhar(*args, **kwargs):
            raise RuntimeError('Detalhe interno que não deve aparecer')
        sessao = Conversa(agente=SimpleNamespace(invoke=falhar))
        self.assertEqual(sessao.perguntar('Olá'), MENSAGEM_FALHA)
        self.assertEqual(sessao._mensagens, [])
        self.assertEqual(sessao.turnos[0]['tipo_erro'], 'RuntimeError')

    def test_comandos_nao_chamam_modelo(self):
        sessao = Conversa(agente=SimpleNamespace(invoke=lambda *a, **kw: self.fail('Comando fez chamada ao modelo')))
        with patch('builtins.input', side_effect=['/fontes', '/limpar', '/sair']), patch('builtins.print'):
            conversar(sessao)
        self.assertEqual(sessao.turnos, [])


if __name__ == '__main__':
    unittest.main()
