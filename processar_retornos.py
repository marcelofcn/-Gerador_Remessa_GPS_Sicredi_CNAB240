"""
PROCESSAMENTO AUTOMÁTICO DE RETORNOS BANCÁRIOS (SICREDI)
--------------------------------------------------------
Versão: 3.0.0
Status: PRODUÇÃO
Data de Atualização: 2026-08-18
Responsabilidades:
- Monitorar pasta retorno/input
- Processar arquivos .RET
- Utilizar a classificação oficial G099 fornecida pelo leitor
- Separar pagamentos por situação
- Gerar relatório executivo resumo.txt
- Preservar códigos e descrições das ocorrências
- Mover arquivo para processed com segurança

Arquitetura:

Arquivo .RET
     ↓
LeitorRetornoSicredi
     ↓
código G099
     ↓
descrição oficial
     ↓
situação oficial
     ↓
relatório executivo
"""

import time
import shutil
from pathlib import Path
from datetime import datetime
from decimal import Decimal

from app.services.retorno.leitor_retorno import LeitorRetornoSicredi


# ============================================================
# CONFIGURAÇÕES DE CAMINHO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_RET = BASE_DIR / "retorno" / "input"
PROC_RET = BASE_DIR / "retorno" / "processed"

EMPRESA_NOME = "Comunidade Canção Nova"


# ============================================================
# INTERFACE VISUAL
# ============================================================

def splash_screen():
    """Exibe o cabeçalho do sistema no terminal."""

    azul = "\033[1;34m"
    amarelo = "\033[1;33m"
    reset = "\033[0m"

    print(f"{azul}" + "_" * 62)
    print(
        f"|{amarelo}   ____ _   _   ____                                         {azul}|"
    )
    print(
        f"|{amarelo}  / ___| \\ | | |  _ \\ ___ _ __ ___   ___  ___ ___  __ _      {azul}|"
    )
    print(
        f"|{amarelo} | |   |  \\| | | |_) / _ \\ '_ ` _ \\ / _ \\/ __/ __|/ _` |     {azul}|"
    )
    print(
        f"|{amarelo} | |___| |\\  | |  _ <  __/ | | | | |  __/\\__ \\__ \\ (_| |     {azul}|"
    )
    print(
        f"|{amarelo}  \\____|_| \\_| |_| \\_\\___|_| |_| |_|\\___||___/___/\\__,_|     {azul}|"
    )
    print(f"|{azul}" + "_" * 62 + "|")

    print(
        f"\n{amarelo}"
        "       SISTEMA DE REMESSA DIGITAL | CANÇÃO NOVA & SICREDI"
        f"{reset}"
    )

    print(
        f"{azul}"
        "         Módulo: RETORNO (Feedback) | Status: ATIVO"
        f"{reset}\n"
    )


# ============================================================
# FORMATAÇÃO DE VALORES
# ============================================================

def formatar_valor(valor):
    """
    Formata valor monetário no padrão brasileiro.

    Exemplo:
        1234.56 -> R$ 1.234,56
    """

    try:
        valor_decimal = Decimal(str(valor))
    except Exception:
        valor_decimal = Decimal("0.00")

    texto = f"{valor_decimal:,.2f}"

    # Converte padrão americano para brasileiro
    texto = texto.replace(",", "X")
    texto = texto.replace(".", ",")
    texto = texto.replace("X", ".")

    return f"R$ {texto}"


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar_resultados(resultados):
    """
    Separa os registros exclusivamente pela situação oficial
    determinada pelo LeitorRetornoSicredi.

    NÃO utiliza palavras da descrição para determinar situação.

    Retorna um dicionário com as categorias:
        paga
        agendada
        rejeitada
        excluida
        pendente_analise
    """

    grupos = {
        "paga": [],
        "agendada": [],
        "rejeitada": [],
        "excluida": [],
        "pendente_analise": [],
    }

    for resultado in resultados:

        situacao = resultado.get(
            "situacao",
            "pendente_analise"
        )

        if situacao not in grupos:
            situacao = "pendente_analise"

        grupos[situacao].append(resultado)

    return grupos


# ============================================================
# SOMATÓRIO
# ============================================================

def somar_valores(registros):
    """
    Soma os valores dos registros utilizando Decimal.
    """

    total = Decimal("0.00")

    for registro in registros:

        valor = registro.get(
            "valor_decimal",
            registro.get("valor", 0)
        )

        try:
            total += Decimal(str(valor))
        except Exception:
            continue

    return total


# ============================================================
# RELATÓRIO EXECUTIVO
# ============================================================

