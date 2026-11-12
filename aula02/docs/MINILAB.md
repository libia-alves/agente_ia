# Mini LAB — roteiro de execução e entrega

Para o estudo acadêmico escolhido com documentos reais da SEFAZ-MT, comece por
[SEFAZ_MINILAB.md](SEFAZ_MINILAB.md). Use `--perfil sefaz` nesse conjunto.
O perfil padrão deste roteiro mantém o esquema dos exemplos da aula.

O laboratório está em `aula02`; não escreva código dentro de `.venv`.
O `minilab.py` adapta o exemplo04, mantendo os seis campos e substituindo a medição.
Os arquivos `exemplos/documentos_2026.jsonl` (20 documentos fictícios) e
`exemplos/resultado_experimento.json` são materiais da aula: não são a sua entrega.
Não execute `exemplos/gerar_documentos.py` para produzir o conjunto real.

## 1. Ambiente e preparação

No terminal, a partir da pasta do projeto:

```bash
cd aula02
source .venv/bin/activate
pip install -r requirements.txt
```

As dependências já foram instaladas neste ambiente. O `.env` local já foi criado
com campos vazios; abra-o no editor e preencha `OPENAI_API_KEY`.
Não coloque a chave no código nem no chat. Groq e HF são opcionais.

```bash
mkdir -p resultados
python exemplos/exemplo01.py | tee resultados/preparacao_destinos.txt
python exemplos/exemplo05.py | tee resultados/preparacao_falhas.txt
python minilab.py temperatura | tee resultados/temperatura.txt
```

O exemplo01 faz **um aquecimento e uma chamada medida por destino disponível**.
Ambas podem ser cobradas; o tempo impresso exclui o aquecimento.
O exemplo05 inteiro também faz chamadas cobradas. No bloco 2, registre o que
`_default_params` contém nesta versão; o código não deve concluir descarte se ele
não ocorreu. A inspeção `temperatura` usa `temperature=0.2` e não faz rede:
ela comprova apenas a configuração preparada pelo adaptador, não a aceitação
pelo servidor. Salva modelo, versão e valor efetivo em `resultados/temperatura.json`.

## 2. Dez documentos reais e gabarito manual

Crie `dados/documentos_2026.jsonl`, com exatamente dez linhas. Cada linha é um
objeto JSON completo; quebras no texto devem ser representadas por `\n`.
Escreva o gabarito lendo o documento, **antes de qualquer extração por IA**.
A fonte pode ser uma URL pública ou referência ao documento anonimizado.

A estrutura de uma linha é esta (substitua os marcadores; isto não é documento real):

```json
{"id":"DOC-01","fonte":"URL pública ou referência anonimizada","casos_dificeis":[],"texto":"COLE O DOCUMENTO AQUI","gabarito":{"numero":"IDENTIFICADOR","data":"2026-01-01","valor":null,"partes":["REMETENTE","DESTINATÁRIO"],"objeto":"ASSUNTO","prioridade":"media"}}
```

Os campos escolhidos são número, data, valor, partes, objeto e prioridade.
`valor` deve ser número sem separador de milhar (`125000.50`) ou `null`.
`partes` preserva a ordem remetente/destinatário. `data` usa AAAA-MM-DD.
Para `objeto`, copie o Assunto, sem prefixo e sem ponto final. Sem Assunto, defina
uma frase de referência e revise eventuais paráfrases na análise.
Prioridade: alta/media/baixa; se não explícita, `media` por convenção prévia.
Essa convenção é de avaliação e não deve autorizar tramitação automática.

Inclua dois documentos distintos: um sem valor (`valor: null`) e um com valor
escrito por extenso, marcado com `"casos_dificeis":["valor_por_extenso"]`.
A marcação é manual: o programa não prova a origem real nem verifica semanticamente
se o valor está por extenso. Você precisa conferir esses requisitos.
Se outro campo puder estar ausente, adapte `Documento`, `ESQUEMA_JSON` e `INSTRUCAO`
no `exemplos/exemplo04.py` e as regras de comparação do minilab antes de congelar o conjunto.

```bash
python minilab.py validar
python minilab.py congelar
```

O manifesto registra data e SHA-256; a execução recusa dados alterados.
Isso documenta que o arquivo ficou fixado antes da execução deste programa,
mas não prova autoria humana nem ausência de execuções externas anteriores.
Não ajuste o gabarito para melhorar a nota depois de ver as respostas.

Para conhecer apenas o validador usando o material fictício da aula:

```bash
python minilab.py validar --dados exemplos/documentos_2026.jsonl --treino
```

## 3. Medição e custo mensal

Confira a linha `DESTINO` em `configuracao/modelo_destino.py`. As três implementações usam
esse mesmo modelo e prompt. O padrão preserva `gpt-5.6-luna` da aula.
`MINILAB_MODELO` do `.env` controla apenas os exemplos01/04/05 e o teste de temperatura;
se mudar o modelo principal, mantenha esses valores coerentes.

```bash
python minilab.py executar --volume-mensal 1000
```

**Substitua 1000 pelo volume real do seu setor**; é um exemplo de comando.
Sem volume informado, a projeção mensal fica indisponível.
São 30 chamadas medidas e 3 aquecimentos, com retries desativados.
Cada implementação aquece seu próprio caminho antes da medição.
A ordem é SDK, parser, estruturado, sem paralelismo. Dez documentos e uma única
passagem dão evidência local limitada; não atribua pequenas diferenças de tempo
exclusivamente ao framework. Rede, cache e variação do servidor também interferem.

Cada execução cria uma pasta nova em `resultados/` contendo:

