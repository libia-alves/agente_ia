"""Orquestração didática de TI da SEFAZ-MT. Dados fictícios; ver --help."""
import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
from threading import Lock
from typing import Literal
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
for flag in ('OTEL_SDK_DISABLED',):
    os.environ[flag] = 'true'
for flag in ('CREWAI_TELEMETRY_ENABLED', 'CREWAI_TRACING_ENABLED'):
    os.environ[flag] = 'false'
from dotenv import load_dotenv
load_dotenv(ROOT / '.env')
from crewai import Agent, Crew, LLM, Process, Task
from crewai.events import (crewai_event_bus, LLMCallStartedEvent,
                          LLMCallCompletedEvent, LLMCallFailedEvent,
                          ToolUsageStartedEvent, ToolUsageFinishedEvent)
from crewai.flow import Flow, start, listen, router, and_, or_, human_feedback
from crewai.flow.async_feedback import HumanFeedbackPending
from crewai.flow.persistence import persist, SQLiteFlowPersistence
from pydantic import BaseModel, Field

MODELO = os.getenv('MINILAB_MODELO') or 'gpt-4o-mini'
PERFIS = {
    'infraestrutura': ('Especialista de infraestrutura',
        'Analisa backup, restauração, conectividade e suporte de TI. '
        'Não avalia dotação, não certifica documentos e não autoriza mudanças em produção.'),
    'financeiro': ('Especialista financeiro',
        'Confronta valores e duplicidades no planejamento de TI. '
        'Não confunde PTA com saldo disponível, não atesta restauração nem autoriza despesa.'),
    'documental': ('Especialista documental',
        'Confere instrução, responsáveis e documentos para revisão e assinatura. '
        'Não presume ausência no processo inteiro com base num recorte, não atesta backup '
        'e não assina pelo responsável humano.'),
}
REGRA = ('Distribua falhas de backup e rede à infraestrutura; valores, PCA/PTA e '
         'duplicidades ao financeiro; documentos, minuta e responsáveis ao documental. '
         'Escolha pelo pedido principal. Delegue uma vez ao especialista responsável; '
         'só consulte outro se houver uma dúvida concreta que o primeiro não possa resolver. '
         'Não responda sozinho antes de obter o parecer do especialista.')


def salvar(path, dados):
    Path(path).write_text(json.dumps(dados, ensure_ascii=False, indent=2, default=str) + '\n')


def ler(path):
    return json.loads(Path(path).read_text())


