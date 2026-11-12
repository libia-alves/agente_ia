# Mini LAB — assistente de contratos da SEFAZ

Este é o exercício de **ferramentas, avaliação e falhas** do enunciado atual.
O exercício anterior de extração foi preservado em `aula02`.
Este laboratório pertence à **aula03**. O material original do curso estava
dentro de `.venv`; uma cópia foi preservada em `../material_original/`.

Serviço escolhido: consulta de contratos e simulação de acréscimos para apoiar
o setor de contratos. Os três contratos e os três percentuais são **fictícios**.
Não foram extraídos dos PDFs de `aula02/dados/` nem representam regras da SEFAZ.
A escolha mantém o contexto do órgão presente no trabalho anterior.

Execute no terminal, a partir de `aula03`:

```bash
.venv/bin/python -m lab_ferramentas.exemplo01
.venv/bin/python -m lab_ferramentas.exemplo04 validar
# Executar uma única vez antes de qualquer chamada (já realizado nesta entrega):
.venv/bin/python -m lab_ferramentas.exemplo04 congelar
.venv/bin/python -m lab_ferramentas.exemplo04 executar --volume-mensal 1000
.venv/bin/python -m lab_ferramentas.exemplo05 --configuracao luna
.venv/bin/python -m lab_ferramentas.gerar_relatorio
.venv/bin/python -m unittest discover -s tests -v
```

Os comandos `executar` e `exemplo05` fazem chamadas cobradas à OpenAI com a
chave de `aula03/.env`. Nenhum outro provedor é usado. Os testes usam respostas
simuladas, identificadas como fixtures, e não compõem as tabelas empíricas.
Os resultados reais são gravados em `../resultados/ferramentas/`; os arquivos
`ultima_execucao.txt` e `ultimas_falhas.txt` apontam para as pastas correspondentes.

## Arquivos para conferir e entregar

- `ferramentas.py`: `@tool`, função anotada convertida ao passar na lista de
  `create_agent`, e `StructuredTool` com Pydantic e campos descritos.
- `consultas.json`: doze perguntas, gabarito e critério tolerante a grafia.
- `manifesto.json`: hashes do gabarito, configurações e código, com data anterior
  às chamadas. O programa recusa medir se esses arquivos forem alterados.
- `configuracoes.json`: modelos, raciocínio e tarifas por milhão de tokens.
- `agente.py`: execução, pontuação, custo e `wrap_tool_call`, que devolve
  `ToolMessage` também ao bloquear uma chamada.
- `exemplo05.py`: ataques e respectivos critérios definidos antes da execução.
- `RELATORIO.md`: resumo curto para apresentar.
- `RELATORIO_COMPLETO.md`: análise detalhada e evidências; atualizado pelo gerador.

O gabarito foi preparado com assistência de IA, antes da medição; o aluno deve
ler e compreender as perguntas e explicar os resultados na apresentação.
O `consultas_pge.json` do curso está preservado em `../material_original/`.
A proporção e a tolerância da adaptação seguem o enunciado fornecido.

## Como ler as métricas

Acerto verifica a resposta: valor com tolerância inferior a meio centavo,
situação e grupos de alternativas textuais. A normalização remove acentos,
caixa e pontuação. Assim, `SERVIÇOS` e `servicos` são equivalentes; um número
errado não ganha ponto por semelhança textual. O campo `valor` permite medir
numericamente sem depender de como a resposta formata reais e percentuais.

Ferramenta certa compara o multiconjunto exato das chamadas **tentadas** com o
gabarito: repetições, chamadas excedentes e chamadas bloqueadas são registradas.
Não confunde ferramenta certa com resultado correto, nem avalia argumentos
apenas pelo nome: os argumentos e retornos ficam disponíveis nos logs para
inspeção. Passo significa uma chamada ao modelo, inclusive a resposta final.
Tempo total é a soma das doze latências, incluindo ferramentas locais e rede;
a mediana por consulta também aparece. Não há aquecimento nem retries ocultos.

O custo soma os tokens de **todas** as respostas do agente, inclusive raciocínio
contabilizado pela API como saída, histórico reenviado e schemas. Cache de
entrada tem tarifa própria. Se o uso estiver ausente ou a API falhar, custo
completo é indisponível; o custo parcial conhecido continua no log. Os testes
de falha e barreira são despesas adicionais, fora do total das doze principais.

P95 usa nearest rank: com 12 consultas, é o máximo. Custo mensal pela mediana
é `volume × mediana`; pela cauda, `volume × P95`. Este segundo é um cenário de
estresse em que todas as consultas custam o valor da cauda, não uma previsão
probabilística da fatura. Volume de 1.000/mês é uma hipótese acadêmica. Custos
não incluem infraestrutura, operação, câmbio ou conferência humana.

## Barreira e desafio de proveniência

A barreira simples só aceita números que aparecem na pergunta. Isso pode
bloquear o valor legítimo retornado por uma consulta de contrato ou a taxa
retornada pela consulta de regra. A segunda barreira rastreia, por argumento,
o identificador da chamada e o campo do resultado confiável (`valor` ou
`percentual`). O retorno é capturado antes da contaminação de texto usada no
ataque indireto. Valores da resposta do próprio modelo não viram fontes.

A proveniência aceita `R$ ...` como valor informado e `...%` como percentual;
valores escritos por extenso ou sem essa notação podem causar recusas. É uma
limitação explícita deste protótipo. Origem rastreável não atesta veracidade,
autorização ou cabimento jurídico; fontes reais exigem autenticação e controle
de acesso. O desafio foi implementado para os argumentos numéricos deste
fluxo, sem pretender rastrear qualquer número arbitrário de uma conversa.

Nas doze consultas benignas, conta-se como falso positivo operacional cada
consulta com ao menos um bloqueio. Há também contagem de bloqueios individuais,
pois o agente pode repetir uma tentativa. Q12 é benigna e pede esclarecimento;
se houver bloqueio nela, o trace permite distinguir a chamada indevida do
modelo de um impedimento sobre uma operação legítima. Acerto e erro de execução
são apresentados separadamente. Uma amostra com 12 itens e uma execução por
configuração não estabelece significância estatística nem robustez em produção.

Para instalar somente as dependências deste laboratório em outro ambiente, use
`python -m pip install -r lab_ferramentas/requirements.txt`, a partir de `aula03`.
