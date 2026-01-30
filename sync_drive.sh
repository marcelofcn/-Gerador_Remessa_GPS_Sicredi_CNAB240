#!/bin/bash

# Diretório base do projeto (onde está o script)
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

INPUT_DIR="$BASE_DIR/input"
RETORNO_INPUT_DIR="$BASE_DIR/retorno/input"
RETORNO_PROCESSED_DIR="$BASE_DIR/retorno/processed"

# IDs das pastas no Google Drive
ID_REMESSA="1HY02GCGmzxtpUxJTVJYfNmWMI2CdIea1"
ID_RETORNO="1mFzL7Xi1wD5kP9Ia9YR3rCrOgwf_hLTN"

# Garante diretórios locais
mkdir -p "$INPUT_DIR"
mkdir -p "$RETORNO_INPUT_DIR"
mkdir -p "$RETORNO_PROCESSED_DIR"

echo "📥 Baixando planilhas do RH..."
rclone move gdrive: "$INPUT_DIR" \
  --drive-root-folder-id "$ID_REMESSA" \
  --verbose

echo "📥 Baixando arquivos de retorno do banco..."
rclone move gdrive: "$RETORNO_INPUT_DIR" \
  --drive-root-folder-id "$ID_RETORNO" \
  --verbose

echo "📤 Devolvendo resumos TXT para o Drive..."
rclone copy "$RETORNO_PROCESSED_DIR" gdrive: \
  --include "*.txt" \
  --drive-root-folder-id "$ID_RETORNO" \
  --verbose

while true; do
  bash sync_drive.sh
  sleep 60
done
