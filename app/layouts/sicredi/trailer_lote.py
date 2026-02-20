"""
TRAILER_LOTE.PY
------------------------------------------------------------
Gera Registro Trailer de Lote - CNAB240
Banco: Sicredi (748)
Pagamento: GPS

Versão: 2.0.0
Data: 18/02/2026
Status: PRODUÇÃO

Regra:
Linha deve conter exatamente 240 posições.
------------------------------------------------------------
"""

from app.layouts.utils import num, alfa


def gerar_trailer_lote_gps(
    *,
    lote: int,
    qtd_registros: int,
    valor_total_centavos: int
) -> str:

    if lote <= 0:
        raise ValueError("Trailer Lote inválido: lote deve ser > 0")

    if qtd_registros <= 0:
        raise ValueError("Trailer Lote inválido: qtd_registros deve ser > 0")

    if valor_total_centavos < 0:
        raise ValueError("Trailer Lote inválido: valor_total_centavos negativo")

    linha = ""

    # Banco
    linha += num("748", 3)

    # Número do lote
    linha += num(lote, 4)

    # Tipo de registro
    linha += "5"

    # Uso exclusivo FEBRABAN
    linha += alfa("", 9)

    # Quantidade de registros no lote
    linha += num(qtd_registros, 6)

    # Somatória dos valores do lote
    linha += num(valor_total_centavos, 18)

    # Quantidade de moedas (não utilizado)
    linha += num(0, 18)

    # Complemento
    linha += alfa("", 181)

    if len(linha) != 240:
        raise ValueError(
            f"Trailer Lote inválido: possui {len(linha)} caracteres (esperado 240)."
        )

    return linha
