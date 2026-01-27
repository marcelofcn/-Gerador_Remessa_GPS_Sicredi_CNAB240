from app.layouts.utils import alfa, num

def gerar_header_lote_gps(
    *,
    lote: int,
    empresa: dict,
) -> str:

    linha = ""
    linha += num("748",3)
    linha += num(lote,4)
    linha += "1"
    linha += "C"
    linha += num("22",2)
    linha += num("17",2)
    linha += num("042",3)
    linha += alfa("",1)
    linha += num("2",1)
    linha += num(empresa["cnpj"],14)
    linha += alfa(empresa["convenio"],20)
    linha += num(empresa["agencia"],5)
    linha += alfa(empresa["dv_agencia"],1)
    linha += num(empresa["conta"],12)
    linha += alfa(empresa["dv_conta"],1)
    linha += alfa(" ",1)
    linha += alfa(empresa["razao_social"],30)
    linha += alfa("",40)
    linha += alfa("",30)
    linha += num("",5)
    linha += alfa("",15)
    linha += alfa("",20)
    linha += num("",5)
    linha += alfa("",3)
    linha += alfa("",2)
    linha += alfa("",8)
    linha += alfa("",10)

    assert len(linha) == 240
    return linha
