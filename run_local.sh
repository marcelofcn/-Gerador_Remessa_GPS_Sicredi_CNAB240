#!/bin/bash

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

source "$BASE_DIR/venv/bin/activate"

echo "🚀 Iniciando automacao_remessa..."
python "$BASE_DIR/automacao_remessa.py" &

REMESSA_PID=$!

echo "⏳ Aguardando watchdog subir..."
sleep 3

echo "🔄 Sincronizando Drive..."
bash "$BASE_DIR/sync_drive.sh"

echo "📥 Processando retornos..."
python "$BASE_DIR/processar_retornos.py"

echo "ℹ️ automacao_remessa rodando (PID $REMESSA_PID)"
echo "Para parar: kill $REMESSA_PID"

while true; do
  bash sync_drive.sh
  sleep 60
done
