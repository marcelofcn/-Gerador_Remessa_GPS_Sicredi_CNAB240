# Guia de Operação - RH e Financeiro

## Como preencher a Planilha Excel
Para que a remessa seja gerada corretamente, a planilha `GPS_SICREDI-RH.xlsx` deve seguir estas regras:

1. **Aba:** O nome da aba deve ser exatamente `GPS`.
2. **Coluna Código Receita:** Use apenas os 4 dígitos (ex: `2100` ou `2003`).
3. **Coluna Identificador:** CNPJ da empresa ou CEI (apenas números).
4. **Coluna Competência:** Formato `MMYYYY` (ex: `092025`).
5. **Acentos:** Evite acentos nos nomes, embora o sistema possua um filtro automático para removê-los.

## Processo de Envio
1. Salve a planilha na pasta do projeto.
2. Execute o script `test_gps_sicredi.py`.
3. Localize o arquivo `.REM` gerado.
4. Faça o upload no Gerenciador Financeiro do Sicredi.
5. **Importante:** Verifique o relatório de pré-crítica do banco após o upload.
