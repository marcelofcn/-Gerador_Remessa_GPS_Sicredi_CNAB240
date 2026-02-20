# 🔄 Fluxo Operacional

## 1️⃣ Geração de Remessa

1. Planilha origem (Google Sheets / CSV)
2. Conversão para layout CNAB240
3. Geração do arquivo .REM
4. Controle de NSA (Número Sequencial de Arquivo)
5. Envio ao banco

---

## 2️⃣ Retorno Bancário

1. Banco disponibiliza arquivo .RET
2. Arquivo colocado em:

retorno/input/

3. Sistema detecta automaticamente
4. Processamento do Segmento N
5. Classificação:

- Pago/Agendado
- Rejeitado

6. Geração de relatório executivo:

retorno/processed/resumo_nomearquivo.txt

---

## 3️⃣ Tratamento de Erros

Se houver rejeições:

- Verificar código de ocorrência
- Ajustar cadastro
- Gerar nova remessa
