# Histórico de Alterações - Remessa Sicredi GPS

## [1.1.0] - 2026-01-15
### Corrigido
- **Data do Header:** Ajustado de YYYYMMDD para DDMMAAAA conforme exigência do banco (Crítica Verde).
- **Data do Segmento N:** Corrigida lógica de inversão para datas que começam com "20" (ex: dia 20, 21...).
- **Segmento N (GPS):** Código de receita ajustado para 6 posições (4 dígitos + 2 espaços) para evitar deslocamento de campos.
- **Trailer de Lote:** Adicionado preenchimento de 18 zeros na posição 042-059 (Crítica Laranja).
- **Trailer de Arquivo:** Ajustado preenchimento de zeros e espaços no fechamento (Crítica Rosa).
- **Encoding:** Implementada função `remover_acentos` para garantir que o arquivo seja gerado em ASCII puro (evita erro de caractere Ç, Ã, etc).

## [1.0.0] - 2026-01-10
- Versão inicial do sistema de geração CNAB 240 para GPS.
