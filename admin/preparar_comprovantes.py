#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
ADMIN - PREPARAR COMPROVANTES GPS
===============================================================================

Data de referência:
    23/09/2026

Objetivo:
    Ler os comprovantes de pagamento GPS recebidos do banco, extrair os
    principais dados do conteúdo dos PDFs e criar uma cópia normalizada
    dentro do projeto.

ORIGEM DOS ARQUIVOS
-------------------

Os comprovantes originais devem estar em:

    output/comprovantes_brutos/pasta1/
    output/comprovantes_brutos/pasta2/

Exemplo:

    output/comprovantes_brutos/
    ├── pasta1/
    │   ├── comprovante0.pdf
    │   ├── comprovante1.pdf
    │   └── ...
    │
    └── pasta2/
        ├── comprovante0.pdf
        ├── comprovante1.pdf
        └── ...

IMPORTANTE:

    Os arquivos originais NÃO são renomeados.
    Os arquivos originais NÃO são modificados.

DESTINO
-------

Os comprovantes processados serão copiados para:

    output/comprovantes_normalizados/

Formato do nome:

    PAGAMENTO_GPS_<IDENTIFICADOR>_<COMPETENCIA>_<DATA>_<VALOR>.pdf

Exemplo real:

    PAGAMENTO_GPS_11331838821_072026_14_ago_178.31.pdf

DADOS EXTRAÍDOS
---------------

O script tenta identificar:

    - Identificador
    - Competência
    - Data do pagamento
    - Valor total

IMPORTANTE SOBRE O IDENTIFICADOR
--------------------------------

Os comprovantes bancários podem apresentar o identificador com zeros
à esquerda e também com mais de 11 dígitos.

Exemplo encontrado no comprovante real:

    05 - Identificador:

    00011331838821

O script NÃO corta o número para 11 dígitos.

Primeiro captura o número inteiro:

    00011331838821

Depois remove somente os zeros à esquerda:

    11331838821

Esse valor é utilizado no nome normalizado.

RELATÓRIO
---------

O script cria:

    output/comprovantes_normalizados/RELATORIO_COMPROVANTES.txt

DUPLICIDADES
------------

Se dois comprovantes apresentarem os mesmos dados e o mesmo nome-base,
o script não sobrescreve o arquivo.

Exemplo:

    PAGAMENTO_GPS_11331838821_072026_14_ago_178.31.pdf
    PAGAMENTO_GPS_11331838821_072026_14_ago_178.31_1.pdf
    PAGAMENTO_GPS_11331838821_072026_14_ago_178.31_2.pdf

PENDÊNCIAS
----------

Se algum comprovante não permitir identificar todos os campos obrigatórios,
ele NÃO será copiado silenciosamente.

Será registrado como PENDENTE no relatório.

