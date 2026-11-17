"""Verificações locais sem chave e sem rede."""
import sys
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agno.run.base import RunStatus
from atendimento import calcular_prazo, consultar_chamado
from privacidade import mascarar_antes_do_agente
from registro import resposta_publica
from configuracao import MENSAGEM_PADRAO
from revisor import revisar


class Verificacoes(unittest.TestCase):
    def test_prazo_encadeado(self):
        consulta = consultar_chamado('2026009012')
        prazo = calcular_prazo(consulta['ultima_movimentacao'], 5)
        self.assertEqual(prazo['vencimento'], '2026-11-20')
        self.assertIn('Feriados não considerados', prazo['ressalva'])

    def test_prazo_invalido(self):
        for entrada in [('2026-02-30', 2), ('2026-11-13', -1), ('2026-11-13', True)]:
            self.assertIn('erro', calcular_prazo(*entrada))

    def test_pii_preserva_identificadores(self):
        texto = ('CPF 123.456.789-00; CPF: 12345678900; telefone (65) 99999-1234; '
                 'celular: 65999991234; email pessoa@example.invalid; RG 12.345.678-9; '
                 'protocolo 2026001234; processo 1234567-89.2026.8.11.0000; processo 12345678901')
        filtrado = mascarar_antes_do_agente(texto)
        for dado in ['123.456.789-00', '12345678900', '(65) 99999-1234', '65999991234',
                     'pessoa@example.invalid', '12.345.678-9']:
            self.assertNotIn(dado, filtrado)
        for identificador in ['2026001234', '1234567-89.2026.8.11.0000', '12345678901']:
            self.assertIn(identificador, filtrado)

    def test_status_nao_expoe_erro(self):
        resposta = SimpleNamespace(status=RunStatus.error, content='Erro interno com detalhe técnico')
        self.assertEqual(resposta_publica(resposta), MENSAGEM_PADRAO)

    def test_revisor_falha_sem_metricas(self):
        agente = SimpleNamespace(run=lambda _: SimpleNamespace(status=RunStatus.error))
        with self.assertRaisesRegex(RuntimeError, 'temporariamente indisponível'):
            revisar('Texto de teste.', 'despacho', agente=agente)

    def test_tela_mostra_formulario(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app_revisor.py')).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.selectbox[0].options), 2)

    def test_tela_falha_sem_resultado_anterior(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app_revisor.py')).run()
        app.text_area[0].input('Texto de teste sem dados pessoais.')
        with patch('revisor.revisar', side_effect=RuntimeError('detalhe privado')):
            app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertNotIn('revisao', app.session_state)
        self.assertEqual(app.status[0].label, MENSAGEM_PADRAO)


if __name__ == '__main__':
    unittest.main()
