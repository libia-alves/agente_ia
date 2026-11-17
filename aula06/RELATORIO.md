# Relatório do Mini LAB — TI da SEFAZ-MT

Execuções reais de API com entradas **fictícias**, autorizadas para esta preparação. Manual e prazos hipotéticos; não equivalem a validação do órgão.

Evidências do atendimento: [tudo_20261117T000308914220Z](resultados/tudo_20261117T000308914220Z/manifesto.json).

## Oito perguntas

| ID | Chamadas | Ferramentas | Custo estimado US$ |
|---|---:|---|---:|
| Q01 | 2 | consultar_chamado | 0.00022215 |
| Q02 | 2 | consultar_chamado | 0.00021015 |
| Q03 | 2 | consultar_servico | 0.00022515 |
| Q04 | 2 | consultar_servico | 0.00021150 |
| Q05 | 2 | consultar_servico | 0.00021915 |
| Q06 | 2 | consultar_canal | 0.00020280 |
| Q07 | 3 | consultar_chamado, calcular_prazo | 0.00036675 |
| Q08 | 2 | consultar_chamado | 0.00020325 |

Respostas completas e argumentos de cada ferramenta estão em [atendimento.json](resultados/tudo_20261117T000308914220Z/atendimento.json).

Custo médio medido: US$ 0.00023261. Simulação de 50 perguntas/dia × 22 dias: US$ 0.2559/mês. O custo mensal real permanece pendente do volume do setor. Estimativas por tokens sem desconto de cache.

## Consultas encadeadas e docstrings

| Paralelas | Repetição | Data entregue ao cálculo | Data correta |
|---|---:|---|---|
| True | 1 | 2026-11-13 | True |
| True | 2 | 2026-11-13 | True |
| True | 3 | 2026-11-13 | True |
| False | 1 | 2026-11-13 | True |
| False | 2 | 2026-11-13 | True |
| False | 3 | 2026-11-13 | True |

Nas duas configurações a data foi correta nas três repetições. A amostra não mostrou vantagem de desligar chamadas paralelas. A regra de dependência era idêntica nos grupos.

- Docstring `so_quando`: 3/3 datas corretas; 3/3 vencimentos corretos.
- Docstring `quando_e_retorno`: 3/3 datas corretas; 3/3 vencimentos corretos.

Não houve diferença observada nesta amostra. Isso não prova que a descrição do retorno seja dispensável; a pergunta já mencionava a movimentação e a instrução exigia aguardar dependências.

## Privacidade e falha de API

- `sem_filtro`: CPF no registro = True; protocolo preservado = True; processo preservado = True; verificação de todos os quatro dados fictícios aprovada = False.
- `pre_hook`: CPF no registro = False; protocolo preservado = True; processo preservado = True; verificação de todos os quatro dados fictícios aprovada = True.
- `antes_e_pre_hook`: CPF no registro = False; protocolo preservado = True; processo preservado = True; verificação de todos os quatro dados fictícios aprovada = True.

O modelo deliberadamente inexistente devolveu status `ERROR`. Interceptação: True. Mensagem entregue ao cidadão: “O atendimento está temporariamente indisponível. Tente novamente mais tarde pelo canal institucional.”

## Três revisões pelo formulário

Execução pelo AppTest do Streamlit: [formulario_20261117T000418051783Z](resultados/formulario_20261117T000418051783Z/revisoes.json). O formulário chamou o modelo, recebeu eventos das ferramentas e mostrou os resultados.

| Minuta | Tipo | Tempo (s) | Chamadas | Custo estimado US$ |
|---|---|---:|---:|---:|
| M1 | resposta a e-mail do cidadão | 9.97 | 4 | 0.00098760 |
| M2 | despacho | 7.29 | 4 | 0.00083280 |
| M3 | resposta a e-mail do cidadão | 8.22 | 4 | 0.00085485 |

A execução adicional de revisão sem streaming em `tudo` registrou falha em M1 e sucesso em M2/M3. As três revisões concluídas pelo formulário acima são a evidência principal da Parte 4; a tentativa com falha foi preservada em `revisoes.json` da pasta `tudo`.

## Conferência pendente

Preencha [conferencia_humana.json](resultados/formulario_20261117T000418051783Z/conferencia_humana.json) para registrar quais faltas o agente viu em `avisos` e quais deixou passar. Os campos estão vazios porque a conferência pessoal ainda não foi feita.

Sete testes locais passaram, incluindo cálculo encadeado, entradas inválidas, preservação de protocolos pelo filtro, falha de status e formulário com falha controlada. O servidor Streamlit também respondeu ao endpoint de saúde na porta 8506.

Para concluir a entrega com dados do setor, siga as pendências em [README.md](README.md).
