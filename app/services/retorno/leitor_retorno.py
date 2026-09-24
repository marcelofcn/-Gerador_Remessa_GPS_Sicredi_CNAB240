"""
LEITOR_RETORNO.PY
------------------------------------------------------------
Leitor de arquivo de retorno CNAB240 - Sicredi
Processa Segmento N (Pagamento GPS)

Responsabilidades:
- Validar registros com 240 posições
- Identificar Segmento N
- Extrair contribuinte e valor
- Ler até 5 ocorrências G099
- Traduzir códigos de ocorrência
- Classificar situação do pagamento
- Preservar os códigos originais para auditoria

Fonte oficial das ocorrências:
Tabela G099 - SICREDI
Atualizada em 2026-08-18
Status:
PRODUÇÃO
"""

from decimal import Decimal, InvalidOperation


# ============================================================
# TABELA OFICIAL G099 - SICREDI
# ============================================================

TABELA_G099 = {

    # --------------------------------------------------------
    # RESULTADO DO PAGAMENTO
    # --------------------------------------------------------

    "00": ("Pagamento Confirmado", "paga"),
    "01": ("Insuficiência de Fundos", "rejeitada"),
    "02": ("Crédito ou Débito Cancelado", "rejeitada"),
    "03": ("Débito Autorizado pela Agência - Efetuado", "paga"),

    # --------------------------------------------------------
    # OCORRÊNCIAS CNAB 240
    # --------------------------------------------------------

    "AA": ("Controle Inválido (Arquivo Duplicado)", "rejeitada"),
    "AB": ("Tipo de Operação Inválido", "rejeitada"),
    "AC": ("Tipo de Serviço Inválido", "rejeitada"),
    "AD": ("Forma de Lançamento Inválida", "rejeitada"),
    "AE": ("Tipo/Número de Inscrição Inválido", "rejeitada"),
    "AF": ("Código de Convênio Inválido", "rejeitada"),
    "AG": ("Agência/Conta Corrente/DV Inválido", "rejeitada"),
    "AH": ("Nº Sequencial do Registro Inválido", "rejeitada"),
    "AI": ("Código de Segmento de Detalhe Inválido", "rejeitada"),
    "AJ": ("Tipo de Movimento Inválido", "rejeitada"),
    "AK": ("Código da Câmara de Compensação Inválido", "rejeitada"),
    "AL": ("Banco Favorecido/Depositário Inválido", "rejeitada"),
    "AM": ("Agência Mantenedora do Favorecido Inválida", "rejeitada"),
    "AN": ("Conta Corrente/DV do Favorecido Inválido", "rejeitada"),
    "AO": ("Nome do Favorecido Não Informado", "rejeitada"),
    "AP": ("Data de Lançamento Inválida", "rejeitada"),
    "AQ": ("Tipo/Quantidade da Moeda Inválido", "rejeitada"),
    "AR": ("Valor do Lançamento Inválido", "rejeitada"),
    "AS": ("Aviso ao Favorecido Inválido", "rejeitada"),
    "AT": ("Tipo/Nº de Inscrição do Favorecido Inválido", "rejeitada"),
    "AU": ("Logradouro do Favorecido Não Informado", "rejeitada"),
    "AV": ("Nº do Local do Favorecido Não Informado", "rejeitada"),
    "AW": ("Cidade do Favorecido Não Informada", "rejeitada"),
    "AX": ("CEP/Complemento do Favorecido Inválido", "rejeitada"),
    "AY": ("Sigla do Estado do Favorecido Inválida", "rejeitada"),
    "AZ": ("Banco Depositário Inválido", "rejeitada"),
    "BA": ("Agência Depositária Não Informada", "rejeitada"),
    "BB": ("Seu Número Inválido (Duplicidade)", "rejeitada"),
    "BC": ("Nosso Número Inválido", "rejeitada"),

    # --------------------------------------------------------
    # OPERAÇÕES EFETUADAS / AGENDADAS
    # --------------------------------------------------------

    "BD": ("Inclusão Efetuada com Sucesso - Pagamento Agendado", "agendada"),
    "BE": ("Alteração Efetuada com Sucesso", "agendada"),
    "BF": ("Exclusão Efetuada com Sucesso", "excluida"),
    "BG": ("Agência/Conta Impedida Legalmente/Bloqueada", "rejeitada"),

    # --------------------------------------------------------
    # CONSIGNAÇÃO
    # --------------------------------------------------------

    "BH": ("Empresa Não Pagou Salário", "rejeitada"),
    "BI": ("Falecimento do Mutuário", "rejeitada"),
    "BJ": ("Empresa Não Enviou Remessa do Mutuário", "rejeitada"),
    "BK": ("Empresa Não Enviou Remessa no Vencimento", "rejeitada"),
    "BL": ("Valor da Parcela Inválida", "rejeitada"),
    "BM": ("Identificação do Contrato Inválida", "rejeitada"),
    "BN": ("Operação de Consignação Incluída com Sucesso", "agendada"),
    "BO": ("Operação de Consignação Alterada com Sucesso", "agendada"),
    "BP": ("Operação de Consignação Excluída com Sucesso", "excluida"),
    "BQ": ("Operação de Consignação Liquidada com Sucesso", "paga"),

    # --------------------------------------------------------
    # CÓDIGO DE BARRAS
    # --------------------------------------------------------

    "CA": ("Código de Barras - Código do Banco Inválido", "rejeitada"),
    "CB": ("Código de Barras - Código da Moeda Inválido", "rejeitada"),
    "CC": ("Código de Barras - Dígito Verificador Geral Inválido", "rejeitada"),
    "CD": ("Código de Barras - Valor do Título Inválido", "rejeitada"),
    "CE": ("Código de Barras - Campo Livre Inválido", "rejeitada"),
    "CF": ("Valor do Documento Inválido", "rejeitada"),
    "CG": ("Valor do Abatimento Inválido", "rejeitada"),
    "CH": ("Valor do Desconto Inválido", "rejeitada"),
    "CI": ("Valor de Mora Inválido", "rejeitada"),
    "CJ": ("Valor da Multa Inválido", "rejeitada"),

    # --------------------------------------------------------
    # TRIBUTOS
    # --------------------------------------------------------

    "CK": ("Valor do IR Inválido", "rejeitada"),
    "CL": ("Valor do ISS Inválido", "rejeitada"),
    "CM": ("Valor do IOF Inválido", "rejeitada"),
    "CN": ("Valor de Outras Deduções Inválido", "rejeitada"),
    "CO": ("Valor de Outros Acréscimos Inválido", "rejeitada"),
    "CP": ("Valor do INSS Inválido", "rejeitada"),

    # --------------------------------------------------------
    # OUTRAS OCORRÊNCIAS INFORMADAS NA TABELA
    # --------------------------------------------------------

    "11": ("Agência/Conta Corrente/DV Inválido", "rejeitada"),

    "HA": ("Lote Não Aceito", "rejeitada"),
}


