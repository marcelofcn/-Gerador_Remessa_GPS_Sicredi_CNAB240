"""
GERADOR DE ESPELHO GPS
------------------------------------------------------------
Projeto: Sistema de Remessa CNAB GPS - SICREDI
Data de Atualização: 2026-08-18
Responsabilidades:
- Gerar espelho da Guia GPS em PDF
- Ler CSV de remessa
- Permitir geração normal ou retroativa
- Preservar os dados oficiais do lote quando informados

Uso normal:
    python3 gerador_espelho.py arquivo.csv --nsa 10

Uso retroativo:
    python3 gerador_espelho.py arquivo.csv \
        --nsa 9 \
        --convenio 6XDZ \
        --data-pagamento 13022026 \
        --data-emissao "13/02/2026 09:45:20"

Saída padrão:
    output/espelhos/
"""

import os
import sys
import argparse
import unicodedata
from pathlib import Path
from datetime import datetime

import pandas as pd
from fpdf import FPDF


# ============================================================
# GERADOR PDF
# ============================================================

class GeradorEspelhoGPS:

    @staticmethod
    def remover_acentos(texto):
        """Remove acentos e caracteres especiais para evitar erro no PDF."""
        if not texto:
            return ""

        nfkd = unicodedata.normalize("NFKD", str(texto))

        return "".join(
            c for c in nfkd
            if not unicodedata.combining(c)
        )

    @staticmethod
    def gerar(
        contribuinte,
        data_pagamento,
        nsa,
        convenio,
        output_path,
        data_emissao=None
    ):
        """Gera um espelho em formato de guia oficial GPS."""

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=8)

        # ----------------------------------------------------
        # DATA DE EMISSÃO
        # ----------------------------------------------------

        if not data_emissao:
            data_emissao = datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            )

        # ----------------------------------------------------
        # CONFIGURAÇÃO DE COORDENADAS
        # ----------------------------------------------------

        x_inicio = 10
        y_inicio = 15

        col1_w = 120
        col2_w = 70
        h_row = 12

        # ----------------------------------------------------
        # 1. CABEÇALHO
        # ----------------------------------------------------

        pdf.rect(
            x_inicio,
            y_inicio,
            col1_w,
            h_row * 2
        )

        pdf.set_font("Arial", "B", 9)

        pdf.set_xy(
            x_inicio,
            y_inicio + 2
        )

        pdf.multi_cell(
            col1_w,
            4,
            txt=(
                "MINISTERIO DA PREVIDENCIA SOCIAL - MPS\n"
                "INSTITUTO NACIONAL DO SEGURO SOCIAL - INSS\n"
                "GUIA DA PREVIDENCIA SOCIAL - GPS"
            ),
            align="C"
        )

        # ----------------------------------------------------
        # COLUNA DIREITA
        # ----------------------------------------------------

        # 3. Código de pagamento

        pdf.rect(
            x_inicio + col1_w,
            y_inicio,
            col2_w,
            h_row
        )

        pdf.set_font("Arial", "B", 7)

        pdf.text(
            x_inicio + col1_w + 1,
            y_inicio + 3,
            "3. CODIGO DE PAGAMENTO"
        )

        pdf.set_font("Arial", "", 10)

        pdf.text(
            x_inicio + col1_w + 25,
            y_inicio + 8,
            str(contribuinte["gps"]["codigo_receita"])
        )

        # ----------------------------------------------------
        # 4. COMPETÊNCIA
        # ----------------------------------------------------

        pdf.rect(
            x_inicio + col1_w,
            y_inicio + h_row,
            col2_w,
            h_row
        )

        pdf.set_font("Arial", "B", 7)

        pdf.text(
            x_inicio + col1_w + 1,
            y_inicio + h_row + 3,
            "4. COMPETENCIA (MM/AAAA)"
        )

        pdf.set_font("Arial", "", 10)

        comp = str(
            contribuinte["gps"]["competencia"]
        ).zfill(6)

        pdf.text(
            x_inicio + col1_w + 25,
            y_inicio + h_row + 8,
            f"{comp[:2]}/{comp[2:]}"
        )

        # ----------------------------------------------------
        # 5. IDENTIFICADOR
        # ----------------------------------------------------

        pdf.rect(
            x_inicio + col1_w,
            y_inicio + (h_row * 2),
            col2_w,
            h_row
        )

        pdf.set_font("Arial", "B", 7)

        pdf.text(
            x_inicio + col1_w + 1,
            y_inicio + (h_row * 2) + 3,
            "5. IDENTIFICADOR"
        )

        pdf.set_font("Arial", "", 10)

        pdf.text(
            x_inicio + col1_w + 15,
            y_inicio + (h_row * 2) + 8,
            str(contribuinte["gps"]["identificacao"])
        )

        # ----------------------------------------------------
        # CAMPOS DE VALORES
        # ----------------------------------------------------

        labels_valores = [
            (
                "6. VALOR DO INSS",
                contribuinte["gps"]["valor_inss"]
            ),
            ("7.", 0.0),
            ("8.", 0.0),
            (
                "9. VALOR OUTRAS ENTIDADES",
                contribuinte["gps"]["valor_outras_entidades"]
            ),
            (
                "10. ATM, MULTA E JUROS",
                contribuinte["gps"]["atualizacao_monetaria"]
            ),
            (
                "11. TOTAL",
                contribuinte["valor_total"]
            )
        ]

        current_y = y_inicio + (h_row * 3)

        for label, valor in labels_valores:

            pdf.rect(
                x_inicio + col1_w,
                current_y,
                col2_w,
                h_row
            )

            pdf.set_font("Arial", "B", 7)

            pdf.text(
                x_inicio + col1_w + 1,
                current_y + 3,
                label
            )

            if float(valor) > 0:

                pdf.set_font("Arial", "", 10)

                pdf.set_xy(
                    x_inicio + col1_w,
                    current_y + 5
                )

                pdf.cell(
                    col2_w - 2,
                    5,
                    txt=f"{float(valor):,.2f}",
                    align="R"
                )

            current_y += h_row

        # ----------------------------------------------------
        # COLUNA ESQUERDA
        # ----------------------------------------------------

        # 1. Nome

        y_nome = y_inicio + (h_row * 2)

        pdf.rect(
            x_inicio,
            y_nome,
            col1_w,
            h_row * 3
        )

        pdf.set_font("Arial", "B", 7)

        pdf.text(
            x_inicio + 1,
            y_nome + 3,
            "1. NOME OU RAZAO SOCIAL / FONE / ENDERECO:"
        )

        pdf.set_font("Arial", "", 9)

        nome_limpo = GeradorEspelhoGPS.remover_acentos(
            contribuinte["nome"]
        )

        pdf.set_xy(
            x_inicio + 1,
            y_nome + 5
        )

        pdf.multi_cell(
            col1_w - 2,
            4,
            txt=nome_limpo
        )

        # ----------------------------------------------------
        # 2. VENCIMENTO
        # ----------------------------------------------------

        y_venc = y_inicio + (h_row * 5)

        pdf.rect(
            x_inicio,
            y_venc,
            col1_w,
            h_row
        )

        pdf.set_font("Arial", "B", 7)

        pdf.text(
            x_inicio + 1,
            y_venc + 3,
            "2. VENCIMENTO (Uso do INSS)"
        )

        pdf.set_font("Arial", "", 10)

        dt = str(data_pagamento)

        if len(dt) == 8:
            data_fmt = (
                f"{dt[:2]}/{dt[2:4]}/{dt[4:]}"
            )
        else:
            data_fmt = dt

        pdf.text(
            x_inicio + 10,
            y_venc + 8,
            data_fmt
        )

        # ----------------------------------------------------
        # QUADRO ATENÇÃO
        # ----------------------------------------------------

        y_atencao = y_inicio + (h_row * 6)

        pdf.rect(
            x_inicio,
            y_atencao,
            col1_w,
            h_row * 3
        )

        pdf.set_font("Arial", "B", 6)

        pdf.set_xy(
            x_inicio + 1,
            y_atencao + 2
        )

        txt_atencao = (
            "ATENCAO: E vedada a utilizacao de GPS para "
            "recolhimento de receita de valor inferior "
            "ao estipulado em Resolucao publicada pelo INSS. "
            "A receita que resultar valor inferior devera "
            "ser adicionada a contribuicao ou importancia "
            "correspondente nos meses subsequentes."
        )

        pdf.multi_cell(
            col1_w - 2,
            3,
            txt=txt_atencao
        )

        # ----------------------------------------------------
        # 12. AUTENTICAÇÃO BANCÁRIA
        # ----------------------------------------------------

        y_final = y_inicio + (h_row * 9)

        pdf.rect(
            x_inicio,
            y_final,
            col1_w + col2_w,
            h_row * 2
        )

        pdf.set_font("Arial", "B", 7)

        pdf.text(
            x_inicio + 1,
            y_final + 3,
            "12. AUTENTICACAO BANCARIA"
        )

        # ----------------------------------------------------
        # RODAPÉ TÉCNICO
        # ----------------------------------------------------

        pdf.set_font("Arial", "I", 7)

        info_tecnica = (
            "Remessa pagamentos arquivo de remessa cnab240 - "
            f"Cooperativa Sicredi - Convenio: {convenio} - "
            f"NSA: {int(nsa):06d}"
        )

        pdf.text(
            x_inicio + 2,
            y_final + 14,
            info_tecnica
        )

        pdf.set_font("Arial", "I", 6)

        pdf.text(
            x_inicio + 2,
            y_final + 19,
            f"Espelho gerado em {data_emissao} - Uso Interno."
        )

        # ----------------------------------------------------
        # ARQUIVO
        # ----------------------------------------------------

        os.makedirs(output_path, exist_ok=True)

        nome_pdf = (
            f"GUIA_GPS_"
            f"{contribuinte['gps']['identificacao']}_"
            f"{comp}.pdf"
        )

        caminho_final = os.path.join(
            output_path,
            nome_pdf
        )

        pdf.output(caminho_final)

        return caminho_final


