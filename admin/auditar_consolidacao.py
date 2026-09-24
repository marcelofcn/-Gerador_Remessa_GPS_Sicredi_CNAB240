#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
ADMIN - AUDITORIA DE CONSOLIDAÇÃO DE GUIAS GPS
===============================================================================

Data de referência:
    23/09/2026

Objetivo:
    Auditar a correspondência entre:

        1. Guias / Espelhos GPS
        2. Comprovantes de pagamento GPS

    ANTES de realizar qualquer consolidação.

IMPORTANTE:
    Este script NÃO junta PDFs.
    Este script NÃO altera PDFs.
    Este script NÃO renomeia PDFs.

    Ele apenas lê os arquivos e produz uma auditoria.

-------------------------------------------------------------------------------
DIRETÓRIOS
-------------------------------------------------------------------------------

Guias:

    output/espelhos/GPS_RETROATIVO_CORRIGIDO/

Comprovantes:

    output/comprovantes_normalizados/

Relatório:

    output/guias_completas/RELATORIO_AUDITORIA.txt

-------------------------------------------------------------------------------
CRITÉRIO DE CORRESPONDÊNCIA
-------------------------------------------------------------------------------

A correspondência principal será feita por:

    IDENTIFICADOR NORMALIZADO + COMPETÊNCIA

O identificador pode aparecer como:

    NIT
    PIS
    PASEP
    NIS
    Identificador

Esses identificadores são tratados como o mesmo número-base.

Também são desconsiderados zeros à esquerda.

Exemplo:

    00011331838
    0011331838
    11331838

serão comparados pelo valor normalizado.

-------------------------------------------------------------------------------
VALIDAÇÃO DO VALOR
-------------------------------------------------------------------------------

Depois de encontrar um candidato por:

    IDENTIFICADOR + COMPETÊNCIA

o valor será comparado como validação adicional.

Exemplo:

    Guia        : R$ 178,31
    Comprovante : R$ 178,31

Resultado:

    VALOR OK

Se houver diferença:

    VALOR DIVERGENTE

A diferença de valor NÃO será usada inicialmente para impedir a identificação
do candidato. Ela será registrada para análise.

-------------------------------------------------------------------------------
RESULTADO ESPERADO
-------------------------------------------------------------------------------

Para cada guia:

    ✅ Correspondência única
    ⚠️ Sem comprovante
    ⚠️ Múltiplos comprovantes
    ⚠️ Valor divergente

Também serão identificados:

    ⚠️ Comprovantes sem guia correspondente

