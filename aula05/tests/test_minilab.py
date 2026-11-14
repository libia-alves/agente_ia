"""Integração local: execução real do Flow, somente a equipe/modelos são simulados."""
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import minilab as lab


class FluxoTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.pasta = Path(self.temp.name)
        self.banco = lab.SQLiteFlowPersistence(str(self.pasta / 'estados.db'))
        self.classe = lab.criar_fluxo(self.banco)
        self.rotinas = lab.ler(lab.ROOT / 'rotinas.json')

    def iniciar(self, cenario):
        flow = self.classe()
        resultado = flow.kickoff(inputs={'pedido': self.rotinas[cenario]})
        return flow, resultado

    def saida_falsa(self):
        return SimpleNamespace(raw='Minuta simulada para teste',
            token_usage=SimpleNamespace(model_dump=lambda: {'total_tokens': 30}),
            tasks_output=[SimpleNamespace(agent=area, raw='Parecer simulado: ' + area)
                          for area in lab.PERFIS])

    def test_rotas_simples_sem_chamadas(self):
        for cenario, status in [('incompleta', 'aguardando_documentos'),
                                ('simples', 'encaminhado_para_atendimento')]:
            with self.subTest(cenario=cenario), patch.object(lab, 'llm') as modelo, patch.object(lab, 'equipe_parecer') as crew:
                flow, _ = self.iniciar(cenario)
                estado = lab.conferir_estado(flow, self.banco, self.pasta)
                self.assertEqual(estado['status'], status)
                self.assertTrue(estado['entrada_recebida'])
                self.assertTrue(estado['conferencia_realizada'])
                modelo.assert_not_called()
                crew.assert_not_called()

    def test_barreira_humana_e_retomada_conservadora(self):
        with patch.object(lab, 'equipe_parecer') as crew:
            crew.return_value.kickoff.return_value = self.saida_falsa()
            flow, resultado = self.iniciar('complexa')
        self.assertIsInstance(resultado, lab.HumanFeedbackPending)
        estado = lab.conferir_estado(flow, self.banco, self.pasta)
        self.assertEqual(estado['status'], 'aguardando_revisao_humana')
        self.assertEqual(len(estado['pareceres']), 3)
        self.assertEqual(estado['aprovacoes'], [])
        self.assertEqual(estado['token_usage']['total_tokens'], 30)
        restaurado = self.classe.from_pending(flow.state.id, self.banco)
        with patch.object(lab, 'llm') as modelo:
            restaurado.resume('')
            modelo.assert_not_called()
        final = lab.conferir_estado(restaurado, self.banco, self.pasta)
        self.assertEqual(final['status'], 'revisao_solicitada')
        self.assertEqual(len(final['pareceres']), 3)
        self.assertEqual(final['aprovacoes'][0]['desfecho'], 'revisar')

    def test_aprovacao_simulada_preserva_historico(self):
        with patch.object(lab, 'equipe_parecer') as crew:
            crew.return_value.kickoff.return_value = self.saida_falsa()
            flow, _ = self.iniciar('complexa')
        restaurado = self.classe.from_pending(flow.state.id, self.banco)
        # Simula somente a interpretação do feedback; não é uma aprovação real.
        with patch.object(self.classe, '_collapse_to_outcome', return_value='aprovado'):
            restaurado.resume('Aprovação fictícia do teste de integração')
        final = lab.conferir_estado(restaurado, self.banco, self.pasta)
        self.assertEqual(final['status'], 'minuta_aprovada_para_assinatura_humana')
        self.assertEqual(len(final['pareceres']), 3)
        self.assertEqual(len(final['aprovacoes']), 1)

    def test_documentos_faltantes_tem_precedencia(self):
        for restauracao in (True, False):
            for divergencia in (True, False):
                pedido = lab.Pedido(restauracao_testada=restauracao, divergencia_planejamento=divergencia)
                self.assertEqual(lab.regra(pedido, False), 'complementar')

    def test_diagrama_contem_rotas_e_sincronizacao(self):
        flow = self.classe()
        html = lab.gerar_diagrama(flow, self.pasta)
        self.assertTrue(html.exists())
        estrutura = lab.ler(self.pasta / 'estrutura_diagrama.json')
        self.assertEqual(set(estrutura['start_methods']), {'receber', 'conferir'})
        self.assertEqual(estrutura['nodes']['distribuir']['trigger_condition_type'], 'AND')
        rotas = {e['router_event'] for e in estrutura['edges'] if e['source'] == 'distribuir'}
        self.assertEqual(rotas, {'complementar', 'encaminhar', 'assinar'})
        self.assertTrue((self.pasta / 'diagrama_script.js').exists())

    def test_eventos_contam_destinos_distintos(self):
        eventos = [{'tipo': 'tool_usage_started', 'tool_name': 'Delegate work to coworker',
                    'tool_args': {'coworker': nome}} for nome in ['TI', 'TI', 'Financeiro']]
        eventos.append({'tipo': 'tool_usage_finished', 'tool_name': 'Delegate work to coworker',
                        'tool_args': {'coworker': 'Outro'}})
        self.assertEqual(lab.especialistas_consultados(eventos), ['TI', 'Financeiro'])


if __name__ == '__main__':
    unittest.main()
