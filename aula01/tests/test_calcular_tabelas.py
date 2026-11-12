import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from calcular_tabelas import (BASE, calcular, confiabilidade, estimar_custo, exportar,
                             parecer, relatorio, parametros_aula, precos_aula, tabelas_originais)


class MiniLabTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((BASE / 'processos.json').read_text(encoding='utf-8'))

    def test_confiabilidade_exemplos(self):
        for n, esperado in [(4, 0.81450625), (6, 0.735091890625), (10, 0.5987369392383787)]:
            with self.subTest(n=n):
                self.assertAlmostEqual(confiabilidade(n), esperado)
        self.assertEqual(confiabilidade(3, 0), 0)
        self.assertEqual(confiabilidade(3, 1), 1)

    def test_custo_com_historico_calculado_manualmente(self):
        tokens = dict(sistema_tokens=100, numero_ferramentas=2, tokens_por_ferramenta=50,
                      consulta_tokens=20, retorno_ferramenta_tokens=30, saida_por_etapa_tokens=10)
        custo = estimar_custo(3, tokens, dict(entrada_por_milhao=2, saida_por_milhao=4))
        # Aula: entradas 220, 250, 280. A saída não é somada ao histórico.
        self.assertEqual(custo['entrada_agente'], 750)
        self.assertEqual(custo['entrada_ultimo_passo'], 280)
        self.assertEqual(custo['saida_agente'], 30)
        self.assertAlmostEqual(custo['custo_agente'], 0.00162)
        self.assertAlmostEqual(custo['custo_um_passo'], 0.00048)
        self.assertAlmostEqual(custo['fator'], 3.375)

    def test_numeros_tabela_original_ambos_modelos(self):
        # Valores de referência conferidos diretamente na tabela fornecida.
        casos = [(1, 1000, 1000, 0.000344), (5, 2000, 7500, 0.00222),
                 (10, 3250, 21250, 0.00569), (20, 5750, 67500, 0.01638),
                 (40, 10750, 235000, 0.05276)]
        for modelo, multiplicador in [('gpt-5.6-luna', 1), ('gpt-5.6-terra', 10)]:
            for n, ultimo, entrada, custo_esperado in casos:
                with self.subTest(modelo=modelo, n=n):
                    custo = estimar_custo(n, parametros_aula(), precos_aula(modelo))
                    self.assertEqual(custo['entrada_ultimo_passo'], ultimo)
                    self.assertEqual(custo['entrada_agente'], entrada)
                    self.assertAlmostEqual(custo['custo_agente'], custo_esperado * multiplicador)
        custo = estimar_custo(40, parametros_aula(), precos_aula('gpt-5.6-luna'))
        self.assertAlmostEqual(custo['fator'], 153.37209302325581)

    def test_tabelas_reproduzem_saida_script_fornecido(self):
        original = subprocess.run([sys.executable, str(BASE / 'calcular_tabelas_original.py')],
                                  check=True, capture_output=True, text=True)
        self.assertEqual(tabelas_originais(), original.stdout)

    def test_mensais_pela_tabela_original(self):
        linhas = calcular(self.config)
        for p, esperado in zip(linhas, [0.3352, 0.22512, 0.2276]):
            self.assertAlmostEqual(p['custo_mensal'], esperado)
        self.config['modelo_aula'] = 'gpt-5.6-terra'
        for p, esperado in zip(calcular(self.config), [3.352, 2.2512, 2.276]):
            self.assertAlmostEqual(p['custo_mensal'], esperado)

    def test_personalizacao_nao_altera_estimativa_da_aula(self):
        antes = calcular(self.config)[0]
        self.config['processos'][0]['tokens']['sistema_tokens'] *= 2
        depois = calcular(self.config)[0]
        self.assertEqual(antes['custo_mensal'], depois['custo_mensal'])
        self.assertGreater(depois['personalizado']['custo_mensal'], antes['personalizado']['custo_mensal'])

    def test_custo_zero_nao_divide_por_zero(self):
        p = self.config['processos'][0]
        custo = estimar_custo(4, p['tokens'], dict(entrada_por_milhao=0, saida_por_milhao=0))
        self.assertIsNone(custo['fator'])

    def test_dados_invalidos(self):
        alteracoes = [
            lambda c: c.update(probabilidade_por_etapa=1.1),
            lambda c: c['processos'][0].update(volume_mensal=-1),
            lambda c: c['processos'][0].update(volume_mensal=True),
            lambda c: c['processos'][0].update(etapas=[]),
            lambda c: c['processos'][0]['tokens'].update(consulta_tokens=float('nan')),
            lambda c: c['precos'].update(entrada_por_milhao=-1),
            lambda c: c.update(piloto_id='inexistente'),
            lambda c: c.update(recusado_id=c['piloto_id']),
            lambda c: c.update(modelo_aula='inexistente'),
        ]
        for alterar in alteracoes:
            config = copy.deepcopy(self.config)
            alterar(config)
            with self.subTest(config=config), self.assertRaises(ValueError):
                calcular(config)

    def test_volume_altera_mensal_sem_alterar_custo_unitario(self):
        antes = calcular(self.config)[0]
        self.config['processos'][0]['volume_mensal'] *= 2
        depois = calcular(self.config)[0]
        self.assertEqual(depois['custo_agente'], antes['custo_agente'])
        self.assertEqual(depois['custo_mensal'], 2 * antes['custo_mensal'])

    def test_exportacao_relatorio_e_parecer(self):
        linhas = calcular(self.config)
        texto = relatorio(self.config, linhas)
        self.assertIn('81,45%', texto)
        self.assertIn('59,87%', texto)
        self.assertIn('DADOS HIPOTÉTICOS', texto)
        self.assertIn('Não se recomenda automatizar integralmente', parecer(self.config, linhas))
        with tempfile.TemporaryDirectory() as pasta:
            exportar(Path(pasta), self.config, linhas, texto)
            self.assertEqual((Path(pasta) / 'relatorio.txt').read_text(encoding='utf-8'), texto)
            self.assertTrue((Path(pasta) / 'parecer.txt').exists())
            self.assertEqual((Path(pasta) / 'tabelas_originais.txt').read_text(encoding='utf-8'), tabelas_originais())
            self.assertTrue((Path(pasta) / 'desafio_opcional.csv').exists())
            self.assertEqual(len((Path(pasta) / 'tabelas.csv').read_text(encoding='utf-8-sig').splitlines()), 4)


if __name__ == '__main__':
    unittest.main()
