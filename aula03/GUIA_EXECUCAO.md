# Guia de execução — Mini LAB de agentes de IA

Este guia mostra como preparar o projeto, o que executar e o que esperar de cada comando. Python executa os arquivos diretamente: não existe etapa de compilação.

## 1. Entre na pasta correta

Na máquina usada na atividade:

```bash
cd "/home/ficdevia-15-noite/Área de trabalho/libia/agente_ia/aula03"
```

Para quem baixar do GitHub: baixe o ZIP e abra a pasta extraída no terminal, ou copie a URL exibida no botão **Code** e use:

```bash
git clone URL_DO_REPOSITORIO minilab-agente
cd minilab-agente
```

Substitua `URL_DO_REPOSITORIO` pela URL real antes de executar. Os arquivos `exemplo01.py`, `README.md` e `requirements.txt` precisam aparecer na pasta atual. No VS Code, abra essa pasta e escolha **Terminal → Novo Terminal**.

O repositório deste laboratório corresponde à aula03. Todos os comandos deste guia são executados dentro dele.

## 2. Prepare o Python e instale as dependências

Você precisa do Python instalado. O ambiente utilizado na atividade foi Python 3.14. Os exemplos abaixo de criação e ativação são para Linux/macOS.

Confira a versão:

```bash
python3 --version
```

Na primeira instalação, crie o ambiente virtual e instale os pacotes:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Se o ambiente já estiver preparado, basta ativá-lo ao abrir um novo terminal:

```bash
source .venv/bin/activate
```

O texto `(.venv)` costuma aparecer no início da linha do terminal. O ambiente virtual reúne as dependências deste projeto. Não coloque seus arquivos de código dentro de `.venv`.

No Windows, usando PowerShell, a sequência equivalente é:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Se a ativação não estiver disponível, use diretamente o interpretador do ambiente. No Linux/macOS, por exemplo:

```bash
.venv/bin/python exemplo01.py
```

No Windows:

```powershell
.\.venv\Scripts\python.exe exemplo01.py
```

## 3. Faça primeiro a demonstração local

Esta sequência não usa a API e não exige uma chave.

### A. Mostre as ferramentas

```bash
python exemplo01.py
```

**O que aparece:** o esquema JSON das três ferramentas, com nomes e argumentos. Na terceira, aparecem as descrições de `valor_base` e `percentual` e a orientação de quando não usar a ferramenta.

**O que dizer:** “Aqui estão as ferramentas que o modelo pode escolher. A descrição explica quais dados cada uma recebe.”

### B. Confira as perguntas e o gabarito

```bash
python exemplo04.py validar
```

**Saída esperada:**

```text
12 consultas válidas; proporção 6/3/2/1; gabarito presente.
```

Isso verifica a estrutura do conjunto. A comparação das respostas dos modelos acontece na medição com a API.

**O que dizer:** “Escrevi as perguntas e as respostas esperadas antes de executar os modelos.”

### C. Execute as verificações automáticas

```bash
python -m unittest discover -s tests -v
```

**O que aparece:** os nomes dos testes e, se todos passarem, `OK`. Há seis testes locais nesta versão, com respostas de modelo simuladas.

Eles verificam pontos como o cálculo de custo, a pontuação, os argumentos inválidos e o bloqueio de números sem origem identificada. Não reproduzem uma nova medição de qualidade dos modelos reais.

Para uma apresentação curta, este passo é opcional.

### D. Mostre os resultados já registrados

Abra `lab_ferramentas/RELATORIO.md` no VS Code e pressione **Ctrl + Shift + V**. A prévia mostra as tabelas formatadas.

Para mostrar somente as tabelas da rodada principal original pelo terminal, sem fazer novas chamadas:

```bash
cat resultados/ferramentas/20261111T233707644835Z/tabelas.md
```

**O que dizer:** “O nano acertou nove perguntas. Luna e superior acertaram doze, mas o superior custou cerca de vinte vezes mais que o Luna.”

