# Aula 03 — Mini LAB de ferramentas

O laboratório desta atividade está em `lab_ferramentas/`.

- [Resumo para apresentar](lab_ferramentas/RELATORIO.md)
- [Relatório completo e evidências](lab_ferramentas/RELATORIO_COMPLETO.md)
- [Documentação completa](lab_ferramentas/README.md)
- [Roteiro curto de apresentação](APRESENTACAO.md)

No terminal, dentro de `aula03`:

```bash
source .venv/bin/activate
python exemplo01.py
python exemplo04.py validar
python -m unittest discover -s tests -v
```

Para repetir a medição com chamadas cobradas à OpenAI:

```bash
python exemplo04.py executar --volume-mensal 1000
python exemplo05.py --configuracao luna
python -m lab_ferramentas.gerar_relatorio
```

O gabarito já está congelado: não execute `congelar` novamente.
A chave privada fica em `.env`. Para instalar as dependências:
`python -m pip install -r requirements.txt`.

Os arquivos originais do curso foram encontrados dentro de `.venv` e uma cópia
foi preservada em `material_original/`. Os exemplos na raiz executam a adaptação
do Mini LAB. O exercício da aula 02 continua em `../aula02/`.

Os resultados foram produzidos antes da correção da pasta e movidos com seus
registros originais; os snapshots históricos mantêm os caminhos da época.
A movimentação preservou os hashes do código e do gabarito. Não houve novas
chamadas à API para mudar a localização.
