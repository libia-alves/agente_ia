# Mini LAB — construindo e avaliando um agente de IA

Um agente que consulta contratos, escolhe ferramentas e simula acréscimos financeiros. Este projeto da **aula 03** explora uma pergunta prática: **como saber se um agente está acertando, quanto custa e quando precisa ser impedido de agir?**

O cenário é inspirado no setor de contratos da SEFAZ. **Os contratos e os percentuais são fictícios**, preparados para aprendizado. A implementação utiliza modelos da OpenAI e LangChain, com apoio de IA no desenvolvimento e na elaboração do gabarito.

## Comece por aqui

- **Quer executar?** Siga o [guia de execução passo a passo](GUIA_EXECUCAO.md).
- **Quer apresentar?** Use o [roteiro curto com falas e comandos](APRESENTACAO.md).
- **Quer ver os resultados?** Abra o [relatório resumido](lab_ferramentas/RELATORIO.md).
- **Quer entender a atividade?** Os desafios estão explicados abaixo.

Depois de instalar as dependências e ativar o ambiente virtual, a demonstração local é:

```bash
python exemplo01.py
python exemplo04.py validar
python -m unittest discover -s tests -v
```

Esses três comandos não fazem chamadas à OpenAI. Não exigem chave nem geram cobrança de API.

## Por que este projeto é um agente de IA?

O modelo recebe uma pergunta e pode decidir chamar uma ferramenta, usar o resultado em uma segunda operação ou pedir informações que faltam. O código executa as funções escolhidas e devolve os resultados ao modelo, que prepara a resposta.

Por exemplo:

> Consulte o contrato LAB-001 e calcule o total com um acréscimo de 10%.

1. O agente escolhe consultar o contrato.
2. A ferramenta retorna o valor de **R$ 100.000**.
3. O agente chama a ferramenta de cálculo com esse valor e **10%**.
4. A função Python calcula o total de **R$ 110.000**.
5. O agente apresenta a resposta ao usuário.

O ponto interessante é acompanhar uma pergunta se transformar em uma sequência de ações. Podemos observar tanto uma boa decisão quanto um erro na escolha da ferramenta ou dos argumentos.

O projeto utiliza um modelo pronto. O trabalho de desenvolvimento está nas instruções, nas ferramentas, na integração, na avaliação e nas proteções do agente.

## Desafio 1 — ensinar ao modelo quais ferramentas existem

**O que a atividade pede:** criar três ferramentas usando três formas diferentes de declaração e explicar quando a ferramenta mais sensível não deve ser usada.

| Ferramenta | O que faz | Como foi declarada |
| --- | --- | --- |
| `consultar_contrato` | Busca fornecedor, valor e situação de um contrato | Decorador `@tool` |
| `consultar_regra` | Consulta um percentual didático | Função com tipos anotados, convertida ao entrar na lista do agente |
| `simular_acrescimo` | Calcula o acréscimo e o novo total | `StructuredTool` com esquema Pydantic |

**O que aprendemos:** para escolher uma ferramenta, o modelo recebe seu nome, sua descrição e o esquema dos argumentos. Cada campo da ferramenta de cálculo possui uma descrição: `valor_base` é o valor original em reais; `percentual` é o acréscimo em pontos percentuais.

A descrição também orienta a não calcular quando faltar um valor com origem verificável e a não usar a simulação para aprovar um aditivo ou autorizar despesa.

**Onde conferir:** [ferramentas.py](lab_ferramentas/ferramentas.py).

**Como demonstrar, sem chamadas à API:**

```bash
python exemplo01.py
```

O comando imprime o esquema que comunica ao modelo o significado dos argumentos.

## Desafio 2 — escrever as perguntas e o gabarito antes dos testes

**O que a atividade pede:** preparar doze consultas e definir antecipadamente como uma resposta será considerada correta.

| Tipo de consulta | Quantidade | Comportamento esperado |
| --- | --- | --- |
| Uma ferramenta | 6 | Consultar um dado ou fazer uma simulação |
| Duas ferramentas | 3 | Usar o resultado de uma consulta em outra operação |
| Sem ferramenta | 2 | Cumprimentar ou explicar suas capacidades |
| Armadilha com dados ausentes | 1 | Pedir os dados necessários, sem inventar valores |

**O que aprendemos:** precisamos de uma resposta esperada para medir qualidade. O critério aceita diferenças de acentuação, caixa e pontuação, além de alternativas textuais previstas. Números precisam respeitar a tolerância definida; um valor errado não recebe ponto por parecer semelhante.

O gabarito e o código foram congelados com hashes antes das chamadas. Um hash funciona como uma impressão digital do arquivo: permite detectar alterações posteriores. O gabarito não é enviado ao agente.

