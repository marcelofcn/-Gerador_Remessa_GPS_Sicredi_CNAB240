from app.layouts.utils import alfa, num

def gerar_header_arquivo_sicredi(
    *,
    empresa: dict,
    data_geracao: str,
    hora_geracao: str,
    sequencial: int  # Este é o NSA que o banco pediu
) -> str:
    # Lógica segura de data (DDMMAAAA)
    s = "".join(filter(str.isdigit, data_geracao))
    if len(s) == 8 and s[:4].startswith("20") and not s[4:].startswith("20"):
        dt = f"{s[6:8]}{s[4:6]}{s[0:4]}"
    else:
        dt = s

    linha = ""
    linha += num("748", 3)            # 001-003: Banco
    linha += "0000"                   # 004-007: Lote
    linha += "0"                      # 008: Registro
    linha += alfa("", 9)              # 009-017: CNAB
    linha += num("2", 1)              # 018: Inscrição
    linha += num(empresa["cnpj"], 14) # 019-032: CNPJ
    linha += alfa(empresa["convenio"], 20) # 033-052: Convênio
    linha += num(empresa["agencia"], 5)    # 053-057: Agência
    linha += alfa(empresa["dv_agencia"], 1) # 058: DV Agência
    linha += num(empresa["conta"], 12)     # 059-070: Conta
    linha += alfa(empresa["dv_conta"], 1)  # 071: DV Conta
    linha += alfa(" ", 1)                  # 072: DV Ag/Conta
    linha += alfa(empresa["razao_social"], 30) # 073-102
    linha += alfa("SICREDI", 30)           # 103-132
    linha += alfa("", 10)                  # 133-142
    linha += "1"                           # 143: Remessa
    linha += num(dt, 8)                    # 144-151: Data
    linha += num(hora_geracao, 6)          # 152-157: Hora
    
    # --- NSA: POSIÇÃO 158 A 163 ---
    linha += num(sequencial, 6)            # <--- NSA (Obrigatório Produção)
    
    linha += num("082", 3)                 # 164-166: Versão
    linha += num("01600", 5)               # 167-171: Densidade
    linha += alfa("", 20)                  # 172-191
    linha += alfa("", 20)                  # 192-211
    linha += alfa("", 29)                  # 212-240

    return linha
