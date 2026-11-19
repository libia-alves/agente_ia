"""Aula 08 - Introdução ao LangFlow
Seção: 6 (Fluxos como arquivos e a API REST)
Objetivo: listar, importar, executar e apagar fluxos do LangFlow pela API,
          sem abrir a interface visual.
Requisitos: pip install httpx python-dotenv; LangFlow em execução na porta 7860.
Chave: a API local exige uma chave gerada em Settings > Langflow API Keys,
       lida da variável LANGFLOW_API_KEY no .env da aula (ou dispensa
       a chave se o servidor foi iniciado com LANGFLOW_SKIP_AUTH_AUTO_LOGIN=true).
Uso:
  python cliente_api.py listar
  python cliente_api.py importar fluxo01-atendimento-professor.json
  python cliente_api.py rodar "Atendimento ao professor" "Como solicito licença-prêmio?"
  python cliente_api.py comparar resultados/playground.json
  python cliente_api.py apagar "Atendimento ao professor"
"""
import json
import os
import pathlib
import sys
from time import perf_counter
from uuid import uuid4

import httpx
from dotenv import load_dotenv

BASE = pathlib.Path(__file__).resolve().parent
load_dotenv(BASE / ".env")

URL = os.environ.get("LANGFLOW_URL", "http://127.0.0.1:7860").rstrip("/") + "/api/v1"
CABECALHOS = {"x-api-key": os.environ["LANGFLOW_API_KEY"]} if os.environ.get("LANGFLOW_API_KEY") else {}
cliente = httpx.Client(base_url=URL, headers=CABECALHOS, timeout=240)


def listar() -> list[dict]:
    """Devolve os fluxos criados pelo usuário (sem os modelos de exemplo)."""
    r = cliente.get("/flows/", params={"remove_example_flows": "true", "header_flows": "true"})
    r.raise_for_status()
    return r.json()


def localizar(nome: str) -> dict:
    for fluxo in listar():
        if fluxo["name"] == nome:
            return fluxo
    raise SystemExit(f"fluxo não encontrado: {nome!r}")


def importar(caminho: str) -> dict:
    """Cria um fluxo a partir de um arquivo JSON exportado pela interface ou por este script."""
    dados = json.loads(pathlib.Path(caminho).read_text(encoding="utf-8"))
    corpo = {"name": dados["name"], "description": dados.get("description", ""), "data": dados["data"]}
    r = cliente.post("/flows/", json=corpo)
    r.raise_for_status()
    return r.json()


def rodar(nome: str, mensagem: str) -> str:
    """Executa o fluxo com uma mensagem de chat e devolve o texto da resposta."""
    fluxo = localizar(nome)
    corpo = {
        "input_value": mensagem,
        "input_type": "chat",
        "output_type": "chat",
        "session_id": str(uuid4()),
    }
    r = cliente.post(f"/run/{fluxo['id']}", params={"stream": "false"}, json=corpo)
    r.raise_for_status()
    return r.json()["outputs"][0]["outputs"][0]["results"]["message"]["text"]


def categoria(resposta: str | None) -> str | None:
    if resposta and resposta.strip():
        return resposta.strip().splitlines()[0].strip()
    return None


def comparar(caminho: str) -> list[dict]:
    """Executa as cinco mensagens e compara a primeira linha com o Playground."""
    casos = json.loads((BASE / "casos.json").read_text(encoding="utf-8"))["classificador"]
    playground = json.loads(pathlib.Path(caminho).read_text(encoding="utf-8"))
    respostas_playground = {item["id"]: item.get("resposta") for item in playground}
    resultados = []
    for caso in casos:
        inicio = perf_counter()
        resposta = rodar("Classificação de chamados — TI SEFAZ-MT", caso["mensagem"])
        tempo = round(perf_counter() - inicio, 3)
        api = categoria(resposta)
        visual = categoria(respostas_playground.get(caso["id"]))
        resultados.append({
            "id": caso["id"],
            "mensagem": caso["mensagem"],
            "gabarito": caso["esperado"],
            "playground": visual,
            "api": api,
            "coincidem": api == visual if visual is not None else None,
            "api_correta": api == caso["esperado"],
            "tempo_api_s": tempo,
            "resposta_api": resposta,
        })
    return resultados


def apagar(nome: str) -> None:
    fluxo = localizar(nome)
    cliente.delete(f"/flows/{fluxo['id']}").raise_for_status()


if __name__ == "__main__":
    comando, args = (sys.argv[1] if len(sys.argv) > 1 else "listar"), sys.argv[2:]
    if comando == "listar":
        for f in listar():
            print(f"{f['id']}  {f['name']}")
    elif comando == "importar":
        novo = importar(args[0])
        print(f"importado: {novo['name']} ({novo['id']})")
    elif comando == "rodar":
        print(rodar(args[0], args[1]))
    elif comando == "comparar" and len(args) == 1:
        print(json.dumps(comparar(args[0]), ensure_ascii=False, indent=2))
    elif comando == "apagar":
        apagar(args[0])
        print(f"apagado: {args[0]}")
    else:
        raise SystemExit(__doc__)
