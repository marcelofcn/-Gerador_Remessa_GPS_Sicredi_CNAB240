import time
import os
import shutil
import pandas as pd
import unicodedata
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.services.sicredi.gps_cnab_builder import gerar_cnab_gps_sicredi

# --------------------------------------------------
# CONFIGURAÇÕES DE CAMINHO (ABSOLUTAS)
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
PROCESSED_DIR = BASE_DIR / "processed"
NSA_FILE = BASE_DIR / "nsa.txt"

# --------------------------------------------------
# DADOS DA EMPRESA
# --------------------------------------------------

EMPRESA = {
    "cnpj": "04251333000144",
    "razao_social": "COMUNIDADE CANCAO NOVA",
    "agencia": "0710",
    "dv_agencia": "2",
    "conta": "28203",
    "dv_conta": "5",
    "convenio": "6XDZ",
}

# --------------------------------------------------
# UTILITÁRIOS
# --------------------------------------------------
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
    if not NSA_FILE.exists():
        NSA_FILE.write_text("1")

    atual = int(NSA_FILE.read_text().strip())
    proximo = atual + 1
    NSA_FILE.write_text(str(proximo))
    return proximo


def remover_acentos(texto):
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in nfkd if not unicodedata.combining(c))

# --------------------------------------------------
# HANDLER DE PROCESSAMENTO
# --------------------------------------------------

class ProcessadorHandler(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".csv"):
            return

        caminho_csv = Path(event.src_path)

        print("\n[REMESSA] Arquivo detectado:")
        print(caminho_csv)

        time.sleep(2)

        try:
            df = pd.read_csv(caminho_csv, sep=None, engine="python", encoding="utf-8")
            df.columns = [c.strip().lower() for c in df.columns]

            colunas_obrigatorias = {
                "nome_contribuinte",
                "valor_total",
                "codigo_receita",
                "nit",
                "competencia",
                "valor_inss",
                "data_pagamento",
            }

            faltantes = colunas_obrigatorias - set(df.columns)
            if faltantes:
                raise ValueError(f"Colunas ausentes no CSV: {', '.join(faltantes)}")

            contribuintes = []
            for _, row in df.iterrows():
                contribuintes.append({
                    "nome": str(row["nome_contribuinte"]),
                    "valor_total": float(str(row["valor_total"]).replace(",", ".")),
                    "gps": {
                        "codigo_receita": str(row["codigo_receita"]).split(".")[0],
                        "tipo_identificacao": 2,
                        "identificacao": str(row["nit"]).split(".")[0],
                        "competencia": str(row["competencia"]).replace("/", ""),
                        "valor_inss": float(str(row["valor_inss"]).replace(",", ".")),
                        "valor_outras_entidades": 0.0,
                        "atualizacao_monetaria": (
                            float(str(row.get("juros", 0)).replace(",", ".")) +
                            float(str(row.get("multa", 0)).replace(",", "."))
                        ),
                    },
                })

            nsa = obter_e_incrementar_nsa()
            agora = datetime.now()

            data_pgto = str(df["data_pagamento"].iloc[0]).replace("/", "").replace("-", "")

            cnab = gerar_cnab_gps_sicredi(
                empresa=EMPRESA,
                contribuintes=contribuintes,
                data_pagamento=data_pgto,
                data_geracao=agora.strftime("%d%m%Y"),
                hora_geracao=agora.strftime("%H%M%S"),
                nsa=nsa,
            )

            nome_remessa = f"{EMPRESA['convenio']}{agora.strftime('%d')}00.REM"
            caminho_remessa = OUTPUT_DIR / nome_remessa

            caminho_remessa.write_text(remover_acentos(cnab), encoding="ascii")

            destino_csv = PROCESSED_DIR / caminho_csv.name
            shutil.move(str(caminho_csv), destino_csv)

            print("[REMESSA] Arquivo gerado:")
            print(caminho_remessa)
            print(f"[REMESSA] Concluído com sucesso | NSA {nsa}")

        except Exception as e:
            print(f"[REMESSA] ❌ Erro: {e}")

# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    splash_screen()

    print("[REMESSA] Monitorando diretório:")
    print(INPUT_DIR)

    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)

    observer = Observer()
    observer.schedule(ProcessadorHandler(), str(INPUT_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
