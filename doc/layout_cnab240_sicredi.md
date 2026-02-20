# 📄 Layout CNAB240 – Sicredi (Segmento N – GPS)

Arquivo com 240 posições fixas.

---

## Posições Relevantes no Retorno

| Campo | Posição | Descrição |
|-------|---------|-----------|
| Tipo Registro | 8 | Deve ser "3" |
| Segmento | 14 | Deve ser "N" |
| Nome | 58–87 | Nome do contribuinte |
| Valor | 96–110 | Valor em centavos |
| Ocorrências | 231–240 | Códigos de retorno |

---

## Códigos de Ocorrência Mapeados

| Código | Descrição |
|--------|-----------|
| 00 | Pago/Agendado com Sucesso |
| 01 | Insuficiência de Fundos |
| 02 | Pagamento Cancelado |
| AA | Arquivo Duplicado |
| AF | Código de Convênio Inválido |
| AE | CPF/CNPJ Inválido |
| BD | Data de Pagamento Inválida |

---

## Observação

O sistema considera erro qualquer ocorrência diferente de sucesso.
