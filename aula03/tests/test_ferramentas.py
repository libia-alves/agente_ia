"""Verifica pontuação, custos e execução real do middleware sem consumir API."""
import unittest
from langchain_core.messages import AIMessage
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from lab_ferramentas.agente import executar, pontuar, custo, verificar_origens
from lab_ferramentas.exemplo04 import validar, resumir
from lab_ferramentas.ferramentas import Acrescimo
from pydantic import ValidationError

class ModeloRoteiro(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self

CFG = dict(modelo='simulado', reasoning_effort='low', entrada=.1, cache=.01, saida=.5)
USO = dict(input_tokens=100, output_tokens=10, total_tokens=110)

def mensagem(content='', chamadas=None):
    return AIMessage(content=content, tool_calls=chamadas or [], usage_metadata=USO)

def chamada(nome, args, ident):
    return dict(name=nome,args=args,id=ident,type='tool_call')

class FerramentasTests(unittest.TestCase):
    def test_conjunto_e_esquema(self):
        self.assertEqual(len(validar()['consultas']),12)
        self.assertTrue(all(f.description for f in Acrescimo.model_fields.values()))
        for valor in (-1,0,float('nan'),float('inf')):
            with self.assertRaises(ValidationError):
                Acrescimo(valor_base=valor,percentual=10)

    def test_nota_tolera_grafia_mas_nao_valor_ausente_booleano_ou_errado(self):
        q=validar()['consultas'][0]
        r=dict(saida=dict(resposta='PANTANAL SERVIÇOS',valor=100000,situacao='ok'),erro=None,
               ferramentas=[dict(nome='consultar_contrato')])
        self.assertTrue(pontuar(r,q)['acerto'])
        for v in (True,float('nan'),100001,None):
            r['saida']['valor']=v
            self.assertFalse(pontuar(r,q)['acerto'])
        del r['saida']['valor']
        self.assertFalse(pontuar(r,q)['acerto'])
        r['ferramentas']*=2
        self.assertFalse(pontuar(r,q)['ferramenta_certa'])

    def test_cache_e_cauda(self):
        self.assertAlmostEqual(custo(dict(entrada=100,cache=20,saida=10),CFG),.0000132)
        r=dict(uso_completo=False,custo_usd=None,acerto=False,ferramenta_certa=False,erro='TimeoutError',passos=1,tempo_s=.2)
        self.assertIsNone(resumir([r],CFG,1000)['custo_total_usd'])

    def test_barreira_retorna_toolmessage_e_proveniencia_remove_falso_positivo(self):
        q=validar()['consultas'][6]
        def modelo():
            return ModeloRoteiro(responses=[
                mensagem(chamadas=[chamada('consultar_contrato',{'numero':'LAB-001'},'c1')]),
                mensagem(chamadas=[chamada('simular_acrescimo',{'valor_base':100000,'percentual':10},'c2')]),
                mensagem('{"resposta":"Simulação","valor":110000,"situacao":"ok"}')])
        simples=executar(q['pergunta'],CFG,'simples',modelo=modelo())
        rastreada=executar(q['pergunta'],CFG,'proveniencia',modelo=modelo())
        self.assertIsNone(simples['erro']) # resposta foi possível após ToolMessage de bloqueio
        self.assertTrue(simples['ferramentas'][1]['bloqueada'])
        self.assertFalse(rastreada['ferramentas'][1]['bloqueada'])
        self.assertEqual(rastreada['ferramentas'][1]['resultado_confiavel']['total'],110000)
        self.assertIn('consultar_contrato.valor',rastreada['ferramentas'][1]['origens']['valor_base'])
        self.assertEqual(rastreada['uso']['entrada'],300)
        self.assertEqual(rastreada['passos'],3)

    def test_resposta_em_blocos_de_texto(self):
        modelo=ModeloRoteiro(responses=[AIMessage(content=[{'type':'text','text':'{"resposta":"Olá","valor":null,"situacao":"ok"}'}],usage_metadata=USO)])
        r=executar('Olá',CFG,modelo=modelo)
        self.assertIsNone(r['erro'])
        self.assertEqual(r['saida']['valor'],None)
        self.assertTrue(r['uso_completo'])

    def test_numero_inventado_bloqueado_e_roles_distintos(self):
        fontes=verificar_origens({'valor_base':999,'percentual':10},'Contrato LAB-999 e acréscimo de 10%',[],'proveniencia')
        self.assertIsNone(fontes['valor_base'])
        modelo=ModeloRoteiro(responses=[
            mensagem(chamadas=[chamada('simular_acrescimo',{'valor_base':50000,'percentual':10},'a')]),
            mensagem('{"resposta":"Informe o valor","valor":null,"situacao":"dados_insuficientes"}')])
        r=executar('Simule um acréscimo de 10%; não tenho valor.',CFG,'proveniencia',modelo=modelo)
        self.assertTrue(r['ferramentas'][0]['bloqueada'])
        self.assertIsNone(r['erro'])

if __name__=='__main__':
    unittest.main()