# ============================================================
# UTILITÁRIOS CSV
# ============================================================

def converter_valor(valor):
    """Converte valor monetário do CSV para float."""

    if pd.isna(valor):
        return 0.0

    texto = str(valor).strip().replace(",", ".")

    if not texto:
        return 0.0

    return float(texto)


def normalizar_competencia(valor):
    """
    Normaliza competência para MMYYYY.

    Exemplos:
        072026 -> 072026
        07/2026 -> 072026
        12026  -> 012026
    """

    numeros = "".join(
        filter(str.isdigit, str(valor))
    )

    return numeros.zfill(6)


def normalizar_data_pagamento(valor):
    """
    Converte datas comuns do CSV para DDMMAAAA.

    Exemplo:
        2026-08-10 -> 10082026
    """

    texto = str(valor).strip()

    formatos = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d%m%Y",
    ]

    for formato in formatos:

        try:

            return datetime.strptime(
                texto,
                formato
            ).strftime("%d%m%Y")

        except ValueError:
            continue

    raise ValueError(
        f"Data de pagamento inválida: {valor}"
    )


# ============================================================
# PROCESSAMENTO DO CSV
# ============================================================

def gerar_espelhos_csv(
    csv_path,
    nsa,
    convenio="6XDZ",
    data_pagamento=None,
    data_emissao=None,
    output_path=None
):
    """
    Lê um CSV de remessa e gera uma guia GPS para cada linha.
    """

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV não encontrado: {csv_path}"
        )

    base_dir = Path(__file__).resolve().parents[3]

    if output_path is None:
        output_path = (
            base_dir /
            "output" /
            "espelhos"
        )

    output_path = Path(output_path)

    print("=" * 70)
    print("GERADOR DE ESPELHOS GPS")
    print("=" * 70)
    print(f"CSV       : {csv_path}")
    print(f"NSA       : {int(nsa):06d}")
    print(f"Convênio  : {convenio}")
    print(f"Saída     : {output_path}")
    print("=" * 70)

    # --------------------------------------------------------
    # LEITURA
    # --------------------------------------------------------

    df = pd.read_csv(
        csv_path,
        sep=None,
        engine="python",
        encoding="utf-8"
    )

    df.columns = [
        str(c).strip().lower()
        for c in df.columns
    ]

    campos_obrigatorios = [
        "nome_contribuinte",
        "nit",
        "codigo_receita",
        "competencia",
        "valor_inss",
        "valor_total",
        "data_pagamento"
    ]

    faltantes = [
        campo
        for campo in campos_obrigatorios
        if campo not in df.columns
    ]

    if faltantes:
        raise ValueError(
            "CSV não possui os campos obrigatórios: "
            + ", ".join(faltantes)
        )

    # --------------------------------------------------------
    # DATA DO LOTE
    # --------------------------------------------------------

    if data_pagamento:

        data_pagamento_final = normalizar_data_pagamento(
            data_pagamento
        )

    else:

        data_pagamento_final = normalizar_data_pagamento(
            df["data_pagamento"].iloc[0]
        )

    # --------------------------------------------------------
    # DATA DE EMISSÃO
    # --------------------------------------------------------

    if not data_emissao:

        data_emissao = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )

    # --------------------------------------------------------
    # CRIA SAÍDA
    # --------------------------------------------------------

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # PROCESSAMENTO
    # --------------------------------------------------------

    total = len(df)
    sucessos = 0
    erros = 0

    print(f"📄 Registros encontrados: {total}")
    print(
        f"📅 Data de pagamento: "
        f"{data_pagamento_final[:2]}/"
        f"{data_pagamento_final[2:4]}/"
        f"{data_pagamento_final[4:]}"
    )
    print()

    for indice, row in df.iterrows():

        try:

            competencia = normalizar_competencia(
                row["competencia"]
            )

            contribuinte = {
                "nome": str(
                    row["nome_contribuinte"]
                ).strip(),

                "valor_total": converter_valor(
                    row["valor_total"]
                ),

                "gps": {
                    "codigo_receita": str(
                        row["codigo_receita"]
                    ).split(".")[0],

                    "tipo_identificacao": 2,

                    "identificacao": str(
                        row["nit"]
                    ).split(".")[0],

                    "competencia": competencia,

                    "valor_inss": converter_valor(
                        row["valor_inss"]
                    ),

                    "valor_outras_entidades": 0.0,

                    "atualizacao_monetaria": (
                        converter_valor(
                            row.get("juros", 0)
                        )
                        +
                        converter_valor(
                            row.get("multa", 0)
                        )
                    )
                }
            }

            caminho = GeradorEspelhoGPS.gerar(
                contribuinte=contribuinte,
                data_pagamento=data_pagamento_final,
                nsa=nsa,
                convenio=convenio,
                output_path=output_path,
                data_emissao=data_emissao
            )

            sucessos += 1

            print(
                f"✅ [{indice + 1}/{total}] "
                f"{contribuinte['nome']} "
                f"→ {Path(caminho).name}"
            )

        except Exception as e:

            erros += 1

            print(
                f"❌ [{indice + 1}/{total}] "
                f"Erro: {e}"
            )

    # --------------------------------------------------------
    # RESUMO
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PROCESSAMENTO CONCLUÍDO")
    print("=" * 70)
    print(f"Total      : {total}")
    print(f"Sucesso    : {sucessos}")
    print(f"Erros      : {erros}")
    print(f"Saída      : {output_path}")
    print("=" * 70)

    return sucessos, erros


