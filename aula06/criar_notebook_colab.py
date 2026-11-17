"""Empacota fontes locais em notebook independente para o Google Colab."""
import json
from pathlib import Path
import textwrap

BASE = Path(__file__).resolve().parent
celulas = []


def md(texto):
    celulas.append({'cell_type':'markdown','metadata':{},'source':textwrap.dedent(texto).strip().splitlines(keepends=True)})


def codigo(texto):
    celulas.append({'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],
                    'source':textwrap.dedent(texto).strip().splitlines(keepends=True)})


md('''
# Aula 06 — Desafio opcional no Google Colab
**Atendimento de TI da SEFAZ-MT · dados fictícios**

Entregar as quatro funções da Parte 1 a agentes do **LangChain e CrewAI**, localizar
as consultas no resultado de cada framework e escrever as duas funções que gravam
esse registro. Este notebook contém tudo de que precisa; não depende da pasta do projeto.

**Como usar:** abra este `.ipynb` em https://colab.research.google.com por
**Arquivo → Fazer upload de notebook**, conecte um ambiente **CPU** e execute as células
na ordem. A instalação pode levar alguns minutos. Se o Colab solicitar reinício da
sessão depois da instalação, reinicie e execute novamente a partir da célula 2.

As funções puras funcionam sem chave. As células dos agentes usam uma chave OpenAI
com acesso ao modelo e geram consumo de API. Ao final, baixe o ZIP com as evidências.
Os resultados deste arquivo estão vazios para serem produzidos na sua sessão Colab.
''')
md('''
## 1. Instalar as bibliotecas
Versões fixadas para manter os campos usados no registro. O CrewAI desta versão
requer Python de 3.10 até 3.13; use um runtime compatível no Colab. GPU não é necessária.
''')
codigo('''
import sys
assert (3, 10) <= sys.version_info[:2] < (3, 14), "Selecione um runtime Colab com Python 3.10–3.13."
%pip install -q "crewai==1.15.21" "langchain==1.4.10" "langchain-openai==1.8.0"
''')
md('''
## 2. Criar as quatro ferramentas da Parte 1
A célula abaixo grava `ferramentas.py`. São as mesmas funções Python do minilab;
nenhuma importa Agno, LangChain ou CrewAI. Os prazos são hipotéticos e o cálculo
não considera feriados. Os nomes das fontes e regras precisam de validação do setor.
''')
codigo('%%writefile ferramentas.py\n' + (BASE/'ferramentas.py').read_text(encoding='utf-8'))
md('''
## 3. Executar isoladamente, sem agente e sem chave
Confira os argumentos e os retornos antes de entregá-los aos frameworks.
''')
codigo('''
import runpy
runpy.run_path("ferramentas.py", run_name="__main__")
from ferramentas import consultar_chamado, calcular_prazo
chamado = consultar_chamado("2026009012")
vencimento = calcular_prazo(chamado["ultima_movimentacao"], 5)
assert vencimento["vencimento"] == "2026-11-20"
print("Consulta encadeada em Python puro:", vencimento)
''')
md('''
## 4. Configurar acesso ao modelo
No Colab, abra **Segredos** (ícone de chave), cadastre `OPENAI_API_KEY` e habilite
acesso para este notebook. Se preferir, a célula pede a chave em campo oculto.
A chave fica somente na variável de ambiente e não entra no ZIP.
''')
codigo('''
import os
from getpass import getpass
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"

if not os.environ.get("OPENAI_API_KEY"):
    try:
        from google.colab import userdata
        chave = userdata.get("OPENAI_API_KEY")
    except Exception:
        chave = getpass("Cole sua OPENAI_API_KEY (entrada oculta): ")
    if not chave or not chave.strip():
        raise ValueError("Informe uma chave para executar as células dos agentes.")
    os.environ["OPENAI_API_KEY"] = chave.strip()
    del chave
MODELO = "gpt-4o-mini"
print("Modelo:", MODELO, "· chave configurada, sem exibição")
''')
md('''
## 5. Onde fica o registro em cada framework?

| Framework | Resultado | Pedido de consulta | Retorno da ferramenta |
|---|---|---|---|
| LangChain | `resultado["messages"]` | `AIMessage.tool_calls`: `name`, `args`, `id` | `ToolMessage.content`, relacionado por `tool_call_id` |
| CrewAI (versão fixada) | `resultado.tasks_output[i].messages` | Mensagens `assistant`, campo `tool_calls`: `function.name`, `function.arguments`, `id` | Mensagens `role="tool"`: `content`, relacionado por `tool_call_id` |

As funções **`gravar_registro_langchain`** e **`gravar_registro_crewai`** abaixo
percorrem esses campos e salvam JSON com nome, argumentos e retorno.
`retorno_observado=False` significa pedido sem retorno encontrado; a resposta final
não é usada como prova de que a consulta aconteceu. Uma lista vazia é mantida vazia.

Referências: [create_agent e ToolMessage](https://reference.langchain.com/python/langchain/agents/factory/create_agent),
[TaskOutput no código oficial do CrewAI](https://github.com/crewAIInc/crewAI/blob/main/lib/crewai/src/crewai/tasks/task_output.py).
O campo `messages` também foi conferido no CrewAI 1.15.21 instalado para esta preparação.
''')
codigo('%%writefile desafio_frameworks.py\n' + (BASE/'desafio_frameworks.py').read_text(encoding='utf-8'))
md('''
## 6. Criar a pasta da execução e registrar as entradas
As oito perguntas são fictícias e iguais nos dois frameworks. As ferramentas
continuam sendo as mesmas quatro funções: somente o adaptador do framework muda.
O manifesto guarda versões e hashes antes das consultas, sem credenciais.
''')
codigo('''
import hashlib
import importlib.metadata
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from desafio_frameworks import (
    executar_langchain, executar_crewai,
    gravar_registro_langchain, gravar_registro_crewai,
)
PERGUNTAS = [
    {"id":"Q01", "texto":"Qual a situação do chamado 2026001234?"},
    {"id":"Q02", "texto":"Quem está atendendo a falha de rede do chamado 2026005678?"},
    {"id":"Q03", "texto":"Como peço acesso a um sistema e qual o prazo?"},
    {"id":"Q04", "texto":"Esqueci minha senha. Como devo proceder?"},
    {"id":"Q05", "texto":"Quais informações preciso enviar para restaurar um arquivo?"},
    {"id":"Q06", "texto":"Onde comunico um incidente de segurança?"},
    {"id":"Q07", "texto":"Qual a situação do chamado 2026009012 e quando vencem cinco dias úteis contados da última movimentação?"},
    {"id":"Q08", "texto":"Consulte o chamado 2026999999. Ele já foi resolvido?"},
]
PASTA = Path("resultados_desafio") / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid4().hex[:6])
PASTA.mkdir(parents=True)

def salvar(caminho, dados):
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2, default=str) + "\\n", encoding="utf-8")

manifesto = {
    "inicio_utc": datetime.now(timezone.utc).isoformat(),
    "ambiente": "Google Colab" if "google.colab" in sys.modules else "Validação local",
    "python": sys.version.split()[0], "modelo": MODELO,
    "dados": "fictícios", "setor": "Atendimento de TI da SEFAZ-MT",
    "versoes": {p: importlib.metadata.version(p) for p in ["crewai", "langchain", "langchain-openai"]},
    "sha256_fontes": {nome: hashlib.sha256(Path(nome).read_bytes()).hexdigest()
                      for nome in ["ferramentas.py", "desafio_frameworks.py"]},
}
salvar(PASTA / "manifesto.json", manifesto)
salvar(PASTA / "perguntas.json", PERGUNTAS)
RESUMO = []
print("Pasta desta execução:", PASTA)
''')
md('''
## 7. Executar no LangChain e gravar as consultas
O agente usa `create_agent`, recebe `tool(funcao)` e devolve o estado com `messages`.
A célula salva um arquivo por pergunta, incluindo as consultas efetivamente observadas.
''')
codigo('''
# A função também será reutilizada na célula do CrewAI.
def executar_lote(nome, executar, gravar):
    global RESUMO
    # Reexecutar uma célula substitui somente os registros desse framework.
    RESUMO = [r for r in RESUMO if r["framework"] != nome]
    for pergunta in PERGUNTAS:
        destino = PASTA / f"{nome}_{pergunta['id']}.json"
        try:
            resultado, segundos = executar(pergunta["texto"], MODELO)
            registro = gravar(resultado, destino)
            registro.update(pergunta=pergunta, modelo=MODELO, segundos=segundos, status="concluido")
            salvar(destino, registro)
            linha = {"framework": nome, "pergunta": pergunta["id"], "status": "concluido",
                     "ferramentas": ", ".join(c["nome"] for c in registro["ferramentas"]),
                     "consultas_com_retorno": sum(c["retorno_observado"] for c in registro["ferramentas"]),
                     "segundos": segundos}
        except Exception as erro:
            registro = {"framework": nome, "pergunta": pergunta, "status": "erro", "tipo_erro": type(erro).__name__}
            salvar(destino, registro)
            linha = {"framework": nome, "pergunta": pergunta["id"], "status": "erro",
                     "tipo_erro": type(erro).__name__, "ferramentas": None, "consultas_com_retorno": None, "segundos": None}
        RESUMO.append(linha)
        salvar(PASTA / "resumo.json", RESUMO)
        print(nome, pergunta["id"], linha["status"], linha["ferramentas"])

executar_lote("langchain", executar_langchain, gravar_registro_langchain)
''')
md('''
## 8. Executar no CrewAI e gravar as consultas
O agente recebe `tool(nome)(funcao)`; a tarefa é executada com `Crew.kickoff()`.
O registro vem das mensagens de cada tarefa contidas no `CrewOutput`.
''')
codigo('''
executar_lote("crewai", executar_crewai, gravar_registro_crewai)
''')
md('''
## 9. Comparar os registros e conferir a consulta encadeada
Leia a resposta e os argumentos de Q07 nos dois frameworks. O cálculo só pode usar
`2026-11-13` depois da consulta ao chamado. O vencimento calculado é `2026-11-20`,
**sem considerar feriados**. Não adote essa data como prazo institucional real.
''')
codigo('''
try:
    from IPython.display import display, Markdown
except ImportError:  # Permite validar também num Python local sem IPython.
    display = print
    Markdown = str
# O Colab consegue mostrar uma lista de dicionários sem bibliotecas adicionais.
display(RESUMO)
VERIFICACOES = []
for framework in ["langchain", "crewai"]:
    caminho = PASTA / f"{framework}_Q07.json"
    if not caminho.exists():
        VERIFICACOES.append({"framework": framework, "status": "celula_nao_executada"})
        continue
    registro = json.loads(caminho.read_text(encoding="utf-8"))
    display(Markdown(f"### {framework} — Q07"))
    print(registro.get("resposta", "Execução com erro; consulte o JSON."))
    ferramentas = registro.get("ferramentas", [])
    display(ferramentas)
    consultas = [c for c in ferramentas if c["nome"] == "consultar_chamado" and c["retorno_observado"]]
    calculos = [c for c in ferramentas if c["nome"] == "calcular_prazo" and c["retorno_observado"]]
    datas = [c["argumentos"].get("data_inicial") for c in calculos]
    posicao_consulta = next((i for i, c in enumerate(ferramentas) if c in consultas), None)
    posicoes_calculo = [i for i, c in enumerate(ferramentas) if c in calculos]
    ordem = bool(posicoes_calculo) and posicao_consulta is not None and all(posicao_consulta < i for i in posicoes_calculo)
    verificacao = {"framework": framework, "datas_entregues_ao_calculo": datas,
                   "data_correta": bool(datas) and all(d == "2026-11-13" for d in datas),
                   "consulta_antes_do_calculo_no_registro": ordem}
    VERIFICACOES.append(verificacao)
    print("Conferência:", verificacao)
salvar(PASTA / "verificacoes_encadeamento.json", VERIFICACOES)
''')
md('''
## 10. Gerar o relatório e baixar as evidências
O ZIP reúne respostas, consultas, argumentos, retornos, código e versões. As falhas
ficam registradas como falhas. As verificações acima conferem a data dos argumentos
e a ordem dos registros; leia também as respostas para avaliar sua qualidade.
''')
codigo('''
import shutil
linhas = ["# Aula 06 — Desafio opcional", "", "Setor: TI da SEFAZ-MT. Dados e prazos fictícios.",
          f"Ambiente: {manifesto['ambiente']}. Modelo: {MODELO}.", "",
          "| Framework | Pergunta | Status | Ferramentas | Retornos observados | Tempo (s) |",
          "|---|---|---|---|---:|---:|"]
for r in RESUMO:
    linhas.append(f"| {r['framework']} | {r['pergunta']} | {r['status']} | {r['ferramentas']} | {r['consultas_com_retorno']} | {r['segundos']} |")
linhas += ["", "## Onde se encontra o registro", "",
           '- LangChain: `resultado["messages"]`, pedidos em `AIMessage.tool_calls`, retornos em `ToolMessage`.',
           '- CrewAI: `resultado.tasks_output[i].messages`, pedidos em `assistant.tool_calls`, retornos em `role=tool`.',
           '- Funções de gravação: `gravar_registro_langchain` e `gravar_registro_crewai`, em `desafio_frameworks.py`.',
           "", "## Consulta encadeada", "", json.dumps(VERIFICACOES, ensure_ascii=False, indent=2),
           "", "## Minha análise", "", "[Preencha após ler as respostas: houve consulta correta às fontes? O que variou entre os frameworks?]", ""]
(PASTA / "RELATORIO_DESAFIO.md").write_text("\\n".join(linhas), encoding="utf-8")
for nome in ["ferramentas.py", "desafio_frameworks.py"]:
    shutil.copy2(nome, PASTA / nome)
(PASTA / "versoes.txt").write_text("\\n".join(f"{p}=={v}" for p,v in manifesto["versoes"].items()), encoding="utf-8")
ARQUIVO_ZIP = shutil.make_archive(str(PASTA), "zip", root_dir=PASTA)
print("ZIP pronto:", ARQUIVO_ZIP)
from google.colab import files
files.download(ARQUIVO_ZIP)
''')
md('''
## 11. Conversar com Sofia, a assistente da SEFAZ-MT
Agora você pode fazer perguntas livres. A conversa usa **LangChain**, as mesmas
quatro ferramentas e as diretrizes do setor. Sofia guarda o contexto enquanto
esta sessão estiver aberta. Experimente:

1. `Qual a situação do chamado 2026009012?`
2. `E quando vencem cinco dias úteis a partir dessa movimentação?`

Na segunda pergunta, ela recebe o histórico e pode identificar o chamado anterior.
Use apenas dados fictícios ou anonimizados. A cada mensagem enviada pode haver
consumo de API. O histórico é reenviado ao modelo; use `/limpar` para começar de novo.

Comandos: `/fontes` mostra as consultas da última resposta; `/salvar` exporta a
conversa; `/limpar` apaga o contexto em memória; `/sair` encerra o diálogo.
O Colab descarta a memória ao encerrar a sessão, então exporte o que quiser guardar.
''')
codigo('%%writefile conversa.py\n' + (BASE/'conversa.py').read_text(encoding='utf-8'))
codigo('''
from conversa import Conversa, conversar
NOME_DO_AGENTE = "Sofia" #@param {type:"string"}
INICIAR_CONVERSA = False #@param {type:"boolean"}

if INICIAR_CONVERSA:
    if "sofia" not in globals() or sofia.nome != NOME_DO_AGENTE.strip() or sofia.modelo != MODELO:
        sofia = Conversa(modelo=MODELO, nome=NOME_DO_AGENTE)
    conversar(sofia, pasta=PASTA / "conversas")
else:
    print("Marque INICIAR_CONVERSA e execute esta célula para conversar.")
''')
md('''
## 12. Baixar a conversa salva
Digite `/salvar` durante a conversa e `/sair` para liberar a célula. Depois execute
esta célula para baixar o JSON com perguntas, respostas e ferramentas consultadas.
O arquivo da conversa é separado do ZIP do desafio baixado na etapa 10.
''')
codigo('''
if "sofia" in globals() and sofia.ultimo_arquivo is not None:
    from google.colab import files
    files.download(str(sofia.ultimo_arquivo))
else:
    print("Inicie uma conversa e use /salvar antes de baixar.")
''')
md('''
## Conferência antes de entregar
- [ ] Executei as funções isoladamente, sem chave.
- [ ] Executei as oito perguntas em ambos os frameworks na minha sessão Colab.
- [ ] Verifiquei ferramentas, argumentos e retornos nos JSON.
- [ ] Conferi a data entregue ao cálculo em Q07.
- [ ] Identifiquei os campos dos resultados e as duas funções que gravam o registro.
- [ ] Escrevi minha análise no relatório e baixei o ZIP.
- [ ] Salvei uma cópia deste notebook com as saídas da minha execução.

Este notebook cobre o **desafio opcional**. As Partes 1 a 4 completas do minilab
continuam em `aula06/`; o revisor Streamlit não é iniciado por este notebook.
''')
for indice, celula in enumerate(celulas):
    celula['id'] = f'aula06-{indice:02d}'
notebook = {'cells':celulas, 'metadata':{'colab':{'name':'desafio_aula06_colab.ipynb','provenance':[]},
    'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
    'language_info':{'name':'python','version':'3.12'}}, 'nbformat':4,'nbformat_minor':5}
destino = BASE/'desafio_aula06_colab.ipynb'
destino.write_text(json.dumps(notebook,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(destino)
