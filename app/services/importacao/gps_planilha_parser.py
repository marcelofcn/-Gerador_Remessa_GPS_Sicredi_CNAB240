from decimal import Decimal
from typing import Dict, List
from datetime import datetime
import pandas as pd


class ErroPlanilhaGPS(Exception):
    pass


def parse_planilha_gps(
    caminho_arquivo: str,
    *,
    cnpj_empresa: str,
    razao_social: str
) -> Dict:
    """
    Lê planilha GPS preenchida pelo RH e retorna dados
    estruturados para geração de CNAB 240 Sicredi.
    """

    try:
        df = pd.read_excel(caminho_arquivo, sheet_name="GPS")
    except Exception as e:
        raise ErroPlanilhaGPS(f"Erro ao ler planilha GPS: {e}")

    colunas_esperadas = [
        "nome_contribuinte",
        "nit",
        "codigo_receita",
        "competencia",
        "valor_inss",
        "juros",
        "multa",
        "valor_total",
        "data_pagamento",
    ]

    if list(df.columns) != colunas_esperadas:
        raise ErroPlanilhaGPS(
            f"Colunas inválidas. Esperado exatamente: {colunas_esperadas}"
        )

    # ─────────────────────────────────────────────
    # Regra CNAB: uma única data de pagamento
    # ─────────────────────────────────────────────
    datas_pagamento = df["data_pagamento"].astype(str).unique()
    if len(datas_pagamento) != 1:
        raise ErroPlanilhaGPS(
            "A planilha deve conter apenas UMA data de pagamento."
        )

    data_pagamento = _formatar_data_pagamento(datas_pagamento[0])

    contribuintes: List[Dict] = []

    for _, row in df.iterrows():
        juros = Decimal(str(row["juros"]))
        multa = Decimal(str(row["multa"]))

        contribuintes.append({
            "nome": str(row["nome_contribuinte"]).strip(),
            "valor_total": Decimal(str(row["valor_total"])),
            "gps": {
                "codigo_receita": str(row["codigo_receita"]).strip(),
                "tipo_identificacao": "02",   # 02 = NIT (padrão Sicredi)
                "identificacao": str(row["nit"]).strip(),
                "codigo_tributo": "17",       # GPS
                "competencia": _formatar_competencia(row["competencia"]),
                "valor_inss": Decimal(str(row["valor_inss"])),
                "valor_outras_entidades": Decimal("0.00"),
                "atualizacao_monetaria": juros + multa,
            }
        })

    return {
        "empresa": {
            "cnpj": cnpj_empresa,
            "razao_social": razao_social,
        },
        "contribuintes": contribuintes,
        "data_pagamento": data_pagamento,
    }


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _formatar_competencia(valor) -> str:
    """
    Retorna MMYYYY
    """
    valor = str(valor).strip()
    numeros = "".join(c for c in valor if c.isdigit())

    if len(numeros) == 5:
        numeros = "0" + numeros

    if len(numeros) != 6:
        raise ErroPlanilhaGPS(f"Competência inválida: {valor}")

    mes = int(numeros[:2])
    ano = int(numeros[2:])

    if not 1 <= mes <= 12:
        raise ErroPlanilhaGPS(f"Mês inválido: {valor}")

    return numeros


def _formatar_data_pagamento(valor) -> str:
    """
    Retorna DDMMAAAA (exigido pelo Sicredi no Segmento N)
    """
    valor = str(valor).strip()

    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(valor, fmt).strftime("%d%m%Y")
        except ValueError:
            pass

    raise ErroPlanilhaGPS(f"Data inválida: {valor}")
