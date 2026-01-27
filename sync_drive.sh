#!/bin/bash
# Move os arquivos do Drive para a pasta local input
# O 'move' baixa e deleta do Drive automaticamente para não processar duas vezes

#Puxa planilhas do RH (remessa)
# ID da pasta onde o RH joga o csv 
ID_REMESSA="1HY02GCGmzxtpUxJTVJYfNmWMI2CdIea1"

# Puxa retornos do banco (feedback)
# ID da pasta onde o Financeiro joga o .RET
ID_RETORNO="1mFzL7Xi1wD5kP9Ia9YR3rCrOgwf_hLTN"

# 1. Puxa Planilhas do RH
/usr/bin/rclone move gdrive: /opt/gps-remessa/input --drive-root-folder-id $ID_REMESSA --verbose

# 2. Puxa Arquivos de Retorno do Banco
/usr/bin/rclone move gdrive: /opt/gps-remessa/retorno/input --drive-root-folder-id $ID_RETORNO --verbose

#Devolve os resumos em txt para o RH ler no google drive
# 3. DEVOLVE OS RELATÓRIOS TXT PARA O DRIVE (Servidor -> Drive para o RH ler)
/usr/bin/rclone copy /opt/gps-remessa/retorno/processed/ gdrive: --include "*.txt" --drive-root-folder-id $ID_RETORNO --verbose
