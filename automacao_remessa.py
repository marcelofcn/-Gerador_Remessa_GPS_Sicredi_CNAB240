"""
===============================================================
PROJETO: Sistema de Remessa CNAB GPS - SICREDI
ARQUIVO: automacao_remessa.py
VERSÃO: 3.0.0
DATA: 18/02/2026
STATUS: PRODUÇÃO BLINDADA
===============================================================
"""

import time
import os
import shutil
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

from app.services.sicredi.gps_cnab_builder import gerar_cnab_gps_sicredi


# ==================================================
# CONFIGURAÇÕES
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
PROCESSED_DIR = BASE_DIR / "processed" / "remessas"
NSA_FILE = BASE_DIR / "nsa.txt"


EMPRESA = {
    "cnpj": "04251333000144",
    "razao_social": "COMUNIDADE CANCAO NOVA",
    "agencia": "0710",
    "dv_agencia": "2",
    "conta": "28203",
    "dv_conta": "5",
    "convenio": "6XDZ",
}

def splash_screen():
    """Exibe o cabeçalho estilizado no console."""
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

# ==================================================
# FUNÇÕES UTILITÁRIAS
# ==================================================

def to_decimal(valor):
    return Decimal(str(valor).replace(",", ".")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def normalizar_data(data_str):
    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d%m%Y"]
    for f in formatos:
        try:
            return datetime.strptime(str(data_str), f).strftime("%d%m%Y")
        except ValueError:
            continue
    raise ValueError(f"Data inválida: {data_str}")


def obter_e_incrementar_nsa():
    if not NSA_FILE.exists():
        NSA_FILE.write_text("1")

    atual = int(NSA_FILE.read_text().strip())
    proximo = atual + 1

    NSA_FILE.write_text(str(proximo))
    return proximo


def gerar_nome_remessa(convenio):
    hoje = datetime.now().strftime("%d")

    arquivos_existentes = [
        f for f in os.listdir(OUTPUT_DIR)
        if f.startswith(convenio + hoje) and f.endswith(".REM")
    ]

    sequenciais = []
    for f in arquivos_existentes:
        try:
            sequenciais.append(int(f[-6:-4]))
        except:
            continue

    proximo_seq = max(sequenciais) + 1 if sequenciais else 0

    return f"{convenio}{hoje}{proximo_seq:02d}.REM"


# ==================================================
# PROCESSADOR
# ==================================================

class ProcessadorHandler(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory or not event.src_path.lower().endswith(".csv"):
            return

        print(f"📂 Arquivo detectado: {os.path.basename(event.src_path)}")

        # Aguarda estabilidade do arquivo
        time.sleep(2)

        try:
            df = pd.read_csv(
                event.src_path,
                sep=None,
                engine='python',
                encoding='utf-8'
            )

            df.columns = [c.strip().lower() for c in df.columns]

            contribuintes = []

            for _, row in df.iterrows():

                contribuintes.append({
                    "nome": str(row["nome_contribuinte"]).strip(),
                    "valor_total": to_decimal(row["valor_total"]),
                    "gps": {
                        "codigo_receita": str(row["codigo_receita"]).split('.')[0],
                        "tipo_identificacao": 2,
                        "identificacao": str(row["nit"]).split('.')[0],
                        "competencia": str(row["competencia"]).replace("/", ""),
                        "valor_inss": to_decimal(row["valor_inss"]),
                        "valor_outras_entidades": Decimal("0.00"),
                        "atualizacao_monetaria":
                            to_decimal(row.get("juros", 0)) +
                            to_decimal(row.get("multa", 0))
                    }
                })

            if not contribuintes:
                raise ValueError("Nenhum contribuinte encontrado no CSV.")

            # NSA
            nsa = obter_e_incrementar_nsa()

            agora = datetime.now()

            data_pagamento = normalizar_data(df["data_pagamento"].iloc[0])

            cnab = gerar_cnab_gps_sicredi(
                empresa=EMPRESA,
                contribuintes=contribuintes,
                data_pagamento=data_pagamento,
                data_geracao=agora.strftime("%d%m%Y"),
                hora_geracao=agora.strftime("%H%M%S"),
                nsa=nsa
            )

            nome_remessa = gerar_nome_remessa(EMPRESA["convenio"])

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

            with open(OUTPUT_DIR / nome_remessa, "w", encoding="ascii", newline="") as f:
                f.write(cnab)

            shutil.move(
                event.src_path,
                PROCESSED_DIR / os.path.basename(event.src_path)
            )

            print(f"✅ Remessa gerada: {nome_remessa} | NSA: {nsa}")

        except Exception as e:
            print(f"❌ ERRO: {e}")


# ==================================================
# EXECUÇÃO
# ==================================================

if __name__ == "__main__":

    print("🚀 Sistema de Remessa CNAB GPS - Sicredi")
    print("📡 Monitorando pasta:", INPUT_DIR)

    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    observer.schedule(ProcessadorHandler(), str(INPUT_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
