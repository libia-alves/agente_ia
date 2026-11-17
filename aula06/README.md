# Aula 06 — Mini LAB de atendimento com Agno

Cenário escolhido: **atendimento de TI da SEFAZ-MT com exemplos fictícios**.
Não são registros do órgão. O manual é uma proposta didática e os prazos não são
compromissos de atendimento. Os exemplos originais `exemplo01.py` a `exemplo05.py`
e `revisor_esqueleto.py` foram preservados como material de consulta.

## Começar

A partir da raiz do projeto:

```bash
python3.12 -m venv aula06/.venv
aula06/.venv/bin/pip install -r aula06/requirements.txt
cp aula06/.env.example aula06/.env
```

Preencha `OPENAI_API_KEY` em `aula06/.env`, sem publicar esse arquivo.
O ambiente desta preparação já está instalado e configurado localmente.
`MINILAB_MODELO` escolhe o modelo; `PRECO_ENTRADA` e `PRECO_SAIDA` são preços
em US$ por milhão de tokens. Sem preços, o custo fica `null`, nunca zero inventado.
Para GPT-4o mini, usamos US$ 0,15 na entrada e US$ 0,60 na saída, conforme a
[documentação do modelo](https://developers.openai.com/api/docs/models/gpt-4o-mini).
A estimativa não aplica desconto de cache e não substitui o faturamento do provedor.

## Parte 1 — Cinco perguntas frequentes propostas

As fontes abaixo representam o que seria consultado no setor. Confirme os nomes
reais dos sistemas e documentos antes da entrega.

| Pergunta proposta | Fonte consultada hoje a confirmar | Ferramenta didática |
|---|---|---|
| Qual a situação do meu chamado? | Sistema de gestão de chamados | `consultar_chamado` |
| Como solicito acesso a um sistema? | Catálogo de serviços e procedimento de autorização | `consultar_servico("acesso")` |
| Esqueci a senha; como recuperar? | Procedimento de recuperação de acesso | `consultar_servico("senha")` |
| Como peço restauração de arquivo e qual o prazo? | Catálogo de backup/restauração e planilha de prazos | `consultar_servico("restauracao")`, `calcular_prazo` |
| Onde comunico um incidente de segurança? | Relação de canais institucionais de TI | `consultar_canal("seguranca")` |

As quatro funções e as diretrizes da SEFAZ-MT estão em `ferramentas.py`
(`atendimento.py` mantém compatibilidade com os exemplos): anotações de tipo, momento de uso,
argumentos, formato de retorno e dados locais hipotéticos. Execute sem agente ou chave:

```bash
python3 aula06/atendimento.py
aula06/.venv/bin/python -m unittest discover -s aula06/tests -v
```

O cálculo exclui o dia inicial e fins de semana; **não considera feriados**.
O vencimento didático 20/11/2026 não deve ser adotado em atendimento real sem
calendário do órgão. Nenhuma regra do laboratório foi validada como norma institucional.

## Partes 2 e 3 — Executar e medir

```bash
aula06/.venv/bin/python aula06/minilab.py tudo
```

Também é possível rodar separadamente: `atendimento`, `encadeamento`,
`docstrings`, `privacidade`, `erro` e `revisoes`. Cada etapa usa a API e cria
uma pasta própria em `resultados/`, com entradas e código copiados e hashes
calculados antes das chamadas. O manifesto não inclui a chave.

- `atendimento.json`: oito perguntas, respostas, ferramentas, argumentos,
  retornos, chamadas contadas pelas mensagens do modelo e consumo do `RunOutput`.
- `encadeamento.json`: três repetições com `parallel_tool_calls=True` e três
  com `False`; registra todas as datas efetivamente enviadas a `calcular_prazo`.
  As instruções são iguais nos dois grupos. Habilitar chamadas paralelas permite,
  mas não obriga, que o modelo as solicite simultaneamente.
- `docstrings.json`: duas versões da mesma função, sem alterar sua implementação;
  três perguntas encadeadas por versão, com conferência da data e do vencimento.
- `privacidade.json`: compara debug sem filtro, com pre-hook e com filtragem
  anterior ao agente mais pre-hook. Os arquivos `.log` têm apenas dados fictícios
  e são ignorados pelo Git. O teste observa o logger `agno`, não logs externos.
- `erro_api.json`: modelo deliberadamente inexistente provoca erro de API;
  `resposta.status == RunStatus.error` devolve mensagem pública padronizada.
  A aplicação também trata exceções e falhas durante streaming.
- `custo_mensal.json`: média medida × perguntas/dia × dias/mês. Preencha
  `PERGUNTAS_DIA` com o volume real; até lá existe apenas uma simulação explícita
  de 50 perguntas/dia e 22 dias/mês.

O [PIIDetectionGuardrail](https://docs.agno.com/reference/hooks/pii-guardrail)
foi configurado para CPF, RG, telefone brasileiro e e-mail. Os padrões genéricos
americanos de SSN, telefone e cartão ficam desligados. CPF/RG/telefone sem
pontuação exigem rótulo, para preservar processos numéricos sem rótulo de PII.
Nomes e endereços livres ainda exigem anonimização; regex não garante detectar
todos os dados pessoais. O atendimento filtra antes de entrar no framework e
mantém o pre-hook. O revisor recebe minutas anonimizadas e apenas aponta dados
residuais para decisão do servidor, conforme o exercício.

## Parte 4 — Revisor disponível em formulário

`revisor.py` implementa os cinco pontos do esqueleto: manual externo com dois
tipos, detecção de dados pessoais, legibilidade, instrução e construção do agente.
Como o projeto já continha ambos os arquivos, mantivemos o esqueleto de referência.
O agente tem `output_schema=Revisao`, limite de seis ferramentas e `telemetry=False`.
O formulário anuncia ferramentas durante o streaming e extrai as medidas do
`RunOutput` final, sem banco compartilhado entre servidores.

```bash
aula06/.venv/bin/streamlit run aula06/app_revisor.py --server.address 127.0.0.1 --server.port 8506 --browser.gatherUsageStats false
```

Abra <http://127.0.0.1:8506>. Escolha e-mail ou despacho, cole a minuta anonimizada
e clique em **Revisar**. Confira avisos, ajuste o texto e baixe o resultado.
O arquivo `manual_setor.json` informa claramente a origem hipotética; substitua
suas regras e fonte pelo manual usado no setor antes de disponibilizar em produção.

Para repetir as três revisões **através do próprio formulário**, usando o executor
oficial de testes do Streamlit e chamadas reais à API:

```bash
aula06/.venv/bin/python aula06/testar_formulario.py
```

O resultado fica em `resultados/formulario_*/revisoes.json`. Para o confronto humano,
abra `conferencia_humana.json` dessa pasta: leia os `avisos_agente` e marque
`vista_em_avisos` como `true` ou `false` para cada falta; acrescente outras faltas
que você identificar, justificativas e falsos positivos. O gabarito didático foi
escrito antes da revisão e não é enviado ao modelo.

```bash
aula06/.venv/bin/python aula06/minilab.py conferir --pasta aula06/resultados/formulario_DATA_DA_EXECUCAO
```

O comando produz `confronto.json`, com faltas vistas, deixadas passar e pendentes.
`null` significa **ainda não conferido**. O sistema não transforma uma avaliação
do próprio modelo em conferência do servidor.

## O que falta para entrega literal

- Confirmar as cinco perguntas frequentes e os nomes das fontes do setor.
- Substituir as oito perguntas fictícias por perguntas reais anonimizadas em `dados_minilab.json`.
- Informar o volume diário medido em `.env` e calcular a estimativa mensal real.
- Inserir o manual efetivamente adotado, com identificação da fonte.
- Substituir as três minutas fictícias, fixar previamente as faltas esperadas e repetir a revisão.
- Fazer a conferência pessoal dos avisos e registrar o confronto.

## Desafio opcional no Google Colab

Abra [desafio_aula06_colab.ipynb](desafio_aula06_colab.ipynb) no Google Colab por
**Arquivo → Fazer upload de notebook**. O notebook é independente: contém as quatro
ferramentas, instalação das versões, testes sem chave, entrada protegida da chave,
oito perguntas por framework, registros JSON, comparação da consulta encadeada e
download do relatório com evidências em ZIP. Use um runtime CPU com Python 3.10–3.13.
Execute as células na ordem e salve uma cópia com suas saídas.

As funções `gravar_registro_langchain` e `gravar_registro_crewai` estão em
[desafio_frameworks.py](desafio_frameworks.py) e também embutidas no notebook.
O LangChain registra pedidos e retornos em `resultado["messages"]`; o CrewAI na
versão fixada expõe `resultado.tasks_output[i].messages`. As funções correlacionam
pedidos com retornos pelo ID, preservando nome, argumentos e resultado de cada consulta.

O arquivo entregue não contém credenciais nem saídas apresentadas como execução no
Colab. A validação local está separada em `resultados/desafio_notebook_validacao_local/`.
Para reproduzir essa validação em ambiente próprio, instale `requirements-colab.txt`
e execute `validar_notebook_colab.py`. Esse comando usa API e não acessa o serviço Colab.
`criar_notebook_colab.py` regenera o notebook a partir das ferramentas locais.
`exemplo03.py` permanece preservado como referência do material original.


## Conversar com Sofia

O nome padrão fica em `NOME_AGENTE`, em `ferramentas.py`. No notebook do Colab,
as etapas **11 e 12** permitem conversar e baixar o registro. Troque
`NOME_DO_AGENTE` se desejar, marque `INICIAR_CONVERSA` e execute a célula.
Pergunte primeiro pelo chamado `2026009012`, depois “E qual o prazo de cinco dias
úteis a partir dessa movimentação?”. O histórico é mantido durante a sessão.

Use `/fontes` para conferir as consultas, `/salvar` para exportar perguntas,
respostas e ferramentas em JSON, `/limpar` para iniciar novo atendimento e
`/sair` para encerrar. Após salvar e sair, execute a etapa 12 para baixar o JSON.
As mensagens usam API e o histórico é reenviado; use dados fictícios ou anonimizados.

No terminal local, com o ambiente do desafio e chave configurados:

```bash
aula06/.venv-colab/bin/python aula06/conversa.py
```