## 4. Configure a chave para executar os modelos reais

Esta etapa é necessária para a comparação e os testes de ataques com a OpenAI.

Na primeira configuração, se `.env` ainda não existir, crie-o copiando `.env.example`. No Linux/macOS, este comando preserva um `.env` existente:

```bash
cp -n .env.example .env
```

Abra o arquivo `.env` no editor e preencha somente nele:

```dotenv
OPENAI_API_KEY=SUA_CHAVE_AQUI
```

Substitua `SUA_CHAVE_AQUI` pela sua chave. A chave não deve aparecer no README, nos prints da apresentação ou em commits. O `.env` é ignorado pelo Git; o `.env.example` contém apenas o nome da variável.

Os modelos utilizados estão em `lab_ferramentas/configuracoes.json`. Para repetir a rodada, sua conta precisa ter acesso aos modelos e à API. Os preços e resultados registrados são históricos; uma nova execução pode produzir respostas, tempos e custos diferentes.

## 5. Repita a comparação dos três modelos

**Este comando faz chamadas cobradas à OpenAI:**

```bash
python exemplo04.py executar --volume-mensal 1000
```

**O que acontece:**

1. O programa verifica se os arquivos continuam iguais aos registrados no manifesto.
2. Executa as doze perguntas com cada uma das três configurações.
3. Registra respostas, ferramentas utilizadas, passos, tempo e tokens.
4. Imprime as duas tabelas de avaliação e custo.
5. Mostra a pasta em que os resultados foram salvos.

São **36 consultas ao agente**. Uma consulta pode usar várias chamadas ao modelo. O parâmetro `1000` representa a demanda mensal hipotética e não dispara mil consultas.

**Onde os resultados ficam:**

```text
resultados/ferramentas/DATA_DA_EXECUCAO/
├── medicoes.jsonl    # Respostas e métricas por consulta
├── resumos.json     # Totais e estatísticas por configuração
├── tabelas.md       # Duas tabelas formatadas
├── manifesto.json   # Registro do congelamento
└── ...              # Cópias do código, dados e configurações
```

O arquivo `resultados/ferramentas/ultima_execucao.txt` aponta para a rodada mais recente. Cada rodada cria uma pasta própria, preservando as anteriores.

## 6. Repita os ataques e os testes da barreira

**Este comando também faz chamadas cobradas à OpenAI:**

```bash
python exemplo05.py --configuracao luna
```

Ele executa as doze perguntas com a barreira simples e com a barreira que rastreia a origem dos números. Depois testa os casos de falha, sem barreira e com rastreamento. O nome `luna` é o rótulo da configuração no arquivo JSON.

**O que observar:**

- `FP=True`: houve bloqueio em uma das consultas benignas; o log registra o motivo.
- `resistiu`: o objetivo proibido não foi observado naquele ensaio.
- `falhou`: o comportamento avaliado como proibido apareceu.
- `inconclusivo`: houve erro que impediu avaliar o comportamento.

As evidências ficam em `resultados/ferramentas/falhas-DATA_DA_EXECUCAO/`:

| Arquivo | O que contém |
| --- | --- |
| `barreiras.jsonl` | Respostas e bloqueios das doze perguntas em cada barreira |
| `resumo_barreiras.json` | Quantidade de falsos positivos e acertos |
| `ataques.jsonl` | Resultados dos ataques |
| `falhas.md` | Resumo dos ensaios |

`resultados/ferramentas/ultimas_falhas.txt` aponta para os ensaios mais recentes.

A barreira está em `lab_ferramentas/agente.py`, nas funções `verificar_origens` e `barreira`. Ela é ativada pelo exemplo05. A comparação do exemplo04 usa o agente sem essa barreira.

## 7. Gere o relatório completo usando os resultados salvos

Depois de uma rodada principal e de uma rodada de falhas concluídas:

```bash
python -m lab_ferramentas.gerar_relatorio
```

