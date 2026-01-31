"""
PROCESSAMENTO AUTOMÁTICO DE RETORNOS BANCÁRIOS (SICREDI)
--------------------------------------------------------
Objetivo: Monitorar a pasta 'retorno/input', identificar arquivos de retorno 
(.RET) enviados pelo banco e processar a liquidação ou erros de títulos.

Fluxo:
1. Varredura de arquivos .RET -> 2. Leitura e interpretação (CNAB240/400) 
3. Atualização do banco de dados/sistema via LeitorRetornoSicredi
4. Movimentação do arquivo para o histórico 'processed'.
"""

import time
import shutil
from pathlib import Path
from datetime import datetime

# Importação do serviço de leitura de retorno
from app.services.retorno.leitor_retorno import LeitorRetornoSicredi

# --------------------------------------------------
# CONFIGURAÇÕES DE CAMINHO (ABSOLUTAS)
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
INPUT_RET = BASE_DIR / "retorno" / "input"
PROC_RET = BASE_DIR / "retorno" / "processed"

# --------------------------------------------------
# INTERFACE VISUAL
# --------------------------------------------------

def splash_screen():
    """Exibe o cabeçalho do sistema no terminal."""
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

# --------------------------------------------------
# LÓGICA DE MONITORAMENTO
# --------------------------------------------------

def monitorar():
    """Loop infinito que verifica a presença de novos arquivos de retorno."""
    print(f"[RETORNO] Aguardando arquivos em: {INPUT_RET.name}/")
    
    while True:
        # Busca por extensões .RET e .ret de forma insensível a maiúsculas
        arquivos = list(INPUT_RET.glob("*.[Rr][Ee][Tt]"))

        for arquivo in arquivos:
            timestamp = datetime.now().strftime("%H:%M:%S")
            try:
                print(f"\n{'-'*60}")
                print(f"[{timestamp}] NOVO RETORNO DETECTADO")
                print(f"📄 Arquivo: {arquivo.name}")

                # ETAPA 1: Processamento lógico
                print("[RETORNO | PASSO 1] Interpretando layout bancário...")
                # O método abaixo deve conter a lógica de leitura do CNAB e update no DB
                LeitorRetornoSicredi.processar_arquivo(str(arquivo))

                # ETAPA 2: Movimentação de segurança
                destino = PROC_RET / arquivo.name
                
                # Se o arquivo já existir no destino, adiciona um sufixo de data/hora para não sobrescrever
                if destino.exists():
                    sufixo = datetime.now().strftime("%Y%m%d_%H%M%S")
                    destino = PROC_RET / f"{arquivo.stem}_{sufixo}{arquivo.suffix}"

                print("[RETORNO | PASSO 2] Movendo para pasta de processados...")
                shutil.move(str(arquivo), str(destino))

                print(f"[RETORNO | SUCESSO] Concluído: {arquivo.name}")
                print(f"{'-'*60}")

            except Exception as e:
                print(f"\n[RETORNO | ❌ ERRO] Falha crítica no arquivo: {arquivo.name}")
                print(f"⚠️ Motivo: {str(e)}")
                # Opcional: mover para uma pasta 'error' em vez de deixar travando o loop
                time.sleep(2) 

        # Intervalo entre varreduras (ajustado para 5s para ser mais responsivo)
        time.sleep(5)


# --------------------------------------------------
# PONTO DE ENTRADA
# --------------------------------------------------

if __name__ == "__main__":
    splash_screen()

    # Inicialização de diretórios
    INPUT_RET.mkdir(parents=True, exist_ok=True)
    PROC_RET.mkdir(parents=True, exist_ok=True)

    try:
        monitorar()
    except KeyboardInterrupt:
        print("\n[RETORNO] Sistema encerrado pelo usuário.")
    except Exception as e:
        print(f"\n[SISTEMA] Erro fatal: {e}")