- `resultado.json`: modelo, versões, tarifas, hashes, manifesto, aquecimentos e totais;
- `extracoes.jsonl`: saída, acertos por campo, erros, tokens e tempo de cada documento;
- `tabela.md`: tabela preenchida automaticamente com suas medições e projeção mensal.

Entrada e saída são tokens totais dos dez documentos. Latência é a mediana
por documento, incluindo tentativas que falharam. O parser usa uma chamada por
documento e preserva seu `usage` antes de analisar o JSON. Não há reexecução para
contar tokens. Falhas sem consumo informado tornam o custo indisponível, em vez
de aparentar gratuidade. Aquecimentos ficam registrados fora da tabela.

Campos são comparados por igualdade, ignorando caixa e espaços externos.
Valor aceita diferença menor que meio centavo. Chave ausente não equivale a null.
Partes têm ordem. O objeto tem comparação literal, portanto uma paráfrase correta
pode perder ponto: use o log para relatar essa limitação, sem mudar a regra após medir.
Saída estruturada garante formato, não veracidade dos valores.

O cálculo usa tokens medidos, separando entrada em cache:

```text
US$ = ((entrada - cache) × tarifa_entrada + cache × tarifa_cache
       + saída × tarifa_saída) / 1.000.000
US$/mês = (US$ do conjunto / quantidade de documentos) × volume mensal
```

Tarifas padrão por milhão: entrada US$0,20, cache US$0,02 e saída US$1,20,
para contexto curto, consultadas em 10/11/2026 na
[documentação oficial GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna).
A alternativa GPT-4.1 mini usa US$0,40 / US$0,10 / US$1,60, conforme
[documentação oficial](https://developers.openai.com/api/docs/models/gpt-4.1-mini).
Confira tarifas e acesso na sua conta. O cálculo é de uso da API, sem impostos,
infraestrutura ou trabalho humano; extrapola o perfil de tamanho/cache da amostra.

## 4. Troca efetiva, depois de escolher a vencedora

Guarde o caminho de `resultado.json` da execução principal. Altere somente a linha
`DESTINO` de `configuracao/modelo_destino.py`. A docstring traz uma alternativa OpenAI permitida
pelo enunciado. Para outro provedor, essa linha contém modelo, provedor, variável
da chave, base URL e tarifas; confira o suporte a JSON Schema do modelo escolhido.
Para HF compatível com OpenAI, use provedor `openai`, chave `HF_TOKEN` e
`https://router.huggingface.co/v1` como base URL.

Execute apenas o caminho vencedor, por exemplo, **se o vencedor foi parser**:

```bash
python minilab.py executar --somente parser --comparar resultados/PASTA_PRINCIPAL/resultado.json --volume-mensal 1000
```

O programa exige o mesmo conjunto, registra o diff de `configuracao/modelo_destino.py` e conta
linhas alteradas comparando com a configuração efetivamente executada antes.
Se só substituir a linha DESTINO, a contagem será 1. O diff conta esse arquivo;
registre manualmente qualquer mudança adicional de código/configuração necessária.
Não declare a troca concluída se a chamada ao destino novo falhar.
O fallback para outro modelo OpenAI é troca de modelo, explicitamente permitida;
identifique-o assim no relatório, sem dizer que mudou de provedor.

## 5. Texto da entrega (preencher depois das chamadas)

Órgão/setor: ____. Processo administrativo concreto: ____.
Volume real: ____ documentos/mês. Fonte do volume: ____.
Conjunto: dez documentos públicos/anonimizados. Gabarito registrado em: ____.
Modelo comum e versões: ____. Aquecimento: ____.
Cole a tabela gerada em `tabela.md` e anexe os logs da preparação.

Escreva entre cinco e dez linhas usando os valores medidos:

1. A implementação escolhida foi ____, que acertou ____/60 campos.
2. As demais acertaram ____/60 e ____/60; a diferença observada foi ____.
3. A coluna que mais pesa no setor é ____, porque no processo ____ ela afeta ____.
4. A latência mediana foi ____ s e o custo do conjunto foi US$ ____.
5. Para ____ documentos/mês, os custos projetados são US$ ____, ____ e ____.
6. O estruturado acrescentou ____ tokens de entrada frente a ____ e US$ ____/mês.
7. Esse acréscimo [altera/não altera] a escolha porque ____.
8. Os limites da comparação são o conjunto pequeno, a medição única e ____.

Para o item 12, escolha entre os quatro modos do exemplo05:
importações incompatíveis; parâmetros descartados/reescritos; JSON com estrutura
inesperada; payload ocultado pela abstração. Ligue o escolhido ao seu processo real.
Exemplo de raciocínio para adaptar, **sem presumir que seja seu setor**: num processo
de pagamento, um JSON que passa no parser mas perde o campo de valor pode provocar
encaminhamento com dados incompletos; valide campos obrigatórios e encaminhe
inconsistências para revisão humana. Não afirme que o parser verifica veracidade.

No desafio opcional, relate o JSON de `temperatura` e a saída real do bloco 2.
Para produção, compare parâmetros solicitados com os efetivos antes de chamar,
recuse divergências, mantenha versões fixadas e testes de contrato do payload
contra modelos/provedores suportados. `_default_params` é privado e pode mudar;
a aceitação final requer uma chamada real e inspeção segura da requisição.

## Estado atual

Dependências instaladas e verificações locais disponíveis. Não há medição real
nem tabela final: faltam a chave, os dez documentos reais com gabarito manual,
o órgão/processo e o volume mensal. Os resultados antigos da aula foram preservados.
