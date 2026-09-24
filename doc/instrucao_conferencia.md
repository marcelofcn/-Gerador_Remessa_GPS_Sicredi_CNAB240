# INSTRUÇÕES DE CONFERÊNCIA DO LOTE GPS

**Projeto:** `/home/house/developer/geraremessa`
**Data de referência:** 23/09/2026

---

## 1. Objetivo

Este documento registra os comandos utilizados para conferir a quantidade e a estrutura dos arquivos antes da consolidação das Guias GPS com seus respectivos comprovantes de pagamento.

O processo possui três etapas:

1. Gerar as Guias GPS.
2. Preparar e normalizar os comprovantes.
3. Auditar a correspondência entre Guia e Comprovante.
4. Somente depois gerar os PDFs consolidados.

---

# 2. Conferir a estrutura das pastas

Para verificar quais diretórios existem:

```bash
ls
```

Exemplo:

```text
pasta1
pasta2
```

No nosso caso:

```text
output/comprovantes_brutos/
├── pasta1/
└── pasta2/
```

---

# 3. Verificar quais arquivos existem dentro de uma pasta

Comando:

```bash
find output/comprovantes_brutos/pasta1 -maxdepth 2 -type f | head -20
```

### O que significa

`find` procura arquivos e diretórios.

```text
output/comprovantes_brutos/pasta1
```

É o diretório onde a pesquisa começa.

```text
-maxdepth 2
```

Limita a pesquisa a no máximo dois níveis de profundidade.

```text
-type f
```

Significa procurar somente arquivos.

```text
| head -20
```

Mostra somente os primeiros 20 resultados.

Esse comando foi importante porque descobrimos inicialmente que os PDFs estavam dentro de uma subpasta.

---

# 4. Contar os PDFs da pasta 1

Comando:

```bash
find output/comprovantes_brutos/pasta1 -maxdepth 1 -type f -name "*.pdf" | wc -l
```

### O que significa

```text
find
```

Procura arquivos.

```text
-maxdepth 1
```

Procura somente diretamente dentro de `pasta1`.

```text
-type f
```

Somente arquivos.

```text
-name "*.pdf"
```

Somente arquivos com extensão `.pdf`.

```text
|
```

Envia o resultado para outro comando.

```text
wc -l
```

Conta quantas linhas existem na saída.

Como cada arquivo ocupa uma linha, o resultado representa a quantidade de PDFs.

---

# 5. Contar os PDFs da pasta 2

Comando:

```bash
find output/comprovantes_brutos/pasta2 -maxdepth 1 -type f -name "*.pdf" | wc -l
```

Funciona da mesma maneira para a segunda parte dos comprovantes.

---

# 6. Conferir os arquivos normalizados

Depois de executar:

```bash
python3 admin/preparar_comprovantes.py
```

os comprovantes tratados ficam em:

```text
output/comprovantes_normalizados/
```

Para visualizar os primeiros arquivos:

```bash
ls output/comprovantes_normalizados | head -20
```

O `head -20` mostra somente os primeiros 20 nomes.

Exemplo:

```text
PAGAMENTO_GPS_00011331838_072026_14_ago_178.31.pdf
PAGAMENTO_GPS_00011398460_072026_14_ago_324.20.pdf
...
```

O nome contém:

```text
PAGAMENTO_GPS
NIT
COMPETÊNCIA
DATA
VALOR
```

---

# 7. Contar os comprovantes normalizados

Comando:

```bash
ls output/comprovantes_normalizados/*.pdf | wc -l
```

Esse comando lista somente os PDFs da pasta normalizada e conta quantos existem.

Resultado obtido no lote atual:

```text
130
```

Portanto:

```text
Comprovantes normalizados: 130
```

---

# 8. Conferir as Guias GPS

As Guias retroativas ficam em:

```text
output/espelhos/GPS_RETROATIVO_CORRIGIDO/
```

Para visualizar as primeiras:

```bash
ls output/espelhos/GPS_RETROATIVO_CORRIGIDO | head -20
```

Exemplo:

```text
GUIA_GPS_11327768440_072026.pdf
GUIA_GPS_11347685949_072026.pdf
...
```

O nome contém:

```text
GUIA_GPS
NIT
COMPETÊNCIA
```

---

# 9. Contar as Guias

Comando:

