"""
TRAILER_ARQUIVO.PY
------------------------------------------------------------
Gera Registro Trailer de Arquivo - CNAB240
Banco: Sicredi (748)

Versão: 2.0.0
Data: 18/02/2026
Status: PRODUÇÃO

Regra:
Deve conter exatamente 240 posições.
------------------------------------------------------------
"""

from app.layouts.utils import alfa, num


def gerar_trailer_arquivo(*, qtd_lotes: int, qtd_registros: int) -> str:

    if qtd_lotes <= 0:
        raise ValueError("Trailer Arquivo inválido: qtd_lotes deve ser > 0")

    if qtd_registros <= 0:
        raise ValueError("Trailer Arquivo inválido: qtd_registros deve ser > 0")

    linha = ""

    # Banco
    linha += num("748", 3)

    # Lote
    linha += "9999"

    # Tipo Registro
    linha += "9"

    # Uso exclusivo FEBRABAN
    linha += alfa("", 9)

    # Quantidade de lotes no arquivo
    linha += num(qtd_lotes, 6)

    # Quantidade total de registros no arquivo
    linha += num(qtd_registros, 6)

    # Quantidade de contas para conciliação (não usado)
    linha += num(0, 6)

    # Complemento
    linha += alfa("", 205)

    if len(linha) != 240:
        raise ValueError(
            f"Trailer Arquivo inválido: possui {len(linha)} caracteres (esperado 240)."
        )

    return linha
