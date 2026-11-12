# Mini LAB com documentos públicos da SEFAZ-MT

Este é um estudo acadêmico externo. Você não trabalha na SEFAZ e não tem acesso
à demanda interna do órgão. O recorte escolhido é a gestão de contratos, aditivos
e termos de cooperação da Secretaria de Estado de Fazenda de Mato Grosso.

## O que já foi preparado

Foram selecionados dez extratos distintos publicados em 2026 no Diário Oficial
oficial de Mato Grosso (IOMAT). As fontes estão salvas em `dados/fontes/`.
O conjunto e o gabarito preliminar estão em
`dados/documentos_sefaz_2026.rascunho.jsonl`; a versão para leitura está em
`docs/REVISAO_SEFAZ.md`.

| Publicação | Página | Protocolos selecionados | Fonte |
| --- | --- | --- | --- |
| 25/03/2026 | 6 e 7 | 1796906, 1796913, 1796937 | https://iomat.mt.gov.br/portal/edicoes/download/19004 |
| 06/04/2026 | 15 | 1800180, 1800222 | https://iomat.mt.gov.br/portal/edicoes/download/19024 |
| 30/04/2026 | 37 | 1807541 | https://iomat.mt.gov.br/portal/edicoes/download/19063 |
| 13/05/2026 | 7 | 1811626, 1811667, 1811670, 1811693 | https://iomat.mt.gov.br/portal/edicoes/download/19084 |

Há sete extratos sem valor informado e três com valor numérico acompanhado do
valor por extenso. Exemplo sem valor: protocolo 1807541 (prorrogação de execução).
Exemplo por extenso: protocolo 1811626 (aditivo da reforma da Escola Fazendária).
O valor por extenso também tem representação numérica nesses originais; portanto
este conjunto não testa uma situação em que só exista texto por extenso.
A concentração em cooperações sem valor limita a representatividade da amostra.
A edição de março contém publicação repetida do contrato 019: somente uma cópia
foi selecionada, protocolo 1796937; a repetição 1796945 foi excluída.

O texto foi extraído dos PDFs por coluna, com normalização de espaços, sem
reescrever o conteúdo dos atos. O cabeçalho `Contexto da fonte` foi acrescentado
e identifica a data da publicação, página e protocolo; não integra o ato original.
Cada linha registra a URL e o hash do PDF. A coleção e a pré-anotação foram
preparadas com assistência de IA; isso não equivale ao gabarito manual exigido.

## Sua próxima etapa: conferir o gabarito antes da IA extrair

Abra `docs/REVISAO_SEFAZ.md` e os PDFs correspondentes. Confira cada resposta
prevista. Corrija o que for necessário antes de executar os modelos. Para atender
literalmente ao enunciado, escreva você mesmo os seis campos após ler os documentos;
não declare o rascunho assistido como gabarito manual de sua autoria.

Os seis campos estão definidos em `configuracao/esquema_sefaz.py`:

- `numero`: código do contrato/termo no título; em aditivos, código do contrato alvo;
- `data`: data da **publicação**, em AAAA-MM-DD, não a data de assinatura;
- `valor`: total/global explicitamente informado, ou null se ausente no extrato;
- `partes`: SEFAZ primeiro, depois contratado/cooperado, sem CNPJ;
- `objeto`: transcrição integral do campo OBJETO, sem rótulo nem ponto final;
- `processo`: identificador SEFAZ-PRO, preservando sufixos como `.01`.

A cópia de trabalho já está em `dados/documentos_2026.jsonl`. Nela, escreva/confira
seu gabarito e marque `gabarito_revisado: true` em cada linha que tiver conferido.
O programa exige essa marca antes de congelar ou executar o perfil SEFAZ.
A marca é autodeclaração; não prova autoria humana. Não altere o gabarito depois
de começar a medir para aproximá-lo das respostas dos modelos.

No terminal, na pasta `aula02` com `.venv` ativada:

```bash
python minilab.py validar --perfil sefaz --dados dados/documentos_2026.jsonl
python minilab.py congelar --perfil sefaz --dados dados/documentos_2026.jsonl
```

## Medição, após preencher OPENAI_API_KEY no .env local

```bash
mkdir -p resultados
python exemplos/exemplo01.py | tee resultados/preparacao_destinos.txt
python exemplos/exemplo05.py | tee resultados/preparacao_falhas.txt
python minilab.py executar --perfil sefaz --dados dados/documentos_2026.jsonl --volume-mensal 1000
```

**1000 documentos/mês é uma hipótese didática, não um dado da SEFAZ.**
Identifique assim a projeção. O requisito de volume real permanece sem atendimento
até haver uma fonte institucional que o comprove. Não afirme que os dez extratos
representam toda a atividade da Secretaria. O modelo principal é o mesmo da aula,
`gpt-5.6-luna`, se sua conta tiver acesso. A API é cobrada separadamente de um
plano de chat; sem chave configurada não há medição real.

Para repetir o caminho vencedor, altere a linha DESTINO de `configuracao/modelo_destino.py` e
use, por exemplo, se a implementação escolhida for `sdk`:

```bash
python minilab.py executar --perfil sefaz --dados dados/documentos_2026.jsonl --volume-mensal 1000 --somente sdk --comparar resultados/PASTA_PRINCIPAL/resultado.json
```

Não escolha a implementação nem preencha as colunas de consumo antes de executar.
O arquivo `docs/MINILAB.md` explica os artefatos, custo por milhão, aquecimentos,
comparação de campos e contagem das linhas da troca.

## Base para a análise, ainda sem conclusão experimental

Use no texto: “Estudo acadêmico com dez extratos públicos da SEFAZ-MT; não sou
servidor do órgão. O volume mensal de 1000 documentos foi adotado como cenário
hipotético de projeção e não corresponde a uma demanda institucional verificada.”

Depois, complete cinco a dez linhas com os seus acertos, tokens, latências e custos,
justificando uma escolha com esses números. Compare o custo mensal do estruturado
com os outros caminhos, inclusive se o acréscimo foi nulo ou negativo.
Ainda não há base para afirmar uma implementação vencedora.

Para o item 12, um risco pertinente ao recorte de contratos é o modo 3: JSON
válido com estrutura inesperada. Em uma eventual rotina de conferência contratual,
a ausência de `valor` ou sua associação ao identificador errado pode comprometer
a conferência de despesas. O protocolo 1807541 ilustra que um aditivo pode não
informar valor; recuperar ou inventar um valor nessa situação seria incorreto.
Esse é um cenário de risco proposto para o estudo, não uma falha observada nos
sistemas internos da SEFAZ. Validação de esquema e revisão humana de campos
financeiros são controles diferentes: formato válido não garante dado correto.

O enunciado exige vínculo com o setor do aluno e gabarito manual. Como aqui foi
adotado um órgão externo, apresente a adaptação acadêmica com transparência e
confirme com o professor se ela atende ao critério da atividade.
