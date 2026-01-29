#3️⃣ segmento_n_gps.py — Segmento N (GPS)
#📌 O que ele faz
#Gera o registro tipo 3 – Segmento N, que é onde mora o dinheiro 💰.

#📌 Aqui está o coração do sistema
#Cada contribuinte da planilha vira 1 Segmento N.

#📌 Campos críticos
#Nome do contribuinte
#Data de pagamento
#Valor total
#Dados GPS:
#Código da receita
#NIT
#Competência
#INSS
#Juros / multa

#📌 Detalhe extremamente importante
#Você fez corretamente:
#int(round(valor * 100))
#➡ CNAB sempre trabalha em centavos, sem vírgula.

#📌 Regra mental
#“Se o Segmento N estiver certo, o banco paga.
#Se estiver errado, o banco rejeita ou paga errado.”

from app.layouts.utils import alfa, num

def gerar_segmento_n_gps(*, lote, sequencial, contribuinte, data_pagamento):
    gps = contribuinte["gps"]
    s = "".join(filter(str.isdigit, data_pagamento))
    dt = f"{s[6:8]}{s[4:6]}{s[0:4]}" if (len(s) == 8 and s[:4].startswith("20") and not s[4:].startswith("20")) else s
    
    linha = ""
    linha += num("748", 3) + num(lote, 4) + "3" + num(sequencial, 5) + "N" + "000"
    linha += alfa("", 20) + alfa("", 20) + alfa(contribuinte["nome"], 30)
    linha += num(dt, 8) + num(int(round(contribuinte["valor_total"] * 100)), 15)
    
    # Campos GPS - Alinhamento Crítico
    linha += alfa(gps["codigo_receita"], 6)  # 4 digitos + 2 espaços
    linha += num(gps["tipo_identificacao"], 2)
    linha += num(gps["identificacao"], 14)
    linha += num("17", 2)
    linha += num(gps["competencia"], 6)
    linha += num(int(round(gps["valor_inss"] * 100)), 15)
    linha += num(int(round(gps["valor_outras_entidades"] * 100)), 15)
    linha += num(int(round(gps.get("atualizacao_monetaria", 0) * 100)), 15)
    
    linha += alfa("", 45) + alfa("", 10)
    return linha
