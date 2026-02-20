from pathlib import Path
from pypdf import PdfWriter, PdfReader

PASTA_GUIAS = Path("output/espelhos")
PASTA_COMPROVANTES = Path("output/comprovantes")
PASTA_FINAL = Path("output/guias_completas")

PASTA_FINAL.mkdir(parents=True, exist_ok=True)

def juntar_pdfs():
    for guia in PASTA_GUIAS.glob("GUIA_GPS_*.pdf"):
        
        nome_base = guia.stem.replace("GUIA_GPS_", "")
        comprovantes = list(PASTA_COMPROVANTES.glob(f"PAGAMENTO_GPS_{nome_base}_*.pdf"))
        
        if not comprovantes:
            print(f"⚠️ Comprovante não encontrado para {nome_base}")
            continue
        
        comprovante = comprovantes[0]

        writer = PdfWriter()

        # Guia
        reader_guia = PdfReader(str(guia))
        for page in reader_guia.pages:
            writer.add_page(page)

        # Comprovante
        reader_comprovante = PdfReader(str(comprovante))
        for page in reader_comprovante.pages:
            writer.add_page(page)

        arquivo_final = PASTA_FINAL / f"GUIA_GPS_{nome_base}_COMPLETO.pdf"
        
        with open(arquivo_final, "wb") as f:
            writer.write(f)

        print(f"✅ Gerado: {arquivo_final.name}")

if __name__ == "__main__":
    juntar_pdfs()