def gerar_resumo_txt(
    empresa,
    arquivo_retorno,
    resultados,
    grupos,
    caminho_saida
):
    """
    Gera o relatório executivo do arquivo de retorno.

    O relatório é baseado na situação oficial determinada
    pelo LeitorRetornoSicredi.
    """

    total = len(resultados)

    pagos = grupos["paga"]
    agendados = grupos["agendada"]
    rejeitados = grupos["rejeitada"]
    excluidos = grupos["excluida"]
    pendentes = grupos["pendente_analise"]

    total_pago = somar_valores(pagos)
    total_agendado = somar_valores(agendados)
    total_rejeitado = somar_valores(rejeitados)
    total_excluido = somar_valores(excluidos)
    total_pendente = somar_valores(pendentes)

    total_financeiro = (
        total_pago
        + total_agendado
        + total_rejeitado
        + total_excluido
        + total_pendente
    )

    percentual_pago = (
        len(pagos) / total * 100
        if total
        else 0
    )

    percentual_agendado = (
        len(agendados) / total * 100
        if total
        else 0
    )

    percentual_rejeitado = (
        len(rejeitados) / total * 100
        if total
        else 0
    )

    percentual_excluido = (
        len(excluidos) / total * 100
        if total
        else 0
    )

    percentual_pendente = (
        len(pendentes) / total * 100
        if total
        else 0
    )

    with open(
        caminho_saida,
        "w",
        encoding="utf-8"
    ) as f:

        # ====================================================
        # CABEÇALHO
        # ====================================================

        f.write("=" * 80 + "\n")
        f.write("RELATÓRIO DE RETORNO BANCÁRIO - SICREDI\n")
        f.write("=" * 80 + "\n")
        f.write(f"EMPRESA              : {empresa}\n")
        f.write(f"ARQUIVO DE RETORNO   : {arquivo_retorno}\n")
        f.write(
            "DATA DO PROCESSAMENTO: "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        )
        f.write("=" * 80 + "\n\n")

        # ====================================================
        # RESUMO GERAL
        # ====================================================

        f.write("RESUMO GERAL\n")
        f.write("-" * 80 + "\n")

        f.write(
            f"Total de Registros Processados : {total}\n"
        )

        f.write(
            f"Valor Financeiro Total         : "
            f"{formatar_valor(total_financeiro)}\n"
        )

        f.write("\n")

        # ====================================================
        # SITUAÇÕES
        # ====================================================

        f.write("SITUAÇÃO DOS PAGAMENTOS\n")
        f.write("-" * 80 + "\n")

        f.write(
            f"✅ Pagamentos Confirmados       : "
            f"{len(pagos):>6} "
            f"({percentual_pago:6.2f}%)"
            f"   {formatar_valor(total_pago)}\n"
        )

        f.write(
            f"⏳ Pagamentos Agendados         : "
            f"{len(agendados):>6} "
            f"({percentual_agendado:6.2f}%)"
            f"   {formatar_valor(total_agendado)}\n"
        )

        f.write(
            f"❌ Pagamentos Rejeitados        : "
            f"{len(rejeitados):>6} "
            f"({percentual_rejeitado:6.2f}%)"
            f"   {formatar_valor(total_rejeitado)}\n"
        )

        f.write(
            f"🚫 Pagamentos Excluídos         : "
            f"{len(excluidos):>6} "
            f"({percentual_excluido:6.2f}%)"
            f"   {formatar_valor(total_excluido)}\n"
        )

        f.write(
            f"⚠️ Pendentes de Análise         : "
            f"{len(pendentes):>6} "
            f"({percentual_pendente:6.2f}%)"
            f"   {formatar_valor(total_pendente)}\n"
        )

        f.write("\n")
        f.write("-" * 80 + "\n\n")

        # ====================================================
        # OCORRÊNCIAS
        # ====================================================

        registros_com_ocorrencia = [
            r
            for r in resultados
            if r.get("ocorrencias")
        ]

        if registros_com_ocorrencia:

            f.write("DETALHAMENTO DAS OCORRÊNCIAS G099\n")
            f.write("-" * 80 + "\n\n")

            for r in registros_com_ocorrencia:

                f.write(
                    f"Linha do arquivo : {r.get('linha', '')}\n"
                )

                f.write(
                    f"Contribuinte      : "
                    f"{r.get('nome', '')}\n"
                )

                f.write(
                    f"Valor             : "
                    f"{formatar_valor(r.get('valor', 0))}\n"
                )

                f.write(
                    f"Situação          : "
                    f"{r.get('situacao', '')}\n"
                )

                codigos = r.get("codigos", [])

                f.write(
                    f"Códigos G099      : "
                    f"{', '.join(codigos) if codigos else 'Nenhum'}\n"
                )

                f.write("Ocorrências:\n")

                ocorrencias = r.get(
                    "ocorrencias",
                    []
                )

                for ocorrencia in ocorrencias:

                    f.write(
                        f"  - "
                        f"{ocorrencia.get('codigo', '')} | "
                        f"{ocorrencia.get('descricao', '')} | "
                        f"situação: "
                        f"{ocorrencia.get('situacao', '')}\n"
                    )

                f.write("\n")
                f.write("-" * 60 + "\n\n")

        else:

            f.write(
                "DETALHAMENTO DAS OCORRÊNCIAS G099\n"
            )
            f.write("-" * 80 + "\n")
            f.write(
                "Nenhuma ocorrência G099 informada nos registros.\n\n"
            )

        # ====================================================
        # RESUMO POR CÓDIGO
        # ====================================================

        contagem_codigos = {}

        for r in resultados:

            for ocorrencia in r.get(
                "ocorrencias",
                []
            ):

                codigo = ocorrencia.get(
                    "codigo",
                    ""
                )

                descricao = ocorrencia.get(
                    "descricao",
                    ""
                )

                situacao = ocorrencia.get(
                    "situacao",
                    ""
                )

                chave = (
                    codigo,
                    descricao,
                    situacao
                )

                contagem_codigos[chave] = (
                    contagem_codigos.get(chave, 0)
                    + 1
                )

        f.write("\n")
        f.write("RESUMO POR CÓDIGO G099\n")
        f.write("-" * 80 + "\n")

        if contagem_codigos:

            for (
                codigo,
                descricao,
                situacao
            ), quantidade in sorted(
                contagem_codigos.items()
            ):

                f.write(
                    f"{codigo:>3} | "
                    f"{quantidade:>6} ocorrência(s) | "
                    f"{situacao:<18} | "
                    f"{descricao}\n"
                )

        else:

            f.write(
                "Nenhum código G099 informado.\n"
            )

        # ====================================================
        # RODAPÉ
        # ====================================================

        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write(
            "CLASSIFICAÇÃO BASEADA NA TABELA OFICIAL G099 - SICREDI\n"
        )
        f.write(
            "Códigos e ocorrências preservados para auditoria.\n"
        )
        f.write("=" * 80 + "\n")


