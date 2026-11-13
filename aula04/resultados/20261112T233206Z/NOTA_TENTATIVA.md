# Tentativa preliminar interrompida

Esta tentativa parou na primeira saída estruturada porque o esquema Pydantic de
Decimal incluía regex não aceita pela API (`invalid_json_schema`). As três
medições anteriores são reais, mas não compõem a comparação final.
A implementação passou a usar float finito na saída e Decimal na validação.
As duas rodadas completas foram reiniciadas com o mesmo dossiê e rubrica.
Chamadas da configuração interrompida podem ter sido cobradas; seu consumo não
foi recuperado do kickoff que falhou e não é tratado como zero.
