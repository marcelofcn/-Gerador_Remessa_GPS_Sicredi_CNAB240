#4️⃣ trailer_lote.py — Trailer do Lote
#📌 O que ele faz
#Fecha o lote informando:
#Quantidade de registros no lote
#Valor total do lote (em centavos)

#📌 Por que existe
#O banco:
#Soma tudo
#Confere se bate com os Segmentos N
#Se não bater → rejeição

#📌 Boa prática aplicada
#Você zerou corretamente os campos não usados conforme o layout Sicredi.

from app.layouts.utils import num, alfa

def gerar_trailer_lote_gps(*, lote, qtd_registros, valor_total_centavos):
    linha = ""
    linha += num("748", 3) + num(lote, 4) + "5" + alfa("", 9)
    linha += num(qtd_registros, 6) + num(valor_total_centavos, 18)
    linha += num(0, 18) # OS 18 ZEROS DA CRÍTICA LARANJA
    linha += alfa("", 181)
    return linha
