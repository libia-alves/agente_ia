# Aula 02 — Mini LAB LangChain

Comece pelo [roteiro da SEFAZ-MT](docs/SEFAZ_MINILAB.md).
A preparação já foi executada; a próxima etapa é conferir o gabarito dos dez
extratos antes da medição principal.

## Onde está cada coisa

```text
aula02/
├── README.md                  ← comece aqui
├── minilab.py                 ← programa principal
├── .env                       ← suas chaves (arquivo privado)
├── .env.example               ← modelo de configuração
├── requirements.txt           ← dependências
├── requirements-lock.txt      ← versões registradas
├── configuracao/
│   ├── modelo_destino.py      ← modelo, provedor e tarifas
│   └── esquema_sefaz.py       ← campos e instruções da extração
├── docs/
│   ├── SEFAZ_MINILAB.md       ← roteiro escolhido
│   ├── REVISAO_SEFAZ.md       ← leitura dos documentos e gabarito preliminar
│   └── MINILAB.md             ← detalhes gerais da medição
├── dados/
│   ├── documentos_2026.jsonl  ← sua cópia de trabalho e gabarito
│   ├── documentos_sefaz_2026.rascunho.jsonl
│   └── fontes/                ← PDFs oficiais e textos extraídos
├── exemplos/                  ← exemplos 01 a 07 e material fictício da aula
├── resultados/                ← logs e resultados das suas execuções
├── tests/                     ← testes locais do programa
└── .venv/                     ← ambiente Python
```

Os dados fictícios e o resultado fornecido pela aula ficam em `exemplos/`.
O conjunto público da SEFAZ fica em `dados/`. A revisão para leitura está em
[docs/REVISAO_SEFAZ.md](docs/REVISAO_SEFAZ.md); as alterações no gabarito devem
ser feitas em `dados/documentos_2026.jsonl`.

## Como executar

No terminal, dentro de `aula02`:

```bash
source .venv/bin/activate
python minilab.py validar --perfil sefaz
```

Após conferir os documentos e escrever/revisar pessoalmente o gabarito, marque
`gabarito_revisado: true` em cada documento conferido e execute:

```bash
python minilab.py congelar --perfil sefaz
python minilab.py executar --perfil sefaz --volume-mensal 1000
```

As chamadas de medição usam a API e podem gerar cobrança. O volume de 1000
por mês é uma hipótese acadêmica, não uma demanda verificada da SEFAZ.

Para executar os exemplos de preparação:

```bash
python exemplos/exemplo01.py
python exemplos/exemplo05.py
python minilab.py temperatura
```

Esses exemplos já foram executados; seus registros estão em `resultados/`.
O comando `temperatura` faz somente inspeção local. O exemplo07 é ilustrativo
para Anthropic e requer chave e dependência próprias; não integra o minilab.

Para verificar o código sem chamadas à API:

```bash
python -m unittest discover -s tests -v
```