# ============================================================
# LEITOR
# ============================================================

class LeitorRetornoSicredi:

    @staticmethod
    def interpretar_ocorrencia(codigo):
        """
        Traduz um código G099.

        Retorna:
            codigo
            descricao
            situacao
            conhecida
        """

        codigo = str(codigo).strip().upper()

        if not codigo:
            return None

        if codigo in TABELA_G099:
            descricao, situacao = TABELA_G099[codigo]

            return {
                "codigo": codigo,
                "descricao": descricao,
                "situacao": situacao,
                "conhecida": True,
            }

        # Nunca assumir que código desconhecido é pagamento.
        return {
            "codigo": codigo,
            "descricao": f"Código não mapeado: {codigo}",
            "situacao": "pendente_analise",
            "conhecida": False,
        }

    @staticmethod
    def extrair_ocorrencias(linha):
        """
        Campo G099.

        O SICREDI pode informar até 5 ocorrências,
        cada uma com dois caracteres.

        Campo:
            posições 231-240
            índice Python: 230:240
        """

        campo = linha[230:240]

        ocorrencias = []

        for i in range(0, 10, 2):

            codigo = campo[i:i + 2].strip().upper()

            if not codigo:
                continue

            ocorrencia = LeitorRetornoSicredi.interpretar_ocorrencia(
                codigo
            )

            if ocorrencia:
                ocorrencias.append(ocorrencia)

        return ocorrencias

    @staticmethod
    def determinar_situacao(ocorrencias):
        """
        Determina a situação geral do registro.

        Regra conservadora:
        - qualquer ocorrência desconhecida -> pendente_analise
        - rejeitada -> rejeitada
        - excluida -> excluida
        - agendada -> agendada
        - paga -> paga
        - nenhuma ocorrência -> paga
        """

        if not ocorrencias:
            return "paga"

        # Código desconhecido nunca pode virar "pago".
        if any(not o["conhecida"] for o in ocorrencias):
            return "pendente_analise"

        situacoes = {o["situacao"] for o in ocorrencias}

        if "rejeitada" in situacoes:
            return "rejeitada"

        if "excluida" in situacoes:
            return "excluida"

        if "agendada" in situacoes:
            return "agendada"

        if "paga" in situacoes:
            return "paga"

        return "pendente_analise"

    @staticmethod
    def processar_arquivo(caminho_arquivo):

        resultados = []

        with open(
            caminho_arquivo,
            "r",
            encoding="ascii",
            errors="replace"
        ) as f:

            for numero_linha, linha in enumerate(f, start=1):

                linha_limpa = linha.rstrip("\r\n")

                # ------------------------------------------------
                # VALIDAÇÃO CNAB240
                # ------------------------------------------------

                if len(linha_limpa) != 240:
                    continue

                tipo_registro = linha_limpa[7]
                segmento = linha_limpa[13]

                # ------------------------------------------------
                # SOMENTE SEGMENTO N
                # ------------------------------------------------

                if tipo_registro != "3" or segmento != "N":
                    continue

                # ------------------------------------------------
                # NOME
                # ------------------------------------------------

                nome = linha_limpa[57:87].strip()

                # ------------------------------------------------
                # VALOR
                # ------------------------------------------------

                campo_valor = linha_limpa[95:110].strip()

                try:
                    valor_centavos = Decimal(campo_valor)
                    valor = valor_centavos / Decimal("100")

                except (InvalidOperation, ValueError):
                    valor = Decimal("0.00")

                # ------------------------------------------------
                # OCORRÊNCIAS G099
                # ------------------------------------------------

                ocorrencias = (
                    LeitorRetornoSicredi.extrair_ocorrencias(
                        linha_limpa
                    )
                )

                situacao = (
                    LeitorRetornoSicredi.determinar_situacao(
                        ocorrencias
                    )
                )

                # ------------------------------------------------
                # COMPATIBILIDADE COM O CÓDIGO ANTIGO
                # ------------------------------------------------

                if ocorrencias:

                    status = " | ".join(
                        (
                            f"{o['codigo']} - "
                            f"{o['descricao']}"
                        )
                        for o in ocorrencias
                    )

                else:

                    status = "Pagamento Confirmado"

                # ------------------------------------------------
                # RESULTADO
                # ------------------------------------------------

                resultados.append({

                    "linha": numero_linha,

                    "nome": nome,

                    "valor": float(valor),

                    "valor_decimal": valor,

                    "status": status,

                    "situacao": situacao,

                    "codigos": [
                        o["codigo"]
                        for o in ocorrencias
                    ],

                    "ocorrencias": ocorrencias,
                })

        return resultados
