# RULE-DOCUMENTACAO-FATURAMENTO-031 — Arquivo filter end-date must not precede start date

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
In the Arquivos list filter, the "Data final" (data_arquivo_fim) field is validated against "Data inicial" (data_arquivo_inicio): it must be greater than or equal to the start date, and the end-date calendar disables any day before the start date.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| data_arquivo_inicio | date |  |  |
| data_arquivo_fim | date |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| validation result / form error | Promise.resolve() | Promise.reject(Error) |  |

## Logic
```text
validator(data_arquivo_fim):
  if (!value) OR (data_arquivo_inicio <= value): resolve()
  else: reject("A data final deve ser maior que a data inicial")
disabledDate(current) = current < data_arquivo_inicio.endOf("day")
onSubmit: both dates reformatted to "YYYY-MM-DD" before being passed to onFilter
```

## Edge cases (as implemented)
Validator uses "<=" (i.e. equal dates ARE allowed, contradicting the literal error text "maior que" [greater than], which implies strictly-after); recorded as implemented (an inclusive boundary despite the "maior que" wording). No validator exists preventing data_arquivo_inicio itself from being empty or in the future.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/FilterArquivos/FilterArquivos.tsx | 26-35,53-88 | f9656be2 | primary |
- Merged from: RULE-filtro-FE-05-001

## Notes
Same pattern (and same inclusive-boundary/wording mismatch) recurs in RULE-filtro-FE-05-002.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
