#```🎯 O que este arquivo faz (visão macro)

#Este script é um **daemon simples de monitoramento** que:

#- Fica observando uma pasta (`retorno/input`)
#- Detecta arquivos `.RET` enviados pelo banco
#- Processa cada retorno usando o layout Sicredi
#- Move o arquivo processado para `retorno/processed`
#- Evita reprocessamento
#- Serve como **ponte entre banco → sistema**

#👉 Ele **não gera CNAB**, **não valida remessa**,

#👉 Ele **interpreta o feedback do banco**.```

import time
import os
import shutil
from datetime import datetime
from app.services.retorno.leitor_retorno import LeitorRetornoSicredi

# funcionamento em ambiente local
#BASE_DIR = "/opt/gps-remessa"
BASE_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
# MANTER AS PASTAS DENTRO DO PROJETO
INPUT_RET = f"{BASE_PROJECT_DIR}/retorno/input"
PROC_RET = f"{BASE_PROJECT_DIR}/retorno/processed"

def splash_screen():
    azul = "\033[1;34m"
    amarelo = "\033[1;33m"
    reset = "\033[0m"
    print(f"{azul}" + "_"*62)
    print(f"|{amarelo}   ____ _   _   ____                                         {azul}|")
    print(f"|{amarelo}  / ___| \ | | |  _ \ ___ _ __ ___   ___  ___ ___  __ _      {azul}|")
    print(f"|{amarelo} | |   |  \| | | |_) / _ \ '_ ` _ \ / _ \/ __/ __|/ _` |     {azul}|")
    print(f"|{amarelo} | |___| |\  | |  _ <  __/ | | | | |  __/\__ \__ \ (_| |     {azul}|")
    print(f"|{amarelo}  \____|_| \_| |_| \_\___|_| |_| |_|\___||___/___/\__,_|     {azul}|")
    print(f"|{azul}" + "_"*62 + "|")
    print(f"\n{amarelo}       SISTEMA DE REMESSA DIGITAL | CANÇÃO NOVA & SICREDI{reset}")
    print(f"{azul}         Módulo: RETORNO (Feedback) | Status: ATIVO{reset}\n")

def monitorar():
    while True:
        arquivos = [f for f in os.listdir(INPUT_RET) if f.lower().endswith('.ret')]
        for arq in arquivos:
            caminho = os.path.join(INPUT_RET, arq)
            try:
                print(f"🔍 Lendo Retorno: {arq}")
                dados = LeitorRetornoSicredi.processar_arquivo(caminho)
                # Lógica de geração de relatório TXT/PDF aqui
                shutil.move(caminho, os.path.join(PROC_RET, arq))
                print(f"✅ Feedback gerado para {arq}")
            except Exception as e: print(f"❌ Erro no Retorno: {e}")
        time.sleep(10)

if __name__ == "__main__":
    splash_screen()
    os.makedirs(INPUT_RET, exist_ok=True)
    monitorar()
