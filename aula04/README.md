# Aula 04 — Mini LAB CrewAI na SEFAZ-MT

Caso atual: garantia e suporte técnico de backup, demanda 25.3.108 do PCA 2025
**da Secretaria de Estado de Fazenda de Mato Grosso**. A fonte pública é o
[PCA 2025, página 16](https://www5.sefaz.mt.gov.br/documents/d/sefaz/pca-pdf).
O laboratório analisa o registro histórico de planejamento, sem afirmar sua
situação atual, contratação efetiva ou vínculo do aluno com o órgão.

## Executar

O ambiente `.venv-crewai` usa Python 3.12, compatível com CrewAI 1.15.21.
O `.venv` original tem Python 3.14, incompatível com essa versão do CrewAI.

```bash
cd aula04
source .venv-crewai/bin/activate
python minilab.py testar
python minilab.py executar
```

`executar` faz chamadas reais usando `OPENAI_API_KEY` e `MINILAB_MODELO` de `.env`
desta pasta. Cada execução cria uma nova pasta, sem sobrescrever evidências.
O caminho mais recente fica em `resultados/ultima_execucao.txt`.

Instalação em outro computador:

```bash
python3.12 -m venv .venv-crewai
source .venv-crewai/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Preencha a chave. Para reproduzir também as versões transitivas instaladas,
use `requirements-lock.txt` no lugar de `requirements.txt`.
Para regenerar um relatório a partir dos registros, sem novas chamadas:

```bash
python minilab.py relatorio --pasta resultados/IDENTIFICADOR
```

## Caso, rubrica e fonte

`dossie_projeto.md` apresenta o caso em uma página. O PCA registra R$ 200.000,00
e o PTA registra R$ 1.000,00 para a demanda de backup. A diferença calculável é
R$ 199.000,00. Isso não permite tratar o PTA como saldo orçamentário atual nem
concluir que houve execução ou irregularidade.
A data desejada de 04/11/2025 é histórica; não é um prazo futuro do exercício atual.

`rubrica.json` tem seis critérios objetivos definidos antes das novas execuções:
valor do PCA, backup, garantia e suporte, confronto com PTA, recomendação e
conferência humana antes de assinatura. A cobertura é verificada por termos ou
números; a fidelidade fica com o juiz, sem tentar detectar todo número inventado.
`fonte_publica.json` registra os dados e o hash do PDF; `fontes/` guarda a cópia
pública e as páginas usadas na conferência visual dos cabeçalhos e da demanda.
`protocolo.json` fixa parâmetros, modelos e tarifas antes das medições.

## Equipe e orçamento

Os três agentes analisam infraestrutura, finanças e instrução documental da SEFAZ-MT.
As biografias incluem diretrizes: exigir evidência de restauração, confrontar
PCA/PTA sem confundir PTA com saldo e distinguir lacunas do recorte de ausências
no processo completo. A condição sem biografia usa `backstory=''`, mantendo os
mesmos papéis e objetivos.

O financeiro recebe `context=[t1]`; o parecerista recebe `context=[t1,t2]`.
Na condição estruturada, a última tarefa usa `output_pydantic=Parecer`.
Todos os agentes têm `max_iter=5`, para poucas consultas/correções,
`max_rpm=20`, para limitar rajadas, e `max_execution_time=120`, para limitar
esperas por tarefa. O limite por resposta é de 1.800 tokens, com raciocínio
`none` em todas as condições de produção. O juiz usa `low` e 1.200 tokens.
`max_retry_limit=0` evita novas tentativas automáticas do agente por erro;
`respect_context_window=False` torna o estouro de contexto uma falha explícita.
Esses parâmetros limitam consumo por etapa, sem constituir teto monetário global.

## Medições e falhas

São executadas duas rodadas completas de chamada única, equipe sem biografia,
equipe com biografia e equipe com biografia e saída estruturada.
Cada pasta contém respostas, saídas de tarefas, consumo real, tempo, custo
estimado e notas do juiz. O manifesto com hashes e as cópias do dossiê, rubrica,
protocolo, fonte e código são salvos antes da primeira chamada.

Para reproduzir a falha, o PCA é adulterado de R$ 200.000,00 para R$ 600.000,00
somente na entrada da primeira tarefa. As seguintes recebem a cadeia, sem
cópia independente da fonte. O PTA permanece em R$ 1.000,00.
As duas condições de falha usam saída estruturada; apenas a segunda tem guardrail.
O guardrail ancora o campo `valor_estimado` na fonte original com Decimal,
rejeita valor ausente/inválido e permite até duas correções. Seu retorno usa
`Tuple[bool, Any]`. A saída usa float finito para compatibilidade do esquema JSON.
A validação desse campo não garante a correção de todas as frases ou cálculos.

A comparação de `allow_delegation=False/True` mantém a mesma tarefa e dois
agentes disponíveis. O pedido de consulta ao colega é idêntico nas duas condições.
Habilitar a ferramenta não garante que o modelo a utilizará.
O desafio opcional usa um único agente nas três tarefas sequenciais; seu perfil
combina as três biografias. Por isso o teste é exploratório, com diferença de
perfil além da diferença no número de agentes.

## Leitura dos resultados

O relatório de cada execução apresenta a tabela completa, a variação entre
rodadas, as falhas e os eventos do guardrail. `reavaliacao_juiz.json` repete o
julgamento sobre as mesmas respostas da rodada 1, separando a variação do juiz
da variação da geração. Duas rodadas não sustentam generalização estatística.
A rubrica mede cobertura textual: pode aceitar negações e perder sinônimos.
Os custos do juiz ficam separados da produção. Os tempos de produção excluem
o juiz. As tarifas consultadas em 12/11/2026 estão no protocolo; US$ são
estimativas pelo consumo registrado, não uma leitura da fatura.

## Histórico do IPHAN

Os experimentos anteriores continuam em `resultados/20261112T233206Z`
(tentativa interrompida por incompatibilidade do esquema Decimal) e
`resultados/20261112T233457Z` (experimento completo do IPHAN).
Seus números e conclusões pertencem ao caso do IPHAN e não são resultados da SEFAZ.
Os arquivos de entrada e manifestos originais dessas pastas foram preservados.

## Resultado SEFAZ-MT — 12/11/2026

[Relatório completo da SEFAZ-MT](resultados/20261112T234559Z/relatorio.md),
com as duas rodadas, variação do juiz, falhas, delegação, desafio opcional e
conclusão dos itens 13 a 15. Foram produzidas 13 medições e quatro reavaliações.
A chamada única custou em média US$ 0,001348; a equipe estruturada, US$ 0,007152,
sem ganho de utilidade observado. Todas as condições principais atingiram 6/6.
O guardrail interceptou os R$ 600 mil e restaurou R$ 200 mil, mas a resposta
corrigida omitiu o confronto com PTA (5/6): o valor validado não dispensa revisão.

## Demonstração curta: uma chamada versus três agentes

Dentro de `aula04`, execute sem precisar ativar o ambiente:

```bash
.venv-crewai/bin/python minilab.py comparar
```

O comando faz uma rodada com o mesmo dossiê e modelo: primeiro uma chamada
direta à IA, depois a equipe com técnico, financeiro e parecerista, com saída
estruturada. Usa API e exibe uma tabela com cobertura, notas do juiz, chamadas,
tokens, tempo e custo. O juiz é contabilizado separadamente. Esta demonstração
não substitui as duas rodadas do experimento completo.

Os dois textos ficam em `resposta_unica.txt` e `resposta_equipe.txt` dentro de
uma nova pasta `resultados/comparacao_<identificador>`. O caminho é mostrado no
terminal e salvo em `resultados/ultima_comparacao.txt`. O relatório completo
anterior e `ultima_execucao.txt` permanecem como referências do experimento completo.