===============================================================================
"""

from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
import shutil

import pdfplumber


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

# Raiz do projeto:
#
# /home/house/developer/geraremessa
#
# Como este arquivo está em:
#
# /home/house/developer/geraremessa/admin/preparar_comprovantes.py
#
# .parent       -> admin
# .parent.parent -> geraremessa

BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# ORIGEM DOS COMPROVANTES
# =============================================================================

PASTA_BRUTOS = (
    BASE_DIR
    / "output"
    / "comprovantes_brutos"
)

PASTA1 = PASTA_BRUTOS / "pasta1"
PASTA2 = PASTA_BRUTOS / "pasta2"

PASTAS_ORIGEM = [
    PASTA1,
    PASTA2,
]


# =============================================================================
# DESTINO
# =============================================================================

PASTA_NORMALIZADOS = (
    BASE_DIR
    / "output"
    / "comprovantes_normalizados"
)


# =============================================================================
# CONFIGURAÇÃO DE PDF
# =============================================================================

EXTENSAO_PDF = ".pdf"


# =============================================================================
# NORMALIZAÇÃO DE TEXTO
# =============================================================================

def normalizar_espacos(texto):
    """
    Remove espaços duplicados, tabs e quebras de linha.

    Exemplo:

        "Data    do\nPagamento"

    vira:

        "Data do Pagamento"
    """

    if not texto:
        return ""

    return re.sub(
        r"\s+",
        " ",
        texto
    ).strip()


def normalizar_texto_pdf(texto):
    """
    Normaliza o texto extraído do PDF.

    Mantém números, letras e pontuação.
    """

    if not texto:
        return ""

    texto = texto.replace(
        "\xa0",
        " "
    )

    return normalizar_espacos(
        texto
    )


# =============================================================================
# NORMALIZAÇÃO DO IDENTIFICADOR
# =============================================================================

def normalizar_identificador(identificador):
    """
    Normaliza o identificador encontrado no comprovante.

    IMPORTANTE:

    Não limita o identificador a 11 dígitos.

    Exemplo real:

        00011331838821

    vira:

        11331838821

    Ou seja, somente os zeros à esquerda são removidos.

    Se o identificador for composto somente por zeros, retorna None.
    """

    if not identificador:
        return None

    identificador = str(
        identificador
    ).strip()

    # Remove qualquer caractere que não seja número.
    identificador = re.sub(
        r"\D",
        "",
        identificador
    )

    if not identificador:
        return None

    # Remove somente zeros à esquerda.
    identificador = identificador.lstrip("0")

    if not identificador:
        return None

    return identificador


# =============================================================================
# EXTRAÇÃO DO IDENTIFICADOR
# =============================================================================

def extrair_identificador(texto):
    """
    Extrai o identificador do comprovante.

    O formato real encontrado nos PDFs do Sicredi é semelhante a:

        05 - Identificador:

        00011331838821

    Também aceita variações como:

        Identificador: 00011331838821

        Identificador :

        00011331838821

    IMPORTANTE:

        Não assume que o identificador tenha exatamente 11 dígitos.

    Retorna o identificador já normalizado.
    """

    padroes = [

        # Formato principal observado no PDF:
        #
        # 05 - Identificador:
        # 00011331838821
        r"Identificador\s*:\s*(\d+)",

        # Caso o texto extraído coloque a informação em linhas separadas:
        #
        # Identificador
        # 00011331838821
        r"Identificador\s+(\d+)",

        # Variação com hífen:
        #
        # Identificador - 00011331838821
        r"Identificador\s*-\s*(\d+)",

    ]

    for padrao in padroes:

        match = re.search(
            padrao,
            texto,
            re.IGNORECASE
        )

        if match:

            identificador = match.group(1)

            return normalizar_identificador(
                identificador
            )

    return None


# =============================================================================
# EXTRAÇÃO DA COMPETÊNCIA
# =============================================================================

def extrair_competencia(texto):
    """
    Extrai a competência.

    Exemplo:

        04 - Competência:

        07/2026

    Retorna:

        072026
    """

    padroes = [

        # Exemplo:
        #
        # Competência: 07/2026
        r"Compet[eê]ncia\s*:\s*(\d{2})\s*/\s*(\d{4})",

        # Exemplo:
        #
        # Competência 07/2026
        r"Compet[eê]ncia\s+(\d{2})\s*/\s*(\d{4})",

        # Caso venha diretamente como 072026.
        r"Compet[eê]ncia\s*:\s*(\d{6})",

        r"Compet[eê]ncia\s+(\d{6})",
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

            mes = grupos[0]
            ano = grupos[1]

            # Validação básica do mês.
            if not 1 <= int(mes) <= 12:
                continue

            return f"{mes}{ano}"

        if len(grupos) == 1:

            competencia = grupos[0]

            if len(competencia) == 6:
                mes = int(
                    competencia[:2]
                )

                if 1 <= mes <= 12:
                    return competencia

    return None


# =============================================================================
# EXTRAÇÃO DA DATA DE PAGAMENTO
# =============================================================================

def extrair_data_pagamento(texto):
    """
    Extrai a data do pagamento.

    Exemplo:

        Data do Pagamento:

        14/08/2026

    Retorna:

        14_ago

    O formato segue o padrão utilizado anteriormente pelo
    gps_renomear.py.
    """

    padroes = [

        r"Data\s+do\s+Pagamento\s*:\s*(\d{2})/(\d{2})/(\d{4})",

        r"Data\s+Pagamento\s*:\s*(\d{2})/(\d{2})/(\d{4})",

        r"Data\s+do\s+Pagamento\s+(\d{2})/(\d{2})/(\d{4})",

    ]

    meses = [
        "jan",
        "fev",
        "mar",
        "abr",
        "mai",
        "jun",
        "jul",
        "ago",
        "set",
        "out",
        "nov",
        "dez",
    ]

    for padrao in padroes:

        match = re.search(
            padrao,
            texto,
            re.IGNORECASE
        )

        if not match:
            continue

        dia = match.group(1)
        mes = int(
            match.group(2)
        )
        ano = match.group(3)

        if 1 <= mes <= 12:

            # Validação simples do dia.
            if 1 <= int(dia) <= 31:

                return (
                    f"{dia}_{meses[mes - 1]}"
                )

    return None


# =============================================================================
# EXTRAÇÃO DO VALOR
# =============================================================================

def extrair_valor(texto):
    """
    Extrai o valor total do pagamento.

    Exemplo real:

        11 - Total (R$):

        178,31

    Também aceita:

        Total (R$): 178,31

        Total: 178,31

        Valor Total: 178,31

    Retorna Decimal.
    """

    padroes = [

        # Formato real:
        #
        # Total (R$):
        # 178,31
        r"Total\s*\(\s*R\$\s*\)\s*:\s*([\d.,]+)",

        # Variação:
        #
        # Total (R$) 178,31
        r"Total\s*\(\s*R\$\s*\)\s*([\d.,]+)",

        # Total simples.
        r"Total\s*:\s*([\d.,]+)",

        # Valor Total.
        r"Valor\s+Total\s*:\s*([\d.,]+)",

    ]

    for padrao in padroes:

        match = re.search(
            padrao,
            texto,
            re.IGNORECASE
        )

        if not match:
            continue

        valor_texto = (
            match.group(1)
            .strip()
        )

        try:

            # Formato brasileiro:
            #
            # 1.234,56
            #
            # vira:
            #
            # 1234.56

            if "," in valor_texto:

                valor_texto = (
                    valor_texto
                    .replace(".", "")
                    .replace(",", ".")
                )

            valor = Decimal(
                valor_texto
            )

            return valor

        except InvalidOperation:

            continue

    return None


# =============================================================================
# LEITURA DO PDF
# =============================================================================

def extrair_texto_pdf(caminho_pdf):
    """
    Extrai todo o texto disponível no PDF.
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

    return normalizar_texto_pdf(
        "\n".join(textos)
    )


