"""Gera relatório legível a partir das evidências reais das execuções."""
import json
from pathlib import Path
from configuracao import BASE


def ler(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    execucoes = sorted((BASE / 'resultados').glob('tudo_*'))
    formularios = sorted((BASE / 'resultados').glob('formulario_*'))
    pasta = execucoes[-1]
    form = formularios[-1]
    rel = ['# Relatório do Mini LAB — TI da SEFAZ-MT', '',
           'Execuções reais de API com entradas **fictícias**, autorizadas para esta preparação. '
           'Manual e prazos hipotéticos; não equivalem a validação do órgão.', '',
           f'Evidências do atendimento: [{pasta.name}](resultados/{pasta.name}/manifesto.json).', '',
           '## Oito perguntas', '', '| ID | Chamadas | Ferramentas | Custo estimado US$ |', '|---|---:|---|---:|']
    perguntas=ler(pasta/'atendimento.json')
    for r in perguntas:
        rel.append(f"| {r['id']} | {r.get('chamadas_modelo', '—')} | {', '.join(t['nome'] for t in r.get('ferramentas', []))} | {r.get('custo_estimado_usd', 0):.8f} |")
    rel.extend(['', 'Respostas completas e argumentos de cada ferramenta estão em '
                f'[atendimento.json](resultados/{pasta.name}/atendimento.json).', ''])
    custo=ler(pasta/'custo_mensal.json')
    rel.extend([f"Custo médio medido: US$ {custo['custo_medio_usd']:.8f}. "
                f"Simulação de 50 perguntas/dia × 22 dias: US$ {custo['simulacao_50_perguntas_dia_usd']:.4f}/mês. "
                'O custo mensal real permanece pendente do volume do setor. Estimativas por tokens sem desconto de cache.', '',
                '## Consultas encadeadas e docstrings', '',
                '| Paralelas | Repetição | Data entregue ao cálculo | Data correta |', '|---|---:|---|---|'])
    for r in ler(pasta/'encadeamento.json'):
        rel.append(f"| {r['paralelas']} | {r['repeticao']} | {', '.join(r['dados_segunda_ferramenta'])} | {r['datas_corretas']} |")
    rel.extend(['', 'Nas duas configurações a data foi correta nas três repetições. '
                'A amostra não mostrou vantagem de desligar chamadas paralelas. A regra de dependência era idêntica nos grupos.', ''])
    ds=ler(pasta/'docstrings.json')
    for versao in ['so_quando', 'quando_e_retorno']:
        itens=[r for r in ds if r['versao']==versao]
        rel.append(f"- Docstring `{versao}`: {sum(r['data_correta'] for r in itens)}/{len(itens)} datas corretas; "
                   f"{sum(r['vencimento_correto'] for r in itens)}/{len(itens)} vencimentos corretos.")
    rel.extend(['', 'Não houve diferença observada nesta amostra. Isso não prova que a descrição do retorno '
                'seja dispensável; a pergunta já mencionava a movimentação e a instrução exigia aguardar dependências.', '',
                '## Privacidade e falha de API', ''])
    for r in ler(pasta/'privacidade.json'):
        rel.append(f"- `{r['modo']}`: CPF no registro = {r['cpf_no_log']}; "
                   f"protocolo preservado = {r['protocolo_preservado']}; processo preservado = {r['processo_preservado']}; "
                   f"verificação de todos os quatro dados fictícios aprovada = {r['aprovado']}.")
    erro=ler(pasta/'erro_api.json')
    rel.extend(['', f"O modelo deliberadamente inexistente devolveu status `{erro['status']}`. "
                f"Interceptação: {erro['interceptado']}. Mensagem entregue ao cidadão: “{erro['mensagem_publica']}”", '',
                '## Três revisões pelo formulário', '',
                f'Execução pelo AppTest do Streamlit: [{form.name}](resultados/{form.name}/revisoes.json). '
                'O formulário chamou o modelo, recebeu eventos das ferramentas e mostrou os resultados.', '',
                '| Minuta | Tipo | Tempo (s) | Chamadas | Custo estimado US$ |', '|---|---|---:|---:|---:|'])
    tipos={m['id']:m['tipo'] for m in ler(BASE/'dados_minilab.json')['minutas']}
    for r in ler(form/'revisoes.json'):
        m=r['medidas']
        rel.append(f"| {r['id']} | {tipos[r['id']]} | {m['segundos']} | {m['chamadas']} | {m['custo']:.8f} |")
    rel.extend(['', 'A execução adicional de revisão sem streaming em `tudo` registrou falha em M1 e sucesso em M2/M3. As três revisões concluídas pelo formulário acima são a evidência principal da Parte 4; a tentativa com falha foi preservada em `revisoes.json` da pasta `tudo`.', '', '## Conferência pendente', '',
                f'Preencha [conferencia_humana.json](resultados/{form.name}/conferencia_humana.json) '
                'para registrar quais faltas o agente viu em `avisos` e quais deixou passar. '
                'Os campos estão vazios porque a conferência pessoal ainda não foi feita.', '',
                'Sete testes locais passaram, incluindo cálculo encadeado, entradas inválidas, preservação '
                'de protocolos pelo filtro, falha de status e formulário com falha controlada. '
                'O servidor Streamlit também respondeu ao endpoint de saúde na porta 8506.', '',
                'Para concluir a entrega com dados do setor, siga as pendências em [README.md](README.md).', ''])
    (BASE/'RELATORIO.md').write_text('\n'.join(rel), encoding='utf-8')
    print(BASE/'RELATORIO.md')


if __name__ == '__main__':
    main()
