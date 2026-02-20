import pandas as pd
import os
from pathlib import Path
from app.services.sicredi.gerador_espelho import GeradorEspelhoGPS

# --- CONFIGURAÇÃO PARA O DIA 13/02/2026 ---
NOME_ARQUIVO_CSV = "REMESSA_GPS_20260213_121628_ok.csv" 
NSA_DAQUELE_DIA = 9 
CONVENIO_OFICIAL = "6XDZ"

# Datas Fixas para o Rodapé e Vencimento
DATA_PAGAMENTO_RETROATIVA = "13022026" 
DATA_HORA_EMISSAO_RODAPE = "13/02/2026 09:45:20"

# Caminhos
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "processed" / "remessas" / NOME_ARQUIVO_CSV
OUTPUT_ESPELHOS = BASE_DIR / "output" / "espelhos" / "GPS_RETROATIVO_CORRIGIDO"

def gerar_retroativos():
    if not CSV_PATH.exists():
        print(f"❌ Arquivo nao encontrado em: {CSV_PATH}")
        return

    print(f"📖 Lendo CSV: {NOME_ARQUIVO_CSV}")
    os.makedirs(OUTPUT_ESPELHOS, exist_ok=True)

    # Lê o CSV
    df = pd.read_csv(CSV_PATH, sep=None, engine='python', encoding='utf-8')
    df.columns = [c.strip().lower() for c in df.columns]

    conv_f = lambda v: float(str(v).replace(',', '.')) if pd.notnull(v) else 0.0

    count = 0
    for _, row in df.iterrows():
        try:
            # --- CORREÇÃO DA COMPETÊNCIA (Bug 12/026) ---
            # Remove tudo que não é número
            comp_raw = "".join(filter(str.isdigit, str(row["competencia"])))
            # Garante 6 dígitos (Ex: 12026 vira 012026)
            competencia_limpa = comp_raw.zfill(6) 

            c_data = {
                "nome": str(row["nome_contribuinte"]),
                "valor_total": conv_f(row["valor_total"]),
                "gps": {
                    "codigo_receita": str(row["codigo_receita"]).split('.')[0],
                    "identificacao": str(row["nit"]).split('.')[0],
                    "competencia": competencia_limpa,
                    "valor_inss": conv_f(row["valor_inss"]),
                    "valor_outras_entidades": 0.0,
                    "atualizacao_monetaria": conv_f(row.get("juros", 0)) + conv_f(row.get("multa", 0))
                }
            }
            
            # Chama o gerador
            GeradorEspelhoGPS.gerar(
                contribuinte=c_data, 
                data_pagamento=DATA_PAGAMENTO_RETROATIVA, 
                nsa=NSA_DAQUELE_DIA, 
                convenio=CONVENIO_OFICIAL,
                output_path=OUTPUT_ESPELHOS,
                data_emissao=DATA_HORA_EMISSAO_RODAPE
            )
            count += 1
            print(f"✅ Guia Gerada: {c_data['nome']} - Comp: {competencia_limpa}")
            
        except Exception as e:
            print(f"❌ Erro na linha: {e}")

    print(f"\n🚀 SUCESSO! {count} guias geradas em: {OUTPUT_ESPELHOS}")

if __name__ == "__main__":
    gerar_retroativos()
