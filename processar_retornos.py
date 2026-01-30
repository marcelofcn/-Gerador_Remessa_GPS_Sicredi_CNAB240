import time
import shutil
from pathlib import Path

from app.services.retorno.leitor_retorno import LeitorRetornoSicredi

# --------------------------------------------------
# CONFIGURAÇÕES DE CAMINHO
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
INPUT_RET = BASE_DIR / "retorno" / "input"
PROC_RET = BASE_DIR / "retorno" / "processed"

# --------------------------------------------------
# VISUAL
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
    print(f"{azul}         Módulo: RETORNO (Feedback) | Status: ATIVO{reset}\n")

# --------------------------------------------------
# LOOP DE MONITORAMENTO
# --------------------------------------------------

def monitorar():
    print("[RETORNO] Monitorando diretório:")
    print(INPUT_RET.resolve())

    while True:
        arquivos = list(INPUT_RET.glob("*.RET")) + list(INPUT_RET.glob("*.ret"))

        for arquivo in arquivos:
            try:
                print("\n[RETORNO | ETAPA 1] Arquivo de retorno detectado")
                print(f"📄 Nome........: {arquivo.name}")
                print(f"📂 Origem......: {arquivo.resolve()}")

                print("[RETORNO | ETAPA 2] Processando retorno bancário (Sicredi)")
                LeitorRetornoSicredi.processar_arquivo(str(arquivo))

                print("[RETORNO | ETAPA 3] Retorno interpretado com sucesso")

                destino = PROC_RET / arquivo.name

                print("[RETORNO | ETAPA 4] Movendo arquivo para processados")
                print(f"➡️ Destino.....: {destino.resolve()}")

                shutil.move(str(arquivo), str(destino))

                print("[RETORNO | SUCESSO] Processamento finalizado")

            except Exception as e:
                print("\n[RETORNO | ERRO] Falha no processamento")
                print(f"📄 Arquivo.....: {arquivo.name}")
                print(f"📂 Caminho.....: {arquivo.resolve()}")
                print("❌ Motivo.....:", e)

        time.sleep(10)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    splash_screen()

    INPUT_RET.mkdir(parents=True, exist_ok=True)
    PROC_RET.mkdir(parents=True, exist_ok=True)

    monitorar()

