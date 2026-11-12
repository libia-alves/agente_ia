# ============================================================
# Aula 01 – Introdução a Agentes de IA
# Módulo: Agentes Autônomos | Curso: Formação em IA – UNEMAT/RISC
# Apoio: gera as tabelas de confiabilidade e de custo da Seção 5
# Seção 5 – A aritmética da autonomia
# Requisitos: nenhum (biblioteca padrão)
# ============================================================
"""Calcula as duas tabelas que sustentam a Seção 5, sem chamar modelo algum.

Esta aula é conceitual e não tem exemplos que consultem a API. As duas tabelas
abaixo, porém, precisam de números corretos, e reproduzi-las na calculadora é
parte do Mini LAB. O script existe para que o professor possa recalculá-las
com os parâmetros do próprio órgão, e para que o aluno confira as contas.
"""

# Parâmetros do agente hipotético, escolhidos por serem típicos de um
# assistente com quatro ferramentas declaradas.
PROMPT_SISTEMA = 600      # tokens da instrução de sistema
ESQUEMAS = 400            # tokens dos esquemas das quatro ferramentas
OBSERVACAO = 250          # tokens que cada resultado de ferramenta acrescenta

# Preço por milhão de tokens na faixa de contexto curto, confirmado na página
# oficial de preços da OpenAI em setembro de 2026.
PRECOS = {"gpt-5.6-luna": (0.20, 1.20), "gpt-5.6-terra": (2.00, 12.00)}
SAIDA_POR_PASSO = 120     # tokens de saída gerados a cada passo


def tabela_confiabilidade() -> None:
    """A probabilidade de o processo inteiro sair certo, em função dos passos."""
    print("=" * 68)
    print("Tabela 1 — Confiabilidade composta: a chance de tudo dar certo")
    print("=" * 68)
    taxas = (0.99, 0.95, 0.90, 0.80)
    print(f"\n{'passos':>8} " + "".join(f"{int(t*100):>10}%" for t in taxas))
    print("-" * 56)
    for n in (1, 3, 5, 10, 20):
        linha = f"{n:>8} "
        for taxa in taxas:
            linha += f"{taxa ** n * 100:>10.1f}%"
        print(linha)
    print("\nA célula que ancora a discussão: dez passos a 95% por passo")
    print(f"resultam em {0.95 ** 10 * 100:.0f}% de acerto no processo inteiro.")


def tabela_custo() -> None:
    """O custo acumulado do laço, que reenvia o histórico a cada passo."""
    print("\n" + "=" * 68)
    print("Tabela 2 — O custo do laço, que cresce com o quadrado dos passos")
    print("=" * 68)
    base = PROMPT_SISTEMA + ESQUEMAS
    print(f"\nprompt de sistema {PROMPT_SISTEMA} + esquemas {ESQUEMAS} = {base} tokens fixos")
    print(f"cada passo acrescenta {OBSERVACAO} tokens de observação\n")
    print(f"{'passos':>7} {'entrada do':>12} {'entrada':>12} {'US$':>12} {'US$':>12}")
    print(f"{'':>7} {'último passo':>12} {'acumulada':>12} {'luna':>12} {'terra':>12}")
    print("-" * 60)
    for n in (1, 5, 10, 20, 40):
        # A cada passo, o pedido carrega tudo o que veio antes.
        acumulada = sum(base + OBSERVACAO * i for i in range(n))
        ultimo = base + OBSERVACAO * (n - 1)
        saida = SAIDA_POR_PASSO * n
        custos = []
        for modelo in ("gpt-5.6-luna", "gpt-5.6-terra"):
            entrada_usd, saida_usd = PRECOS[modelo]
            custos.append(acumulada / 1e6 * entrada_usd + saida / 1e6 * saida_usd)
        print(f"{n:>7} {ultimo:>12} {acumulada:>12} "
              f"{custos[0]:>12.5f} {custos[1]:>12.5f}")

    um = sum(base + OBSERVACAO * i for i in range(1)) / 1e6 * 0.20 + SAIDA_POR_PASSO / 1e6 * 1.20
    quarenta = (sum(base + OBSERVACAO * i for i in range(40)) / 1e6 * 0.20
                + SAIDA_POR_PASSO * 40 / 1e6 * 1.20)
    print(f"\nQuarenta passos custam {quarenta / um:.0f} vezes um passo, e não quarenta.")
    print("Dobrar o número de passos aproximadamente quadruplica a conta, porque")
    print("cada passo novo paga também tudo o que veio antes dele.")


if __name__ == "__main__":
    tabela_confiabilidade()
    tabela_custo()
