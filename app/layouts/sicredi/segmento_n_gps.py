"""
SEGMENTO_N_GPS.PY
------------------------------------------------------------
Gera Registro Detalhe Segmento N - CNAB240
Banco: Sicredi (748)
Pagamento: GPS

Versão: 2.0.0
Data: 18/02/2026
Status: PRODUÇÃO

Regra crítica:
Linha deve conter exatamente 240 posições.
Valores devem ser calculados com Decimal.
------------------------------------------------------------
"""

from decimal import Decimal, ROUND_HALF_UP
from app.layouts.utils import alfa, num


def _valor_centavos(valor):
    return int(
        (Decimal(str(valor)) * 100)
        .quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )


def gerar_segmento_n_gps(*, lote, sequencial, contribuinte, data_pagamento):

    if "gps" not in contribuinte:
        raise ValueError("Contribuinte sem bloco 'gps'.")

    gps = contribuinte["gps"]

    campos_obrigatorios = [
        "codigo_receita",
        "tipo_identificacao",
        "identificacao",
        "competencia",
        "valor_inss",
        "valor_outras_entidades"
    ]

    for campo in campos_obrigatorios:
        if campo not in gps:
            raise ValueError(f"Campo obrigatório ausente no GPS: {campo}")

    # ─────────────────────────────────────────────
    # DATA PAGAMENTO (DDMMAAAA obrigatório)
    # ─────────────────────────────────────────────
    if not data_pagamento or len(data_pagamento) != 8:
        raise ValueError("Data de pagamento inválida. Esperado DDMMAAAA.")

    dt = data_pagamento

    # ─────────────────────────────────────────────
    # MONTAGEM DA LINHA
    # ─────────────────────────────────────────────

    linha = ""

    # Controle
    linha += num("748", 3)
    linha += num(lote, 4)
    linha += "3"
    linha += num(sequencial, 5)
    linha += "N"
    linha += "000"

    # Favorecido
    linha += alfa("", 20)
    linha += alfa("", 20)
    linha += alfa(contribuinte["nome"], 30)

    # Pagamento
    linha += num(dt, 8)
    linha += num(_valor_centavos(contribuinte["valor_total"]), 15)

    # GPS
    linha += alfa(gps["codigo_receita"], 6)
    linha += num(gps["tipo_identificacao"], 2)
    linha += num(gps["identificacao"], 14)
    linha += num("17", 2)
    linha += num(gps["competencia"], 6)
    linha += num(_valor_centavos(gps["valor_inss"]), 15)
    linha += num(_valor_centavos(gps["valor_outras_entidades"]), 15)
    linha += num(_valor_centavos(gps.get("atualizacao_monetaria", 0)), 15)

    # Complemento
    linha += alfa("", 45)
    linha += alfa("", 10)

    # ─────────────────────────────────────────────
    # VALIDAÇÃO FINAL
    # ─────────────────────────────────────────────
    if len(linha) != 240:
        raise ValueError(
            f"Segmento N inválido: possui {len(linha)} caracteres (esperado 240)."
        )

    return linha