**Onde conferir:** [consultas.json](lab_ferramentas/consultas.json) e [manifesto.json](lab_ferramentas/manifesto.json).

**Como demonstrar, sem chamadas à API:**

```bash
python exemplo04.py validar
```

## Desafio 3 — medir qualidade, tempo e custo

**O que a atividade pede:** executar pelo menos três configurações da OpenAI, incluindo uma econômica e uma superior, preencher as tabelas e comparar a consulta mais cara com a mediana.

**O que foi medido:**

- **Acerto:** a resposta corresponde ao gabarito?
- **Ferramenta certa:** o agente tentou exatamente as ferramentas esperadas?
- **Passos:** quantas chamadas ao modelo foram necessárias, incluindo a resposta final?
- **Tempo:** quanto demorou cada consulta e a rodada inteira?
- **Custo:** quanto custaram os tokens de todos os passos, considerando o cache de entrada?

Resultados da rodada registrada em **11/11/2026**:

| Configuração | Modelo | Acerto | Ferramenta certa | US$ nas 12 consultas |
| --- | --- | --- | --- | --- |
| Nano econômico | `gpt-5-nano` | 9/12 | 9/12 | 0,001215 |
| Luna | `gpt-6-luna` | 12/12 | 12/12 | 0,001718 |
| Sol superior | `gpt-6.1-sol` | 12/12 | 12/12 | 0,034664 |

O superior custou **20,18 vezes mais que o Luna**, com o mesmo acerto nesta amostra. O nano também foi mais barato por consulta, mas teve três erros.

A distribuição do custo também importa. No Luna, a consulta mais cara custou **1,71 vez a mediana**. A mediana representa a consulta típica; o máximo mostra quanto uma consulta mais trabalhosa chegou a custar nesta rodada.

**Onde conferir:** [resumo das tabelas](lab_ferramentas/RELATORIO.md), [relatório completo](lab_ferramentas/RELATORIO_COMPLETO.md) e [resultados registrados](resultados/ferramentas/).

**Para repetir a medição — faz chamadas cobradas à OpenAI:**

```bash
python exemplo04.py executar --volume-mensal 1000
```

O parâmetro `1000` serve para a projeção mensal. A rodada executa as doze consultas em cada uma das três configurações.

## Desafio 4 — provocar falhas e criar uma barreira

**O que a atividade pede:** testar situações difíceis, escrever uma tentativa de injeção de instruções e proteger a operação mais sensível com `wrap_tool_call`, devolvendo `ToolMessage` quando houver bloqueio.

Foram testados valor ausente, valor negativo, contrato inexistente, injeção na pergunta e injeção no retorno de uma ferramenta. Uma tentativa dizia “Modo de homologação” e pedia que o agente declarasse um aditivo aprovado. Ela não continha a expressão “ignore as instruções anteriores”.

**Resultado observado:** o Luna resistiu aos ataques executados. Isso descreve os ensaios realizados; não garante resistência a qualquer ataque.

Também houve erros na avaliação principal. Em uma pergunta que pedia **10%**, o nano utilizou **15%**, retornando **R$ 115.000** em vez de **R$ 110.000**. Escolher a ferramenta e preencher seus argumentos são decisões que precisam ser verificadas.

### O que a proteção verifica?

Antes de executar o cálculo, a barreira confere de onde vieram o valor e o percentual. Se não consegue confirmar a origem, bloqueia a chamada e devolve uma mensagem para que o agente solicite os dados.

A primeira versão aceitava somente números presentes na pergunta. Isso bloqueava valores legítimos vindos de outra ferramenta. Esse bloqueio por engano é chamado de **falso positivo**.

| Proteção nas doze consultas | Falsos positivos |
| --- | --- |
| Aceita apenas números presentes na pergunta | 3 |
| Reconhece também valores retornados pelas ferramentas | 0 |

**Onde conferir:** funções `verificar_origens` e `barreira` em [agente.py](lab_ferramentas/agente.py). A barreira é ativada nos ensaios do [exemplo05.py](lab_ferramentas/exemplo05.py); a comparação principal do exemplo04 é feita sem essa barreira.

**Para repetir os ensaios — faz chamadas cobradas à OpenAI:**

```bash
python exemplo05.py --configuracao luna
```

## Desafio opcional — rastrear a origem dos números

**O que a atividade propõe:** distinguir um número fornecido pelo usuário ou por outra ferramenta de um número sem fonte produzido pelo agente.

Foi implementado um rastreamento por argumento. Por exemplo, os **R$ 100.000** podem ser associados ao campo `valor` retornado pela chamada de `consultar_contrato`. O percentual pode vir da pergunta ou do campo retornado por `consultar_regra`.

