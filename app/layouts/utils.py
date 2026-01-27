def num(valor, tamanho):
    """
    Campo numérico:
    - alinhado à direita
    - preenchido com zeros à esquerda
    """
    if valor is None:
        valor = ""

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
