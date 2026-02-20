import os
import unicodedata
from fpdf import FPDF
from datetime import datetime

class GeradorEspelhoGPS:
    @staticmethod
    def remover_acentos(texto):
        """Remove acentos e caracteres especiais para evitar erro no PDF."""
        if not texto: 
            return ""
        nfkd = unicodedata.normalize('NFKD', str(texto))
        return "".join([c for c in nfkd if not unicodedata.combining(c)])

    @staticmethod
    def gerar(contribuinte, data_pagamento, nsa, convenio, output_path, data_emissao=None):
        """Gera um espelho em formato de guia oficial GPS com 12 campos."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=8)
        
        # Define a data de emissão (se não informada, usa a atual)
        if not data_emissao:
            data_emissao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        # --- CONFIGURAÇÃO DE COORDENADAS (GRID) ---
        x_inicio = 10
        y_inicio = 15
        col1_w = 120  # Largura coluna esquerda
        col2_w = 70   # Largura coluna direita (valores)
        h_row = 12    # Altura padrão das linhas

        # --- 1. CABEÇALHO (LOGO E TÍTULO) ---
        pdf.rect(x_inicio, y_inicio, col1_w, h_row * 2) 
        pdf.set_font("Arial", 'B', 9)
        pdf.set_xy(x_inicio, y_inicio + 2)
        pdf.multi_cell(col1_w, 4, txt="MINISTERIO DA PREVIDENCIA SOCIAL - MPS\nINSTITUTO NACIONAL DO SEGURO SOCIAL - INSS\nGUIA DA PREVIDENCIA SOCIAL - GPS", align='C')

        # --- 2. COLUNA DA DIREITA (CAMPOS 3 A 11) ---
        
        # 3. Código de Pagamento
        pdf.rect(x_inicio + col1_w, y_inicio, col2_w, h_row)
        pdf.set_font("Arial", 'B', 7)
        pdf.text(x_inicio + col1_w + 1, y_inicio + 3, "3. CODIGO DE PAGAMENTO")
        pdf.set_font("Arial", '', 10)
        pdf.text(x_inicio + col1_w + 25, y_inicio + 8, str(contribuinte['gps']['codigo_receita']))

        # 4. Competência (Correção do bug MM/YYYY)
        pdf.rect(x_inicio + col1_w, y_inicio + h_row, col2_w, h_row)
        pdf.set_font("Arial", 'B', 7)
        pdf.text(x_inicio + col1_w + 1, y_inicio + h_row + 3, "4. COMPETENCIA (MM/AAAA)")
        pdf.set_font("Arial", '', 10)
        comp = str(contribuinte['gps']['competencia']).zfill(6) # Garante 012026
        pdf.text(x_inicio + col1_w + 25, y_inicio + h_row + 8, f"{comp[:2]}/{comp[2:]}")

        # 5. Identificador (NIT/CNPJ)
        pdf.rect(x_inicio + col1_w, y_inicio + (h_row * 2), col2_w, h_row)
        pdf.set_font("Arial", 'B', 7)
        pdf.text(x_inicio + col1_w + 1, y_inicio + (h_row * 2) + 3, "5. IDENTIFICADOR")
        pdf.set_font("Arial", '', 10)
        pdf.text(x_inicio + col1_w + 15, y_inicio + (h_row * 2) + 8, str(contribuinte['gps']['identificacao']))

        # --- CAMPOS DE VALORES ---
        labels_valores = [
            ("6. VALOR DO INSS", contribuinte['gps']['valor_inss']),
            ("7.", 0.0),
            ("8.", 0.0),
            ("9. VALOR OUTRAS ENTIDADES", contribuinte['gps']['valor_outras_entidades']),
            ("10. ATM, MULTA E JUROS", contribuinte['gps']['atualizacao_monetaria']),
            ("11. TOTAL", contribuinte['valor_total'])
        ]

        current_y = y_inicio + (h_row * 3)
        for label, valor in labels_valores:
            pdf.rect(x_inicio + col1_w, current_y, col2_w, h_row)
            pdf.set_font("Arial", 'B', 7)
            pdf.text(x_inicio + col1_w + 1, current_y + 3, label)
            if valor > 0:
                pdf.set_font("Arial", '', 10)
                pdf.set_xy(x_inicio + col1_w, current_y + 5)
                pdf.cell(col2_w - 2, 5, txt=f"{valor:,.2f}", align='R')
            current_y += h_row

        # --- 3. COLUNA DA ESQUERDA (CAMPOS 1, 2 E ATENÇÃO) ---
        
        # 1. Nome / Razão Social
        y_nome = y_inicio + (h_row * 2)
        pdf.rect(x_inicio, y_nome, col1_w, h_row * 3)
        pdf.set_font("Arial", 'B', 7)
        pdf.text(x_inicio + 1, y_nome + 3, "1. NOME OU RAZAO SOCIAL / FONE / ENDERECO:")
        pdf.set_font("Arial", '', 9)
        nome_limpo = GeradorEspelhoGPS.remover_acentos(contribuinte['nome'])
        pdf.set_xy(x_inicio + 1, y_nome + 5)
        pdf.multi_cell(col1_w - 2, 4, txt=nome_limpo)

        # 2. Vencimento
        y_venc = y_inicio + (h_row * 5)
        pdf.rect(x_inicio, y_venc, col1_w, h_row)
        pdf.set_font("Arial", 'B', 7)
        pdf.text(x_inicio + 1, y_venc + 3, "2. VENCIMENTO (Uso do INSS)")
        pdf.set_font("Arial", '', 10)
        # Formata data_pagamento de DDMMAAAA para DD/MM/AAAA
        dt = str(data_pagamento)
        data_fmt = f"{dt[:2]}/{dt[2:4]}/{dt[4:]}"
        pdf.text(x_inicio + 10, y_venc + 8, data_fmt)

        # Quadro de Atenção
        y_atencao = y_inicio + (h_row * 6)
        pdf.rect(x_inicio, y_atencao, col1_w, h_row * 3)
        pdf.set_font("Arial", 'B', 6)
        pdf.set_xy(x_inicio + 1, y_atencao + 2)
        txt_atencao = ("ATENCAO: E vedada a utilizacao de GPS para recolhimento de receita de valor inferior "
                      "ao estipulado em Resolucao publicada pelo INSS. A receita que resultar valor inferior "
                      "devera ser adicionada a contribuicao ou importancia correspondente nos meses subsequentes.")
        pdf.multi_cell(col1_w - 2, 3, txt=txt_atencao)

        # --- 4. CAMPO 12: AUTENTICAÇÃO BANCÁRIA ---
        y_final = y_inicio + (h_row * 9)
        pdf.rect(x_inicio, y_final, col1_w + col2_w, h_row * 2)
        pdf.set_font("Arial", 'B', 7)
        pdf.text(x_inicio + 1, y_final + 3, "12. AUTENTICACAO BANCARIA")
        
        # Rodapé com informações técnicas solicitadas
        pdf.set_font("Arial", 'I', 7)
        info_tecnica = (f"Remessa pagamentos arquivo de remessa cnab240 - Cooperativa Sicredi - "
                        f"Convenio: {convenio} - NSA: {nsa:06d}")
        pdf.text(x_inicio + 2, y_final + 14, info_tecnica)
        
        pdf.set_font("Arial", 'I', 6)
        pdf.text(x_inicio + 2, y_final + 19, f"Espelho gerado em {data_emissao} - Uso Interno.")

        # Salvar o arquivo
        nome_pdf = f"GUIA_GPS_{contribuinte['gps']['identificacao']}_{comp}.pdf"
        caminho_final = os.path.join(output_path, nome_pdf)
        pdf.output(caminho_final)
        
        return caminho_final
