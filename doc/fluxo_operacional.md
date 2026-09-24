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


## Upgrade 19/08/2026
1. Fluxo completo atual do Projeto GPS
FLUXO A — Geração da Remessa
                    ┌──────────────────────┐
                    │     ARQUIVO CSV      │
                    │ dados dos pagamentos │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ automacao_remessa.py │
                    │                      │
                    │ • monitora /input    │
                    │ • lê CSV             │
                    │ • valida/converte    │
                    │ • gera NSA           │
                    │ • monta pagamentos   │
                    └──────────┬───────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ gps_cnab_builder.py    │
                  │                         │
                  │ monta o CNAB 240       │
                  └───────────┬─────────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
      header_arquivo    header_lote      segmento_n_gps
             │                │                │
             └────────────────┼────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ trailer_lote.py     │
                    │ trailer_arquivo.py  │
                    └──────────┬───────────┘
                               │
                               ▼
                         ARQUIVO .REM
                               │
                               ▼
                         BANCO SICREDI

#2. Fluxo B — Retorno bancário

Depois que o Sicredi processa a remessa:
                    BANCO SICREDI
                          │
                          ▼
                    arquivo .RET
                          │
                          ▼
                  retorno/input/
                          │
                          ▼
              processar_retornos.py
                          │
                          ▼
              leitor_retorno.py
                          │
                          ▼
               Segmentos N encontrados
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          paga        agendada      rejeitada
             │            │            │
             └────────────┼────────────┘
                          ▼
                  relatório executivo
                          │
                          ▼
                 retorno/processed/

# 3. Fluxo C — Geração da Guia GPS

Esse fluxo é independente do retorno bancário.
CSV / dados da remessa
          │
          ▼
gerador_espelho.py
          │
          ▼
GeradorEspelhoGPS
          │
          ▼
GUIA_GPS_*.pdf

# 4. Fluxo D — Consolidação administrativa

Depois temos o processo de auditoria/conferência:
             GUIAS GPS
                 │
                 ▼
       output/espelhos/
                 │
                 │
                 │       COMPROVANTES BANCÁRIOS
                 │                  │
                 │                  ▼
                 │       output/comprovantes_brutos/
                 │                  │
                 └──────────┬───────┘
                            ▼
                  consolidar_lote.py
                            │
                            ▼
                  cruzamento NIT/NOME
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
             encontrado           não encontrado
                  │                   │
                  ▼                   ▼
          Guia + comprovante     pendência
                  │
                  ▼
        output/guias_completas/
                  │
                  ▼
          GUIA CONSOLIDADA

O consolidar_lote.py também gera:

RESUMO_LOTE.txt

com:

total de guias;
quantidade consolidada;
pendências;
valor total auditado.

# 5. O que cada programa faz

Essa parte eu colocaria na documentação porque evita confusão futura.
| Arquivo                 | Responsabilidade                                       |
| ----------------------- | ------------------------------------------------------ |
| `automacao_remessa.py`  | Entrada operacional do CSV e geração da remessa        |
| `gps_cnab_builder.py`   | Montagem estrutural do CNAB240                         |
| `header_arquivo.py`     | Header do arquivo CNAB                                 |
| `header_lote_gps.py`    | Header do lote GPS                                     |
| `segmento_n_gps.py`     | Registro de pagamento GPS                              |
| `trailer_lote.py`       | Trailer do lote                                        |
| `trailer_arquivo.py`    | Trailer do arquivo                                     |
| `processar_retornos.py` | Monitoramento e processamento dos `.RET`               |
| `leitor_retorno.py`     | Interpretação dos registros do retorno                 |
| `gerador_espelho.py`    | Geração da Guia GPS em PDF                             |
| `consolidar_lote.py`    | Auditoria e união Guia + comprovante                   |
| `gerar_retroativo.py`   | Ferramenta excepcional para recuperação/retroatividade |
| `juntar_pdf.py`         | Ferramenta administrativa antiga; ainda sob avaliação  |

# 6. Estrutura de diretórios operacional

A documentação deve mostrar a estrutura sem __pycache__, .pyc e arquivos temporários:
6. Estrutura de diretórios operacional

A documentação deve mostrar a estrutura sem __pycache__, .pyc e arquivos temporários:

