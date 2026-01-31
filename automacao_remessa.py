"""
AUTOMAÇÃO DE GERAÇÃO DE REMESSA CNAB (SICREDI)
----------------------------------------------
Objetivo: Monitorar uma pasta de entrada ('input'), detectar novos arquivos CSV
contendo dados de contribuintes e gerar automaticamente arquivos de remessa no 
padrão CNAB para pagamento de GPS via Sicredi.

Fluxo:
1. Detecta novo CSV -> 2. Processa e valida colunas -> 3. Incrementa NSA (Número Sequencial)
4. Gera arquivo .REM -> 5. Move o CSV original para 'processed'.
"""

import time
import os
import shutil
import pandas as pd
import unicodedata
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Importação do serviço de construção do CNAB
from app.services.sicredi.gps_cnab_builder import gerar_cnab_gps_sicredi

# --------------------------------------------------
# CONFIGURAÇÕES DE CAMINHO (ABSOLUTAS)
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
PROCESSED_DIR = BASE_DIR / "processed" / "remessas"
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


def obter_e_incrementar_nsa():
    """Gerencia o contador de remessas para o cabeçalho do arquivo."""
    if not NSA_FILE.exists():
        NSA_FILE.write_text("1")

    try:
        conteudo = NSA_FILE.read_text().strip()
        atual = int(conteudo) if conteudo else 0
    except ValueError:
        atual = 0
        
    proximo = atual + 1
    NSA_FILE.write_text(str(proximo))
    return proximo


def remover_acentos(texto):
    """Normaliza strings para o padrão ASCII exigido pelos bancos."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in nfkd if not unicodedata.combining(c))

# --------------------------------------------------
# HANDLER DE PROCESSAMENTO
# --------------------------------------------------

class ProcessadorHandler(FileSystemEventHandler):
    """Classe responsável por reagir a novos arquivos na pasta input."""

    def on_created(self, event):
        # Ignora diretórios e arquivos que não sejam CSV
        if event.is_directory or not event.src_path.lower().endswith(".csv"):
            return

        caminho_csv = Path(event.src_path)

        print(f"\n[REMESSA] {datetime.now().strftime('%H:%M:%S')} - Arquivo detectado:")
        print(f" > {caminho_csv.name}")

        # Pequena pausa para garantir que o SO terminou de escrever o arquivo
        time.sleep(2)

        try:
            # Tenta ler com UTF-8, se falhar usa Latin-1 (comum em arquivos Excel/Windows)
            try:
                df = pd.read_csv(caminho_csv, sep=None, engine="python", encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(caminho_csv, sep=None, engine="python", encoding="latin-1")

            # Padroniza nomes de colunas
            df.columns = [c.strip().lower() for c in df.columns]

            colunas_obrigatorias = {
                "nome_contribuinte", "valor_total", "codigo_receita",
                "nit", "competencia", "valor_inss", "data_pagamento"
            }

            faltantes = colunas_obrigatorias - set(df.columns)
            if faltantes:
                raise ValueError(f"Colunas ausentes no CSV: {', '.join(faltantes)}")

            contribuintes = []
            for _, row in df.iterrows():
                # Tratamento de valores numéricos (converte vírgula para ponto e remove espaços)
                def limpar_valor(val):
                    return float(str(val).replace(".", "").replace(",", ".").strip())

                contribuintes.append({
                    "nome": str(row["nome_contribuinte"]),
                    "valor_total": limpar_valor(row["valor_total"]),
                    "gps": {
                        "codigo_receita": str(row["codigo_receita"]).split(".")[0].strip(),
                        "tipo_identificacao": 2, # Geralmente NIT/PIS
                        "identificacao": str(row["nit"]).replace(".", "").replace("-", "").strip(),
                        "competencia": str(row["competencia"]).replace("/", "").strip(),
                        "valor_inss": limpar_valor(row["valor_inss"]),
                        "valor_outras_entidades": 0.0,
                        "atualizacao_monetaria": (
                            limpar_valor(row.get("juros", 0)) +
                            limpar_valor(row.get("multa", 0))
                        ),
                    },
                })

            nsa = obter_e_incrementar_nsa()
            agora = datetime.now()

            # Formata data de pagamento do primeiro registro (assume-se lote único por data)
            data_pgto = str(df["data_pagamento"].iloc[0]).replace("/", "").replace("-", "").strip()

            # Chama o construtor do CNAB Sicredi
            cnab = gerar_cnab_gps_sicredi(
                empresa=EMPRESA,
                contribuintes=contribuintes,
                data_pagamento=data_pgto,
                data_geracao=agora.strftime("%d%m%Y"),
                hora_geracao=agora.strftime("%H%M%S"),
                nsa=nsa,
            )

            # Define nome do arquivo (Ex: 6XDZ3001.REM) e salva
            nome_remessa = f"{EMPRESA['convenio']}{agora.strftime('%d%m')}{str(nsa)[-2:]}.REM"
            caminho_remessa = OUTPUT_DIR / nome_remessa

            # CNAB deve ser ASCII sem acentos
            caminho_remessa.write_text(remover_acentos(cnab), encoding="ascii")

            # Move o arquivo CSV processado para a pasta de histórico
            destino_csv = PROCESSED_DIR / caminho_csv.name
            
            # Se já existir um arquivo com mesmo nome em 'processed', remove antes de mover
            if destino_csv.exists():
                destino_csv.unlink()
                
            shutil.move(str(caminho_csv), destino_csv)

            print(f"[REMESSA] Sucesso: {nome_remessa} gerado.")
            print(f"[REMESSA] NSA: {nsa} | Registros: {len(contribuintes)}")

        except Exception as e:
            print(f"[REMESSA] ❌ Erro ao processar {caminho_csv.name}: {e}")

# --------------------------------------------------
# EXECUÇÃO PRINCIPAL - MAIN
# --------------------------------------------------

if __name__ == "__main__":
    splash_screen()

    # Garante que as pastas existam
    for pasta in [INPUT_DIR, OUTPUT_DIR, PROCESSED_DIR]:
        pasta.mkdir(parents=True, exist_ok=True)

    # --- NOVIDADE: VARREDURA INICIAL ---
    print(f"[SISTEMA] Verificando arquivos pendentes em: {INPUT_DIR}")
    handler = ProcessadorHandler()
    
    # Busca arquivos que já estão na pasta antes do script iniciar
    arquivos_pendentes = list(INPUT_DIR.glob("*.csv")) + list(INPUT_DIR.glob("*.CSV"))
    
    if arquivos_pendentes:
        print(f"[SISTEMA] Encontrados {len(arquivos_pendentes)} arquivos. Processando...")
        for arquivo_path in arquivos_pendentes:
            # Simula o evento de criação para processar o que já existe
            class MockEvent:
                src_path = str(arquivo_path)
                is_directory = False
            
            handler.on_created(MockEvent())
    else:
        print("[SISTEMA] Nenhum arquivo pendente. Aguardando novos...")

    # --- INICIA MONITORAMENTO EM TEMPO REAL ---
    observer = Observer()
    observer.schedule(handler, str(INPUT_DIR), recursive=False)
    observer.start()
    
    print(f"[REMESSA] Monitoramento ativo em: {INPUT_DIR}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[REMESSA] Encerrando...")
        observer.stop()

    observer.join()