-------------------------------------------------------------------------------
"""

from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime
import re
import unicodedata

import pdfplumber


# =============================================================================
# CONFIGURAÇÃO DOS CAMINHOS
# =============================================================================

# Este arquivo está em:
#
# /home/house/developer/geraremessa/admin/auditar_consolidacao.py
#
# Portanto:
#
# parent        = /home/house/developer/geraremessa/admin
# parent.parent = /home/house/developer/geraremessa

BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# DIRETÓRIO DAS GUIAS
# =============================================================================

PASTA_GUIAS = (
    BASE_DIR
    / "output"
    / "espelhos"
    / "GPS_RETROATIVO_CORRIGIDO"
)


# =============================================================================
# DIRETÓRIO DOS COMPROVANTES
# =============================================================================

PASTA_COMPROVANTES = (
    BASE_DIR
    / "output"
    / "comprovantes_normalizados"
)


# =============================================================================
# DIRETÓRIO DO RELATÓRIO
# =============================================================================

PASTA_RELATORIO = (
    BASE_DIR
    / "output"
    / "guias_completas"
)


ARQUIVO_RELATORIO = (
    PASTA_RELATORIO
    / "RELATORIO_AUDITORIA.txt"
)


# =============================================================================
# NORMALIZAÇÃO DE TEXTO
# =============================================================================

def normalizar_texto(texto):
    """
    Normaliza texto para facilitar comparações.

    Remove:
        - acentos
        - caracteres especiais
        - espaços duplicados

    Exemplo:

        "João da Silva"

    vira:

        "JOAODASILVA"
    """

    if not texto:
        return ""

    texto = str(texto)

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    texto = texto.upper()

    texto = re.sub(
        r"[^A-Z0-9]",
        "",
        texto
    )

    return texto


# =============================================================================
# NORMALIZAÇÃO DO NIT / PIS / PASEP / NIS
# =============================================================================

def normalizar_identificador(valor):
    """
    Normaliza NIT/PIS/PASEP/NIS.

    REGRA IMPORTANTE:

        Os zeros à esquerda são desconsiderados.

    Exemplo:

        00011331838 -> 11331838
        0011331838  -> 11331838
        11331838    -> 11331838

    Não alteramos o PDF nem o nome original.

    A normalização existe apenas para comparação.

    """

    if valor is None:
        return ""

    texto = str(valor).strip()

    # Mantém somente números.
    numeros = re.sub(
        r"\D",
        "",
        texto
    )

    if not numeros:
        return ""

    # Remove zeros à esquerda.
    numeros = numeros.lstrip("0")

    # Caso o identificador fosse composto somente por zeros.
    if not numeros:
        return "0"

    return numeros


# =============================================================================
# NORMALIZAÇÃO DA COMPETÊNCIA
# =============================================================================

def normalizar_competencia(valor):
    """
    Normaliza competência para o formato:

        MMAAAA

    Exemplo:

        07/2026 -> 072026
        072026  -> 072026
    """

    if valor is None:
        return ""

    numeros = re.sub(
        r"\D",
        "",
        str(valor)
    )

    if len(numeros) == 6:
        return numeros

    return ""


# =============================================================================
# CONVERSÃO DE VALOR
# =============================================================================

def converter_valor(valor):
    """
    Converte valores monetários brasileiros para Decimal.

    Exemplos:

        1.234,56 -> Decimal("1234.56")
        178,31   -> Decimal("178.31")
        178.31   -> Decimal("178.31")
    """

    if valor is None:
        return None

    texto = str(valor).strip()

    if not texto:
        return None

    try:

        # Formato brasileiro:
        #
        # 1.234,56
        #
        if "," in texto:

            texto = (
                texto
                .replace(".", "")
                .replace(",", ".")
            )

        return Decimal(texto)

    except InvalidOperation:

        return None


# =============================================================================
# LEITURA DE PDF
# =============================================================================

def extrair_texto_pdf(caminho_pdf):
    """
    Extrai todo o texto disponível no PDF.

    Todas as páginas são lidas.
    """

    textos = []

    with pdfplumber.open(
        caminho_pdf
    ) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text()

            if texto:

                textos.append(
                    texto
                )

    return "\n".join(
        textos
    )


# =============================================================================
# EXTRAÇÃO DE IDENTIFICADOR
# =============================================================================

def extrair_identificador(texto):
    """
    Tenta localizar o NIT/PIS/PASEP/NIS dentro do comprovante.

    Exemplos:

        Identificador: 00011331838
        Identificador : 11331838
        NIT: 11331838
        PIS: 11331838
        PASEP: 11331838
        NIS: 11331838

    Retorna o identificador normalizado.
    """

    if not texto:
        return ""

    padroes = [

        r"Identificador\s*[:\-]?\s*(\d{8,11})",

        r"NIT\s*[:\-]?\s*(\d{8,11})",

        r"PIS\s*[:\-]?\s*(\d{8,11})",

        r"PASEP\s*[:\-]?\s*(\d{8,11})",

        r"NIS\s*[:\-]?\s*(\d{8,11})",

    ]

    for padrao in padroes:

        match = re.search(
            padrao,
            texto,
            re.IGNORECASE
        )

        if match:

            return normalizar_identificador(
                match.group(1)
            )

    return ""


# =============================================================================
# EXTRAÇÃO DA COMPETÊNCIA
# =============================================================================

def extrair_competencia(texto):
    """
    Procura a competência no texto.

    Exemplos:

        Competência: 07/2026
        Competência : 07/2026
        Competencia: 072026
    """

    if not texto:
        return ""

    padroes = [

        r"Compet[eê]ncia\s*[:\-]?\s*(\d{2})\s*/\s*(\d{4})",

        r"Compet[eê]ncia\s*[:\-]?\s*(\d{6})",

    ]

    for padrao in padroes:

        match = re.search(
            padrao,
            texto,
            re.IGNORECASE
        )

        if not match:
            continue

        grupos = match.groups()

        if len(grupos) == 2:

            return normalizar_competencia(
                f"{grupos[0]}{grupos[1]}"
            )

        if len(grupos) == 1:

            return normalizar_competencia(
                grupos[0]
            )

    return ""


# =============================================================================
# EXTRAÇÃO DO VALOR
# =============================================================================

def extrair_valor(texto):
    """
    Procura o valor total no PDF.

    Exemplos aceitos:

        Total (R$): 178,31
        Total: 178,31
        Valor Total: 178,31
    """

    if not texto:
        return None

    padroes = [

        r"Total\s*\(R\$\)\s*[:\-]?\s*([\d.,]+)",

        r"Total\s*[:\-]?\s*R?\$?\s*([\d.,]+)",

        r"Valor\s+Total\s*[:\-]?\s*R?\$?\s*([\d.,]+)",

    ]

    for padrao in padroes:

        match = re.search(
            padrao,
            texto,
            re.IGNORECASE
        )

        if not match:
            continue

        valor_texto = match.group(1)

        valor = converter_valor(
            valor_texto
        )

        if valor is not None:

            return valor

    return None


# =============================================================================
# EXTRAÇÃO DA GUIA
# =============================================================================

def ler_guia(caminho_pdf):
    """
    Lê uma guia GPS.

    O identificador e a competência são extraídos principalmente do nome
    do arquivo.

    Exemplo:

        GUIA_GPS_12943750249_072026.pdf

    Também tenta extrair o valor do conteúdo do PDF.
    """

    resultado = {

        "path": caminho_pdf,

        "nome": caminho_pdf.name,

        "identificador_original": "",

        "identificador": "",

        "competencia": "",

        "valor": None,

        "texto": "",

    }

    # -------------------------------------------------------------------------
    # Extrai dados do nome do arquivo
    # -------------------------------------------------------------------------

    match = re.match(
        r"GUIA_GPS_(\d+)_(\d{6})\.pdf$",
        caminho_pdf.name,
        re.IGNORECASE
    )

    if match:

        resultado["identificador_original"] = (
            match.group(1)
        )

        resultado["identificador"] = (
            normalizar_identificador(
                match.group(1)
            )
        )

        resultado["competencia"] = (
            normalizar_competencia(
                match.group(2)
            )
        )

    # -------------------------------------------------------------------------
    # Lê conteúdo do PDF
    # -------------------------------------------------------------------------

    try:

        texto = extrair_texto_pdf(
            caminho_pdf
        )

        resultado["texto"] = texto

        # ---------------------------------------------------------------------
        # Valor
        # ---------------------------------------------------------------------

        resultado["valor"] = extrair_valor(
            texto
        )

    except Exception as erro:

        resultado["erro"] = str(
            erro
        )

    return resultado


# =============================================================================
# EXTRAÇÃO DO COMPROVANTE
# =============================================================================

def ler_comprovante(caminho_pdf):
    """
    Lê um comprovante normalizado.

    O nome do arquivo já possui:

        PAGAMENTO_GPS_NIT_COMP_DATA_VALOR.pdf

    Porém, o conteúdo do PDF será considerado a fonte principal.

    Isso evita depender exclusivamente do nome do arquivo.
    """

    resultado = {

        "path": caminho_pdf,

        "nome": caminho_pdf.name,

        "identificador": "",

        "competencia": "",

        "valor": None,

        "texto": "",

    }

    # -------------------------------------------------------------------------
    # Lê PDF
    # -------------------------------------------------------------------------

    try:

        texto = extrair_texto_pdf(
            caminho_pdf
        )

        resultado["texto"] = texto

    except Exception as erro:

        resultado["erro"] = str(
            erro
        )

        return resultado

    # -------------------------------------------------------------------------
    # Identificador
    # -------------------------------------------------------------------------

    resultado["identificador"] = (
        extrair_identificador(
            texto
        )
    )

    # -------------------------------------------------------------------------
    # Competência
    # -------------------------------------------------------------------------

    resultado["competencia"] = (
        extrair_competencia(
            texto
        )
    )

    # -------------------------------------------------------------------------
    # Valor
    # -------------------------------------------------------------------------

    resultado["valor"] = (
        extrair_valor(
            texto
        )
    )

    # -------------------------------------------------------------------------
    # Se algum dado não foi encontrado no conteúdo, tenta o nome.
    # -------------------------------------------------------------------------

    if not resultado["identificador"]:

        match = re.match(
            r"PAGAMENTO_GPS_(\d+)_(\d{6})_",
            caminho_pdf.name,
            re.IGNORECASE
        )

        if match:

            resultado["identificador"] = (
                normalizar_identificador(
                    match.group(1)
                )
            )

            if not resultado["competencia"]:

                resultado["competencia"] = (
                    normalizar_competencia(
                        match.group(2)
                    )
                )

    return resultado


# =============================================================================
# CHAVE DE CORRESPONDÊNCIA
# =============================================================================

def criar_chave(identificador, competencia):
    """
    Cria a chave usada para cruzamento.

    Chave:

        identificador + competência

    Exemplo:

        11331838 + 072026

    vira:

        11331838|072026
    """

    identificador = normalizar_identificador(
        identificador
    )

    competencia = normalizar_competencia(
        competencia
    )

    if not identificador or not competencia:

        return ""

    return (
        f"{identificador}|{competencia}"
    )


# =============================================================================
# COMPARAÇÃO DE VALORES
# =============================================================================

def valores_iguais(valor1, valor2):
    """
    Compara valores monetários com precisão centesimal.
    """

    if valor1 is None or valor2 is None:

        return False

    return (
        Decimal(valor1).quantize(Decimal("0.01"))
        ==
        Decimal(valor2).quantize(Decimal("0.01"))
    )


# =============================================================================
# FORMATAÇÃO MONETÁRIA
# =============================================================================

def formatar_valor(valor):
    """
    Formata Decimal para relatório.
    """

    if valor is None:

        return "NÃO IDENTIFICADO"

    return (
        f"R$ {valor:.2f}"
    )


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================

def executar():

    print()

    print("=" * 78)
    print(" AUDITORIA DE CONSOLIDAÇÃO DE GUIAS GPS")
    print("=" * 78)

    print()

    print(
        f"Data/hora: "
        f"{datetime.now():%d/%m/%Y %H:%M:%S}"
    )

    print()

    print("Projeto:")
    print(
        f"  {BASE_DIR}"
    )

    print()

    print("Guias:")
    print(
        f"  {PASTA_GUIAS}"
    )

    print()

    print("Comprovantes:")
    print(
        f"  {PASTA_COMPROVANTES}"
    )

    print()

    print("Relatório:")
    print(
        f"  {PASTA_RELATORIO}"
    )

    print()

    print("=" * 78)

    # =========================================================================
    # PREPARAÇÃO
    # =========================================================================

    PASTA_RELATORIO.mkdir(
        parents=True,
        exist_ok=True
    )

    # =========================================================================
    # LOCALIZAÇÃO DOS ARQUIVOS
    # =========================================================================

    guias = sorted(
        PASTA_GUIAS.glob(
            "GUIA_GPS_*.pdf"
        )
    )

    comprovantes = sorted(
        PASTA_COMPROVANTES.glob(
            "PAGAMENTO_GPS_*.pdf"
        )
    )

    print()

    print("-" * 78)
    print("CONTAGEM DOS ARQUIVOS")
    print("-" * 78)

    print(
        f"Guias encontradas        : {len(guias)}"
    )

    print(
        f"Comprovantes encontrados : {len(comprovantes)}"
    )

    # =========================================================================
    # LER GUIAS
    # =========================================================================

    print()

    print("-" * 78)
    print("LENDO GUIAS")
    print("-" * 78)

    dados_guias = []

    for caminho in guias:

        dados = ler_guia(
            caminho
        )

        dados_guias.append(
            dados
        )

    print(
        f"Guias lidas: {len(dados_guias)}"
    )

    # =========================================================================
    # LER COMPROVANTES
    # =========================================================================

    print()

    print("-" * 78)
    print("LENDO COMPROVANTES")
    print("-" * 78)

    dados_comprovantes = []

    for caminho in comprovantes:

        dados = ler_comprovante(
            caminho
        )

        dados_comprovantes.append(
            dados
        )

    print(
        f"Comprovantes lidos: "
        f"{len(dados_comprovantes)}"
    )

    # =========================================================================
    # CRIAR ÍNDICE DOS COMPROVANTES
    # =========================================================================

    indice_comprovantes = {}

    comprovantes_invalidos = []

    for comprovante in dados_comprovantes:

        chave = criar_chave(
            comprovante["identificador"],
            comprovante["competencia"]
        )

        if not chave:

            comprovantes_invalidos.append(
                comprovante
            )

            continue

        indice_comprovantes.setdefault(
            chave,
            []
        ).append(
            comprovante
        )

    # =========================================================================
    # AUDITORIA DAS GUIAS
    # =========================================================================

    correspondencias = []

    sem_comprovante = []

    multiplos_comprovantes = []

    valor_divergente = []

    guias_invalidas = []

    chaves_guias = set()

    for guia in dados_guias:

        identificador = guia[
            "identificador"
        ]

        competencia = guia[
            "competencia"
        ]

        chave = criar_chave(
            identificador,
            competencia
        )

        if not chave:

            guias_invalidas.append(
                guia
            )

            continue

        chaves_guias.add(
            chave
        )

        candidatos = indice_comprovantes.get(
            chave,
            []
        )

        # ---------------------------------------------------------------------
        # Nenhum comprovante
        # ---------------------------------------------------------------------

        if len(candidatos) == 0:

            sem_comprovante.append(
                guia
            )

            continue

        # ---------------------------------------------------------------------
        # Mais de um comprovante
        # ---------------------------------------------------------------------

        if len(candidatos) > 1:

            multiplos_comprovantes.append(
                {
                    "guia": guia,
                    "candidatos": candidatos,
                }
            )

            continue

        # ---------------------------------------------------------------------
        # Correspondência única
        # ---------------------------------------------------------------------

        comprovante = candidatos[0]

        valor_ok = valores_iguais(
            guia["valor"],
            comprovante["valor"]
        )

        registro = {

            "guia": guia,

            "comprovante": comprovante,

            "valor_ok": valor_ok,

        }

        correspondencias.append(
            registro
        )

        if not valor_ok:

            valor_divergente.append(
                registro
            )

    # =========================================================================
    # COMPROVANTES SEM GUIA
    # =========================================================================

    comprovantes_sem_guia = []

    for comprovante in dados_comprovantes:

        chave = criar_chave(
            comprovante["identificador"],
            comprovante["competencia"]
        )

        if not chave:

            continue

        if chave not in chaves_guias:

            comprovantes_sem_guia.append(
                comprovante
            )

    # =========================================================================
    # RESUMO
    # =========================================================================

    total_correspondencias = len(
        correspondencias
    )

    total_sem_comprovante = len(
        sem_comprovante
    )

    total_multiplos = len(
        multiplos_comprovantes
    )

    total_valor_divergente = len(
        valor_divergente
    )

    total_comprovantes_sem_guia = len(
        comprovantes_sem_guia
    )

    total_guias_invalidas = len(
        guias_invalidas
    )

    total_comprovantes_invalidos = len(
        comprovantes_invalidos
    )

    # =========================================================================
    # RESULTADO NA TELA
    # =========================================================================

    print()

    print("-" * 78)
    print("RESULTADO DA AUDITORIA")
    print("-" * 78)

    print(
        f"✅ Correspondência única : "
        f"{total_correspondencias}"
    )

    print(
        f"⚠️ Sem comprovante        : "
        f"{total_sem_comprovante}"
    )

    print(
        f"⚠️ Múltiplos comprovantes : "
        f"{total_multiplos}"
    )

    print(
        f"⚠️ Valor divergente       : "
        f"{total_valor_divergente}"
    )

    print(
        f"⚠️ Comprovante sem guia   : "
        f"{total_comprovantes_sem_guia}"
    )

    print(
        f"❌ Guias com nome inválido: "
        f"{total_guias_invalidas}"
    )

    print(
        f"❌ Comprovantes inválidos : "
        f"{total_comprovantes_invalidos}"
    )

    # =========================================================================
    # GERAÇÃO DO RELATÓRIO
    # =========================================================================

    linhas = []

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "RELATÓRIO DE AUDITORIA DE CONSOLIDAÇÃO GPS"
    )

    linhas.append(
        "=" * 78
    )

    linhas.append(
        f"Data/hora: "
        f"{datetime.now():%d/%m/%Y %H:%M:%S}"
    )

    linhas.append(
        f"Projeto: {BASE_DIR}"
    )

    linhas.append(
        ""
    )

    linhas.append(
        "GUIAS"
    )

    linhas.append(
        str(PASTA_GUIAS)
    )

    linhas.append(
        ""
    )

    linhas.append(
        "COMPROVANTES"
    )

    linhas.append(
        str(PASTA_COMPROVANTES)
    )

    linhas.append(
        ""
    )

    linhas.append(
        "-" * 78
    )

    linhas.append(
        "CRITÉRIO DE CORRESPONDÊNCIA"
    )

    linhas.append(
        "-" * 78
    )

    linhas.append(
        "Identificador normalizado + competência"
    )

    linhas.append(
        "Zeros à esquerda do identificador são ignorados."
    )

    linhas.append(
        "NIT/PIS/PASEP/NIS são tratados como o mesmo identificador-base."
    )

    linhas.append(
        ""
    )

    linhas.append(
        "-" * 78
    )

    linhas.append(
        "RESUMO"
    )

    linhas.append(
        "-" * 78
    )

    linhas.append(
        f"Guias encontradas        : {len(guias)}"
    )

    linhas.append(
        f"Comprovantes encontrados : {len(comprovantes)}"
    )

    linhas.append(
        f"Correspondências únicas  : {total_correspondencias}"
    )

    linhas.append(
        f"Sem comprovante          : {total_sem_comprovante}"
    )

    linhas.append(
        f"Múltiplos comprovantes   : {total_multiplos}"
    )

    linhas.append(
        f"Valor divergente         : {total_valor_divergente}"
    )

    linhas.append(
        f"Comprovante sem guia     : {total_comprovantes_sem_guia}"
    )

    linhas.append(
        f"Guias inválidas          : {total_guias_invalidas}"
    )

    linhas.append(
        f"Comprovantes inválidos   : {total_comprovantes_invalidos}"
    )

    # =========================================================================
    # CORRESPONDÊNCIAS
    # =========================================================================

    linhas.append("")

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "CORRESPONDÊNCIAS ENCONTRADAS"
    )

    linhas.append(
        "=" * 78
    )

    if not correspondencias:

        linhas.append(
            "Nenhuma correspondência encontrada."
        )

    else:

        for item in correspondencias:

            guia = item["guia"]
            comprovante = item["comprovante"]

            linhas.append("")

            linhas.append(
                f"GUIA: {guia['nome']}"
            )

            linhas.append(
                f"  Identificador : "
                f"{guia['identificador_original']}"
            )

            linhas.append(
                f"  ID normalizado: "
                f"{guia['identificador']}"
            )

            linhas.append(
                f"  Competência   : "
                f"{guia['competencia']}"
            )

            linhas.append(
                f"  Valor guia    : "
                f"{formatar_valor(guia['valor'])}"
            )

            linhas.append(
                f"COMPROVANTE: "
                f"{comprovante['nome']}"
            )

            linhas.append(
                f"  ID normalizado: "
                f"{comprovante['identificador']}"
            )

            linhas.append(
                f"  Competência   : "
                f"{comprovante['competencia']}"
            )

            linhas.append(
                f"  Valor         : "
                f"{formatar_valor(comprovante['valor'])}"
            )

            linhas.append(
                f"  VALOR: "
                f"{'OK' if item['valor_ok'] else 'DIVERGENTE'}"
            )

            linhas.append(
                "-" * 78
            )

    # =========================================================================
    # GUIAS SEM COMPROVANTE
    # =========================================================================

    linhas.append("")

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "GUIAS SEM COMPROVANTE"
    )

    linhas.append(
        "=" * 78
    )

    if not sem_comprovante:

        linhas.append(
            "Nenhuma."
        )

    else:

        for guia in sem_comprovante:

            linhas.append(
                f"{guia['nome']} | "
                f"ID={guia['identificador']} | "
                f"COMP={guia['competencia']} | "
                f"VALOR={formatar_valor(guia['valor'])}"
            )

    # =========================================================================
    # MÚLTIPLOS COMPROVANTES
    # =========================================================================

    linhas.append("")

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "GUIAS COM MÚLTIPLOS COMPROVANTES"
    )

    linhas.append(
        "=" * 78
    )

    if not multiplos_comprovantes:

        linhas.append(
            "Nenhuma."
        )

    else:

        for item in multiplos_comprovantes:

            guia = item["guia"]

            linhas.append("")

            linhas.append(
                f"GUIA: {guia['nome']}"
            )

            for comprovante in item[
                "candidatos"
            ]:

                linhas.append(
                    f"  -> {comprovante['nome']}"
                )

    # =========================================================================
    # VALORES DIVERGENTES
    # =========================================================================

    linhas.append("")

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "CORRESPONDÊNCIAS COM VALOR DIVERGENTE"
    )

    linhas.append(
        "=" * 78
    )

    if not valor_divergente:

        linhas.append(
            "Nenhuma."
        )

    else:

        for item in valor_divergente:

            guia = item["guia"]

            comprovante = item[
                "comprovante"
            ]

            linhas.append("")

            linhas.append(
                f"GUIA: {guia['nome']}"
            )

            linhas.append(
                f"  Valor guia       : "
                f"{formatar_valor(guia['valor'])}"
            )

            linhas.append(
                f"  Comprovante      : "
                f"{comprovante['nome']}"
            )

            linhas.append(
                f"  Valor comprovante: "
                f"{formatar_valor(comprovante['valor'])}"
            )

    # =========================================================================
    # COMPROVANTES SEM GUIA
    # =========================================================================

    linhas.append("")

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "COMPROVANTES SEM GUIA"
    )

    linhas.append(
        "=" * 78
    )

    if not comprovantes_sem_guia:

        linhas.append(
            "Nenhum."
        )

    else:

        for comprovante in comprovantes_sem_guia:

            linhas.append(
                f"{comprovante['nome']} | "
                f"ID={comprovante['identificador']} | "
                f"COMP={comprovante['competencia']} | "
                f"VALOR={formatar_valor(comprovante['valor'])}"
            )

    # =========================================================================
    # SALVA RELATÓRIO
    # =========================================================================

    with open(
        ARQUIVO_RELATORIO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(
            "\n".join(linhas)
        )

    # =========================================================================
    # FINAL
    # =========================================================================

    print()

    print("=" * 78)
    print(" AUDITORIA FINALIZADA")
    print("=" * 78)

    print()

    print(
        f"📋 Relatório:"
    )

    print(
        f"   {ARQUIVO_RELATORIO}"
    )

    print()

    print("=" * 78)

    print()


# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":

    executar()
