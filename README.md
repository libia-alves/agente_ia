# Agentes de IA — estudos e projetos do curso

Este repositório reúne as atividades do **módulo de Agentes Autônomos do curso de Formação em IA**. Ao longo das aulas, vamos construir agentes de inteligência artificial, conectar modelos a ferramentas e aprender a avaliar suas decisões antes de ampliar sua autonomia.

Cada pasta registra uma etapa desse aprendizado: conceitos, exemplos em Python, exercícios práticos e resultados. O repositório será ampliado conforme novas aulas e novos agentes forem desenvolvidos.

## O que estamos aprendendo?

Um agente pode receber um objetivo, escolher uma ferramenta, pedir que a aplicação execute uma operação e usar o resultado para decidir o próximo passo. Isso permite criar assistentes que consultam informações, fazem cálculos e ajudam em tarefas de um setor.

Por exemplo, para responder “qual é o valor de um contrato com 10% de acréscimo?”, o agente pode consultar o contrato, enviar o valor à ferramenta de cálculo e apresentar o resultado.

Neste módulo, estudamos como:

- Identificar tarefas que podem receber apoio de um agente e definir seus limites.
- Integrar modelos de linguagem a aplicações Python.
- Criar ferramentas com nomes, descrições e argumentos bem definidos.
- Acompanhar as chamadas e os resultados que levam à resposta final.
- Medir acerto, tempo, quantidade de passos e custo por consulta.
- Provocar falhas, aplicar proteções e definir quando uma pessoa precisa conferir o resultado.

## Organização das aulas

| Aula | Tema | Atividades neste repositório |
| --- | --- | --- |
| [Aula 01](aula01/README.md) | Planejamento da automação por agentes | Mapeamento de processos, riscos, etapas e estimativas de custo |
| [Aula 02](aula02/README.md) | Introdução ao LangChain | Integração com modelos, extração de dados de documentos e avaliação de resultados |
| [Aula 03](aula03/README.md) | Agente LangChain com acesso a ferramentas | Declaração de ferramentas, consultas e cálculos, medição de custo e testes de falhas |
| [Aula 04](aula04/README.md) | Equipes CrewAI | Comparação de chamada única, agentes e validação de pareceres |
| [Aula 05](aula05/README.md) | Orquestração CrewAI | Hierarquia, Flow com desvios, persistência e revisão humana |

Cada aula possui seu próprio README com a proposta e as instruções de execução.

## Aula 03 — do texto às chamadas de ferramentas

Nesta aula, estudamos como o modelo solicita operações e como a aplicação executa essas solicitações. O material usa um assistente jurídico como cenário; no Mini LAB, adaptamos a prática para um assistente de contratos.

### 1. Como o modelo conhece uma ferramenta

O modelo recebe o **nome**, a **descrição** e o **esquema dos argumentos**. Esses elementos explicam para que a ferramenta serve e quais dados devem ser enviados. A aplicação executa a função Python quando recebe uma chamada válida.

Estudamos três formas de declarar ferramentas: o decorador `@tool`, uma função anotada convertida na lista de ferramentas e `StructuredTool` com um esquema Pydantic. Descrever o significado de cada argumento ajuda a evitar o uso de um valor no campo errado.

### 2. Como acompanhar as decisões do agente

Estudamos a criação de agentes com `create_agent` e o fluxo de mensagens entre modelo e ferramentas. O agente pode solicitar uma consulta, receber os dados, pedir um cálculo e então responder. Registrar esse fluxo permite conferir quais argumentos foram utilizados em cada operação.

### 3. Como controlar as operações

O **middleware** permite intervir durante a execução. Na aula, conhecemos controles para limitar chamadas, acompanhar argumentos e exigir conferência humana em operações sensíveis.

Na prática do Mini LAB, implementamos uma barreira em `wrap_tool_call`: antes de permitir um cálculo, ela verifica a origem dos números. Quando bloqueia a operação, devolve uma `ToolMessage` para manter o fluxo de mensagens consistente.

### 4. Como avaliar qualidade e custo

Preparamos perguntas com gabarito antes da execução e comparamos configurações da OpenAI. Avaliamos a resposta, a escolha das ferramentas, os passos, o tempo e o custo total.

Também estudamos a distribuição de custo: a consulta típica pode custar menos que uma consulta que exige vários passos. Por isso, analisamos a mediana e a cauda ao estimar uma demanda mensal.

### 5. Como investigar falhas

Testamos situações com dados ausentes, argumentos inválidos e tentativas de inserir instruções maliciosas na pergunta ou no retorno de uma ferramenta.

Uma proteção também pode bloquear uma operação correta por engano. No laboratório, rastrear a origem dos valores permitiu aceitar números retornados pelas ferramentas e reduzir esses bloqueios indevidos.

## Agente desenvolvido no Mini LAB

O assistente da aula03 possui três ferramentas:

| Ferramenta | Função |
| --- | --- |
| `consultar_contrato` | Buscar fornecedor, valor e situação de um contrato |
| `consultar_regra` | Consultar um percentual didático de acréscimo |
| `simular_acrescimo` | Calcular o acréscimo e o novo total |

Os contratos e percentuais desse assistente são **fictícios**, utilizados para aprendizado. Uma simulação não representa autorização de despesa nem aprovação de aditivo.

- [Conhecer o laboratório e seus desafios](aula03/README.md)
- [Ver o resumo dos resultados](aula03/lab_ferramentas/RELATORIO.md)
- [Consultar o relatório completo](aula03/lab_ferramentas/RELATORIO_COMPLETO.md)
- [Seguir o roteiro de apresentação](aula03/APRESENTACAO.md)

## Como começar

Clone o repositório e entre na aula que deseja estudar:

```bash
git clone https://github.com/libia-alves/agente_ia.git
cd agente_ia
```

Para preparar e demonstrar o laboratório da aula03 no Linux/macOS:

```bash
cd aula03
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python exemplo01.py
python exemplo04.py validar
```

O primeiro exemplo mostra as ferramentas. O comando `validar` confere as doze perguntas e o gabarito. Ambos são locais e não fazem chamadas à API.

Para executar os modelos reais, configure sua chave no `.env` da aula e siga as instruções do README correspondente. Essas execuções podem gerar cobrança. Mantenha a chave fora dos arquivos publicados.

## Sobre os estudos

As implementações foram desenvolvidas com auxílio de IA e devem ser lidas junto aos materiais do curso. Os resultados registrados representam os ensaios realizados; a conferência humana continua necessária antes de decisões com consequência administrativa.

O conteúdo da aula03 toma como referência o material **“Um Agente LangChain com Acesso a Ferramentas”**, dos professores **Dr. Benevid Felix da Silva** e **Dr. Robson Gomes de Melo**.