Este comando **não chama a OpenAI**. Ele lê os registros indicados por `ultima_execucao.txt` e `ultimas_falhas.txt` e atualiza `lab_ferramentas/RELATORIO_COMPLETO.md`.

O arquivo `lab_ferramentas/RELATORIO.md`, usado na apresentação, é um resumo da rodada original e permanece igual. Para apresentar uma nova rodada, confira se os números do resumo ainda correspondem aos resultados que você deseja mostrar.

## 8. Comandos alternativos e ajuda

As entradas da raiz e os módulos abaixo executam os mesmos exemplos. Use uma forma por vez:

| Entrada na raiz | Forma equivalente como módulo |
| --- | --- |
| `python exemplo01.py` | `python -m lab_ferramentas.exemplo01` |
| `python exemplo04.py validar` | `python -m lab_ferramentas.exemplo04 validar` |
| `python exemplo04.py executar --volume-mensal 1000` | `python -m lab_ferramentas.exemplo04 executar --volume-mensal 1000` |
| `python exemplo05.py --configuracao luna` | `python -m lab_ferramentas.exemplo05 --configuracao luna` |

Não execute diretamente `python lab_ferramentas/exemplo04.py`: os arquivos do pacote usam importações relativas. Use a entrada da raiz ou a forma com `-m`.

Para consultar as opções disponíveis:

```bash
python exemplo04.py --help
python exemplo05.py --help
```

## 9. Erros comuns

| Mensagem ou situação | Como resolver |
| --- | --- |
| `can't open file` / arquivo não encontrado | Confira a pasta atual e o nome digitado. Na raiz, use `python exemplo01.py`. |
| Nome com `^?` ou `\x7f` | Pressione Ctrl+C e digite o comando novamente em uma linha. |
| `the following arguments are required: acao` | Informe a ação: `python exemplo04.py validar` ou `python exemplo04.py executar --volume-mensal 1000`. |
| `ModuleNotFoundError` | Ative `.venv` e rode `python -m pip install -r requirements.txt`. |
| Erro de importação relativa | Use `python exemplo04.py ...` na raiz ou `python -m lab_ferramentas.exemplo04 ...`. |
| `python: command not found` | Ative o ambiente ou use `.venv/bin/python` no Linux/macOS. |
| Erro ao criar `.venv` | Confira a instalação do Python e se o suporte a ambientes virtuais está disponível no sistema. |
| Chave ausente ou erro de autenticação | Confira o preenchimento de `OPENAI_API_KEY` no `.env` da raiz. Não envie a chave no chat. |
| Modelo sem acesso ou erro da API | Confira a configuração usada e o acesso da sua conta. Preserve os erros nos registros; não os apresente como acertos. |
| Arquivo de resultados não encontrado ao gerar relatório | Execute na raiz e confira os caminhos escritos nos dois arquivos de ponteiro. |
| `FileExistsError` ao executar `congelar` | O manifesto já existe. Esta entrega já foi congelada; esse comando não faz parte da execução habitual. |
| Gabarito/código alterado após congelamento | Compare com os arquivos versionados. Para restaurar a rodada original, recupere os arquivos correspondentes; para estudar mudanças, prepare um novo experimento com gabarito e manifesto antes das chamadas. |

Não apague o manifesto para contornar a verificação: ele documenta o que estava definido antes da avaliação.

## 10. Sequência recomendada para apresentar

1. Execute `python exemplo01.py` e mostre as ferramentas.
2. Execute `python exemplo04.py validar` e mostre que há doze perguntas.
3. Abra o relatório resumido e apresente os acertos e os custos.
4. Mostre a tabela de barreiras: três bloqueios indevidos na versão simples e zero com rastreamento.
5. Explique a escolha do Luna e a necessidade de conferência humana antes de aprovar despesa.

Essa apresentação pode ser feita inteiramente com os registros existentes. As falas estão em [APRESENTACAO.md](APRESENTACAO.md).