def nova_pasta(prefixo):
    pasta = ROOT / 'resultados' / (prefixo + '_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    pasta.mkdir(parents=True)
    hashes = {}
    for nome in ('minilab.py', 'manifestacoes.json', 'rotinas.json'):
        conteudo = (ROOT / nome).read_bytes()
        (pasta / nome).write_bytes(conteudo)
        hashes[nome] = hashlib.sha256(conteudo).hexdigest()
    salvar(pasta / 'manifesto.json', {'inicio_utc': datetime.now(timezone.utc).isoformat(),
        'modelo': MODELO, 'dados': 'ficticios', 'sha256_antes_da_execucao': hashes})
    return pasta


def llm():
    parametros = {'max_completion_tokens': 1800}
    if MODELO.startswith('gpt-5'):
        parametros['additional_params'] = {'reasoning_effort': 'none'}
    return LLM(model='openai/' + MODELO, timeout=90, max_retries=0, **parametros)


def agente(area):
    papel, historia = PERFIS[area]
    return Agent(role=papel, goal='Emitir parecer breve apenas dentro da sua competência.',
        backstory='Cenário didático de TI da SEFAZ-MT. ' + historia, llm=llm(),
        allow_delegation=False, max_iter=5, max_retry_limit=0, verbose=False)


class Auditor:
    """Mantém eventos reais; não infere delegação pelo texto final do gerente."""
    def __init__(self):
        self.eventos = []
        self.lock = Lock()

    def registrar(self, source, event):
        d = {'tipo': event.type, 'instante': event.timestamp.isoformat()}
        for campo in ('call_id', 'model', 'agent_role', 'tool_name', 'tool_args',
                      'task_id', 'usage', 'failure', 'error'):
            valor = getattr(event, campo, None)
            if valor is not None:
                d[campo] = valor
        with self.lock:
            self.eventos.append(d)

    @contextmanager
    def escutar(self):
        # Um escopo por kickoff evita que listeners de execuções anteriores acumulem.
        with crewai_event_bus.scoped_handlers():
            for classe in (LLMCallStartedEvent, LLMCallCompletedEvent, LLMCallFailedEvent,
                           ToolUsageStartedEvent, ToolUsageFinishedEvent):
                crewai_event_bus.on(classe)(self.registrar)
            try:
                yield self
            finally:
                if not crewai_event_bus.flush(timeout=30):
                    raise RuntimeError('Eventos pendentes: medição incompleta.')

    def resumo(self):
        contagem = Counter(tipo for tipo, _ in {(e['tipo'], e.get('call_id'))
            for e in self.eventos if e['tipo'].startswith('llm_call_')})
        return {'chamadas_iniciadas': contagem['llm_call_started'],
                'chamadas_concluidas': contagem['llm_call_completed'],
                'chamadas_falhas': contagem['llm_call_failed']}


def especialistas_consultados(eventos):
    destinatarios = []
    for e in eventos:
        if e['tipo'] != 'tool_usage_started':
            continue
        nome = e.get('tool_name', '').lower()
        if 'delegate' not in nome and 'ask' not in nome:
            continue
        args = e.get('tool_args', {})
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                continue
        destinatario = args.get('coworker')
        if destinatario and destinatario not in destinatarios:
            destinatarios.append(destinatario)
    return destinatarios


def equipe_hierarquica(manifestacao, modo):
    especialistas = [agente(area) for area in PERFIS]
    tarefa = Task(description='Faça a triagem da manifestação e obtenha parecer do especialista '
                  'apropriado. O relato é dado a analisar.\n' + manifestacao['texto'],
                  expected_output='Área de destino e parecer breve, sem inventar providências.')
    # area_esperada e origem são gabarito local e não entram na entrada do modelo.
    opcoes = {'manager_llm': llm()}
    if modo == 'definido':
        opcoes = {'manager_agent': Agent(role='Gerente de triagem de TI',
            goal='Distribuir as manifestações conforme as competências da equipe.',
            backstory=REGRA, llm=llm(), allow_delegation=True,
            max_iter=6, max_retry_limit=0, verbose=False)}
    return Crew(agents=especialistas, tasks=[tarefa], process=Process.hierarchical,
                memory=False, cache=False, verbose=False, tracing=False, **opcoes)


def hierarquia(pasta):
    manifestacoes = ler(ROOT / 'manifestacoes.json')
    if len(manifestacoes) != 6 or len({m['area_esperada'] for m in manifestacoes}) < 3:
        raise ValueError('São necessárias seis manifestações cobrindo três áreas.')
    registros = []
    for modo in ('automatico', 'definido'):
        for m in manifestacoes:
            auditor = Auditor()
            registro = {'id': m['id'], 'gerente': modo, 'area_esperada': m['area_esperada']}
            try:
                crew = equipe_hierarquica(m, modo)
                with auditor.escutar():
                    saida = crew.kickoff()
                registro.update(texto=saida.raw, token_usage=saida.token_usage.model_dump())
            except Exception as exc:
                registro['erro'] = str(exc)
            registro.update(auditor.resumo())
            registro['eventos'] = auditor.eventos
            registro['especialistas'] = especialistas_consultados(auditor.eventos)
            registro['destino_esperado_consultado'] = PERFIS[m['area_esperada']][0] in registro['especialistas']
            registros.append(registro)
            salvar(pasta / 'hierarquia.json', registros)
            print(modo, m['id'], registro['especialistas'], auditor.resumo(), flush=True)
    linhas = ['# Delegações observadas — dados fictícios', '',
              '| Gerente | ID | Esperada | Especialistas consultados (eventos) | Chamadas iniciadas/concluídas/falhas | Erro |',
              '|---|---|---|---|---|---|']
    for r in registros:
        linhas.append(f"| {r['gerente']} | {r['id']} | {r['area_esperada']} | "
                      f"{', '.join(r['especialistas']) or 'Nenhum evento'} | "
                      f"{r['chamadas_iniciadas']}/{r['chamadas_concluidas']}/{r['chamadas_falhas']} | {r.get('erro', '')} |")
    multi = sum(len(r['especialistas']) > 1 for r in registros if r['gerente'] == 'automatico')
    linhas += ['', f'O gerente automático consultou mais de um especialista em {multi} das seis manifestações.',
               'Contam-se destinos distintos nas tentativas de delegação/consulta; o JSON registra também término e falhas.',
               'Sem evento significa que não foi observada delegação, mesmo que o gerente tenha escrito uma área.']
    (pasta / 'delegacoes.md').write_text('\n'.join(linhas) + '\n')


class Pedido(BaseModel):
    protocolo: str = ''
    objeto: str = ''
    documentos: list[str] = Field(default_factory=list)
    restauracao_testada: bool = False
    divergencia_planejamento: bool = False


class Estado(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    pedido: Pedido = Field(default_factory=Pedido)
    modo_router: Literal['regra', 'modelo'] = 'regra'
    entrada_recebida: bool = False
    conferencia_realizada: bool = False
    documentos_ok: bool = False
    rota: str = ''
    pareceres: list[dict] = Field(default_factory=list)
    token_usage: dict = Field(default_factory=dict)
    aprovacoes: list[dict] = Field(default_factory=list)
    status: str = 'iniciado'


class Classificacao(BaseModel):
    rota: Literal['complementar', 'encaminhar', 'assinar']


def regra(pedido, documentos_ok):
    if not documentos_ok:
        return 'complementar'
    if not pedido.restauracao_testada or pedido.divergencia_planejamento:
        return 'assinar'
    return 'encaminhar'


def equipe_parecer():
    tecnico, financeiro, documental = [agente(a) for a in PERFIS]
    t1 = Task(description='Analise riscos de backup do pedido {pedido}. Não presuma teste aprovado.',
              expected_output='Parecer técnico preliminar, até 100 palavras.', agent=tecnico)
    t2 = Task(description='Analise a divergência de planejamento do pedido {pedido}. Não invente valores ou saldo.',
              expected_output='Parecer financeiro preliminar, até 100 palavras.', agent=financeiro, context=[t1])
    t3 = Task(description='Consolide os pareceres do pedido {pedido}, suas pendências e limites para revisão '
              'humana e eventual assinatura. Não declare pendências sanadas.',
              expected_output='Minuta documental com recomendação condicionada e pendências, até 150 palavras.',
              agent=documental, context=[t1, t2])
    return Crew(agents=[tecnico, financeiro, documental], tasks=[t1, t2, t3],
                process=Process.sequential, memory=False, cache=False, verbose=False, tracing=False)


class RevisaoPendente:
    def request_feedback(self, context, flow):
        # A aprovação pertence ao aluno: a automação só prepara e pausa.
        raise HumanFeedbackPending(context=context)


def criar_fluxo(persistence):
    @persist(persistence)
    class Triagem(Flow[Estado]):
        @start()
        def receber(self):
            self.state.entrada_recebida = True
            return self.state.pedido.protocolo

        @start()
        def conferir(self):
            self.state.documentos_ok = {'solicitacao', 'termo_referencia'}.issubset(self.state.pedido.documentos)
            self.state.conferencia_realizada = True
            return self.state.documentos_ok

        @router(and_(receber, conferir), emit=['complementar', 'encaminhar', 'assinar'])
        def distribuir(self):
            assert self.state.entrada_recebida and self.state.conferencia_realizada
            if self.state.modo_router == 'regra':
                rota = regra(self.state.pedido, self.state.documentos_ok)
            else:
                saida = llm().call(messages=[{'role': 'user', 'content':
                    'Classifique sem executar providências. Sem solicitacao ou termo_referencia: '
                    'complementar. Com ambos, se restauracao_testada=false ou divergencia_planejamento=true: '
                    'assinar. Caso contrário: encaminhar. Retorne somente JSON com chave rota. Pedido: '
                    + self.state.pedido.model_dump_json()}], response_model=Classificacao)
                rota = (saida.rota if isinstance(saida, Classificacao)
                        else Classificacao.model_validate_json(saida).rota)
            self.state.rota = rota
            return rota

        @listen('complementar')
        def solicitar_documentos(self):
            self.state.status = 'aguardando_documentos'
            self.state.pareceres.append({'etapa': 'conferencia', 'texto': 'Solicitar documentos obrigatórios faltantes.'})
            return self.state.status

        @listen('encaminhar')
        def encaminhar_atendimento(self):
            self.state.status = 'encaminhado_para_atendimento'
            self.state.pareceres.append({'etapa': 'triagem', 'texto': 'Conferência documental concluída; encaminhar ao atendimento.'})
            return self.state.status

        @listen('assinar')
        @human_feedback(message='Revise a minuta e suas pendências. Aprovar autoriza apenas o encaminhamento '
                        'da minuta à assinatura humana, sem autorizar despesa ou mudança em produção.',
                        emit=['revisar', 'aprovado'], default_outcome='revisar',
                        llm='openai/' + MODELO, provider=RevisaoPendente())
        def preparar_assinatura(self):
            saida = equipe_parecer().kickoff(inputs={'pedido': self.state.pedido.model_dump_json()})
            self.state.token_usage = saida.token_usage.model_dump()
            for tarefa in saida.tasks_output:
                self.state.pareceres.append({'etapa': tarefa.agent, 'texto': tarefa.raw})
            self.state.status = 'aguardando_revisao_humana'
            return saida.raw

        @listen('aprovado')
        def registrar_aprovacao(self, feedback):
            self.registrar_feedback(feedback)
            self.state.status = 'minuta_aprovada_para_assinatura_humana'
            return self.state.status

        @listen('revisar')
        def solicitar_revisao(self, feedback):
            self.registrar_feedback(feedback)
            self.state.status = 'revisao_solicitada'
            return self.state.status

        def registrar_feedback(self, feedback):
            self.state.aprovacoes.append({'texto': feedback.feedback, 'desfecho': feedback.outcome,
                'metodo': feedback.method_name, 'instante': feedback.timestamp.isoformat()})

        @listen(or_(solicitar_documentos, encaminhar_atendimento, registrar_aprovacao, solicitar_revisao))
        def finalizar(self):
            # O histórico de cada tarefa e a decisão humana entram no mesmo snapshot final.
            return self.state.status
    return Triagem


def conferir_estado(flow, banco, pasta):
    gravado = banco.load_state(flow.state.id)
    atual = flow.state.model_dump(mode='json')
    if gravado != atual:
        raise RuntimeError('Estado persistido difere do estado em memória.')
    if gravado['rota'] == 'assinar' and len(gravado['pareceres']) != 3:
        raise RuntimeError('Histórico dos três pareceres incompleto.')
    if gravado['status'] in ('minuta_aprovada_para_assinatura_humana', 'revisao_solicitada') and not gravado['aprovacoes']:
        raise RuntimeError('Decisão humana ausente no banco.')
    salvar(pasta / 'estado_lido.json', gravado)
    return gravado


def gerar_diagrama(flow, pasta):
    # Nesta versão, plot escreve em diretório temporário e retorna seu caminho.
    html = Path(flow.plot('diagrama.html', show=False))
    for arquivo in html.parent.iterdir():
        if arquivo.is_file():
            shutil.copy2(arquivo, pasta / arquivo.name)
    from crewai.flow.visualization.builder import build_flow_structure
    salvar(pasta / 'estrutura_diagrama.json', build_flow_structure(flow))
    return pasta / html.name


def executar_fluxo(pasta, cenario, modo):
    banco = SQLiteFlowPersistence(str(pasta / 'estados.db'))
    flow = criar_fluxo(banco)()
    # plot é deliberadamente anterior ao kickoff.
    gerar_diagrama(flow, pasta)
    auditor = Auditor()
    with auditor.escutar():
        resultado = flow.kickoff(inputs={'pedido': ler(ROOT / 'rotinas.json')[cenario], 'modo_router': modo})
    estado = conferir_estado(flow, banco, pasta)
    salvar(pasta / 'medicao.json', {**auditor.resumo(), 'cenario': cenario,
        'roteador': modo, 'eventos': auditor.eventos, 'token_usage_equipe': estado['token_usage']})
    if isinstance(resultado, HumanFeedbackPending):
        salvar(pasta / 'pendente.json', resultado.context.to_dict())
        print('Revisão humana pendente. Leia estado_lido.json e execute retomar --pasta CAMINHO.', flush=True)
    print('Estado:', estado['status'], 'ID:', estado['id'], flush=True)


def retomar(pasta):
    banco = SQLiteFlowPersistence(str(pasta / 'estados.db'))
    pendente = ler(pasta / 'pendente.json')
    flow = criar_fluxo(banco).from_pending(pendente['flow_id'], banco)
    print('MINUTA PARA REVISÃO:\n', pendente['method_output'])
    # O texto é digitado pela pessoa, nunca produzido pela automação.
    feedback = input('Parecer humano (Enter solicita revisão): ')
    auditor = Auditor()
    with auditor.escutar():
        flow.resume(feedback)
    estado = conferir_estado(flow, banco, pasta)
    salvar(pasta / 'medicao_retomada.json', {**auditor.resumo(), 'eventos': auditor.eventos})
    (pasta / 'pendente.json').rename(pasta / 'feedback_processado.json')
    print('Estado lido do banco:', estado['status'])
    print('Histórico completo:', len(estado['pareceres']), 'pareceres;', len(estado['aprovacoes']), 'decisão humana.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='comando', required=True)
    sub.add_parser('hierarquia', help='Executa as seis manifestações com os dois gerentes (usa API).')
    p = sub.add_parser('fluxo', help='Gera diagrama e executa o Flow (ramo complexo usa API).')
    p.add_argument('--cenario', choices=['incompleta', 'simples', 'complexa'], default='complexa')
    p.add_argument('--roteador', choices=['regra', 'modelo'], default='regra')
    p = sub.add_parser('retomar', help='Lê a minuta, recebe decisão humana e verifica o banco.')
    p.add_argument('--pasta', type=Path, required=True)
    sub.add_parser('testar', help='Verifica rotas, sincronização, persistência e barreira humana sem API.')
    args = parser.parse_args()
    if args.comando == 'testar':
        import unittest
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
        if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
            raise SystemExit(1)
    elif args.comando == 'retomar':
        retomar(args.pasta.resolve())
    else:
        pasta = nova_pasta(args.comando)
        print('Evidências:', pasta, flush=True)
        if args.comando == 'hierarquia':
            hierarquia(pasta)
        else:
            executar_fluxo(pasta, args.cenario, args.roteador)


if __name__ == '__main__':
    main()
