#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from pathlib import Path
import pdfplumber
from PyPDF2 import PdfReader

def extrair_dados_gps_pagamento(caminho_pdf):
    """
    Extrai NIT, competência, data e valor do comprovante de pagamento GPS.
    """
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto = ""
            for pagina in pdf.pages:
                texto += pagina.extract_text() + "\n"

        # NIT / Identificador
        nit_match = re.search(r"Identificador\s*:\s*(\d+)", texto, re.I)
        nit = nit_match.group(1) if nit_match else "SEM_NIT"

        # Competência
        comp_match = re.search(r"Competência\s*:\s*(\d{2}/\d{4})", texto, re.I)
        competencia = comp_match.group(1).replace("/", "") if comp_match else "SEM_COMP"

        # Data do pagamento
        data_match = re.search(r"Data do Pagamento\s*:\s*(\d{2}/\d{2}/\d{4})", texto, re.I)
        data = ""
        if data_match:
            dia, mes, ano = data_match.group(1).split("/")
            meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun',
                    'jul', 'ago', 'set', 'out', 'nov', 'dez']
            data = f"{dia}_{meses[int(mes)-1]}"

        # Valor total
        valor_match = re.search(r"Total\s*\(R\$.*\)\s*:\s*([\d.,]+)", texto, re.I)
        valor = valor_match.group(1).replace('.', '').replace(',', '.') if valor_match else "0.00"

        return nit, competencia, data, valor

    except Exception as e:
        print(f"Erro ao processar {caminho_pdf}: {e}")
        return "SEM_NIT", "SEM_COMP", "", "0.00"


def renomear_gps_na_pasta(pasta="."):
    pasta_path = Path(pasta)
    arquivos_pdf = [f for f in pasta_path.iterdir() if f.suffix.lower() == ".pdf"]

    if not arquivos_pdf:
        print("Nenhum arquivo PDF encontrado na pasta.")
        return

    for arquivo in arquivos_pdf:
        nome_original = arquivo.name
        # Detectar se é guia ou comprovante
        if "GUIA" in nome_original.upper():
            # Extração básica da guia
            # Se já estiver no formato, pula
            if re.match(r"GUIA_GPS_\d+_\d{6}\.pdf", nome_original):
                print(f"⏭️  Pulando guia já renomeada: {nome_original}")
                continue
            # Tentar extrair NIT e competência do nome antigo
            nit_match = re.search(r"(\d{11})", nome_original)
            comp_match = re.search(r"(\d{6})", nome_original)
            nit = nit_match.group(1) if nit_match else "SEM_NIT"
            competencia = comp_match.group(1) if comp_match else "SEM_COMP"
            novo_nome = f"GUIA_GPS_{nit}_{competencia}.pdf"
        else:
            # Comprovante GPS
            nit, competencia, data, valor = extrair_dados_gps_pagamento(str(arquivo))
            novo_nome = f"PAGAMENTO_GPS_{nit}_{competencia}_{data}_{valor}.pdf"

        novo_caminho = arquivo.parent / novo_nome
        contador = 1
        # Evitar sobrescrever
        while novo_caminho.exists():
            base = novo_nome.replace(".pdf", "")
            novo_caminho = arquivo.parent / f"{base}_{contador}.pdf"
            contador += 1

        arquivo.rename(novo_caminho)
        print(f"✅ Renomeado: {nome_original} -> {novo_nome}")


def main():
    import sys
    if len(sys.argv) > 1:
        pasta = sys.argv[1]
    else:
        pasta = "."

    print(f"📂 Renomeando arquivos na pasta: {pasta}")
    renomear_gps_na_pasta(pasta)


if __name__ == "__main__":
    main()
