# 🏦 Sistema de Remessa Digital – GPS (CNAB240)

## Integração Financeira  
**Comunidade Canção Nova & Sicredi**

---

## 📌 Visão Geral

Sistema corporativo para automação do processo de:

- Geração de arquivos CNAB240 (Pagamento de GPS – INSS)
- Processamento automático de arquivos de retorno (.RET)
- Geração de relatório executivo de pagamentos
- Consolidação de guia + comprovante em PDF
- Controle de NSA (Número Sequencial de Arquivo)
- Sincronização automática com Google Drive (rclone)

Projeto desenvolvido para uso interno do setor financeiro.

---

## 🧱 Arquitetura do Sistema
app/
├── layouts/
│ └── sicredi/ # Estrutura CNAB240
│
├── services/
│ ├── sicredi/ # Builder de remessa
│ └── retorno/ # Processamento de retorno
│ ├── leitor_retorno.py
│
├── processar_retornos.py # Orquestrador do retorno
├── gerar_retroativo.py
├── juntar_pdf.py
└── sync_drive.sh

## 🔄 Fluxo Operacional

### 1️⃣ Remessa
- Geração do arquivo CNAB240
- Controle automático de NSA
- Envio ao banco

### 2️⃣ Retorno
- Arquivo `.RET` colocado em `retorno/input/`
- Processamento automático
- Classificação:
  - Pagamentos Efetuados
  - Pagamentos Rejeitados
- Geração de relatório executivo (`resumo_arquivo.txt`)
- Movimentação automática para `retorno/processed/`

---

## 📊 Relatório Gerado

O sistema produz um resumo executivo contendo:

- Total de registros processados
- Total de pagamentos efetivados
- Total de rejeições
- Percentual de efetivação
- Valores financeiros consolidados
- Lista detalhada de ocorrências negativas

---

## 🔐 Controle de Segurança

- `.gitignore` bloqueia:
  - Arquivos reais de remessa
  - Arquivos de retorno bancário
  - Dados sensíveis
  - Arquivo de controle NSA
- Separação clara entre:
  - Layout bancário
  - Lógica de negócio
  - Orquestração

---

## ⚙️ Instalação

### Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
Instalar dependências
pip install -r requirements.txt