# ============================================================
# ARGUMENTOS
# ============================================================

def criar_parser():

    parser = argparse.ArgumentParser(
        description=(
            "Gera espelhos GPS a partir de um CSV de remessa."
        )
    )

    parser.add_argument(
        "csv",
        help="Caminho do arquivo CSV de remessa."
    )

    parser.add_argument(
        "--nsa",
        required=True,
        type=int,
        help="NSA da remessa."
    )

    parser.add_argument(
        "--convenio",
        default="6XDZ",
        help="Convênio Sicredi. Padrão: 6XDZ"
    )

    parser.add_argument(
        "--data-pagamento",
        help=(
            "Data de pagamento a utilizar no lote. "
            "Ex.: 13022026 ou 13/02/2026. "
            "Se omitida, usa a primeira data do CSV."
        )
    )

    parser.add_argument(
        "--data-emissao",
        help=(
            "Data/hora da emissão do espelho. "
            "Ex.: '13/02/2026 09:45:20'. "
            "Se omitida, usa a data/hora atual."
        )
    )

    parser.add_argument(
        "--output",
        help=(
            "Pasta de saída dos espelhos. "
            "Padrão: output/espelhos/"
        )
    )

    return parser


# ============================================================
# MAIN
# ============================================================

def main():

    parser = criar_parser()

    args = parser.parse_args()

    gerar_espelhos_csv(
        csv_path=args.csv,
        nsa=args.nsa,
        convenio=args.convenio,
        data_pagamento=args.data_pagamento,
        data_emissao=args.data_emissao,
        output_path=args.output
    )


if __name__ == "__main__":
    main()