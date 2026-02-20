"""
GPS_CNAB_BUILDER.PY
------------------------------------------------------------
Construtor oficial do arquivo CNAB240 - Pagamento GPS
Banco: Sicredi
Layout: CNAB 240 posições fixas

Versão: 2.0.0
Data: 18/02/2026 17:10
Status: PRODUÇÃO

Responsabilidades:
- Montar Header de Arquivo
- Montar Header de Lote
- Gerar Segmentos N (um por contribuinte)
- Calcular total financeiro em centavos (Decimal)
- Gerar Trailer de Lote
- Gerar Trailer de Arquivo
- Validar integridade estrutural (240 colunas)

Regra crítica:
Nenhuma linha pode ter tamanho diferente de 240.
------------------------------------------------------------
"""

from decimal import Decimal, ROUND_HALF_UP

from app.layouts.sicredi.header_arquivo import gerar_header_arquivo_sicredi
from app.layouts.sicredi.header_lote_gps import gerar_header_lote_gps
from app.layouts.sicredi.segmento_n_gps import gerar_segmento_n_gps
from app.layouts.sicredi.trailer_lote import gerar_trailer_lote_gps
from app.layouts.sicredi.trailer_arquivo import gerar_trailer_arquivo


def gerar_cnab_gps_sicredi(
    *,
    empresa: dict,
    contribuintes: list,
    data_pagamento: str,
    data_geracao: str,
    hora_geracao: str = "000000",
    nsa: int = 1
) -> str:
    """
    Constrói o arquivo CNAB240 Sicredi para pagamento de GPS.
    Retorna string final pronta para gravação em arquivo .REM
    """

    # ─────────────────────────────────────────────
    # VALIDAÇÕES BÁSICAS DE SEGURANÇA
    # ─────────────────────────────────────────────

    if not empresa:
        raise ValueError("Dados da empresa não informados.")

    if not contribuintes:
        raise ValueError("Lista de contribuintes vazia.")

    if not data_pagamento or len(data_pagamento) != 8:
        raise ValueError("Data de pagamento inválida. Formato esperado: DDMMAAAA.")

    linhas = []
    lote_servico = 1

    # ─────────────────────────────────────────────
    # HEADER DE ARQUIVO
    # ─────────────────────────────────────────────
    linhas.append(
        gerar_header_arquivo_sicredi(
            empresa=empresa,
            data_geracao=data_geracao,
            hora_geracao=hora_geracao,
            sequencial=nsa
        )
    )

    # ─────────────────────────────────────────────
    # HEADER DE LOTE
    # ─────────────────────────────────────────────
    linhas.append(
        gerar_header_lote_gps(
            lote=lote_servico,
            empresa=empresa
        )
    )

    # ─────────────────────────────────────────────
    # SEGMENTOS N
    # ─────────────────────────────────────────────
    total_centavos_lote = 0
    sequencial_no_lote = 1

    for contribuinte in contribuintes:

        if "valor_total" not in contribuinte:
            raise ValueError("Contribuinte sem campo 'valor_total'.")

        valor_total = Decimal(str(contribuinte["valor_total"]))

        valor_centavos = int(
            (valor_total * 100)
            .quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )

        total_centavos_lote += valor_centavos

        linhas.append(
            gerar_segmento_n_gps(
                lote=lote_servico,
                sequencial=sequencial_no_lote,
                contribuinte=contribuinte,
                data_pagamento=data_pagamento
            )
        )

        sequencial_no_lote += 1

    # ─────────────────────────────────────────────
    # TRAILER DE LOTE
    # ─────────────────────────────────────────────
    qtd_registros_lote = len(contribuintes) + 2

    linhas.append(
        gerar_trailer_lote_gps(
            lote=lote_servico,
            qtd_registros=qtd_registros_lote,
            valor_total_centavos=total_centavos_lote
        )
    )

    # ─────────────────────────────────────────────
    # TRAILER DE ARQUIVO
    # ─────────────────────────────────────────────
    qtd_total_registros = len(linhas) + 1

    linhas.append(
        gerar_trailer_arquivo(
            qtd_lotes=1,
            qtd_registros=qtd_total_registros
        )
    )

    # ─────────────────────────────────────────────
    # VALIDAÇÃO ESTRUTURAL FINAL (240 POSIÇÕES)
    # ─────────────────────────────────────────────
    linhas_finais = []

    for numero, linha in enumerate(linhas, start=1):
        linha_str = str(linha)

        if len(linha_str) != 240:
            raise ValueError(
                f"Linha {numero} inválida: possui {len(linha_str)} caracteres (esperado 240)."
            )

        linhas_finais.append(linha_str)

    # Padrão CNAB exige CRLF
    return "\r\n".join(linhas_finais) + "\r\n"
