# 🏗️ Arquitetura do Sistema

## Visão Geral

O sistema é dividido em três camadas principais:

1. Layout Bancário (CNAB240)
2. Serviços de Negócio
3. Orquestração

---

## Estrutura de Diretórios

app/
├── layouts/
│   └── sicredi/
│       ├── header_arquivo.py
│       ├── header_lote_gps.py
│       ├── segmento_n_gps.py
│       ├── trailer_lote.py
│       └── trailer_arquivo.py
│
├── services/
│   ├── sicredi/
│   │   ├── gps_cnab_builder.py
│   │   └── gerador_espelho.py
│   │
│   └── retorno/
│       └── leitor_retorno.py
│
├── processar_retornos.py
└── gerar_retroativo.py

---

## Responsabilidades

### Layout
Responsável por montar cada linha fixa de 240 posições conforme padrão CNAB.

### Leitor de Retorno
- Interpreta arquivo .RET
- Identifica Segmento N
- Traduz códigos de ocorrência
- Retorna estrutura organizada

### Orquestrador (processar_retornos.py)
- Classifica pagamentos OK/Erro
- Gera relatório executivo
- Move arquivo processado
