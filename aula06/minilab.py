"""Executa o Mini LAB e salva evidências sem inventar resultados de API."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import time
import types

from agno.agent import Agent
from agno.run.base import RunStatus
from atendimento import FUNCOES, INSTRUCAO, NOME_AGENTE, consultar_chamado, calcular_prazo
from configuracao import BASE, MODELO, PRECO_ENTRADA, PRECO_SAIDA, modelo, MENSAGEM_PADRAO
from privacidade import filtro_pii, mascarar_antes_do_agente
from registro import extrair


def salvar(caminho, dados):
    Path(caminho).write_text(json.dumps(dados, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')


def construir(paralelas=False, ferramentas=None, debug=False, filtros=True):
    return Agent(name=NOME_AGENTE, model=modelo(request_params={'parallel_tool_calls': paralelas}),
                 tools=FUNCOES if ferramentas is None else ferramentas, instructions=f"Seu nome é {NOME_AGENTE}.\n" + INSTRUCAO,
                 tool_call_limit=6, telemetry=False, debug_mode=debug,
                 pre_hooks=[filtro_pii()] if filtros else None)


def executar(agente, texto):
    inicio = time.perf_counter()
    # CPF etc. são filtrados antes de entrar no logger do framework.
    try:
        registro = extrair(agente.run(mascarar_antes_do_agente(texto)))
    except Exception as erro:
        registro = {'status': 'exception', 'resposta': MENSAGEM_PADRAO,
                    'tipo_erro': type(erro).__name__, 'custo_estimado_usd': None}
    registro['segundos'] = round(time.perf_counter() - inicio, 3)
    return registro


def pasta_nova(etapa):
    pasta = BASE / 'resultados' / (etapa + '_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    pasta.mkdir(parents=True)
    hashes = {}
    for nome in ['minilab.py', 'atendimento.py', 'ferramentas.py', 'configuracao.py', 'privacidade.py', 'registro.py',
                 'revisor.py', 'app_revisor.py', 'dados_minilab.json', 'manual_setor.json']:
        arquivo = BASE / nome
        shutil.copy2(arquivo, pasta / nome)
        hashes[nome] = hashlib.sha256(arquivo.read_bytes()).hexdigest()
    salvar(pasta / 'manifesto.json', {'inicio_utc': datetime.now(timezone.utc).isoformat(),
           'origem_dados': 'ficticia', 'modelo': MODELO, 'preco_entrada_usd_milhao': PRECO_ENTRADA,
           'preco_saida_usd_milhao': PRECO_SAIDA, 'sha256_antes_execucao': hashes})
    return pasta


def atendimento(pasta, dados):
    registros = []
    for item in dados['perguntas']:
        registro = {**item, **executar(construir(), item['texto'])}
        registros.append(registro)
        salvar(pasta / 'atendimento.json', registros)
        print(item['id'], registro['status'], flush=True)
    concluidas = [r for r in registros if r['status'] == 'COMPLETED' or r['status'] == 'completed']
    custos = [r['custo_estimado_usd'] for r in concluidas if r.get('custo_estimado_usd') is not None]
    media = sum(custos) / len(custos) if custos else None
    volume = os.getenv('PERGUNTAS_DIA') or dados['perguntas_dia']
    volume = int(volume) if volume else None
    dias = int(os.getenv('DIAS_MES') or dados['dias_mes'])
    salvar(pasta / 'custo_mensal.json', {'respostas_concluidas': len(concluidas), 'total_perguntas': len(registros),
           'custo_medio_usd': media, 'perguntas_dia': volume, 'dias_mes': dias,
           'custo_mensal_usd': media * volume * dias if media is not None and volume else None,
           'formula': 'perguntas_dia × dias_mes × custo_medio_usd',
           'simulacao_50_perguntas_dia_usd': media * 50 * dias if media is not None else None,
           'nota': 'Estimativa por tokens sem desconto de cache; volume de 50/dia é apenas hipótese. Falhas ficam fora da média; métricas ausentes não são zero.'})


PERGUNTA_ENCADEADA = 'Quando vencem cinco dias úteis contados da última movimentação do chamado 2026009012?'


def encadeamento(pasta):
    registros = []
    for paralelas in [True, False]:
        for repeticao in range(1, 4):
            r = executar(construir(paralelas=paralelas), PERGUNTA_ENCADEADA)
            calculos = [t for t in r.get('ferramentas', []) if t['nome'] == 'calcular_prazo']
            datas = [t['argumentos'].get('data_inicial') for t in calculos]
            r.update(paralelas=paralelas, repeticao=repeticao, dados_segunda_ferramenta=datas,
                     data_esperada='2026-11-13', datas_corretas=bool(datas) and all(d == '2026-11-13' for d in datas))
            registros.append(r)
            salvar(pasta / 'encadeamento.json', registros)
            print('paralelas', paralelas, repeticao, r['status'], datas, flush=True)


def docstrings(pasta):
    registros = []
    curta = 'Use para saber em que etapa está um chamado de TI informado pelo cidadão.'
    for nome, doc in [('so_quando', curta), ('quando_e_retorno', consultar_chamado.__doc__)]:
        copia = types.FunctionType(consultar_chamado.__code__, consultar_chamado.__globals__,
                                   consultar_chamado.__name__, consultar_chamado.__defaults__)
        copia.__annotations__ = dict(consultar_chamado.__annotations__)
        copia.__doc__ = doc
        for repeticao in range(1, 4):
            r = executar(construir(ferramentas=[copia, calcular_prazo]), PERGUNTA_ENCADEADA)
            r.update(versao=nome, docstring=doc, repeticao=repeticao)
            datas = [t['argumentos'].get('data_inicial') for t in r.get('ferramentas', []) if t['nome'] == 'calcular_prazo']
            r['data_correta'] = bool(datas) and all(d == '2026-11-13' for d in datas)
            r['vencimento_correto'] = any(v in r['resposta'] for v in ['2026-11-20', '20/11/2026', '20 de novembro de 2026'])
            registros.append(r)
            salvar(pasta / 'docstrings.json', registros)
            print('docstring', nome, repeticao, r['status'], flush=True)


@contextmanager
def capturar_logs():
    linhas = []
    class Coletor(logging.Handler):
        def emit(self, record):
            linhas.append(self.format(record))
    coletor = Coletor()
    logger = logging.getLogger('agno')
    nivel = logger.level
    logger.addHandler(coletor)
    logger.setLevel(logging.DEBUG)
    try:
        yield linhas
    finally:
        logger.removeHandler(coletor)
        logger.setLevel(nivel)


def privacidade(pasta):
    pergunta = ('Meu CPF é 123.456.789-00, telefone (65) 99999-1234, '
                'e-mail pessoa@example.invalid, RG 12.345.678-9. '
                'Consulte o chamado 2026001234, processo 1234567-89.2026.8.11.0000.')
    registros = []
    for modo in ['sem_filtro', 'pre_hook', 'antes_e_pre_hook']:
        texto = mascarar_antes_do_agente(pergunta) if modo == 'antes_e_pre_hook' else pergunta
        with capturar_logs() as linhas:
            try:
                resposta = construir(debug=True, filtros=modo != 'sem_filtro').run(texto)
                status = resposta.status.value
            except Exception as erro:
                status = type(erro).__name__
        log = '\n'.join(linhas)
        (pasta / (modo + '.log')).write_text(log, encoding='utf-8')
        r = {'modo': modo, 'status': status, 'linhas': len(log.splitlines()),
             'cpf_no_log': '123.456.789-00' in log,
             'telefone_no_log': '(65) 99999-1234' in log,
             'email_no_log': 'pessoa@example.invalid' in log,
             'rg_no_log': '12.345.678-9' in log,
             'protocolo_preservado': '2026001234' in log,
             'processo_preservado': '1234567-89.2026.8.11.0000' in log}
        r['aprovado'] = bool(linhas) and not any(r[k] for k in ['cpf_no_log', 'telefone_no_log', 'email_no_log', 'rg_no_log']) and r['protocolo_preservado'] and r['processo_preservado']
        registros.append(r)
        salvar(pasta / 'privacidade.json', registros)
        print(modo, r, flush=True)


def erro_api(pasta):
    # Nome de modelo deliberadamente inexistente; sem depender de falha acidental.
    agente = Agent(model=modelo(id='modelo-inexistente-minilab-erro'), telemetry=False)
    try:
        resposta = agente.run('Responda olá.')
        # A verificação exigida pelo enunciado é anterior à leitura do conteúdo.
        if resposta.status == RunStatus.error:
            mensagem = MENSAGEM_PADRAO
        else:
            mensagem = 'Falha não reproduzida.'
        resultado = {'status': resposta.status.value, 'mensagem_publica': mensagem,
                     'interceptado': resposta.status == RunStatus.error}
    except Exception as erro:
        resultado = {'status': 'exception', 'tipo_erro': type(erro).__name__,
                     'mensagem_publica': MENSAGEM_PADRAO, 'interceptado': True,
                     'nota': 'Esta versão levantou exceção; ramo status continua implementado.'}
    salvar(pasta / 'erro_api.json', resultado)
    print('erro_api', resultado, flush=True)


def revisoes(pasta, dados):
    from revisor import revisar, construir_agente
    registros, conferencia = [], []
    for m in dados['minutas']:
        try:
            revisao, medidas = revisar(m['texto'], m['tipo'], agente=construir_agente())
            r = {'id': m['id'], 'status': 'completed', 'revisao': revisao.model_dump(), 'medidas': medidas}
        except Exception as erro:
            r = {'id': m['id'], 'status': 'error', 'tipo_erro': type(erro).__name__}
        registros.append(r)
        conferencia.append({'id': m['id'], 'avisos_agente': r.get('revisao', {}).get('avisos', []),
                            'faltas_previas_didaticas': m['faltas_previas'],
                            'avaliacao_servidor': [{'falta': falta, 'vista_em_avisos': None, 'justificativa': ''} for falta in m['faltas_previas']],
                            'falsos_positivos': None})
        salvar(pasta / 'revisoes.json', registros)
        salvar(pasta / 'conferencia_humana.json', conferencia)
        print('revisao', m['id'], r['status'], flush=True)


def conferir(pasta):
    itens = json.loads((pasta / 'conferencia_humana.json').read_text(encoding='utf-8'))
    resultado = []
    for item in itens:
        valores = [v['vista_em_avisos'] for v in item['avaliacao_servidor']]
        resultado.append({'id': item['id'], 'total_faltas': len(valores),
                          'vistas': sum(v is True for v in valores),
                          'deixou_passar': sum(v is False for v in valores),
                          'pendentes': sum(v is not True and v is not False for v in valores)})
    salvar(pasta / 'confronto.json', resultado)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('etapa', choices=['atendimento', 'encadeamento', 'docstrings', 'privacidade', 'erro', 'revisoes', 'tudo', 'conferir'])
    parser.add_argument('--pasta', type=Path)
    args = parser.parse_args()
    if args.etapa == 'conferir':
        if not args.pasta:
            parser.error('Informe --pasta com a execução que você conferiu.')
        conferir(args.pasta)
        return
    if not os.getenv('OPENAI_API_KEY'):
        parser.error('Configure OPENAI_API_KEY em aula06/.env para executar com modelo.')
    pasta = pasta_nova(args.etapa)
    print('Evidências:', pasta, flush=True)
    dados = json.loads((BASE / 'dados_minilab.json').read_text(encoding='utf-8'))
    etapas = {'atendimento': lambda: atendimento(pasta, dados), 'encadeamento': lambda: encadeamento(pasta),
              'docstrings': lambda: docstrings(pasta), 'privacidade': lambda: privacidade(pasta),
              'erro': lambda: erro_api(pasta), 'revisoes': lambda: revisoes(pasta, dados)}
    for nome in etapas if args.etapa == 'tudo' else [args.etapa]:
        etapas[nome]()


if __name__ == '__main__':
    main()
