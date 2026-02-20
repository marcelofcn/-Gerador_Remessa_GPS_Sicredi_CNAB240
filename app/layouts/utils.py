"""
===============================================================
PROJETO: Sistema de Remessa CNAB GPS - SICREDI
EMPRESA: Associação Internacional Privada de Fiéis
Comunidade Canção Nova - AIPF
CONVÊNIO: 6XDZ

ARQUIVO:app/layouts/utils.py 

VERSÃO: 2.1.0
DATA: 18/02/2026
HORA: 18:40
AMBIENTE: Ubuntu 22.04

"""
from decimal import Decimal, ROUND_HALF_UP

def num(valor, tamanho):
    """
    Campo numérico:
    - alinhado à direita
    - preenchido com zeros à esquerda
    - aceita int ou Decimal (centavos)
    """
    if valor is None:
        valor = 0

    if isinstance(valor, Decimal):
        valor = int(valor)

    valor_str = str(valor)
    # remove qualquer caractere não numérico
    valor_str = "".join(filter(str.isdigit, valor_str))
    return valor_str.zfill(tamanho)[:tamanho]

def alfa(valor, tamanho):
    """
    Campo alfanumérico:
    - alinhado à esquerda
    - preenchido com espaços à direita
    """
    if valor is None:
        valor = ""
    valor_str = str(valor).upper()
    return valor_str.ljust(tamanho)[:tamanho]

def to_centavos(valor):
    """
    Converte float ou string para inteiro em centavos, usando arredondamento correto.
    """
    return int((Decimal(str(valor)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
