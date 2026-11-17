# ============================================================
# Aula 06 – Introdução ao Agno
# Módulo: Agentes Autônomos | Curso: Formação em IA – UNEMAT/RISC
# Exemplo 05: O tempo de espera e o custo da revisão de minutas
# Seção 6 – O agente atrás de um formulário
# Requisitos: pip install agno openai python-dotenv pydantic
# ============================================================
"""Mede o agente revisor pelo tempo de quem está olhando a tela.

O exemplo olha para o servidor que aperta o botão e espera. A primeira parte
revisa as três minutas de `minutas.json` e imprime o tempo, as chamadas ao
modelo e o custo de cada uma; a segunda acompanha uma revisão evento por
evento e mede em quanto tempo a tela consegue mostrar o primeiro sinal de que
algo está acontecendo.
"""
import json
import pathlib
import time

from revisor import PRECO_ENTRADA, PRECO_SAIDA, construir_agente, revisar

BASE = pathlib.Path(__file__).parent


def medir_as_tres_minutas(agente) -> None:
    minutas = json.loads((BASE / "minutas.json").read_text(encoding="utf-8"))["minutas"]
    print("=" * 78)
    print("PARTE 1 — revisão das três minutas")
    print("=" * 78)
    print(f"{'Minuta':<8}{'Segundos':>9}{'Chamadas':>10}{'Ferram.':>9}{'Alter.':>8}"
          f"{'Avisos':>8}{'Entrada':>9}{'Saída':>8}{'US$':>9}")

    totais = [0.0, 0, 0, 0.0]
    for m in minutas:
        revisao, med = revisar(m["texto"], m["tipo"], agente=agente)
        print(f"{m['id']:<8}{med['segundos']:>9.1f}{med['chamadas']:>10}"
              f"{len(med['ferramentas']):>9}{len(revisao.alteracoes):>8}"
              f"{len(revisao.avisos):>8}{med['tokens_entrada']:>9}"
              f"{med['tokens_saida']:>8}{med['custo']:>9.5f}")
        totais[0] += med["segundos"]
        totais[1] += med["tokens_entrada"]
        totais[2] += med["tokens_saida"]
        totais[3] += med["custo"]

    print("-" * 78)
    print(f"{'total':<8}{totais[0]:>9.1f}{'':>10}{'':>9}{'':>8}{'':>8}"
          f"{totais[1]:>9}{totais[2]:>8}{totais[3]:>9.5f}")
    print(f"\nCusto por minuta revisada: US$ {totais[3] / len(minutas):.5f}")


def medir_o_tempo_de_espera(agente) -> None:
    minutas = json.loads((BASE / "minutas.json").read_text(encoding="utf-8"))["minutas"]
    m = minutas[0]
    pedido = f"Tipo de documento: {m['tipo']}\n\nMinuta a revisar:\n{m['texto']}"

    print("\n" + "=" * 78)
    print("PARTE 2 — a mesma revisão, acompanhada evento por evento")
    print("=" * 78)

    inicio = time.perf_counter()
    primeiro_sinal = None
    for evento in agente.run(pedido, stream=True, stream_events=True):
        decorrido = time.perf_counter() - inicio
        if type(evento).__name__ == "ToolCallStartedEvent":
            nome = evento.tool.tool_name
            if primeiro_sinal is None:
                primeiro_sinal = decorrido
            print(f"  {decorrido:5.1f}s  a tela pode exibir: consultando {nome}")
    total = time.perf_counter() - inicio

    print(f"\n  primeiro sinal possível na tela: {primeiro_sinal:.1f}s")
    print(f"  resposta completa na tela       : {total:.1f}s")
    print(f"  tempo sem informação alguma     : {total - primeiro_sinal:.1f}s a menos de espera cega")
    print("\nCom `output_schema` o texto não pode ser exibido aos poucos, porque até o")
    print("último token o JSON está incompleto e não valida. O que se transmite ao")
    print("usuário não é a resposta em formação, e sim a ação em curso.")


def main() -> None:
    # Um único agente para as três minutas, como a aplicação faz com
    # `@st.cache_resource`: a instanciação é paga uma vez.
    agente = construir_agente()
    medir_as_tres_minutas(agente)
    medir_o_tempo_de_espera(agente)


if __name__ == "__main__":
    main()