# =============================================================================
# EXTRAÇÃO COMPLETA
# =============================================================================

def extrair_dados_comprovante(caminho_pdf):
    """
    Lê um comprovante e extrai os campos necessários.
    """

    texto = extrair_texto_pdf(
        caminho_pdf
    )

    identificador = extrair_identificador(
        texto
    )

    competencia = extrair_competencia(
        texto
    )

    data = extrair_data_pagamento(
        texto
    )

    valor = extrair_valor(
        texto
    )

    return {

        "nit": identificador,

        "competencia": competencia,

        "data": data,

        "valor": valor,

        "texto": texto,

    }


# =============================================================================
# FORMATAÇÃO DO VALOR
# =============================================================================

def formatar_valor_nome(valor):
    """
    Formata o Decimal para utilização no nome do arquivo.

    Exemplo:

        Decimal("178.31")

    vira:

        178.31
    """

    if valor is None:

        return "SEM_VALOR"

    return f"{valor:.2f}"


# =============================================================================
# CRIAÇÃO DO NOME NORMALIZADO
# =============================================================================

def criar_nome_normalizado(dados):
    """
    Cria o nome padronizado:

        PAGAMENTO_GPS_<NIT>_<COMPETENCIA>_<DATA>_<VALOR>.pdf
    """

    nit = dados["nit"]

    competencia = dados["competencia"]

    data = dados["data"]

    valor = formatar_valor_nome(
        dados["valor"]
    )

    return (
        f"PAGAMENTO_GPS_"
        f"{nit}_"
        f"{competencia}_"
        f"{data}_"
        f"{valor}.pdf"
    )


