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
    nsa: int = 1  # <--- NOVO PARÂMETRO PARA PRODUÇÃO
) -> str:

    linhas = []
    lote = 1

    # ─── Header Arquivo ─────────────────────────────────────
    linhas.append(
        gerar_header_arquivo_sicredi(
            empresa=empresa,
            data_geracao=data_geracao,
            hora_geracao=hora_geracao,
            sequencial=nsa  # <--- PASSANDO O NSA PARA O LAYOUT DO HEADER
        )
    )

    # ─── Header Lote ────────────────────────────────────────
    linhas.append(
        gerar_header_lote_gps(
            lote=lote,
            empresa=empresa
        )
    )

    # ─── Segmentos N ────────────────────────────────────────
    total_centavos = 0
    sequencial_no_lote = 1

    for contribuinte in contribuintes:
        valor_centavos = int(round(contribuinte["valor_total"] * 100))
        total_centavos += valor_centavos

        linhas.append(
            gerar_segmento_n_gps(
                lote=lote,
                sequencial=sequencial_no_lote,
                contribuinte=contribuinte,
                data_pagamento=data_pagamento
            )
        )
        sequencial_no_lote += 1

    # ─── Trailer Lote ───────────────────────────────────────
    qtd_registros_lote = 2 + len(contribuintes)

    linhas.append(
        gerar_trailer_lote_gps(
            lote=lote,
            qtd_registros=qtd_registros_lote,
            valor_total_centavos=total_centavos
        )
    )

    # ─── Trailer Arquivo ────────────────────────────────────
    qtd_registros_arquivo = len(linhas) + 1

    linhas.append(
        gerar_trailer_arquivo(
            qtd_lotes=1,
            qtd_registros=qtd_registros_arquivo
        )
    )

    return "\r\n".join(linhas) + "\r\n"
