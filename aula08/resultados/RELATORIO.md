# Resultados do Mini LAB · 18/11/2026

Langflow 1.12.10, modelo OpenAI `gpt-6-luna`. O painel **Settings → Model Providers** mostrou o OpenAI conectado, com as opções **Disconnect** e **Replace**, após carregar `OPENAI_API_KEY` do terminal. A chave do cliente foi criada em **Settings → Langflow API Keys** e gravada no `.env` local.

O exemplo do professor foi importado. A pergunta P01 reconstitui o cenário da seção 4.3 sobre remoção durante o ano letivo. O material registra **321 tokens e cerca de 3 s**. A execução abaixo mediu **309 tokens e 3,2 s**. A cópia no servidor usa temperatura 1, o valor aceito pelo modelo. O arquivo da aula foi preservado.

O atendimento do setor foi criado como fluxo vazio e preenchido com quatro componentes e três ligações pela interface de programação do Langflow. O resumo foi gerado duplicando esse grafo e substituindo o prompt. O agente foi adaptado do modelo **Simple Agent** incluído na instalação.

## Playground

| Fluxo | Mensagem de teste | Resposta correta? | Tokens | Tempo |
| --- | --- | --- | ---: | ---: |
| Professor | P01 · Posso pedir remoção no meio do ano letivo? | Sim, encaminhou à DRE ou ao RH | 309 | 3,2 s |
| Atendimento | A01 · Esqueci a senha de rede | Sim, orientou a recuperação sem pedir senha | 333 | 1,9 s |
| Atendimento | A02 · O que registrar para pedir acesso? | Sim, pediu sistema, perfil e autorização da chefia | 342 | 1,9 s |
| Atendimento | A03 · Apaguei um arquivo da rede | Sim, pediu caminho e data aproximada | 426 | 3,2 s |
| Atendimento | A04 · E-mail pediu código de verificação | Sim, orientou a proteger o código e acionar a TI | 381 | 1,8 s |
| Atendimento | A05 · Quando o chamado será resolvido? | Sim, não inventou prazo e indicou o chamado existente | 328 | 2,5 s |
| Atendimento | A06 · Qual o valor do IPVA? | Sim, encaminhou ao atendimento tributário | 365 | 2,5 s |
| Resumo | R01 · Comunicado de manutenção do banco de dados | Sim, conforme a conferência abaixo | 1.407 | 9,5 s |
| Classificador | C01 · Autenticação parou para todas as equipes | Sim, URGENTE | 268 | 1,6 s |
| Classificador | C02 · Liberar perfil de consulta | Sim, NORMAL | 266 | 1,5 s |
| Classificador | C03 · Recebemos o aviso, obrigado | Sim, INFORMATIVO | 269 | 2,5 s |
| Classificador | C04 · “É urgente”, mas o acesso funciona | Sim, NORMAL | 294 | 2,1 s |
| Classificador | C05 · “Só avisando”, com sessão desconhecida | Sim, URGENTE | 281 | 1,2 s |
| Agente | G01 · Início e fim previsto da manutenção, com URL | Sim, leu e citou o comunicado oficial | 1.979 | 3,6 s |
| Agente | G02 · Onde pedir ajuda online com os sistemas? | Sim, encontrou e citou a Central de Atendimento | 5.581 | 8,0 s |

[Entradas, respostas e identificadores de execução](playground.json)

## Conferência do resumo

O teste usou uma paráfrase de comunicado público real da SEFAZ-MT. A autoria é institucional e o trecho usado não contém dados pessoais. O laboratório usou esse material porque não havia um documento interno recebido pelo setor para anonimizar. O resumo identificou a unidade emissora, a data de publicação de **28/06/2024 às 10h34** e a ausência de número. [Comunicado original da SEFAZ-MT](https://www5.sefaz.mt.gov.br/pt/-/sefaz-far%C3%A1-parada-programada-para-manuten%C3%A7%C3%A3o-no-banco-de-dados-1)

| Providência ou impacto | Responsável no texto | Prazo ou janela conferida |
| --- | --- | --- |
| Atualizar o banco de dados | SEFAZ-MT | Parada a partir de 30/06/2024 às 07h. O horário de término da manutenção não é informado. |
| Autorizar NF-e em contingência pela SVRS | O texto identifica a SVRS como ambiente de autorização. A equipe responsável pela ativação não é informada. | Ativa durante a parada e até 01/07/2024 às 09h. |
| Emitir NFC-e em contingência | Contribuinte, pelo próprio emissor | Horário específico não informado. |
| Restabelecer emissão de NF3-e e Guia Florestal integrada à Sema | Responsável específico não informado | Indisponibilidade até o restabelecimento, sem horário informado. |

## Agente no Flow Activity

| Caso | Tokens | Latência | Ferramentas exibidas no Playground |
| --- | ---: | ---: | --- |
| G01 · Direta | 1.979 | 3,62 s | `FETCH CONTENT` (310 ms) |
| G02 · Vaga | 5.581 | 7,99 s | `PERFORM SEARCH` (2.678 ms) → `FETCH CONTENT` (460 ms) |

G01 já forneceu a página. G02 precisou buscar resultados e abrir a página selecionada. A etapa de busca acrescentou 2,68 s de ferramenta e trouxe resultados adicionais ao contexto do modelo. A execução completa consumiu **3.602 tokens a mais** e levou **4,37 s a mais**. A resposta direta identificou as 21h de 01/06/2022 e as 09h de 02/06/2022 como início e fim previsto. A resposta vaga indicou a Central de Atendimento. [Comunicado de manutenção](https://www5.sefaz.mt.gov.br/pt/-/22139486-manutencao-no-sistema-de-ti-da-sefaz-e-adiada-para-quarta-feira-01-), [Central de Atendimento](https://www5.sefaz.mt.gov.br/central-de-atendimento)

## Classificador pela API

As **cinco classificações** coincidiram com o Playground e com o gabarito. C04 ficou **NORMAL** porque a palavra “urgente” veio sem evidência de interrupção. C05 ficou **URGENTE** porque a sessão desconhecida indica um possível incidente ativo, apesar de “só avisando”. [Comparação das cinco execuções](comparacao_api.json)

## Desafio opcional

O agente usou só o componente URL. Nos dois testes, `FETCH CONTENT` recebeu apenas o endereço configurado e a resposta citou apenas a Central de Atendimento. O segundo teste pediu explicitamente uma página externa. O agente consultou a fonte oficial e respondeu com o horário encontrado nela. [Execuções do desafio](desafio_opcional.json), [Central de Atendimento](https://www5.sefaz.mt.gov.br/central-de-atendimento)