# =============================================================================
# EVITAR SOBRESCRITA
# =============================================================================

def caminho_disponivel(caminho):
    """
    Retorna um caminho que ainda não existe.

    Se existir:

        arquivo.pdf

    tenta:

        arquivo_1.pdf
        arquivo_2.pdf
        ...
    """

    if not caminho.exists():

        return caminho

    contador = 1

    while True:

        novo_nome = (
            f"{caminho.stem}_{contador}"
            f"{caminho.suffix}"
        )

        novo_caminho = (
            caminho.parent
            / novo_nome
        )

        if not novo_caminho.exists():

            return novo_caminho

        contador += 1


# =============================================================================
# PROCESSAMENTO DE UM COMPROVANTE
# =============================================================================

def processar_comprovante(
    caminho_pdf,
    pasta_origem
):
    """
    Processa um único comprovante.

    O arquivo original nunca é alterado.
    """

    try:

        dados = extrair_dados_comprovante(
            caminho_pdf
        )

    except Exception as erro:

        return {

            "status": "ERRO",

            "origem": caminho_pdf,

            "pasta_origem": pasta_origem,

            "erro": str(erro),

        }

    # -------------------------------------------------------------------------
    # Verifica campos obrigatórios.
    # -------------------------------------------------------------------------

    campos_faltantes = []

    if not dados["nit"]:

        campos_faltantes.append(
            "IDENTIFICADOR"
        )

    if not dados["competencia"]:

        campos_faltantes.append(
            "COMPETENCIA"
        )

    if not dados["data"]:

        campos_faltantes.append(
            "DATA_PAGAMENTO"
        )

    if dados["valor"] is None:

        campos_faltantes.append(
            "VALOR"
        )

    # -------------------------------------------------------------------------
    # Se faltar algum campo, não copia.
    # -------------------------------------------------------------------------

    if campos_faltantes:

        return {

            "status": "PENDENTE",

            "origem": caminho_pdf,

            "pasta_origem": pasta_origem,

            "dados": dados,

            "campos_faltantes": campos_faltantes,

        }

    # -------------------------------------------------------------------------
    # Cria o nome normalizado.
    # -------------------------------------------------------------------------

    nome_normalizado = criar_nome_normalizado(
        dados
    )

    caminho_destino_base = (
        PASTA_NORMALIZADOS
        / nome_normalizado
    )

    # -------------------------------------------------------------------------
    # Evita sobrescrita.
    # -------------------------------------------------------------------------

    caminho_destino = caminho_disponivel(
        caminho_destino_base
    )

    # -------------------------------------------------------------------------
    # Copia o PDF original.
    # -------------------------------------------------------------------------

    shutil.copy2(
        caminho_pdf,
        caminho_destino
    )

    # -------------------------------------------------------------------------
    # Detecta duplicidade.
    # -------------------------------------------------------------------------

    duplicado = (
        caminho_destino != caminho_destino_base
    )

    return {

        "status": (
            "DUPLICADO"
            if duplicado
            else "OK"
        ),

        "origem": caminho_pdf,

        "pasta_origem": pasta_origem,

        "destino": caminho_destino,

        "dados": dados,

        "nome_base": nome_normalizado,

        "duplicado": duplicado,

    }


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================

