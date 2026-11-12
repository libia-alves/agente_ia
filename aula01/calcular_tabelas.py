#!/usr/bin/env python3
"""Mini LAB de automação: cálculos e relatórios, sem dependências externas."""
import argparse
import csv
import io
import json
import math
from contextlib import redirect_stdout
from pathlib import Path

if __package__:
    from . import calcular_tabelas_original as aula
else:
    import calcular_tabelas_original as aula

BASE = Path(__file__).resolve().parent


def parametros_aula():
    return dict(sistema_tokens=aula.PROMPT_SISTEMA, numero_ferramentas=4,
                tokens_por_ferramenta=aula.ESQUEMAS // 4, consulta_tokens=0,
                retorno_ferramenta_tokens=aula.OBSERVACAO,
                saida_por_etapa_tokens=aula.SAIDA_POR_PASSO)


def precos_aula(modelo):
    entrada, saida = aula.PRECOS[modelo]
    return dict(entrada_por_milhao=entrada, saida_por_milhao=saida)


def tabelas_originais():
    captura = io.StringIO()
    with redirect_stdout(captura):
        aula.tabela_confiabilidade()
        aula.tabela_custo()
    return captura.getvalue()


def numero(valor, campo, minimo=0, inteiro=False):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f'{campo}: informe um número.')
    if not math.isfinite(valor) or valor < minimo or (inteiro and int(valor) != valor):
        raise ValueError(f'{campo}: valor inválido ({valor}).')
    return valor


def confiabilidade(etapas, probabilidade=0.95):
    numero(etapas, 'etapas', minimo=1, inteiro=True)
    numero(probabilidade, 'probabilidade')
    if probabilidade > 1:
        raise ValueError('probabilidade deve estar entre 0 e 1.')
    return probabilidade ** etapas


