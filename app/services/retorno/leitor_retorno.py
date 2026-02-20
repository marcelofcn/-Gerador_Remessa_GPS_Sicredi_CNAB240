"""
LEITOR_RETORNO.PY
------------------------------------------------------------
Leitor de arquivo de retorno CNAB240 - Sicredi
Processa Segmento N (Pagamento GPS)

Versão: 1.2.0
Status: PRODUÇÃO
"""

from decimal import Decimal, InvalidOperation


class LeitorRetornoSicredi:

    OCORRENCIAS = {
        "00": "Pago/Agendado com Sucesso",
        "01": "Insuficiência de Fundos",
        "02": "Pagamento Cancelado",
        "03": "Débito Autorizado pela Agência",
        "AA": "Arquivo Duplicado (NSA já enviado)",
        "AF": "Código de Convênio Inválido",
        "AE": "CPF/CNPJ do Favorecido Inválido",
        "BD": "Data de Pagamento Inválida",
    }

    @staticmethod
    def processar_arquivo(caminho_arquivo):

        resultados = []

        with open(caminho_arquivo, "r", encoding="ascii", errors="replace") as f:

            for numero_linha, linha in enumerate(f, start=1):

                linha_limpa = linha.rstrip("\r\n")

                if len(linha_limpa) != 240:
                    continue

                tipo_registro = linha_limpa[7]
                segmento = linha_limpa[13]

                if tipo_registro == "3" and segmento == "N":

                    nome = linha_limpa[57:87].strip()

                    try:
                        valor_centavos = Decimal(linha_limpa[95:110])
                        valor = float(valor_centavos / Decimal("100"))
                    except (InvalidOperation, ValueError):
                        valor = 0.0

                    raw_erros = linha_limpa[230:240].strip()

                    erros_traduzidos = []

                    for i in range(0, len(raw_erros), 2):
                        codigo = raw_erros[i:i+2]

                        if codigo.strip():
                            erros_traduzidos.append(
                                LeitorRetornoSicredi.OCORRENCIAS.get(
                                    codigo,
                                    f"Código não mapeado: {codigo}"
                                )
                            )

                    status_final = (
                        " | ".join(erros_traduzidos)
                        if erros_traduzidos
                        else "Pago/Agendado com Sucesso"
                    )

                    resultados.append({
                        "linha": numero_linha,
                        "nome": nome,
                        "valor": valor,
                        "status": status_final
                    })

        return resultados
