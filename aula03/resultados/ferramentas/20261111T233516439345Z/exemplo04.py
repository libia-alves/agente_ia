"""Partes 2 e 3: congelamento e medição auditável de configurações OpenAI."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import statistics
from datetime import datetime, timezone
from dotenv import load_dotenv
from .agente import PROMPT, executar, pontuar

PASTA = Path(__file__).resolve().parent
SAIDA = PASTA.parent / 'resultados' / 'ferramentas'
ARQUIVOS = ['consultas.json', 'configuracoes.json', 'ferramentas.py', 'agente.py', 'exemplo04.py', 'exemplo05.py']

def agora():
    return datetime.now(timezone.utc).isoformat()

def ler(nome):
    return json.loads((PASTA / nome).read_text(encoding='utf-8'))

def salvar(caminho, valor):
    caminho.write_text(json.dumps(valor, ensure_ascii=False, indent=2), encoding='utf-8')

def hashes():
    return {n: hashlib.sha256((PASTA / n).read_bytes()).hexdigest() for n in ARQUIVOS}

def validar():
    dados = ler('consultas.json')
    consultas = dados['consultas']
    from collections import Counter
    assert Counter(c['grupo'] for c in consultas) == {'uma': 6, 'duas': 3, 'nenhuma': 2, 'armadilha': 1}
    assert len({c['id'] for c in consultas}) == 12
    for c in consultas:
        assert len(c['ferramentas']) == {'uma':1,'duas':2,'nenhuma':0,'armadilha':0}[c['grupo']]
        assert set(c['gabarito']) == {'valor', 'situacao', 'grupos'}
    return dados

def conferir():
    manifesto = ler('manifesto.json')
    if manifesto['sha256'] != hashes():
        raise ValueError('Gabarito/código alterado após congelamento; preserve a execução e crie uma nova versão antes de medir.')
    return manifesto

def resumir(registros, cfg, volume):
    completos = all(r['uso_completo'] for r in registros)
    custos = [r['custo_usd'] for r in registros]
    resumo = dict(configuracao=cfg, consultas=len(registros), acertos=sum(r['acerto'] for r in registros),
                  ferramentas_certas=sum(r['ferramenta_certa'] for r in registros),
                  erros=sum(bool(r['erro']) for r in registros),
                  passos_mediana=statistics.median(r['passos'] for r in registros),
                  passos_max=max(r['passos'] for r in registros),
                  tempo_total_s=sum(r['tempo_s'] for r in registros),
                  tempo_mediana_s=statistics.median(r['tempo_s'] for r in registros), custo_total_usd=None)
    if completos:
        ordenados = sorted(custos)
        med = statistics.median(custos)
        p95 = ordenados[-1]  # nearest rank ceil(.95 * 12) = 12; cauda = máximo desta amostra
        resumo.update(custo_total_usd=sum(custos), minimo=min(custos), mediana=med, p95=p95,
                      maximo=max(custos), media=statistics.mean(custos), razao_max_mediana=max(custos)/med if med else None,
                      mensal_mediana=med*volume, mensal_cauda=p95*volume, volume_mensal=volume)
    return resumo

def tabelas(resumos):
    linhas = ['| Configuração | Acerto | Ferramenta certa | Passos (med./máx) | Tempo total / mediana | US$ nas 12 |',
              '| --- | --- | --- | --- | --- | --- |']
    dist = ['| Configuração | Mínimo US$ | Mediana US$ | P95 US$ | Máximo US$ | Máx./mediana | Mês mediana US$ | Mês cauda US$ |',
            '| --- | --- | --- | --- | --- | --- | --- | --- |']
    def fmt(v):
        return 'indisponível' if v is None else f'{v:.6f}'
    for r in resumos:
        nome = r['configuracao']['nome']
        linhas.append(f"| {nome} | {r['acertos']}/12 | {r['ferramentas_certas']}/12 | {r['passos_mediana']:g}/{r['passos_max']} | {r['tempo_total_s']:.2f}s / {r['tempo_mediana_s']:.2f}s | {fmt(r['custo_total_usd'])} |")
        dist.append('| '+nome+' | '+' | '.join(fmt(r.get(k)) for k in ('minimo','mediana','p95','maximo','razao_max_mediana','mensal_mediana','mensal_cauda'))+' |')
    return '\n'.join(linhas)+'\n\n'+ '\n'.join(dist)+'\n'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('acao', choices=['validar','congelar','executar'])
    p.add_argument('--volume-mensal', type=int, default=1000)
    args = p.parse_args()
    if args.volume_mensal <= 0:
        p.error('volume mensal deve ser positivo')
    dados = validar()
    if args.acao == 'validar':
        print('12 consultas válidas; proporção 6/3/2/1; gabarito presente.')
        return
    if args.acao == 'congelar':
        with (PASTA/'manifesto.json').open('x', encoding='utf-8') as f:
            json.dump(dict(congelado_em=agora(), sha256=hashes(), criterio=dados['criterio'], prompt=PROMPT), f, ensure_ascii=False, indent=2)
        print('Gabarito e código congelados antes das chamadas.')
        return
    manifesto = conferir()
    load_dotenv(PASTA.parent / '.env')
    pasta = SAIDA / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    pasta.mkdir(parents=True)
    salvar(pasta/'manifesto.json', manifesto)
    salvar(pasta/'consultas.json', dados)
    salvar(pasta/'configuracoes.json', ler('configuracoes.json'))
    salvar(pasta/'ambiente.json', {n:importlib.metadata.version(n) for n in ['langchain','langchain-openai','openai','pydantic']})
    # Copia o código executado para tornar a medição reproduzível mesmo após futuras edições.
    for nome in ARQUIVOS:
        (pasta/nome).write_bytes((PASTA/nome).read_bytes())
    resumos = []
    for cfg in ler('configuracoes.json')['configuracoes']:
        registros = []
        for consulta in dados['consultas']:
            r = executar(consulta['pergunta'], cfg)
            r.update(id=consulta['id'], **pontuar(r, consulta))
            registros.append(r)
            with (pasta/'medicoes.jsonl').open('a', encoding='utf-8') as f:
                f.write(json.dumps(dict(configuracao=cfg['nome'], **r), ensure_ascii=False)+'\n')
            print(cfg['nome'], consulta['id'], 'acerto='+str(r['acerto']), 'erro='+str(r['erro']), flush=True)
        resumos.append(resumir(registros, cfg, args.volume_mensal))
        salvar(pasta/'resumos.json', resumos)
        (pasta/'tabelas.md').write_text(tabelas(resumos), encoding='utf-8')
    (SAIDA/'ultima_execucao.txt').write_text(str(pasta), encoding='utf-8')
    print(tabelas(resumos))
    print('Resultados:', pasta)

if __name__ == '__main__':
    main()
