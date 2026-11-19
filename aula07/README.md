# Aula 07 · Agentes com memória persistente

O objetivo é entender **o que um agente lembra entre chamadas**, quanto esse contexto custa e como inspecionar ou excluir informações persistidas. Os exemplos usam Agno, SQLite e um atendimento fictício sobre IPVA.

## Exemplos

| Arquivo | O que você observa |
| --- | --- |
| [exemplo01.py](exemplo01.py) | Demonstra histórico de sessão, memórias do usuário, resumo da sessão e memória agêntica. A pergunta sobre a placa permite observar a lembrança e os tokens de entrada no segundo turno. |
| [exemplo02.py](exemplo02.py) | Compara cinco configurações no mesmo roteiro de 12 turnos. Mede acertos nas verificações de memória, consumo de tokens, tempo e custo estimado. |
| [exemplo03.py](exemplo03.py) | Inspeciona as tabelas do SQLite e testa em etapas a exclusão de uma sessão e das memórias do usuário. |
| [exemplo04.py](exemplo04.py) | Provoca três falhas para observar seus efeitos. São elas troca de sessão, memória desatualizada e crescimento do histórico sem limite. |

## Como executar

Na raiz do repositório, prepare um ambiente com Python 3.12:

```bash
python3.12 -m venv aula07/.venv
aula07/.venv/bin/python -m pip install "agno==3.2.1" "SQLAlchemy==2.1.9" "openai==3.54.0" "python-dotenv==1.2.4"
```

Crie `aula07/.env` e preencha a variável `OPENAI_API_KEY`. Os scripts usam o modelo `gpt-5.6-luna`. Use a sua credencial com acesso a esse modelo e mantenha o arquivo local.

```bash
aula07/.venv/bin/python aula07/exemplo01.py
aula07/.venv/bin/python aula07/exemplo02.py
aula07/.venv/bin/python aula07/exemplo03.py
aula07/.venv/bin/python aula07/exemplo04.py
```

Cada exemplo pode ser executado separadamente e faz chamadas à OpenAI. O exemplo 02 lê [roteiro_atendimento.json](roteiro_atendimento.json) e grava [resultado_memoria.json](resultado_memoria.json) com as medições da rodada. A estimativa usa os valores definidos no script.

Os scripts reiniciam os bancos de teste que usam. O `.gitignore` mantém os bancos, as credenciais e o ambiente virtual fora do Git. Para repetir os experimentos, use os dados fictícios dos roteiros.
