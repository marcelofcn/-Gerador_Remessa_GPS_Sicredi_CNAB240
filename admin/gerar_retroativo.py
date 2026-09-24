import pandas as pd
import os
import sys
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================================

# Raiz do projeto:
# /home/house/developer/geraremessa
BASE_DIR = Path(__file__).resolve().parent.parent

# Permite importar o pacote "app" quando o script
# é executado diretamente com:
# python3 admin/gerar_retroativo.py
sys.path.insert(0, str(BASE_DIR))

from app.services.sicredi.gerador_espelho import GeradorEspelhoGPS


# ============================================================
# CONFIGURAÇÃO DO RETROATIVO
# ============================================================

NOME_ARQUIVO_CSV = "REMESSA_GPS_20260812_103822.csv"

NSA_DAQUELE_DIA = 35

CONVENIO_OFICIAL = "6XDZ"


# ============================================================
# DATAS FIXAS
# ============================================================

# Data de pagamento/vencimento da retroativa
DATA_PAGAMENTO_RETROATIVA = "14082026"

# Data/hora que aparecerá no rodapé do espelho
DATA_HORA_EMISSAO_RODAPE = "13/08/2026 08:25:20"


# ============================================================
# CAMINHOS
# ============================================================

# CSV:
# /home/house/developer/geraremessa/processed/remessas/...
CSV_PATH = BASE_DIR / "processed" / "remessas" / NOME_ARQUIVO_CSV

# Saída:
# /home/house/developer/geraremessa/output/espelhos/GPS_RETROATIVO_CORRIGIDO
OUTPUT_ESPELHOS = (
    BASE_DIR
    / "output"
    / "espelhos"
    / "GPS_RETROATIVO_CORRIGIDO"
)


# ============================================================
# FUNÇÃO AUXILIAR PARA VALORES
# ============================================================

def converter_float(valor):
    """
    Converte valores do CSV para float.

    Aceita valores como:
    1234.56
    1234,56

    Valores vazios/NaN retornam 0.0.
    """
    if pd.isnull(valor):
        return 0.0

    texto = str(valor).strip()

    if not texto:
        return 0.0

    return float(texto.replace(",", "."))


# ============================================================
# GERAÇÃO DAS GUIAS
# ============================================================

def gerar_retroativos():

    # --------------------------------------------------------
    # Verifica se o CSV existe
    # --------------------------------------------------------

    if not CSV_PATH.exists():
        print()
        print("❌ ERRO: Arquivo CSV não encontrado!")
        print(f"   Caminho procurado:")
        print(f"   {CSV_PATH}")
        print()
        return

    print()
    print("=" * 70)
    print("GERAÇÃO DE GUIAS RETROATIVAS")
    print("=" * 70)
    print()
    print(f"📁 Projeto:       {BASE_DIR}")
    print(f"📄 CSV:           {CSV_PATH}")
    print(f"📂 Saída:         {OUTPUT_ESPELHOS}")
    print(f"📅 Pagamento:     {DATA_PAGAMENTO_RETROATIVA}")
    print(f"🕐 Emissão:       {DATA_HORA_EMISSAO_RODAPE}")
    print(f"🔢 NSA:            {NSA_DAQUELE_DIA}")
    print(f"🏦 Convênio:       {CONVENIO_OFICIAL}")
    print()

    # --------------------------------------------------------
    # Cria diretório de saída
    # --------------------------------------------------------

    os.makedirs(OUTPUT_ESPELHOS, exist_ok=True)

    # --------------------------------------------------------
    # Lê o CSV
    # --------------------------------------------------------

    print(f"📖 Lendo CSV: {NOME_ARQUIVO_CSV}")

    try:
        df = pd.read_csv(
            CSV_PATH,
            sep=None,
            engine="python",
            encoding="utf-8"
        )
    except Exception as e:
        print()
        print("❌ ERRO ao ler o CSV:")
        print(f"   {e}")
        print()
        return

    # Normaliza nomes das colunas
    df.columns = [c.strip().lower() for c in df.columns]

    print(f"✅ CSV carregado: {len(df)} registros")
    print()

    # --------------------------------------------------------
    # Verifica colunas necessárias
    # --------------------------------------------------------

    colunas_obrigatorias = [
        "nome_contribuinte",
        "valor_total",
        "codigo_receita",
        "nit",
        "competencia",
        "valor_inss",
    ]

    colunas_faltando = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if colunas_faltando:
        print("❌ ERRO: O CSV não possui as colunas obrigatórias:")
        for coluna in colunas_faltando:
            print(f"   - {coluna}")

        print()
        print("Colunas encontradas:")
        for coluna in df.columns:
            print(f"   - {coluna}")

        print()
        return

    # --------------------------------------------------------
    # Geração
    # --------------------------------------------------------

    count = 0
    erros = 0

    for indice, row in df.iterrows():

        try:

            # ------------------------------------------------
            # COMPETÊNCIA
            # ------------------------------------------------

            comp_raw = "".join(
                filter(
                    str.isdigit,
                    str(row["competencia"])
                )
            )

            # Garante 6 dígitos
            #
            # Exemplo:
            # 12026 -> 012026
            #
            competencia_limpa = comp_raw.zfill(6)

            # ------------------------------------------------
            # DADOS DO CONTRIBUINTE
            # ------------------------------------------------

            nome = str(row["nome_contribuinte"]).strip()

            codigo_receita = (
                str(row["codigo_receita"])
                .split(".")[0]
                .strip()
            )

            identificacao = (
                str(row["nit"])
                .split(".")[0]
                .strip()
            )

            # ------------------------------------------------
            # VALORES
            # ------------------------------------------------

            valor_total = converter_float(
                row["valor_total"]
            )

            valor_inss = converter_float(
                row["valor_inss"]
            )

            # Juros
            juros = converter_float(
                row.get("juros", 0)
            )

            # Multa
            multa = converter_float(
                row.get("multa", 0)
            )

            atualizacao_monetaria = juros + multa

            # ------------------------------------------------
            # MONTA ESTRUTURA
            # ------------------------------------------------

            c_data = {
                "nome": nome,

                "valor_total": valor_total,

                "gps": {
                    "codigo_receita": codigo_receita,

                    "identificacao": identificacao,

                    "competencia": competencia_limpa,

                    "valor_inss": valor_inss,

                    "valor_outras_entidades": 0.0,

                    "atualizacao_monetaria": (
                        atualizacao_monetaria
                    ),
                },
            }

            # ------------------------------------------------
            # GERA O ESPELHO
            # ------------------------------------------------

            GeradorEspelhoGPS.gerar(
                contribuinte=c_data,

                data_pagamento=DATA_PAGAMENTO_RETROATIVA,

                nsa=NSA_DAQUELE_DIA,

                convenio=CONVENIO_OFICIAL,

                output_path=OUTPUT_ESPELHOS,

                data_emissao=DATA_HORA_EMISSAO_RODAPE,
            )

            count += 1

            print(
                f"✅ Guia {count}: "
                f"{nome} - "
                f"Comp: {competencia_limpa}"
            )

        except Exception as e:

            erros += 1

            print(
                f"❌ Erro na linha "
                f"{indice + 1}: {e}"
            )

    # --------------------------------------------------------
    # RESULTADO FINAL
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PROCESSAMENTO FINALIZADO")
    print("=" * 70)
    print()
    print(f"✅ Guias geradas: {count}")
    print(f"❌ Erros:         {erros}")
    print()
    print(f"📂 Diretório:")
    print(f"   {OUTPUT_ESPELHOS}")
    print()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    gerar_retroativos()
