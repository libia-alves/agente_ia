import unittest
import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from minilab import CAMPOS, correto, custo, extrair, pontuar, resumir, main

GABARITO = dict(numero='OF-1', data='2026-01-01', valor=None,
                partes=['Remetente', 'Destinatário'], objeto='Teste', prioridade='media')


class MedicaoTests(unittest.TestCase):
    def test_chave_ausente_nao_e_null(self):
        self.assertFalse(pontuar({}, GABARITO)['valor'])
        self.assertEqual(sum(pontuar(GABARITO, GABARITO).values()), len(CAMPOS))

    def test_partes_preservam_ordem_e_valor_nao_aceita_booleano(self):
        self.assertFalse(correto('partes', list(reversed(GABARITO['partes'])), GABARITO['partes']))
        self.assertFalse(correto('valor', True, 1.0))
        self.assertFalse(correto('valor', float('nan'), 10))
        self.assertTrue(correto('valor', 1.001, 1.0))

    def test_cache_tem_preco_proprio(self):
        self.assertAlmostEqual(custo(dict(entrada=100, cache=20, saida=10),
                                     dict(entrada=2, cache=1, saida=4)), 0.00022)

    def test_parser_usa_uma_chamada_e_preserva_tokens_quando_json_invalido(self):
        chamadas = []
        def invocar(mensagens):
            chamadas.append(mensagens)
            return AIMessage(content='isto não é JSON', usage_metadata=dict(input_tokens=100, output_tokens=20, total_tokens=120))
        prompt = ChatPromptTemplate.from_messages([('human', '{documento}')])
        r = extrair('parser', dict(id='1', texto='Texto', gabarito=GABARITO),
                    None, RunnableLambda(invocar), prompt)
        self.assertEqual(len(chamadas), 1)
        self.assertTrue(r['uso_disponivel'])
        self.assertEqual((r['entrada'], r['saida']), (100, 20))
        self.assertIsNotNone(r['erro'])

    def test_resposta_sdk_invalida_preserva_consumo(self):
        cliente=Mock()
        cliente.chat.completions.create.return_value=SimpleNamespace(
            usage=SimpleNamespace(prompt_tokens=20,completion_tokens=4,prompt_tokens_details=None),
            choices=[SimpleNamespace(message=SimpleNamespace(content='invalido'))],model='teste')
        r=extrair('sdk',dict(id='1',texto='Texto',gabarito=GABARITO),cliente,None,None)
        self.assertEqual(cliente.chat.completions.create.call_count,1)
        self.assertTrue(r['uso_disponivel'])
        self.assertEqual(r['entrada'],20)
        self.assertEqual(r['erro'],'JSONDecodeError')

    def test_erro_de_rede_nao_parece_custo_zero(self):
        cliente=Mock()
        cliente.chat.completions.create.side_effect=TimeoutError()
        r=extrair('sdk',dict(id='1',texto='Texto',gabarito=GABARITO),cliente,None,None)
        resumo=resumir('sdk',[r],dict(entrada=.2,cache=.02,saida=1.2),1000)
        self.assertIsNone(resumo['custo_usd'])
        self.assertIsNone(resumo['custo_mensal_usd'])
        self.assertEqual(resumo['invalidos'],1)

    def test_fluxo_completo_com_api_simulada(self):
        # Dados sintéticos só para o teste; não são o conjunto de entrega.
        with tempfile.TemporaryDirectory() as temporario:
            raiz=Path(temporario)
            dados=raiz/'documentos.jsonl'
            documentos=[dict(id=str(i),texto='Teste',fonte='fixture do teste',
                             casos_dificeis=['valor_por_extenso'] if i==1 else [],
                             gabarito=dict(GABARITO,valor=20.0 if i==1 else None)) for i in range(10)]
            dados.write_text('\n'.join(json.dumps(d) for d in documentos))
            (raiz/'configuracao').mkdir()
            (raiz/'configuracao/modelo_destino.py').write_text('DESTINO = "fixture"\n')
            with patch.object(sys,'argv',['minilab.py','congelar','--dados',str(dados)]):
                main()
            self.assertTrue(dados.with_suffix('.manifesto.json').exists())
            def api_simulada(tipo, doc, *_):
                return dict(id=doc['id'],entrada=10,saida=5,cache=0,uso_disponivel=True,
                            extraido=doc['gabarito'],erro=None,latencia_s=0.5,
                            corretos={k:True for k in CAMPOS})
            with patch('minilab.RAIZ',raiz), patch.dict(os.environ,{'OPENAI_API_KEY':'teste'}), \
                 patch('minilab.OpenAI'), patch('minilab.init_chat_model'), \
                 patch('minilab.extrair',side_effect=api_simulada) as chamada, \
                 patch.object(sys,'argv',['minilab.py','executar','--dados',str(dados),'--volume-mensal','1000']):
                main()
            self.assertEqual(chamada.call_count,33)  # 30 medidas + 3 aquecimentos
            pasta=next((raiz/'resultados').iterdir())
            resultado=json.loads((pasta/'resultado.json').read_text())
            self.assertEqual(len(resultado['resultados']),3)
            self.assertEqual(len((pasta/'extracoes.jsonl').read_text().splitlines()),30)
            self.assertTrue((pasta/'tabela.md').exists())
            self.assertEqual(resultado['resultados'][0]['acertos'],60)
            self.assertAlmostEqual(resultado['resultados'][0]['custo_mensal_usd'],0.008)


if __name__ == '__main__':
    unittest.main()
