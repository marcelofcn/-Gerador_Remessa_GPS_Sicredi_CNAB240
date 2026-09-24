```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
ADMIN - CONSOLIDAR LOTE DE GPS
===============================================================================

Data de referência:
    23/09/2026

Objetivo:
    Unir cada Guia GPS (espelho) ao seu respectivo comprovante de pagamento
    bancário, gerando um único arquivo PDF por guia.

Fluxo:
    1. Localiza as guias em:
           output/espelhos/

    2. Localiza os comprovantes em:
           output/comprovantes/

       ou, opcionalmente, em:
           output/comprovantes_brutos/

    3. Identifica a guia pelo padrão:

           GUIA_GPS_<NIT>_<COMPETENCIA>.pdf

       Exemplo:

           GUIA_GPS_12345678901_082026.pdf

    4. Procura o comprovante correspondente pelo padrão:

           PAGAMENTO_GPS_<NIT>_<COMPETENCIA>_*.pdf

       Exemplo:

           PAGAMENTO_GPS_12345678901_082026_14_ago_1234.56.pdf

    5. Se houver exatamente UM comprovante correspondente:
           Guia + Comprovante -> PDF final

    6. Se não houver comprovante:
           registra como pendência.

    7. Se houver mais de um comprovante:
           NÃO escolhe automaticamente.
           Registra como ambiguidade para conferência manual.

    8. Gera relatório:

           output/guias_completas/RESUMO_LOTE.txt

===============================================================================

IMPORTANTE
===============================================================================

A correspondência principal é feita através de:

           NIT + COMPETÊNCIA

Isso evita depender de texto extraído do PDF ou de aproximação por nome.

O script NÃO altera as guias originais e NÃO altera os comprovantes.

Ele apenas cria os PDFs consolidados em:

           output/guias_completas/

===============================================================================
"""

from pathlib import Path
from datetime import datetime
import re
import shutil

from pypdf import PdfReader, PdfWriter


# =============================================================================
# CONFIGURAÇÃO DE DIRETÓRIOS
# =============================================================================

# Este arquivo está em:
#
# /home/house/developer/geraremessa/admin/consolidar_lote.py
#
# Portanto:
#
# parent        -> /home/house/developer/geraremessa/admin
# parent.parent -> /home/house/developer/geraremessa

BASE_DIR = Path(__file__).resolve().parent.parent


# -----------------------------------------------------------------------------
# Pasta onde estão as guias/espelhos
# -----------------------------------------------------------------------------

PASTA_GUIAS = BASE_DIR / "output" / "espelhos"


# -----------------------------------------------------------------------------
# Pasta onde estão os comprovantes já renomeados pelo gps_renomear.py
# -----------------------------------------------------------------------------

PASTA_COMPROVANTES = BASE_DIR / "output" / "comprovantes"


# -----------------------------------------------------------------------------
# Pasta alternativa para comprovantes brutos.
#
# Esta pasta será usada somente se PASTA_COMPROVANTES não existir ou
# não possuir PDFs.
# -----------------------------------------------------------------------------

PASTA_COMPROVANTES_BRUTOS = (
    BASE_DIR
    / "output"
    / "comprovantes_brutos"
)


# -----------------------------------------------------------------------------
# Pasta onde serão gravados os PDFs finais
# -----------------------------------------------------------------------------

PASTA_FINAL = (
    BASE_DIR
    / "output"
    / "guias_completas"
)


# =============================================================================
# CONFIGURAÇÕES DO PROCESSAMENTO
# =============================================================================

# Se True:
#
#   Quando o PDF final já existir, ele será substituído.
#
# Se False:
#
#   O arquivo existente será preservado e a guia será registrada como
#   "já existente".
#
# Recomendo deixar False durante os testes.
#

SOBRESCREVER_EXISTENTES = False


# -----------------------------------------------------------------------------
# Extensões aceitas
# -----------------------------------------------------------------------------

EXTENSAO_PDF = ".pdf"


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def imprimir_cabecalho():
    """
    Mostra na tela as informações principais da execução.
    """

    print()
    print("=" * 78)
    print(" CONSOLIDAÇÃO DE GUIAS GPS + COMPROVANTES")
    print("=" * 78)
    print()
    print(f"Data/hora da execução : {datetime.now():%d/%m/%Y %H:%M:%S}")
    print(f"Projeto               : {BASE_DIR}")
    print()
    print(f"Guias                 : {PASTA_GUIAS}")
    print(f"Comprovantes          : {PASTA_COMPROVANTES}")
    print(f"Brutos                : {PASTA_COMPROVANTES_BRUTOS}")
    print(f"Saída final           : {PASTA_FINAL}")
    print()
    print(f"Sobrescrever arquivos : {SOBRESCREVER_EXISTENTES}")
    print()
    print("=" * 78)
    print()


def obter_pasta_comprovantes():
    """
    Determina qual pasta de comprovantes será utilizada.

    Prioridade:

        1. output/comprovantes/
        2. output/comprovantes_brutos/

    A pasta escolhida precisa possuir pelo menos um PDF.
    """

    if PASTA_COMPROVANTES.exists():

        arquivos = list(
            PASTA_COMPROVANTES.glob("*.pdf")
        )

        if arquivos:
            return PASTA_COMPROVANTES

    if PASTA_COMPROVANTES_BRUTOS.exists():

        arquivos = list(
            PASTA_COMPROVANTES_BRUTOS.glob("*.pdf")
        )

        if arquivos:
            return PASTA_COMPROVANTES_BRUTOS

    return None


def extrair_chave_guia(nome_arquivo):
    """
    Extrai NIT e competência do nome da guia.

    Formato esperado:

        GUIA_GPS_<NIT>_<COMPETENCIA>.pdf

    Exemplo:

        GUIA_GPS_12345678901_082026.pdf

    Retorno:

        {
            "nit": "12345678901",
            "competencia": "082026",
            "chave": "12345678901_082026"
        }

    Caso o nome não esteja no padrão esperado, retorna None.
    """

    padrao = re.compile(
        r"^GUIA_GPS_(\d{11})_(\d{6})\.pdf$",
        re.IGNORECASE
    )

    match = padrao.match(nome_arquivo)

    if not match:
        return None

    nit = match.group(1)
    competencia = match.group(2)

    return {
        "nit": nit,
        "competencia": competencia,
        "chave": f"{nit}_{competencia}",
    }


def extrair_chave_comprovante(nome_arquivo):
    """
    Extrai NIT e competência do nome do comprovante.

    Formato esperado:

        PAGAMENTO_GPS_<NIT>_<COMPETENCIA>_*.pdf

    Exemplo:

        PAGAMENTO_GPS_12345678901_082026_14_ago_1234.56.pdf

    Retorno:

        {
            "nit": "12345678901",
            "competencia": "082026",
            "chave": "12345678901_082026"
        }

    Caso o nome não esteja no padrão esperado, retorna None.
    """

    padrao = re.compile(
        r"^PAGAMENTO_GPS_(\d{11})_(\d{6})_.*\.pdf$",
        re.IGNORECASE
    )

    match = padrao.match(nome_arquivo)

    if not match:
        return None

    nit = match.group(1)
    competencia = match.group(2)

    return {
        "nit": nit,
        "competencia": competencia,
        "chave": f"{nit}_{competencia}",
    }


def listar_guias():
    """
    Localiza todas as guias PDF.

    É utilizado rglob() para permitir que existam subpastas dentro de:

        output/espelhos/

    Exemplo:

        output/espelhos/
        output/espelhos/GPS_RETROATIVO_CORRIGIDO/
        output/espelhos/outro_lote/

    Todas serão pesquisadas.
    """

    if not PASTA_GUIAS.exists():
        return []

    return sorted(
        PASTA_GUIAS.rglob("GUIA_GPS_*.pdf")
    )


def listar_comprovantes(pasta):
    """
    Localiza todos os comprovantes PDF da pasta informada.
    """

    if not pasta.exists():
        return []

    return sorted(
        pasta.glob("*.pdf")
    )


def mapear_comprovantes(comprovantes):
    """
    Cria um índice dos comprovantes utilizando:

        NIT + competência

    Exemplo de estrutura:

        {
            "12345678901_082026": [
                Path("PAGAMENTO_GPS_12345678901_082026_14_ago_1234.56.pdf")
            ]
        }

    Se houver dois comprovantes para a mesma chave, os dois ficam no índice.

    Isso é proposital.

    A função NÃO escolhe um deles.
    A decisão de ambiguidade será feita durante a consolidação.
    """

    mapa = {}

    ignorados = []

    for comprovante in comprovantes:

        dados = extrair_chave_comprovante(
            comprovante.name
        )

        if not dados:

            ignorados.append(comprovante)

            continue

        chave = dados["chave"]

        mapa.setdefault(
            chave,
            []
        ).append(comprovante)

    return mapa, ignorados


def criar_pdf_consolidado(guia, comprovante, arquivo_final):
    """
    Cria o PDF final:

        GUIA + COMPROVANTE

    Todas as páginas da guia são adicionadas primeiro.

    Depois todas as páginas do comprovante.

    Exemplo:

        [Página 1 - Guia]
        [Página 2 - Guia]
        [Página 3 - Comprovante]
        [Página 4 - Comprovante]

    Retorna True em caso de sucesso.
    """

    try:

        writer = PdfWriter()

        # ---------------------------------------------------------------------
        # Adiciona as páginas da guia
        # ---------------------------------------------------------------------

        reader_guia = PdfReader(
            str(guia)
        )

        for pagina in reader_guia.pages:
            writer.add_page(pagina)

        # ---------------------------------------------------------------------
        # Adiciona as páginas do comprovante
        # ---------------------------------------------------------------------

        reader_comprovante = PdfReader(
            str(comprovante)
        )

        for pagina in reader_comprovante.pages:
            writer.add_page(pagina)

        # ---------------------------------------------------------------------
        # Grava o arquivo final
        # ---------------------------------------------------------------------

        with open(
            arquivo_final,
            "wb"
        ) as arquivo:

            writer.write(arquivo)

        return True

    except Exception as erro:

        print()
        print(
            f"❌ Erro ao juntar PDFs:"
        )
        print(
            f"   Guia       : {guia.name}"
        )
        print(
            f"   Comprovante: {comprovante.name}"
        )
        print(
            f"   Erro       : {erro}"
        )
        print()

        return False


def nome_arquivo_final(guia):
    """
    Define o nome do PDF consolidado.

    A partir de:

        GUIA_GPS_12345678901_082026.pdf

    gera:

        GUIA_GPS_12345678901_082026_COMPLETO.pdf
    """

    return (
        guia.parent
        / f"{guia.stem}_COMPLETO.pdf"
    )


# =============================================================================
# PROCESSAMENTO PRINCIPAL
# =============================================================================

def executar_consolidacao():
    """
    Executa todo o processo de consolidação.
    """

    imprimir_cabecalho()

    # -------------------------------------------------------------------------
    # Cria pasta de saída
    # -------------------------------------------------------------------------

    PASTA_FINAL.mkdir(
        parents=True,
        exist_ok=True
    )

    # -------------------------------------------------------------------------
    # Determina a pasta dos comprovantes
    # -------------------------------------------------------------------------

    pasta_comprovantes = obter_pasta_comprovantes()

    if pasta_comprovantes is None:

        print(
            "❌ Nenhum diretório de comprovantes válido foi encontrado."
        )

        print()
        print(
            f"Verifique:"
        )
        print(
            f"   {PASTA_COMPROVANTES}"
        )
        print(
            f"   {PASTA_COMPROVANTES_BRUTOS}"
        )
        print()

        return

    # -------------------------------------------------------------------------
    # Busca guias
    # -------------------------------------------------------------------------

    guias = listar_guias()

    # -------------------------------------------------------------------------
    # Busca comprovantes
    # -------------------------------------------------------------------------

    comprovantes = listar_comprovantes(
        pasta_comprovantes
    )

    if not guias:

        print(
            "❌ Nenhuma guia encontrada."
        )

        print(
            f"   Pasta pesquisada: {PASTA_GUIAS}"
        )

        return

    if not comprovantes:

        print(
            "❌ Nenhum comprovante encontrado."
        )

        print(
            f"   Pasta pesquisada: {pasta_comprovantes}"
        )

        return

    # -------------------------------------------------------------------------
    # Mostra resumo inicial
    # -------------------------------------------------------------------------

    print(
        f"📄 Guias encontradas        : {len(guias)}"
    )

    print(
        f"🧾 Comprovantes encontrados : {len(comprovantes)}"
    )

    print(
        f"📂 Pasta de comprovantes    : {pasta_comprovantes}"
    )

    print()

    # -------------------------------------------------------------------------
    # Mapeia os comprovantes pela chave NIT + competência
    # -------------------------------------------------------------------------

    mapa_comprovantes, comprovantes_ignorados = (
        mapear_comprovantes(
            comprovantes
        )
    )

    # -------------------------------------------------------------------------
    # Controle de comprovantes já utilizados
    #
    # Isto impede que o mesmo comprovante seja associado a duas guias.
    # -------------------------------------------------------------------------

    comprovantes_utilizados = set()

    # -------------------------------------------------------------------------
    # Contadores
    # -------------------------------------------------------------------------

    total_guias = len(guias)

    consolidados = 0
    sem_comprovante = 0
    multiplos_comprovantes = 0
    nomes_invalidos = 0
    ja_existentes = 0
    erros = 0

    valor_nao_aplicavel = 0

    # -------------------------------------------------------------------------
    # Listas para relatório
    # -------------------------------------------------------------------------

    pendencias = []
    ambiguidades = []
    invalidos = []
    existentes = []
    erros_processamento = []

    # =========================================================================
    # PROCESSA CADA GUIA
    # =========================================================================

    for indice, guia in enumerate(
        guias,
        start=1
    ):

        print(
            f"[{indice}/{total_guias}] "
            f"Processando: {guia.name}"
        )

        # ---------------------------------------------------------------------
        # Extrai NIT + competência do nome
        # ---------------------------------------------------------------------

        dados_guia = extrair_chave_guia(
            guia.name
        )

        if not dados_guia:

            nomes_invalidos += 1

            invalidos.append(
                guia.name
            )

            print(
                "   ⚠️ Nome da guia fora do padrão esperado."
            )

            print()

            continue

        chave = dados_guia["chave"]

        nit = dados_guia["nit"]

        competencia = dados_guia["competencia"]

        # ---------------------------------------------------------------------
        # Procura comprovantes para a mesma chave
        # ---------------------------------------------------------------------

        candidatos = mapa_comprovantes.get(
            chave,
            []
        )

        # ---------------------------------------------------------------------
        # Remove candidatos que já foram utilizados
        # ---------------------------------------------------------------------

        candidatos_disponiveis = [
            comprovante
            for comprovante in candidatos
            if comprovante.resolve()
            not in comprovantes_utilizados
        ]

        # ---------------------------------------------------------------------
        # Nenhum comprovante
        # ---------------------------------------------------------------------

        if not candidatos_disponiveis:

            sem_comprovante += 1

            pendencias.append(
                {
                    "guia": guia.name,
                    "nit": nit,
                    "competencia": competencia,
                    "motivo": "Nenhum comprovante correspondente encontrado.",
                }
            )

            print(
                f"   ❌ Sem comprovante"
            )

            print()

            continue

        # ---------------------------------------------------------------------
        # Mais de um comprovante
        # ---------------------------------------------------------------------

        if len(candidatos_disponiveis) > 1:

            multiplos_comprovantes += 1

            lista_nomes = [
                item.name
                for item in candidatos_disponiveis
            ]

            ambiguidades.append(
                {
                    "guia": guia.name,
                    "nit": nit,
                    "competencia": competencia,
                    "comprovantes": lista_nomes,
                }
            )

            print(
                f"   ⚠️ {len(candidatos_disponiveis)} "
                f"comprovantes encontrados."
            )

            print(
                "   ❌ Consolidação não realizada para esta guia."
            )

            for item in candidatos_disponiveis:

                print(
                    f"      - {item.name}"
                )

            print()

            continue

        # ---------------------------------------------------------------------
        # Exatamente um comprovante
        # ---------------------------------------------------------------------

        comprovante = candidatos_disponiveis[0]

        arquivo_final = (
            PASTA_FINAL
            / f"{guia.stem}_COMPLETO.pdf"
        )

        # ---------------------------------------------------------------------
        # Verifica se o arquivo final já existe
        # ---------------------------------------------------------------------

        if arquivo_final.exists():

            if not SOBRESCREVER_EXISTENTES:

                ja_existentes += 1

                existentes.append(
                    {
                        "guia": guia.name,
                        "arquivo": arquivo_final.name,
                    }
                )

                # -----------------------------------------------------------------
                # IMPORTANTE:
                #
                # O comprovante não é marcado como utilizado aqui porque não
                # criamos um novo arquivo nesta execução.
                # -----------------------------------------------------------------

                print(
                    f"   ⏭️ Já existe: {arquivo_final.name}"
                )

                print()

                continue

        # ---------------------------------------------------------------------
        # Junta os PDFs
        # ---------------------------------------------------------------------

        sucesso = criar_pdf_consolidado(
            guia=guia,
            comprovante=comprovante,
            arquivo_final=arquivo_final,
        )

        if not sucesso:

            erros += 1

            erros_processamento.append(
                {
                    "guia": guia.name,
                    "comprovante": comprovante.name,
                    "erro": "Falha durante a criação do PDF consolidado.",
                }
            )

            print()

            continue

        # ---------------------------------------------------------------------
        # Marca comprovante como utilizado
        # ---------------------------------------------------------------------

        comprovantes_utilizados.add(
            comprovante.resolve()
        )

        # ---------------------------------------------------------------------
        # Sucesso
        # ---------------------------------------------------------------------

        consolidados += 1

        print(
            f"   ✅ Consolidado"
        )

        print(
            f"      Guia       : {guia.name}"
        )

        print(
            f"      Comprovante: {comprovante.name}"
        )

        print(
            f"      Resultado  : {arquivo_final.name}"
        )

        print()

    # =========================================================================
    # RELATÓRIO FINAL
    # =========================================================================

    data_execucao = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    linhas = []

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "RELATÓRIO DE CONSOLIDAÇÃO DE GUIAS GPS"
    )

    linhas.append(
        "=" * 78
    )

    linhas.append(
        f"Data/hora da execução : {data_execucao}"
    )

    linhas.append(
        f"Projeto               : {BASE_DIR}"
    )

    linhas.append(
        f"Pasta das guias       : {PASTA_GUIAS}"
    )

    linhas.append(
        f"Pasta dos comprovantes: {pasta_comprovantes}"
    )

    linhas.append(
        f"Pasta de saída        : {PASTA_FINAL}"
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
        f"Total de guias encontradas       : {total_guias}"
    )

    linhas.append(
        f"Consolidadas com sucesso         : {consolidados}"
    )

    linhas.append(
        f"Sem comprovante                  : {sem_comprovante}"
    )

    linhas.append(
        f"Com múltiplos comprovantes      : {multiplos_comprovantes}"
    )

    linhas.append(
        f"Nome de guia inválido            : {nomes_invalidos}"
    )

    linhas.append(
        f"PDFs já existentes               : {ja_existentes}"
    )

    linhas.append(
        f"Erros durante processamento      : {erros}"
    )

    linhas.append(
        f"Comprovantes sem padrão de nome : {len(comprovantes_ignorados)}"
    )

    linhas.append(
        ""
    )

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "PENDÊNCIAS - SEM COMPROVANTE"
    )

    linhas.append(
        "=" * 78
    )

    if pendencias:

        for item in pendencias:

            linhas.append(
                f"Guia       : {item['guia']}"
            )

            linhas.append(
                f"NIT        : {item['nit']}"
            )

            linhas.append(
                f"Competência: {item['competencia']}"
            )

            linhas.append(
                f"Motivo     : {item['motivo']}"
            )

            linhas.append(
                "-" * 78
            )

    else:

        linhas.append(
            "Nenhuma pendência."
        )

    linhas.append(
        ""
    )

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "AMBIGUIDADES - MAIS DE UM COMPROVANTE"
    )

    linhas.append(
        "=" * 78
    )

    if ambiguidades:

        for item in ambiguidades:

            linhas.append(
                f"Guia       : {item['guia']}"
            )

            linhas.append(
                f"NIT        : {item['nit']}"
            )

            linhas.append(
                f"Competência: {item['competencia']}"
            )

            linhas.append(
                "Comprovantes encontrados:"
            )

            for nome in item["comprovantes"]:

                linhas.append(
                    f"   - {nome}"
                )

            linhas.append(
                "-" * 78
            )

    else:

        linhas.append(
            "Nenhuma ambiguidade."
        )

    linhas.append(
        ""
    )

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "GUIAS COM NOME FORA DO PADRÃO"
    )

    linhas.append(
        "=" * 78
    )

    if invalidos:

        for nome in invalidos:

            linhas.append(
                f"- {nome}"
            )

    else:

        linhas.append(
            "Nenhuma."
        )

    linhas.append(
        ""
    )

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "PDFs QUE JÁ EXISTIAM"
    )

    linhas.append(
        "=" * 78
    )

    if existentes:

        for item in existentes:

            linhas.append(
                f"Guia   : {item['guia']}"
            )

            linhas.append(
                f"Arquivo: {item['arquivo']}"
            )

            linhas.append(
                "-" * 78
            )

    else:

        linhas.append(
            "Nenhum."
        )

    linhas.append(
        ""
    )

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "COMPROVANTES IGNORADOS"
    )

    linhas.append(
        "=" * 78
    )

    if comprovantes_ignorados:

        for comprovante in comprovantes_ignorados:

            linhas.append(
                f"- {comprovante.name}"
            )

    else:

        linhas.append(
            "Nenhum."
        )

    linhas.append(
        ""
    )

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "ERROS"
    )

    linhas.append(
        "=" * 78
    )

    if erros_processamento:

        for item in erros_processamento:

            linhas.append(
                f"Guia       : {item['guia']}"
            )

            linhas.append(
                f"Comprovante: {item['comprovante']}"
            )

            linhas.append(
                f"Erro       : {item['erro']}"
            )

            linhas.append(
                "-" * 78
            )

    else:

        linhas.append(
            "Nenhum erro."
        )

    linhas.append(
        ""
    )

    linhas.append(
        "=" * 78
    )

    linhas.append(
        "FIM DO RELATÓRIO"
    )

    linhas.append(
        "=" * 78
    )

    # -------------------------------------------------------------------------
    # Salva relatório
    # -------------------------------------------------------------------------

    arquivo_relatorio = (
        PASTA_FINAL
        / "RESUMO_LOTE.txt"
    )

    with open(
        arquivo_relatorio,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(
            "\n".join(linhas)
        )

    # =========================================================================
    # RESUMO NA TELA
    # =========================================================================

    print()
    print("=" * 78)
    print(" PROCESSAMENTO FINALIZADO")
    print("=" * 78)
    print()
    print(
        f"📄 Guias encontradas       : {total_guias}"
    )
    print(
        f"✅ Consolidadas            : {consolidados}"
    )
    print(
        f"❌ Sem comprovante         : {sem_comprovante}"
    )
    print(
        f"⚠️ Múltiplos comprovantes : {multiplos_comprovantes}"
    )
    print(
        f"⚠️ Nome inválido           : {nomes_invalidos}"
    )
    print(
        f"⏭️ Já existentes           : {ja_existentes}"
    )
    print(
        f"❌ Erros                   : {erros}"
    )
    print()
    print(
        f"📂 Saída:"
    )
    print(
        f"   {PASTA_FINAL}"
    )
    print()
    print(
        f"📋 Relatório:"
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
    executar_consolidacao()
```
