"""
HEADER_LOTE_GPS.PY
------------------------------------------------------------
Gera o Registro Header de Lote - CNAB240
Banco: Sicredi (748)
Tipo Registro: 1
Serviço: Pagamento GPS

Versão: 1.1.0
Data: 18/02/2026
Status: PRODUÇÃO

Regra crítica:
Linha deve conter exatamente 240 posições.
------------------------------------------------------------
"""

from app.layouts.utils import alfa, num


def gerar_header_lote_gps(
    *,
    lote: int,
    empresa: dict,
) -> str:

    # ─────────────────────────────────────────────
    # VALIDAÇÕES
    # ─────────────────────────────────────────────
    campos_obrigatorios = [
        "cnpj",
        "convenio",
        "agencia",
        "dv_agencia",
        "conta",
        "dv_conta",
        "razao_social"
    ]

    for campo in campos_obrigatorios:
        if campo not in empresa:
            raise ValueError(f"Campo obrigatório ausente em empresa: {campo}")

    linha = ""

    # ─────────────────────────────────────────────
    # HEADER LOTE
    # ─────────────────────────────────────────────

    linha += num("748", 3)              # Código do Banco
    linha += num(lote, 4)               # Número do Lote
    linha += "1"                        # Tipo de Registro
    linha += "C"                        # Tipo de Operação
    linha += num("22", 2)               # Tipo de Serviço
    linha += num("17", 2)               # Forma de Lançamento
    linha += num("042", 3)              # Versão Layout Lote
    linha += alfa("", 1)                # Uso FEBRABAN
    linha += num("2", 1)                # Tipo de Inscrição
    linha += num(empresa["cnpj"], 14)   # CNPJ Empresa
    linha += alfa(empresa["convenio"], 20)
    linha += num(empresa["agencia"], 5)
    linha += alfa(empresa["dv_agencia"], 1)
    linha += num(empresa["conta"], 12)
    linha += alfa(empresa["dv_conta"], 1)
    linha += alfa("", 1)
    linha += alfa(empresa["razao_social"], 30)
    linha += alfa("", 40)
    linha += alfa("", 30)
    linha += num("", 5)
    linha += alfa("", 15)
    linha += alfa("", 20)
    linha += num("", 5)
    linha += alfa("", 3)
    linha += alfa("", 2)
    linha += alfa("", 8)
    linha += alfa("", 10)

    # ─────────────────────────────────────────────
    # VALIDAÇÃO ESTRUTURAL
    # ─────────────────────────────────────────────
    if len(linha) != 240:
        raise ValueError(
            f"Header de lote inválido: possui {len(linha)} caracteres (esperado 240)."
        )

    return linha
