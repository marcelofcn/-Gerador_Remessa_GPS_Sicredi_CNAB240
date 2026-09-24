# Arquitetura Técnica do Sistema

## Fluxo de Dados
1. **Parser (`gps_planilha_parser.py`):** Utiliza Pandas para ler a aba `GPS` do Excel. Converte valores monetários para float e valida o CNPJ da empresa.
2. **Builder (`gps_cnab_builder.py`):** Orquestra a criação do arquivo. Ele chama cada layout na ordem correta (Header > Lote > Segmentos > Trailers).
3. **Layouts (`app/layouts/sicredi/`):** Contém funções puras que recebem dicionários e retornam strings de exatamente 240 caracteres.

## Funções Utilitárias (`utils.py`)
- `num(valor, tamanho)`: Formata números com zeros à esquerda.
- `alfa(texto, tamanho)`: Formata strings, remove acentos e preenche com espaços à direita.

## Padrão de Linha
O sistema utiliza `\r\n` (CRLF) como finalizador de linha, padrão exigido para processamento em sistemas de Mainframe bancário.