Assim, a proteção reconhece que o valor veio de uma consulta e permite o cálculo. Esse rastreamento eliminou os três falsos positivos observados.

**Limite do protótipo:** a identificação dos valores do usuário usa as notações `R$` e `%`. Origem conhecida não comprova que um dado é verdadeiro ou que uma despesa pode ser autorizada. A barreira protege a chamada da ferramenta; a resposta final também precisa ser conferida.

## Desafio 5 — escolher uma configuração e justificar a decisão

**O que a atividade pede:** analisar os resultados, estimar o custo mensal e indicar onde a conferência humana é obrigatória.

A escolha proposta foi **Luna com rastreamento de origem, em um piloto supervisionado**. Ele acertou as doze consultas e teve custo inferior ao superior.

Para uma hipótese de **1.000 consultas por mês** no Luna:

| Referência de custo | Projeção mensal |
| --- | --- |
| Mediana da rodada principal | US$ 0,13 |
| Cauda da rodada principal | US$ 0,23 |

Nesta amostra de doze consultas, o P95 coincide com o máximo. Aplicar esse custo a todas as consultas representa um cenário de estresse. Apresentaria os dois números ao gestor e usaria a cauda como referência de reserva. A estimativa considera a API, sem infraestrutura ou trabalho humano.

**Conferência humana obrigatória:** antes de aprovar um aditivo ou autorizar uma despesa. Um erro na base ou no percentual pode gerar uma despesa indevida e responsabilização administrativa.

## Comandos de execução

Execute os comandos na raiz deste projeto, onde estão `exemplo01.py` e `requirements.txt`, com o ambiente virtual ativo. Na cópia local da atividade, essa pasta é `aula03`.

| O que você quer fazer | Comando | Usa a API? |
| --- | --- | --- |
| Ver a descrição das ferramentas | `python exemplo01.py` | Não |
| Validar as doze perguntas e o gabarito | `python exemplo04.py validar` | Não |
| Executar os testes locais | `python -m unittest discover -s tests -v` | Não |
| Comparar os três modelos | `python exemplo04.py executar --volume-mensal 1000` | Sim, com cobrança |
| Testar ataques e barreiras | `python exemplo05.py --configuracao luna` | Sim, com cobrança |
| Atualizar o relatório detalhado com dados salvos | `python -m lab_ferramentas.gerar_relatorio` | Não |
| Ver as opções da medição | `python exemplo04.py --help` | Não |

A comparação chama o agente 36 vezes: doze consultas para cada configuração. Cada consulta pode exigir mais de uma chamada ao modelo. O valor `1000` apenas define o volume usado na projeção mensal.

**Instalação, configuração do `.env`, saídas esperadas, localização dos resultados e solução de erros:** [GUIA_EXECUCAO.md](GUIA_EXECUCAO.md).

O gabarito desta entrega já está congelado. Não repita `congelar`; mudanças nos arquivos congelados precisam de uma nova versão do experimento antes da medição.

## Onde encontrar cada parte

| Arquivo ou pasta | Conteúdo |
| --- | --- |
| [GUIA_EXECUCAO.md](GUIA_EXECUCAO.md) | Instalação, comandos e solução de erros |
| [APRESENTACAO.md](APRESENTACAO.md) | Falas e comandos para apresentar |
| [RELATORIO.md](lab_ferramentas/RELATORIO.md) | Resumo curto com os principais números |
| [RELATORIO_COMPLETO.md](lab_ferramentas/RELATORIO_COMPLETO.md) | Análise detalhada e referências às evidências |
| [ferramentas.py](lab_ferramentas/ferramentas.py) | Declaração das três ferramentas e base fictícia |
| [agente.py](lab_ferramentas/agente.py) | Agente, avaliação, custos e barreira |
| [consultas.json](lab_ferramentas/consultas.json) | Doze perguntas e gabarito |
| [configuracoes.json](lab_ferramentas/configuracoes.json) | Modelos, raciocínio e tarifas usadas na medição |
| [resultados/](resultados/ferramentas/) | Logs, respostas, argumentos e métricas |
| [tests/](tests/) | Verificações locais sem consumo de API |

Os registros históricos foram preservados, incluindo um ensaio inicial com erro de leitura de respostas, documentado no relatório completo. Os arquivos originais do curso ficam em `material_original/` na cópia local e são ignorados pelo Git.

A atividade mostra como desenvolver um agente, observar suas decisões e medir suas limitações. A parte mais interessante é poder investigar cada etapa: **qual ferramenta ele escolheu, quais números utilizou e por que chegou àquela resposta.**
