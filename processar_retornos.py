"""
PROCESSAMENTO AUTOMÁTICO DE RETORNOS BANCÁRIOS (SICREDI)
--------------------------------------------------------
Versão: 2.0.0
Status: PRODUÇÃO

Responsabilidades:
- Monitorar pasta retorno/input
- Processar arquivos .RET
- Separar pagamentos OK e ERRO
- Gerar relatório executivo resumo.txt
- Mover arquivo para processed com segurança
"""

import time
import shutil
from pathlib import Path
from datetime import datetime

from app.services.retorno.leitor_retorno import LeitorRetornoSicredi

# --------------------------------------------------
# CONFIGURAÇÕES DE CAMINHO
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
INPUT_RET = BASE_DIR / "retorno" / "input"
PROC_RET = BASE_DIR / "retorno" / "processed"

EMPRESA_NOME = "Comunidade Canção Nova"

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
# RELATÓRIO EXECUTIVO
# --------------------------------------------------

def gerar_resumo_txt(
    empresa,
    pagamentos_ok,
    pagamentos_erro,
    caminho_saida
):
    total = len(pagamentos_ok) + len(pagamentos_erro)
    total_ok = len(pagamentos_ok)
    total_erro = len(pagamentos_erro)

    valor_ok = sum(p["valor"] for p in pagamentos_ok)
    valor_erro = sum(p["valor"] for p in pagamentos_erro)

    percentual = (total_ok / total * 100) if total else 0

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write(f"EMPRESA: {empresa}\n")
        f.write(f"Data do Processamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")

        f.write("# 📊 RESUMO GERAL\n\n")
        f.write(f"Total de Registros Processados    : {total}\n")
        f.write(f"✅ Pagamentos Efetuados           : {total_ok}\n")
        f.write(f"❌ Pagamentos Não Efetuados       : {total_erro}\n")
        f.write(f"Taxa de Efetivação                : {percentual:.2f}%\n")
        f.write(f"Valor Total Pago                  : R$ {valor_ok:,.2f}\n")
        f.write(f"Valor Total Rejeitado             : R$ {valor_erro:,.2f}\n")
        f.write("\n" + "-"*70 + "\n\n")

        if total_erro > 0:
            f.write("# ❌ OCORRÊNCIAS - PAGAMENTOS NÃO EFETUADOS\n")
            f.write("-"*70 + "\n\n")

            for p in pagamentos_erro:
                f.write(f"Contribuinte : {p['nome']}\n")
                f.write(f"Valor        : R$ {p['valor']:,.2f}\n")
                f.write(f"Motivo       : {p['motivo']}\n")
                f.write("-"*50 + "\n")

        f.write("\n" + "="*70 + "\n")
        f.write("FIM DO RELATÓRIO\n")
        f.write("="*70 + "\n")


# --------------------------------------------------
# MONITORAMENTO
# --------------------------------------------------

def monitorar():
    print(f"[RETORNO] Monitorando pasta: {INPUT_RET}")

    while True:

        arquivos = list(INPUT_RET.glob("*.[Rr][Ee][Tt]"))

        for arquivo in arquivos:

            timestamp = datetime.now().strftime("%H:%M:%S")

            try:
                print(f"\n{'-'*60}")
                print(f"[{timestamp}] NOVO RETORNO DETECTADO")
                print(f"📄 Arquivo: {arquivo.name}")

                # 1️⃣ Leitura do retorno
                resultados = LeitorRetornoSicredi.processar_arquivo(str(arquivo))

                pagamentos_ok = []
                pagamentos_erro = []

                for r in resultados:

                    status = r["status"]

                    # Considera erro qualquer ocorrência diferente de sucesso
                    if (
                        "Inválido" in status
                        or "Fundos" in status
                        or "Cancelado" in status
                        or "Duplicado" in status
                        or "Inválida" in status
                    ):
                        pagamentos_erro.append({
                            "nome": r["nome"],
                            "valor": r["valor"],
                            "motivo": status
                        })
                    else:
                        pagamentos_ok.append({
                            "nome": r["nome"],
                            "valor": r["valor"]
                        })

                # 2️⃣ Gerar relatório
                resumo_path = PROC_RET / f"resumo_{arquivo.stem}.txt"

                gerar_resumo_txt(
                    empresa=EMPRESA_NOME,
                    pagamentos_ok=pagamentos_ok,
                    pagamentos_erro=pagamentos_erro,
                    caminho_saida=str(resumo_path)
                )

                # 3️⃣ Mover RET para processados
                destino = PROC_RET / arquivo.name

                if destino.exists():
                    sufixo = datetime.now().strftime("%Y%m%d_%H%M%S")
                    destino = PROC_RET / f"{arquivo.stem}_{sufixo}{arquivo.suffix}"

                shutil.move(str(arquivo), str(destino))

                print("[RETORNO | SUCESSO] Processado com relatório gerado.")
                print(f"{'-'*60}")

            except Exception as e:
                print(f"\n[RETORNO | ❌ ERRO] Falha no arquivo: {arquivo.name}")
                print(f"Motivo: {str(e)}")

        time.sleep(5)


# --------------------------------------------------
# EXECUÇÃO
# --------------------------------------------------

if __name__ == "__main__":

    INPUT_RET.mkdir(parents=True, exist_ok=True)
    PROC_RET.mkdir(parents=True, exist_ok=True)

    try:
        monitorar()
    except KeyboardInterrupt:
        print("\n[RETORNO] Sistema encerrado pelo usuário.")
    except Exception as e:
        print(f"\n[SISTEMA] Erro fatal: {e}")