7. Fluxo operacional do usuário
Essa é provavelmente a parte mais importante para quem vai operar o sistema.

ETAPA 1 — Preparar o CSV

Colocar o CSV em:
~/developer/geraremessa/input/

O CSV deve conter os campos necessários para o pagamento, incluindo:
nome_contribuinte
valor_total
codigo_receita
nit
competencia
valor_inss
juros
multa
data_pagamento

ETAPA 2 — Executar a automação
cd ~/developer/geraremessa
python3 automacao_remessa.py

O sistema passa a monitorar:
input/

Quando detectar um .csv:

lê o arquivo;
normaliza as colunas;
transforma valores monetários em Decimal;
transforma a data para DDMMAAAA;
gera o NSA;
monta o CNAB240;
valida os registros;
gera o .REM;
grava em output/;
move o CSV processado para:
processed/remessas/

ETAPA 3 — Enviar a remessa ao Sicredi

O arquivo:
output/XXXXXX.REM
é o arquivo que será enviado ao banco.

Não versionar esse arquivo no Git.

ETAPA 4 — Receber o retorno
Depois do processamento bancário, colocar o .RET em:
retorno/input/

ETAPA 5 — Processar retorno
Executar:
cd ~/developer/geraremessa
python3 processar_retornos.py

O sistema monitora continuamente:
retorno/input/

Quando encontra um .RET:

abre o arquivo;
identifica os registros Segmento N;
lê o código de ocorrência;
consulta a classificação oficial;
classifica cada pagamento;
contabiliza os resultados;
gera o relatório;
move o .RET para:
retorno/processed/

8. Exemplo real já validado
Esse ponto eu colocaria na documentação de testes/homologação:
Arquivo:
6XDZ11081309.RET

Resultado:

Segmentos N encontrados: 280

agendada: 140
paga:     140

Resultado:
[RETORNO | SUCESSO] Processado com relatório gerado.

resumo_6XDZ11081309.txt

9. Onde eu colocaria isso nos documentos existentes

Temos estes documentos:
doc/
├── arquitetura.md
├── auditoria_tecnica.md
├── fluxo_operacional.md
├── layout_cnab240_sicredi.md
├── reavaliacao18082026.md
└── validacoes_e_ocorrencias.md

Eu faria assim:

fluxo_operacional.md

Atualizar bastante.

Colocaria nele:

fluxo CSV → REM;
envio ao banco;
RET → relatório;
geração de espelho;
consolidação;
diretórios;
procedimentos operacionais.
arquitetura.md

Atualizar a arquitetura dos módulos:
automacao_remessa
       ↓
gps_cnab_builder
       ↓
layouts Sicredi

e

processar_retornos
       ↓
leitor_retorno
       ↓
classificação G099
       ↓
relatório

validacoes_e_ocorrencias.md

Aqui deve ficar a tabela oficial G099 e as regras:

código → descrição → classificação

Essa passa a ser a fonte de verdade.

auditoria_tecnica.md

Registrar:

o que foi encontrado;
problemas antigos;
correções;
decisões arquiteturais;
resultado dos testes.
layout_cnab240_sicredi.md

Deixar focado no CNAB:

240 posições;
Header;
Header Lote;
Segmento N;
Trailer Lote;
Trailer Arquivo;
posições;
campos;
regras de valores.
reavaliacao18082026.md

Manter como histórico da revisão atual, não como manual operacional.

E uma decisão importante

Eu não mexeria mais agora no automacao_remessa.py nem no CNAB.

O fluxo de geração já está relativamente consolidado:

CSV
 ↓
automacao_remessa
 ↓
gps_cnab_builder
 ↓
CNAB240
 ↓
.REM

O que acabamos de validar foi o retorno:

.RET
 ↓
processar_retornos
 ↓
leitor_retorno
 ↓
G099
 ↓
classificação
 ↓
relatório

Próxima etapa técnica que eu faria: atualizar primeiro o doc/fluxo_operacional.md com esse fluxo real e, em seguida, o doc/validacoes_e_ocorrencias.md com a G099. Depois partimos para arquitetura.md e auditoria_tecnica.md.

Se você quiser fazer isso diretamente no projeto,
posso também te passar o conteúdo completo dos quatro .md já revisados, pronto para substituir os atuais, mantendo o histórico do que já foi decidido.