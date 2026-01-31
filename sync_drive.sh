#!/bin/bash

################################################################################
# ORQUESTRADOR DE TRÁFEGO - CANÇÃO NOVA & SICREDI
################################################################################

BASE_DIR="/home/house/developer/geraremessa"
INPUT_DIR="$BASE_DIR/input"
OUTPUT_DIR="$BASE_DIR/output"
PROCESSED_DIR="$BASE_DIR/processed/remessas"

# IDs CONFIRMADOS DO DRIVE
ID_ENTRADA_RH="1HY02GCGmzxtpUxJTVJYfNmWMI2CdIea1"
ID_GPS_REMESSA_PRONTA="1rwaQAv51umedVr0QwplMrDm1H34lZ7nq"
ID_BACKUP_CSV_LIDO="1rmTQKf3bo5ssslsz8j46y_mHLgKJZFvS"

echo "------------------------------------------------------------"
echo "🚀 INICIANDO SINCRONIZAÇÃO: $(date +'%d/%m/%Y %H:%M:%S')"
echo "------------------------------------------------------------"

# 1. BUSCA PLANILHA DO RH (Limpa o Drive após baixar para o PC)
echo "📥 [ENTRADA] Coletando arquivos da pasta GPS_PARA_PROCESSAR..."
rclone move gdrive: "$INPUT_DIR" --drive-root-folder-id "$ID_ENTRADA_RH" --verbose

# 2. ENVIA REMESSAS CNAB PRONTAS (Para o RH baixar e subir no Banco)
echo "📤 [REMESSA] Enviando arquivos .REM para o Drive..."
rclone copy "$OUTPUT_DIR" gdrive: --drive-root-folder-id "$ID_GPS_REMESSA_PRONTA" --include "*.REM" --verbose

# 3. FAZ BACKUP DO CSV PROCESSADO (Para conferência posterior)
echo "📤 [BACKUP] Enviando cópia do CSV processado para o Drive..."
rclone copy "$PROCESSED_DIR" gdrive: --drive-root-folder-id "$ID_BACKUP_CSV_LIDO" --include "*.csv" --verbose

echo "------------------------------------------------------------"
echo "✅ CICLO FINALIZADO COM SUCESSO"
echo "------------------------------------------------------------"
while true; do bash sync_drive.sh; sleep 180; done