```bash
ls output/espelhos/GPS_RETROATIVO_CORRIGIDO/*.pdf | wc -l
```

Resultado obtido no lote atual:

```text
140
```

Portanto:

```text
Guias geradas: 140
```

---

# 10. Situação atual do lote

Até este ponto temos:

```text
Guias geradas:             140
Comprovantes normalizados: 130
```

A diferença numérica é:

```text
140 - 130 = 10
```

Isso **não significa automaticamente que existem exatamente 10 guias sem pagamento**, porque podem existir:

* comprovantes duplicados;
* comprovantes sem guia;
* uma guia com mais de um comprovante;
* arquivos pertencentes a outra competência/lote.

Por isso não devemos simplesmente assumir que os 10 são pendências.

A confirmação será feita pelo:

```bash
python3 admin/auditar_consolidacao.py
```

---

# 11. Por que não usar apenas a quantidade?

Quantidade é uma conferência inicial.

O cruzamento correto utiliza:

```text
NIT + competência
```

Exemplo:

```text
GUIA_GPS_12943750249_072026.pdf
```

possui:

```text
NIT = 12943750249
Competência = 072026
```

Um comprovante como:

```text
PAGAMENTO_GPS_12943750249_072026_14_ago_178.31.pdf
```

possui a mesma chave:

```text
12943750249 + 072026
```

Portanto, esses dois arquivos podem ser relacionados.

---

# 12. O que o auditor fará

O script:

```text
admin/auditar_consolidacao.py
```

vai comparar todos os arquivos.

Ele produzirá quatro situações principais:

### Correspondência única

```text
1 guia
+
1 comprovante
```

Situação pronta para consolidação.

### Guia sem comprovante

Existe uma guia, mas nenhum comprovante possui a mesma chave.

Deve ser investigada antes da consolidação.

### Múltiplos comprovantes

Uma mesma combinação:

```text
NIT + competência
```

aparece em mais de um comprovante.

Não devemos escolher automaticamente qual utilizar.

### Comprovante sem guia

Existe um comprovante normalizado, mas não existe Guia correspondente.

Também deve ser investigado.

---

# 13. Regra importante

Até a auditoria ser concluída:

**NÃO executar a consolidação final.**

O objetivo é garantir que cada arquivo:

```text
GUIA_GPS_<NIT>_<COMPETENCIA>.pdf
```

seja unido somente ao comprovante:

```text
PAGAMENTO_GPS_<MESMO_NIT>_<MESMA_COMPETENCIA>_...
```

---

# 14. Fluxo definitivo

O processo completo ficará:

```text
CSV
 │
 ▼
gerar_retroativo.py
 │
 ▼
output/espelhos/GPS_RETROATIVO_CORRIGIDO/
 │
 │
 │       comprovantes recebidos do banco
 │                 │
 │                 ▼
 │       preparar_comprovantes.py
 │                 │
 │                 ▼
 │       output/comprovantes_normalizados/
 │
 ▼
auditar_consolidacao.py
 │
 ▼
RELATORIO_AUDITORIA.txt
 │
 │
 │  somente depois da conferência
 ▼
consolidação final
 │
 ▼
output/guias_completas/
```

---

## 15. Comandos básicos de conferência

Para repetir a conferência no futuro:

### Guias

```bash
ls output/espelhos/GPS_RETROATIVO_CORRIGIDO/*.pdf | wc -l
```

### Comprovantes normalizados

```bash
ls output/comprovantes_normalizados/*.pdf | wc -l
```

### Primeiras Guias

```bash
ls output/espelhos/GPS_RETROATIVO_CORRIGIDO | head -20
```

### Primeiros comprovantes

```bash
ls output/comprovantes_normalizados | head -20
```

### Executar auditoria

```bash
python3 admin/auditar_consolidacao.py
```

### Visualizar relatório

```bash
cat output/guias_completas/RELATORIO_AUDITORIA.txt
```

---

# 16. Estado conhecido deste lote

Na conferência realizada em 23/09/2026:

```text
Guias:                  140
Comprovantes:           130
Comprovantes OK:        126
Duplicados:               4
Pendentes:                0
Erros:                    0
```

Esses números são provenientes da preparação dos comprovantes.

A quantidade de correspondências entre Guia e Comprovante ainda deve ser determinada pela auditoria por:

```text
NIT + competência
```

antes da geração dos PDFs consolidados.
