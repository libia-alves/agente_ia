# Mini LAB de automação por agentes

Calculadora didática em Python, sem dependências externas. Mapeia três processos, aplica as tabelas originais da aula, calcula custos mensais e gera relatório, parecer para revisão pela dupla e planilhas CSV.

O script fornecido foi preservado, sem alterações, em `calcular_tabelas_original.py`. O arquivo adicionado em `.venv/calcular_tabelas.py` também foi mantido. A implementação principal importa a cópia fora do ambiente virtual: a pasta `.venv` pode ser recriada sem perder o material da aula.

Os processos, volumes, prazos e parâmetros personalizados são **exemplos hipotéticos**. Os preços e nomes de modelos da referência são reproduzidos do script didático fornecido, sem validação como cotações comerciais atuais. As seções sobre quadrantes e modos de falha ainda precisam ser conferidas com o material da aula. Há uma diferença de numeração: o cabeçalho do script chama a aritmética de Seção 5; o enunciado, de Seção 6.

## Executar

Todos os arquivos do Mini LAB estão em `aula01`. A partir da raiz do projeto, entre nessa pasta:

```bash
cd aula01
python3 calcular_tabelas.py
python3 calcular_tabelas.py --saida resultados
```

A segunda opção grava ou atualiza:

- `resultados/relatorio.txt`: tabelas originais, aplicação aos processos, desafio opcional, mapeamento e parecer.
- `resultados/parecer.txt`: parecer curto, com custo derivado da Tabela 2 original; aproximadamente uma página, conforme a formatação de impressão.
- `resultados/tabelas.csv`: resumo com custos da aula e personalizados, identificados em colunas distintas.
- `resultados/tabelas_originais.txt`: saída exata das duas tabelas do script fornecido.
- `resultados/desafio_opcional.csv`: Tabela 2 personalizada de cada processo, para 1, 5, 10, 20, 40 e o número real de etapas.

Para executar apenas o material original:

```bash
python3 calcular_tabelas_original.py
```

O programa somente calcula e gera arquivos; não consulta sistemas nem executa ações administrativas.

## Adaptar ao seu setor

Edite `processos.json`, mantendo exatamente três processos:

- Preencha PEAS, etapas, ferramentas e volume mensal. O número de etapas corresponde à quantidade de itens em `etapas`.
- Registre reversibilidade, rapidez e prazo de detecção, autonomia, conferência humana, duas falhas justificadas e informação ausente.
- Ajuste `piloto_id`, `recusado_id`, `critico_id` e justificativas. A recomendação é uma decisão explícita do responsável, não uma seleção automática por preço.
- Em `modelo_aula`, selecione um dos nomes definidos no script original. O custo principal e o parecer usam os parâmetros originais e o preço didático desse modelo, em USD.
- Os campos `tokens` de cada processo e `precos` são usados somente no desafio opcional. Preços de entrada e saída são por milhão de tokens e devem usar a mesma moeda de `moeda`. Não há conversão cambial automática; registre a origem e a data de preços atualizados em `fonte`.
- Altere `dados_hipoteticos` para `false` somente após substituir os exemplos por medições do órgão. Complete órgão e nomes da dupla no parecer exportado.

Para preservar o exemplo:

```bash
cp processos.json meus_processos.json
python3 calcular_tabelas.py --config meus_processos.json --saida minha_entrega
```

Alterações manuais nos arquivos exportados serão substituídas na próxima geração.

## Fórmulas originais

A Tabela 1 mostra taxas de 99%, 95%, 90% e 80% nos passos 1, 3, 5, 10 e 20. A aplicação aos processos usa `p ** n`, com `p = 0.95` por padrão e independência entre etapas. A contagem é didática; mudar a granularidade das etapas muda a interpretação do modelo.

Na Tabela 2 original:

```text
Sistema = 600 tokens
Esquemas das quatro ferramentas = 400 tokens no total
Observação adicionada por passo = 250 tokens
Saída por passo = 120 tokens
Entrada acumulada = n × 1000 + n × (n − 1) / 2 × 250
Saída acumulada = n × 120
Custo = (entrada × preço_entrada + saída × preço_saída) / 1.000.000
Custo mensal = custo por execução × volume mensal
```

O modelo simplificado da aula cobra a saída, mas não a soma novamente ao histórico de entrada. Não inclui cache, truncamento, tarifas de ferramentas, revisão humana, infraestrutura, impostos ou retrabalho. A aplicação usa a fórmula para o número exato de etapas, sem arredondar para a linha mais próxima da tabela.

Com os valores do modelo `gpt-5.6-luna` no material, uma execução com 1 passo custa USD 0,000344; com 40 passos, USD 0,052760. A razão exata é aproximadamente **153,37**, arredondada para **153 vezes** na aula. A comparação é entre 40 passos e 1 passo **do mesmo agente**, incluindo esquemas de ferramentas em ambos.

## Desafio opcional

Defina S = sistema, F = quantidade de ferramentas × tokens por definição, Q = consulta inicial, R = observação típica de ferramenta e O = saída por passo:

```text
Entrada acumulada = n × (S + F + Q) + n × (n − 1) / 2 × R
Entrada do último passo = S + F + Q + (n − 1) × R
Saída acumulada = n × O
Fator n/1 = custo com n passos / custo com 1 passo
```

A consulta inicial é incluída na base reenviada a cada chamada. A referência original equivale a Q=0 porque o script não separa esse parâmetro. Não há um acréscimo separado de saída ao histórico: permanece a simplificação original.

O relatório mostra tanto o fator do número real de etapas quanto o fator **40/1** de cada cenário personalizado. Compare **40/1** com 153,37 para responder se o fator da aula se mantém. Os fatores personalizados não são forçados a 153. Se o custo de um passo for zero, a razão é indefinida.

As ferramentas do mapeamento são capacidades; `numero_ferramentas` conta definições efetivamente enviadas ao modelo. Use medições de tokens para substituir os tamanhos de exemplo. Fluxos com múltiplas chamadas por etapa exigem rever essa aproximação.

A grade usa reversibilidade e detecção rápida/tardia com prazos explícitos, sem um limite universal presumido. No caso financeiro, o quadrante de difícil reversão descreve o risco de ampliar a automação até a liberação; o relatório de conferência isolado é reversível. O agente proposto fica restrito ao apoio documental. A barreira descrita é um requisito para futura integração, não uma permissão aplicada por esta calculadora.

## Verificação

Execute dentro de `aula01`:

```bash
python3 -m unittest discover -s tests -v
```

Os testes conferem os números da aula, a reprodução das tabelas originais, a fórmula personalizada, volumes, validação e exportação.
