class LeitorRetornoSicredi:
    OCORRENCIAS = {
        "00": "✅ Pago/Agendado com Sucesso",
        "01": "❌ Insuficiência de Fundos",
        "02": "⚠️ Pagamento Cancelado",
        "03": "✅ Débito Autorizado pela Agência",
        "AA": "❌ Arquivo Duplicado (NSA já enviado)",
        "AF": "❌ Código de Convênio Inválido",
        "AE": "❌ CPF/CNPJ do Favorecido Inválido",
        "BD": "❌ Data de Pagamento Inválida",
    }

    @staticmethod
    def processar_arquivo(caminho_arquivo):
        resultados = []
        with open(caminho_arquivo, 'r', encoding='ascii') as f:
            for linha in f:
                if len(linha) >= 240 and linha[13] == 'N':
                    nome = linha[57:87].strip()
                    valor = float(linha[95:110]) / 100
                    raw_erros = linha[230:240].strip()
                    
                    erros_traduzidos = []
                    for i in range(0, len(raw_erros), 2):
                        par = raw_erros[i:i+2]
                        if par.strip():
                            erros_traduzidos.append(
                                LeitorRetornoSicredi.OCORRENCIAS.get(par, f"Erro {par}")
                            )
                    resultados.append({
                        "nome": nome, "valor": valor, 
                        "status": " | ".join(erros_traduzidos) if erros_traduzidos else "Sem Retorno"
                    })
        return resultados
