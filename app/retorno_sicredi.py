import os

class AnalisadorRetornoSicredi:
    # Mapeamento baseado na sua nota G099
    DICIONARIO_ERROS = {
        "00": "✅ Pagamento Confirmado / Agendado com Sucesso",
        "01": "❌ Insuficiência de Fundos - Débito Não Efetuado",
        "02": "⚠️ Crédito ou Débito cancelado pelo pagador/credor",
        "03": "✅ Débito autorizado pela agência - Efetuado",
        "11": "❌ Agência/Conta/DV Inválido",
        "AA": "❌ Arquivo Duplicado (Controle/NSA Inválido)",
        "AB": "❌ Tipo de Operação Inválido (Verificar posição 9 do Header Lote)",
        "AC": "❌ Tipo de Serviço Inválido (Diferente de 22)",
        "AD": "❌ Forma de Lançamento Inválida (Diferente de 17)",
        "AE": "❌ Tipo/Número de Inscrição Inválido (CPF/CNPJ)",
        "AF": "❌ Código de Convênio Inválido (Posição 33-52)",
        # Adicione outros conforme o manual evoluir
    }

    @staticmethod
    def ler_arquivo(caminho_arquivo):
        relatorio = []
        
        if not os.path.exists(caminho_arquivo):
            return "Arquivo não encontrado."

        with open(caminho_arquivo, 'r', encoding='ascii') as f:
            linhas = f.readlines()

        for num_linha, linha in enumerate(linhas):
            # Identifica Segmento N (Pagamento de Tributos)
            # Posição 14 (Index 13 no Python) é o Segmento
            if len(linha) >= 240 and linha[13] == 'N':
                nome_contribuinte = linha[57:87].strip()
                identificacao = linha[118:132].strip() # NIT/CNPJ
                # Nota G099: Ocorrências nas posições 231 a 240 (Index 230:240)
                ocorrencias_raw = linha[230:240].strip()
                
                # Quebrar as ocorrências de 2 em 2 caracteres
                erros_detalhados = []
                for i in range(0, len(ocorrencias_raw), 2):
                    codigo = ocorrencias_raw[i:i+2]
                    if codigo and codigo != "  ":
                        descricao = AnalisadorRetornoSicredi.DICIONARIO_ERROS.get(
                            codigo, f"Erro desconhecido ({codigo})"
                        )
                        erros_detalhados.append(descricao)

                relatorio.append({
                    "linha": num_linha + 1,
                    "contribuinte": nome_contribuinte,
                    "id": identificacao,
                    "status": erros_detalhados if erros_detalhados else ["Sem ocorrências"]
                })
        
        return relatorio

# --- Exemplo de execução ---
# if name == "__main__":
#     resultado = AnalisadorRetornoSicredi.ler_arquivo("/opt/gps-remessa/retorno/6XDZ1600.RET")
#     for item in resultado:
#         print(f"Contribuinte: {item['contribuinte']} | Status: {', '.join(item['status'])}")
