# -Gerador_Remessa_GPS_Sicredi_CNAB240
🏦 Gerador de Remessa GPS Sicredi (CNAB 240)
Este repositório contém o sistema de geração de arquivos de remessa para pagamento de GPS (Guia da Previdência Social) sem código de barras, homologado para o padrão Sicredi CNAB 240.

📍 Localização dos Arquivos
Após a execução do sistema, o arquivo de remessa é gerado na raiz do projeto seguindo o padrão de nomenclatura do Sicredi: CCCDDMSS.REM.
CCC: Código do convênio (Ex: 6XDZ)
DD: Dia do mês
M: Mês (conforme mapa de caracteres Sicredi)
SS: Sequencial do dia (Ex: 00)
Exemplo de arquivo gerado hoje: 6XDZ15000.REM

🚀 Como Rodar e Gerar a Remessa
Certifique-se de que a planilha GPS_SICREDI-RH.xlsx está na raiz com os dados do RH.
Limpe o cache e execute o script de teste:
code
Bash
find . -name "pycache" -type d -exec rm -rf {} +
python3 test_gps_sicredi.py

🛠️ Correções Implementadas (Checklist de Homologação)
O sistema foi ajustado para atender às seguintes exigências do banco:
✅ Data no Header (Verde): Corrigida para formato DDMMAAAA (Posição 144-151).
✅ Segmento N (GPS):
Data de pagamento em DDMMAAAA.
Código de Receita ajustado para 6 posições (4 dígitos + 2 espaços) para evitar deslocamento.
Identificador de Tributo fixado em 17.
✅ Trailer de Lote (Laranja): Inclusão de 18 zeros obrigatórios após o valor total (Posição 042-059).
✅ Trailer de Arquivo (Rosa): Inclusão de 6 zeros de controle e preenchimento com espaços.
✅ Tratamento ASCII: Remoção automática de acentos e cedilhas (Ex: Ç -> C) para evitar rejeição no processamento bancário.

🔍 Validação Rápida via Terminal
Para verificar se o arquivo gerado está correto antes de subir ao banco:

1. Verificar formato da data no Header:
code
Bash
sed -n '1p' *.REM | cut -c144-151
# Resultado esperado: DDMMAAAA (Ex: 15012026)

2. Verificar se existem acentos (não deve retornar nada):
code
Bash
grep -P '[^\x00-\x7f]' *.REM

3. Verificar tamanho das linhas (deve ser 240 + CRLF):
code
Bash
awk '{ print length }' *.REM | uniq

📂 Estrutura de Pastas
app/layouts/sicredi/: Contém as regras de montagem das linhas (Header, Segmento N, Trailers).
app/services/sicredi/: Contém o builder que organiza os dados da planilha no formato CNAB.
test_gps_sicredi.py: Ponto de entrada para execução e geração do arquivo.
Documentação atualizada em 15/01/2026 para a Versão 1.1 (Homologada).
