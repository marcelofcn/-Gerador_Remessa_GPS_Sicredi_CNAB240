import time
import os
import shutil
import pandas as pd
import unicodedata
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.services.sicredi.gps_cnab_builder import gerar_cnab_gps_sicredi

<<<<<<<< HEAD:automacao_remessa.py
# --- CONFIGURAÇÕES DE PRODUÇÃO ---
BASE_DIR = "/opt/gps-remessa"
INPUT_DIR = f"{BASE_DIR}/input"
OUTPUT_DIR = f"{BASE_DIR}/output"
PROCESSED_DIR = f"{BASE_DIR}/processed"
NSA_FILE = f"{BASE_DIR}/nsa.txt"
========
# --- codigo no servidor alterado para uso local ---

# --- CONFIGURAÇÕES DINÂMICAS ---
# Isso pega o caminho de onde o script 'automacao_remessa.py' está localizado
BASE_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Se você quiser manter as pastas dentro da pasta do projeto no PC:
INPUT_DIR = os.path.join(BASE_PROJECT_DIR, "dados", "input")
OUTPUT_DIR = os.path.join(BASE_PROJECT_DIR, "dados", "output")
PROCESSED_DIR = os.path.join(BASE_PROJECT_DIR, "dados", "processed")
NSA_FILE = os.path.join(BASE_PROJECT_DIR, "dados", "nsa.txt")

# --- CONFIGURAÇÕES DE PRODUÇÃO ---servidor linux srv-financeiro
#BASE_DIR = "/opt/gps-remessa"
#INPUT_DIR = f"{BASE_DIR}/input"
#OUTPUT_DIR = f"{BASE_DIR}/output"
#PROCESSED_DIR = f"{BASE_DIR}/processed"
#NSA_FILE = f"{BASE_DIR}/nsa.txt"
>>>>>>>> 6f16bb7 (inclusao comentarios nos codigos principais):.automacao_remessa.py

EMPRESA = {
    "cnpj": "04251333000144",
    "razao_social": "COMUNIDADE CANCAO NOVA",
    "agencia": "0710",
    "dv_agencia": "2",
    "conta": "28203",
    "dv_conta": "5",
    "convenio": "6XDZ", # <--- TI: Confirmar código de produção
}

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
    print(f"{azul}         Módulo: REMESSA (CSV -> CNAB) | Status: ATIVO{reset}\n")

def obter_e_incrementar_nsa():
    if not os.path.exists(NSA_FILE):
        with open(NSA_FILE, "w") as f: f.write("1")
    with open(NSA_FILE, "r") as f:
        conteudo = f.read().strip()
        atual = int(conteudo) if conteudo else 1
    proximo = atual + 1
    with open(NSA_FILE, "w") as f: f.write(str(proximo))
    return proximo

def remover_acentos(texto):
    if not texto: return ""
    nfkd = unicodedata.normalize('NFKD', str(texto))
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

class ProcessadorHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".csv"): return
        print(f"📂 Detectado: {os.path.basename(event.src_path)}")
        time.sleep(2)
        try:
            df = pd.read_csv(event.src_path, sep=None, engine='python', encoding='utf-8')
            df.columns = [c.strip().lower() for c in df.columns]
            contribuintes = []
            for _, row in df.iterrows():
                contribuintes.append({
                    "nome": str(row["nome_contribuinte"]),
                    "valor_total": float(str(row["valor_total"]).replace(',','.')),
                    "gps": {
                        "codigo_receita": str(row["codigo_receita"]).split('.')[0],
                        "tipo_identificacao": 2,
                        "identificacao": str(row["nit"]).split('.')[0],
                        "competencia": str(row["competencia"]).replace("/", ""),
                        "valor_inss": float(str(row["valor_inss"]).replace(',','.')),
                        "valor_outras_entidades": 0.0,
                        "atualizacao_monetaria": float(str(row.get("juros", 0)).replace(',','.')) + float(str(row.get("multa", 0)).replace(',','.'))
                    }
                })
            nsa = obter_e_incrementar_nsa()
            agora = datetime.now()
            data_pgto = str(df["data_pagamento"].iloc[0]).replace("/", "").replace("-", "")
            cnab = gerar_cnab_gps_sicredi(empresa=EMPRESA, contribuintes=contribuintes, data_pagamento=data_pgto, data_geracao=agora.strftime("%d%m%Y"), hora_geracao=agora.strftime("%H%M%S"), nsa=nsa)
            cnab_limpo = remover_acentos(cnab)
            nome_remessa = f"{EMPRESA['convenio']}{agora.strftime('%d')}00.REM"
            with open(f"{OUTPUT_DIR}/{nome_remessa}", "w", encoding="ascii", newline="") as f: f.write(cnab_limpo)
            shutil.move(event.src_path, f"{PROCESSED_DIR}/{os.path.basename(event.src_path)}")
            print(f"✅ Sucesso: {nome_remessa} (NSA {nsa})")
        except Exception as e: print(f"❌ Erro: {e}")

if __name__ == "__main__":
    splash_screen()
    os.makedirs(INPUT_DIR, exist_ok=True)
    observer = Observer()
    observer.schedule(ProcessadorHandler(), INPUT_DIR, recursive=False)
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: observer.stop()
    observer.join()