# ============================================================
# PROCESSAMENTO DE UM ARQUIVO
# ============================================================

def processar_arquivo_retorno(arquivo):
    """
    Processa um único arquivo .RET.
    """

    print(f"📄 Arquivo: {arquivo.name}")

    # --------------------------------------------------------
    # 1. LEITURA
    # --------------------------------------------------------

    resultados = (
        LeitorRetornoSicredi.processar_arquivo(
            str(arquivo)
        )
    )

    print(
        f"📊 Registros Segmento N encontrados: "
        f"{len(resultados)}"
    )

    # --------------------------------------------------------
    # 2. CLASSIFICAÇÃO OFICIAL
    # --------------------------------------------------------

    grupos = classificar_resultados(
        resultados
    )

    print(
        f"   paga: {len(grupos['paga'])}"
    )

    print(
        f"   agendada: {len(grupos['agendada'])}"
    )

    print(
        f"   rejeitada: {len(grupos['rejeitada'])}"
    )

    print(
        f"   excluida: {len(grupos['excluida'])}"
    )

    print(
        f"   pendente_analise: "
        f"{len(grupos['pendente_analise'])}"
    )

    # --------------------------------------------------------
    # 3. RELATÓRIO
    # --------------------------------------------------------

    resumo_path = (
        PROC_RET
        / f"resumo_{arquivo.stem}.txt"
    )

    gerar_resumo_txt(
        empresa=EMPRESA_NOME,
        arquivo_retorno=arquivo.name,
        resultados=resultados,
        grupos=grupos,
        caminho_saida=str(resumo_path)
    )

    # --------------------------------------------------------
    # 4. MOVER ARQUIVO PARA PROCESSED
    # --------------------------------------------------------

    destino = PROC_RET / arquivo.name

    if destino.exists():

        sufixo = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        destino = (
            PROC_RET
            / f"{arquivo.stem}_{sufixo}{arquivo.suffix}"
        )

    shutil.move(
        str(arquivo),
        str(destino)
    )

    print(
        "[RETORNO | SUCESSO] "
        "Processado com relatório gerado."
    )

    print(
        f"📄 Relatório: {resumo_path.name}"
    )

    print(
        f"📦 RET movido para: {destino.name}"
    )

    print("-" * 60)


# ============================================================
# MONITORAMENTO
# ============================================================

def monitorar():

    print(
        f"[RETORNO] Monitorando pasta: "
        f"{INPUT_RET}"
    )

    while True:

        arquivos = list(
            INPUT_RET.glob("*.[Rr][Ee][Tt]")
        )

        for arquivo in arquivos:

            timestamp = datetime.now().strftime(
                "%H:%M:%S"
            )

            try:

                print("\n" + "-" * 60)

                print(
                    f"[{timestamp}] "
                    "NOVO RETORNO DETECTADO"
                )

                processar_arquivo_retorno(
                    arquivo
                )

            except Exception as e:

                print(
                    "\n[RETORNO | ❌ ERRO] "
                    f"Falha no arquivo: {arquivo.name}"
                )

                print(
                    f"Motivo: {str(e)}"
                )

        time.sleep(5)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    INPUT_RET.mkdir(
        parents=True,
        exist_ok=True
    )

    PROC_RET.mkdir(
        parents=True,
        exist_ok=True
    )

    splash_screen()

    try:

        monitorar()

    except KeyboardInterrupt:

        print(
            "\n[RETORNO] "
            "Sistema encerrado pelo usuário."
        )

    except Exception as e:

        print(
            f"\n[SISTEMA] Erro fatal: {e}"
        )