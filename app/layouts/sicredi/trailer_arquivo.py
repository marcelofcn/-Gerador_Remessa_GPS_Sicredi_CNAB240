#5️⃣ trailer_arquivo.py — Trailer do Arquivo
#📌 O que ele faz
#Fecha o arquivo inteiro.

#📌 Informa
#Quantidade de lotes
#Quantidade total de registros (header + lote + segmentos + trailers)

#📌 Regra mental
#“Header abre, Trailer fecha.
#Sem trailer, o banco ignora tudo.”


from app.layouts.utils import alfa, num

def gerar_trailer_arquivo(qtd_lotes, qtd_registros):
    linha = ""
    linha += num("748", 3) + "9999" + "9" + alfa("", 9)
    linha += num(qtd_lotes, 6) + num(qtd_registros, 6)
    linha += num(0, 6) # OS 6 ZEROS DO EXEMPLO DO BANCO
    linha += alfa("", 205)
    return linha