def estimar_custo(etapas, parametros, precos):
    """Uma chamada por etapa; reenvia contexto completo, sem cache ou truncamento.

    Segue a simplificação do script da aula: somente as observações crescem na
    entrada. A saída é cobrada, mas não é somada novamente ao histórico de entrada.
    O fator compara n passos com um passo do mesmo agente, incluindo ferramentas.
    """
    numero(etapas, 'etapas', minimo=1, inteiro=True)
    for campo in ('sistema_tokens', 'numero_ferramentas', 'tokens_por_ferramenta',
                  'consulta_tokens', 'retorno_ferramenta_tokens', 'saida_por_etapa_tokens'):
        numero(parametros[campo], campo, inteiro=True)
    for campo in ('entrada_por_milhao', 'saida_por_milhao'):
        numero(precos[campo], campo)
    sistema = parametros['sistema_tokens']
    consulta = parametros['consulta_tokens']
    saida = parametros['saida_por_etapa_tokens']
    ferramentas = parametros['numero_ferramentas'] * parametros['tokens_por_ferramenta']
    contexto_inicial = sistema + ferramentas + consulta
    historico = parametros['retorno_ferramenta_tokens']
    entrada_agente = etapas * contexto_inicial + (etapas * (etapas - 1) // 2) * historico
    saida_agente = etapas * saida

    def custo(entrada, resposta):
        return (entrada * precos['entrada_por_milhao'] + resposta * precos['saida_por_milhao']) / 1_000_000

    um_passo = custo(contexto_inicial, saida)
    agente = custo(entrada_agente, saida_agente)
    return {
        'entrada_ultimo_passo': contexto_inicial + (etapas - 1) * historico,
        'entrada_agente': entrada_agente, 'saida_agente': saida_agente,
        'custo_um_passo': um_passo, 'custo_agente': agente,
        'fator': agente / um_passo if um_passo else None,
    }


def quadrante(processo):
    return ('Reversível' if processo['reversivel'] else 'Difícil de reverter') + ' / detecção ' + (
        'rápida' if processo['deteccao_rapida'] else 'tardia')


def validar(config):
    if config['modelo_aula'] not in aula.PRECOS:
        raise ValueError('modelo_aula deve ser um dos modelos do script original.')
    numero(config['probabilidade_por_etapa'], 'probabilidade_por_etapa')
    confiabilidade(1, config['probabilidade_por_etapa'])
    if not isinstance(config['dados_hipoteticos'], bool):
        raise ValueError('dados_hipoteticos deve ser true ou false.')
    processos = config['processos']
    if not isinstance(processos, list) or len(processos) != 3:
        raise ValueError('O Mini LAB exige exatamente três processos.')
    ids = set()
    for processo in processos:
        for campo in ('id', 'nome', 'natureza', 'tempo_deteccao', 'autonomia',
                      'conferencia_humana', 'informacao_ausente', 'onde_esta', 'barreira_codigo'):
            if not isinstance(processo[campo], str) or not processo[campo].strip():
                raise ValueError(f'{campo}: texto obrigatório.')
        if processo['id'] in ids:
            raise ValueError('Cada processo deve ter um id único.')
        ids.add(processo['id'])
        for campo in ('reversivel', 'deteccao_rapida'):
            if not isinstance(processo[campo], bool):
                raise ValueError(f'{campo}: use true ou false.')
        numero(processo['volume_mensal'], 'volume_mensal', inteiro=True)
        for campo in ('etapas', 'ferramentas'):
            valores = processo[campo]
            if not isinstance(valores, list) or not valores or any(not isinstance(x, str) or not x.strip() for x in valores):
                raise ValueError(f'{campo}: informe uma lista de textos não vazia.')
        for campo in ('desempenho', 'ambiente', 'atuadores', 'sensores'):
            if not isinstance(processo['peas'][campo], str) or not processo['peas'][campo].strip():
                raise ValueError(f'PEAS: {campo} é obrigatório.')
        if not isinstance(processo['falhas'], list) or len(processo['falhas']) != 2:
            raise ValueError('Informe exatamente duas falhas por processo.')
        for falha in processo['falhas']:
            for campo in ('nome', 'justificativa'):
                if not isinstance(falha[campo], str) or not falha[campo].strip():
                    raise ValueError(f'Falha: {campo} é obrigatório.')
        estimar_custo(len(processo['etapas']), processo['tokens'], config['precos'])
    for campo in ('piloto_id', 'recusado_id', 'critico_id'):
        if config[campo] not in ids:
            raise ValueError(f'{campo}: processo não encontrado.')
    if config['piloto_id'] == config['recusado_id']:
        raise ValueError('O piloto e o processo recusado devem ser diferentes.')
    for campo in ('moeda', 'fonte'):
        if not isinstance(config['precos'][campo], str) or not config['precos'][campo].strip():
            raise ValueError(f'precos.{campo}: texto obrigatório.')
    for campo in ('justificativa_piloto', 'justificativa_recusa'):
        if not isinstance(config[campo], str) or not config[campo].strip():
            raise ValueError(f'{campo}: texto obrigatório.')


def calcular(config):
    validar(config)
    linhas = []
    for processo in config['processos']:
        n = len(processo['etapas'])
        custo = estimar_custo(n, parametros_aula(), precos_aula(config['modelo_aula']))
        personalizado = estimar_custo(n, processo['tokens'], config['precos'])
        personalizado['custo_mensal'] = personalizado['custo_agente'] * processo['volume_mensal']
        personalizado['fator_40_passos'] = estimar_custo(40, processo['tokens'], config['precos'])['fator']
        linhas.append({**processo, 'numero_etapas': n,
                       'confiabilidade': confiabilidade(n, config['probabilidade_por_etapa']),
                       **custo, 'custo_mensal': custo['custo_agente'] * processo['volume_mensal'],
                       'personalizado': personalizado, 'quadrante': quadrante(processo)})
    return linhas


def percentual(valor):
    return f'{valor * 100:.2f}%'.replace('.', ',')


def dinheiro(valor, moeda='USD'):
    return f"{moeda} {valor:.6f}".replace('.', ',')


def fator_formatado(fator):
    return f'{fator:.2f}x'.replace('.', ',') if fator is not None else 'indefinido (base zero)'


def passos_desafio(processo):
    return sorted({1, 5, 10, 20, 40, processo['numero_etapas']})


def parecer(config, linhas):
    por_id = {p['id']: p for p in linhas}
    piloto = por_id[config['piloto_id']]
    recusado = por_id[config['recusado_id']]
    return '\n\n'.join([
        'PARECER TÉCNICO — PILOTO DE AUTOMAÇÃO POR AGENTES',
        ('Estudo didático com dados hipotéticos.' if config['dados_hipoteticos'] else
         'Estudo com dados informados pelo responsável; validar as premissas antes do piloto.')
        + ' Autores da dupla: __________________ e __________________. Órgão/setor: __________________.',
        f"Recomenda-se um piloto de {piloto['nome']}, com {piloto['volume_mensal']} execuções mensais e "
        f"{piloto['numero_etapas']} etapas. Adotando {percentual(config['probabilidade_por_etapa'])} de sucesso "
        f"por etapa independente, a confiabilidade composta é {percentual(piloto['confiabilidade'])}; "
        f"a probabilidade de pelo menos uma falha é {percentual(1 - piloto['confiabilidade'])}. "
        f"O custo mensal estimado de tokens é {dinheiro(piloto['custo_mensal'])}, "
        f"aplicando a Tabela 2 original ao modelo {config['modelo_aula']}. "
        + config['justificativa_piloto'],
        f"O processo está no quadrante {piloto['quadrante']}. Prazo de detecção assumido: "
        f"{piloto['tempo_deteccao'].rstrip('.')}. Autonomia: {piloto['autonomia']} "
        f"Conferência humana obrigatória: {piloto['conferencia_humana']}",
        f"Para funcionar, o agente precisa receber: {piloto['informacao_ausente']} "
        f"Hoje essa informação está em: {piloto['onde_esta']} O piloto deve registrar decisões e "
        'correções e medir a taxa de acerto e o tempo de atendimento antes de ampliar sua autonomia.',
        f"Não se recomenda automatizar integralmente {recusado['nome']}: "
        f"suas {recusado['numero_etapas']} etapas resultam em {percentual(recusado['confiabilidade'])} "
        f"de confiabilidade composta, com {percentual(1 - recusado['confiabilidade'])} de chance de ao menos "
        f"uma falha. {config['justificativa_recusa']}",
        'Limites: estimativas sob independência das etapas e uma chamada por etapa; preços reproduzidos do '
        'script didático fornecido, sem validação como preços comerciais atuais. Não incluem trabalho humano, '
        'infraestrutura, tarifas de ferramentas, impostos ou retrabalho. Conferir quadrantes e falhas com as '
        'seções 5 e 8, ainda não fornecidas. O cabeçalho do script chama a aritmética de Seção 5; o enunciado, de Seção 6.',
    ]) + '\n'


def relatorio(config, linhas):
    texto = ['MINI LAB — AVALIAÇÃO DE PROCESSOS',
             'DADOS HIPOTÉTICOS — substituir pelos dados do órgão.' if config['dados_hipoteticos'] else 'Dados fornecidos pelo responsável.',
             'Tabelas originais reproduzidas de calcular_tabelas_original.py, na pasta aula01.',
             'Valores e nomes de modelos são os do material didático fornecido; não são cotações atuais verificadas.',
             'Nota: o script original menciona Seção 5, enquanto o enunciado menciona Seção 6.',
             tabelas_originais(),
             'APLICAÇÃO DA TABELA 1 AOS PROCESSOS',
             'Hipótese: P(sucesso completo) = p ** n, com etapas independentes.',
             f"p = {percentual(config['probabilidade_por_etapa'])}",
             'Etapas | Sucesso completo | Ao menos uma falha']
    for n in sorted(set(range(1, 11)) | {p['numero_etapas'] for p in linhas}):
        p = confiabilidade(n, config['probabilidade_por_etapa'])
        texto.append(f'{n:>6} | {percentual(p):>16} | {percentual(1-p)}')
    texto += ['', 'APLICAÇÃO DA TABELA 2 AOS PROCESSOS',
              f"Modelo selecionado: {config['modelo_aula']}. Moeda: USD. Parâmetros originais da aula.",
              'A fórmula original é aplicada ao número exato de etapas, inclusive quando não há essa linha na tabela.',
              'Processo | Chamadas | Entrada total | Saída total | Custo/execução | Volume/mês | Custo/mês | Fator n/1']
    for p in linhas:
        texto.append(f"{p['nome']} | {p['numero_etapas']} | {p['entrada_agente']} | {p['saida_agente']} | "
                     f"{dinheiro(p['custo_agente'])} | {p['volume_mensal']} | "
                     f"{dinheiro(p['custo_mensal'])} | {fator_formatado(p['fator'])}")
    texto += ['', 'DESAFIO OPCIONAL — PARÂMETROS PERSONALIZADOS',
              f"Preços personalizados: {config['precos']['fonte']}",
              'Processo | Custo/execução | Custo/mês | Fator n/1 | Fator 40/1']
    for p in linhas:
        custo = p['personalizado']
        moeda = config['precos']['moeda']
        texto.append(f"{p['nome']} | {dinheiro(custo['custo_agente'], moeda)} | "
                     f"{dinheiro(custo['custo_mensal'], moeda)} | {fator_formatado(custo['fator'])} | "
                     f"{fator_formatado(custo['fator_40_passos'])}")
    for p in linhas:
        texto += ['', f"Tabela 2 personalizada — {p['nome']}",
                  'Passos | Entrada último passo | Entrada acumulada | Saída acumulada | Custo/execução | Fator n/1']
        for n in passos_desafio(p):
            custo = estimar_custo(n, p['tokens'], config['precos'])
            texto.append(f"{n} | {custo['entrada_ultimo_passo']} | {custo['entrada_agente']} | "
                         f"{custo['saida_agente']} | {dinheiro(custo['custo_agente'], config['precos']['moeda'])} | "
                         f"{fator_formatado(custo['fator'])}")
    referencia = estimar_custo(40, parametros_aula(), precos_aula(config['modelo_aula']))['fator']
    texto += [f'Fator original de 40 passos / 1 passo: {fator_formatado(referencia)} (153x após arredondamento).',
              'Compare a coluna 40/1 personalizada com essa referência; n/1 usa as etapas reais do processo.',
              'Os parâmetros personalizados ainda são exemplos hipotéticos, não medições do órgão.' if config['dados_hipoteticos'] else
              'Os parâmetros personalizados foram informados pelo responsável e precisam ser conferidos com medições.',
              '', 'Modelo de custo: uma chamada por etapa; mesma simplificação de histórico do script original.',
              'S=sistema; F=número de ferramentas × tokens por definição; Q=consulta; R=retorno; O=saída por etapa.',
              'Entrada do agente = n×(S+F+Q) + n×(n−1)/2×R. Saída do agente = n×O.',
              'A saída é cobrada, mas não é adicionada ao histórico de entrada no modelo didático original.',
              'No cenário original: S=600, F=400, Q=0, R=250, O=120.',
              'Um passo de referência inclui sistema, esquemas de ferramentas e uma saída.',
              'Custo = (entrada×preço_entrada + saída×preço_saída)/1.000.000.',
              'O fator compara n passos com 1 passo do mesmo agente, usando os mesmos parâmetros e preços.',
              'O fator de 153x não é universal e depende dos tamanhos de contexto e da relação entre os preços.',
              'Custos excluem tarifas externas, infraestrutura, revisão humana, impostos e retrabalho.', '', 'GRADE DE AUTONOMIA (CLASSIFICAÇÃO PROVISÓRIA)']
    for reversivel in (True, False):
        for rapida in (True, False):
            nomes = [p['nome'] for p in linhas if p['reversivel'] == reversivel and p['deteccao_rapida'] == rapida]
            texto.append(f"{quadrante({'reversivel': reversivel, 'deteccao_rapida': rapida})}: " + ('; '.join(nomes) or 'Nenhum'))
    for p in linhas:
        texto += ['', p['nome'].upper(), f"Natureza: {p['natureza']}", f"Volume mensal: {p['volume_mensal']}", 'PEAS:']
        for chave, rotulo in [('desempenho', 'Medida de desempenho'), ('ambiente', 'Ambiente'), ('atuadores', 'Atuadores'), ('sensores', 'Sensores')]:
            texto.append(f"  {rotulo}: {p['peas'][chave]}")
        texto += ['Etapas:'] + [f'{i}. {etapa}' for i, etapa in enumerate(p['etapas'], 1)]
        texto += ['Ferramentas: ' + '; '.join(p['ferramentas']),
                  'Parâmetros de tokens: ' + json.dumps(p['tokens'], ensure_ascii=False),
                  f"Confiabilidade: {percentual(p['confiabilidade'])}",
                  f"Quadrante: {p['quadrante']}. Detecção: {p['tempo_deteccao']}",
                  f"Escopo da classificação: {p.get('escopo_quadrante', 'Processo descrito nas etapas.')}",
                  f"Autonomia: {p['autonomia']}", f"Conferência humana: {p['conferencia_humana']}",
                  'Falhas prováveis (confirmar nomes na Seção 8):']
        texto += [f"- {f['nome']}: {f['justificativa']}" for f in p['falhas']]
        texto += [f"Informação ausente: {p['informacao_ausente']}", f"Onde está hoje: {p['onde_esta']}"]
    pior = min(linhas, key=lambda p: p['confiabilidade'])
    critico = next(p for p in linhas if p['id'] == config['critico_id'])
    texto += ['', f"Pior confiabilidade: {pior['nome']} ({percentual(pior['confiabilidade'])}), "
              'pois exige o maior número de etapas bem-sucedidas em sequência sob a mesma probabilidade por etapa.',
              f"Barreira exigida para {critico['nome']}: {critico['barreira_codigo']}",
              'A barreira acima é um requisito proposto: este programa somente calcula e gera relatórios.',
              '', parecer(config, linhas)]
    return '\n'.join(texto)


def exportar(pasta, config, linhas, texto):
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / 'relatorio.txt').write_text(texto, encoding='utf-8')
    (pasta / 'parecer.txt').write_text(parecer(config, linhas), encoding='utf-8')
    (pasta / 'tabelas_originais.txt').write_text(tabelas_originais(), encoding='utf-8')
    with (pasta / 'tabelas.csv').open('w', encoding='utf-8-sig', newline='') as arquivo:
        escritor = csv.writer(arquivo, delimiter=';')
        escritor.writerow(['processo', 'etapas', 'volume_mensal', 'confiabilidade', 'moeda',
                           'modelo_aula', 'custo_um_passo', 'custo_agente', 'custo_mensal', 'fator_n_1',
                           'quadrante', 'moeda_personalizada', 'custo_personalizado', 'mensal_personalizado',
                           'fator_personalizado_n_1', 'fator_personalizado_40_1'])
        for p in linhas:
            escritor.writerow([p['nome'], p['numero_etapas'], p['volume_mensal'], p['confiabilidade'],
                               'USD', config['modelo_aula'], p['custo_um_passo'], p['custo_agente'],
                               p['custo_mensal'], p['fator'], p['quadrante'], config['precos']['moeda'],
                               p['personalizado']['custo_agente'], p['personalizado']['custo_mensal'],
                               p['personalizado']['fator'], p['personalizado']['fator_40_passos']])
    with (pasta / 'desafio_opcional.csv').open('w', encoding='utf-8-sig', newline='') as arquivo:
        escritor = csv.writer(arquivo, delimiter=';')
        escritor.writerow(['processo', 'passos', 'entrada_ultimo_passo', 'entrada_acumulada',
                           'saida_acumulada', 'moeda', 'custo_execucao', 'fator_n_1'])
        for p in linhas:
            for n in passos_desafio(p):
                custo = estimar_custo(n, p['tokens'], config['precos'])
                escritor.writerow([p['nome'], n, custo['entrada_ultimo_passo'], custo['entrada_agente'],
                                   custo['saida_agente'], config['precos']['moeda'],
                                   custo['custo_agente'], custo['fator']])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=BASE / 'processos.json', help='Arquivo JSON com processos e preços.')
    parser.add_argument('--saida', type=Path, help='Pasta para exportar relatório, parecer e CSV. Arquivos de mesmo nome são atualizados.')
    args = parser.parse_args()
    try:
        with args.config.open(encoding='utf-8') as arquivo:
            config = json.load(arquivo)
        linhas = calcular(config)
        texto = relatorio(config, linhas)
        if args.saida:
            exportar(args.saida, config, linhas, texto)
        print(texto)
        if args.saida:
            print(f'\nArquivos gravados em: {args.saida.resolve()}')
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as erro:
        parser.exit(2, f'Erro nos dados ou arquivos: {erro}\n')


if __name__ == '__main__':
    main()