def executar():
    """
    Executa o processamento completo das duas pastas.
    """

    print()
    print("=" * 78)
    print(" PREPARAÇÃO DOS COMPROVANTES GPS")
    print("=" * 78)
    print()

    print(
        f"Data/hora: {datetime.now():%d/%m/%Y %H:%M:%S}"
    )

    print()

    print("Projeto:")
    print(
        f"  {BASE_DIR}"
    )

    print()

    print("Origens:")
    print(
        f"  1. {PASTA1}"
    )
    print(
        f"  2. {PASTA2}"
    )

    print()

    print("Destino:")
    print(
        f"  {PASTA_NORMALIZADOS}"
    )

    print()

    print("=" * 78)
    print()

    # -------------------------------------------------------------------------
    # Cria a pasta de destino.
    # -------------------------------------------------------------------------

    PASTA_NORMALIZADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    # -------------------------------------------------------------------------
    # Contadores.
    # -------------------------------------------------------------------------

    resultados = []

    total_encontrados = 0

    total_ok = 0

    total_duplicados = 0

    total_pendentes = 0

    total_erros = 0

    # -------------------------------------------------------------------------
    # Processa cada pasta.
    # -------------------------------------------------------------------------

    for pasta in PASTAS_ORIGEM:

        print()
        print("-" * 78)
        print(
            f"📂 Processando: {pasta}"
        )
        print("-" * 78)

        if not pasta.exists():

            print(
                f"⚠️ Pasta não encontrada: {pasta}"
            )

            continue

        # ---------------------------------------------------------------------
        # rglob permite encontrar PDFs também em subpastas.
        #
        # Isso é importante caso a estrutura seja:
        #
        # pasta1/
        #     alguma_subpasta/
        #         comprovante0.pdf
        #
        # ---------------------------------------------------------------------

        arquivos = sorted(
            arquivo
            for arquivo in pasta.rglob("*")
            if (
                arquivo.is_file()
                and arquivo.suffix.lower() == EXTENSAO_PDF
            )
        )

        print(
            f"PDFs encontrados: {len(arquivos)}"
        )

        print()

        for arquivo in arquivos:

            total_encontrados += 1

            print(
                f"Processando: {arquivo.name}"
            )

            resultado = processar_comprovante(
                caminho_pdf=arquivo,
                pasta_origem=pasta,
            )

            resultados.append(
                resultado
            )

            status = resultado["status"]

            # -----------------------------------------------------------------
            # OK
            # -----------------------------------------------------------------

            if status == "OK":

                total_ok += 1

                dados = resultado["dados"]

                print(
                    "   ✅ OK"
                )

                print(
                    f"      Identificador: "
                    f"{dados['nit']}"
                )

                print(
                    f"      Competência  : "
                    f"{dados['competencia']}"
                )

                print(
                    f"      Data         : "
                    f"{dados['data']}"
                )

                print(
                    f"      Valor        : "
                    f"R$ {dados['valor']:.2f}"
                )

                print(
                    "      Destino      : "
                    f"{resultado['destino'].name}"
                )

            # -----------------------------------------------------------------
            # DUPLICADO
            # -----------------------------------------------------------------

            elif status == "DUPLICADO":

                total_duplicados += 1

                dados = resultado["dados"]

                print(
                    "   ⚠️ DUPLICADO"
                )

                print(
                    f"      Identificador: "
                    f"{dados['nit']}"
                )

                print(
                    f"      Competência  : "
                    f"{dados['competencia']}"
                )

                print(
                    f"      Data         : "
                    f"{dados['data']}"
                )

                print(
                    f"      Valor        : "
                    f"R$ {dados['valor']:.2f}"
                )

                print(
                    "      Destino      : "
                    f"{resultado['destino'].name}"
                )

            # -----------------------------------------------------------------
            # PENDENTE
            # -----------------------------------------------------------------

            elif status == "PENDENTE":

                total_pendentes += 1

                print(
                    "   ⚠️ PENDENTE"
                )

                print(
                    "      Campos não identificados:"
                )

                for campo in resultado[
                    "campos_faltantes"
                ]:

                    print(
                        f"         - {campo}"
                    )

            # -----------------------------------------------------------------
            # ERRO
            # -----------------------------------------------------------------

            else:

                total_erros += 1

                print(
                    "   ❌ ERRO: "
                    f"{resultado.get('erro', 'desconhecido')}"
                )

            print()

    # =========================================================================
    # RELATÓRIO
    # =========================================================================

    arquivo_relatorio = (
        PASTA_NORMALIZADOS
        / "RELATORIO_COMPROVANTES.txt"
    )

    linhas = []

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "RELATÓRIO DE PREPARAÇÃO DOS COMPROVANTES GPS"
    )

    linhas.append(
        "=" * 78
    )

    linhas.append(
        f"Data/hora: {datetime.now():%d/%m/%Y %H:%M:%S}"
    )

    linhas.append(
        f"Projeto: {BASE_DIR}"
    )

    linhas.append("")

    linhas.append(
        "ORIGENS"
    )

    linhas.append(
        f"1. {PASTA1}"
    )

    linhas.append(
        f"2. {PASTA2}"
    )

    linhas.append("")

    linhas.append(
        "DESTINO"
    )

    linhas.append(
        str(PASTA_NORMALIZADOS)
    )

    linhas.append("")

    linhas.append(
        "-" * 78
    )

    linhas.append(
        "CRITÉRIO DO IDENTIFICADOR"
    )

    linhas.append(
        "-" * 78
    )

    linhas.append(
        "O identificador é capturado integralmente."
    )

    linhas.append(
        "Zeros à esquerda são removidos somente na normalização."
    )

    linhas.append(
        "O identificador não é limitado a 11 dígitos."
    )

    linhas.append(
        "Exemplo: 00011331838821 -> 11331838821"
    )

    linhas.append("")

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
        f"PDFs encontrados : {total_encontrados}"
    )

    linhas.append(
        f"Processados OK   : {total_ok}"
    )

    linhas.append(
        f"Duplicados       : {total_duplicados}"
    )

    linhas.append(
        f"Pendentes        : {total_pendentes}"
    )

    linhas.append(
        f"Erros             : {total_erros}"
    )

    # =========================================================================
    # DETALHES
    # =========================================================================

    linhas.append("")

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "ARQUIVOS PROCESSADOS"
    )

    linhas.append(
        "=" * 78
    )

    for resultado in resultados:

        linhas.append(
            f"Origem : {resultado['origem']}"
        )

        linhas.append(
            f"Status : {resultado['status']}"
        )

        if resultado.get("destino"):

            linhas.append(
                f"Destino: {resultado['destino']}"
            )

        dados = resultado.get(
            "dados"
        )

        if dados:

            linhas.append(
                f"Identificador: "
                f"{dados.get('nit')}"
            )

            linhas.append(
                f"Competência  : "
                f"{dados.get('competencia')}"
            )

            linhas.append(
                f"Data         : "
                f"{dados.get('data')}"
            )

            valor = dados.get(
                "valor"
            )

            if valor is not None:

                linhas.append(
                    f"Valor        : "
                    f"R$ {valor:.2f}"
                )

        if resultado.get(
            "campos_faltantes"
        ):

            linhas.append(
                "Campos faltantes:"
            )

            for campo in resultado[
                "campos_faltantes"
            ]:

                linhas.append(
                    f"   - {campo}"
                )

        if resultado.get(
            "erro"
        ):

            linhas.append(
                f"Erro: {resultado['erro']}"
            )

        linhas.append(
            "-" * 78
        )

    # -------------------------------------------------------------------------
    # Grava relatório.
    # -------------------------------------------------------------------------

    with open(
        arquivo_relatorio,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(
            "\n".join(linhas)
        )

    # =========================================================================
    # RESUMO FINAL
    # =========================================================================

    print()

    print("=" * 78)

    print(
        " PROCESSAMENTO FINALIZADO"
    )

    print("=" * 78)

    print()

    print(
        f"📄 PDFs encontrados : "
        f"{total_encontrados}"
    )

    print(
        f"✅ Processados       : "
        f"{total_ok}"
    )

    print(
        f"⚠️ Duplicados        : "
        f"{total_duplicados}"
    )

    print(
        f"⚠️ Pendentes         : "
        f"{total_pendentes}"
    )

    print(
        f"❌ Erros             : "
        f"{total_erros}"
    )

    print()

    print(
        "📂 Comprovantes normalizados:"
    )

    print(
        f"   {PASTA_NORMALIZADOS}"
    )

    print()

    print(
        "📋 Relatório:"
    )

    print(
        f"   {arquivo_relatorio}"
    )

    print()

    print("=" * 78)

    print()


# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":

    executar()
