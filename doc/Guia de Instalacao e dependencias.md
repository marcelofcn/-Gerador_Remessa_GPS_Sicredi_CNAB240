# Guia de Instalação e Dependências

Este documento descreve os requisitos e passos para replicar o ambiente de execução do sistema.

## 📋 Requisitos do Sistema
- SO Recomendado: Ubuntu 22.04 ou 24.04 LTS
- Python: Versão 3.10 ou superior
- Dependências de Sistema: rclone (para sincronização com Google Drive)

## 🐍 Ambiente Python (Dependências)
As bibliotecas necessárias estão listadas no arquivo requirements.txt. As principais são:
- pandas e openpyxl: Processamento de planilhas e CSVs.
- watchdog: Monitoramento de eventos do sistema de arquivos.
- requests: Comunicação via Webhook (Discord/Teams).
- fpdf: Geração de relatórios em PDF.
- yagmail: (Opcional) Envio de e-mails.

## 🛠️ Passo a Passo para Deploy
1. Clonar o projeto para o diretório de destino.
2. Criar o Ambiente Virtual:
   ```bash
   python3 -m venv venv
