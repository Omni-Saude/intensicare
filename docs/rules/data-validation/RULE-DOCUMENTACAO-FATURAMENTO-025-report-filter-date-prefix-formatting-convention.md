# RULE-DOCUMENTACAO-FATURAMENTO-025 — Report filter date-prefix formatting convention

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
When rendering the list of applied filters for the signature inconsistency report generator, any filter key whose name begins with the 3-character prefix "dt_" is formatted as a date via formatDataItem(); every other filter key is rendered as its raw string value.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| filtersPagination (key/value map) | object |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| displayValue | string |  |

## Logic
```text
for each [key, value] in Object.entries(filtersPagination) where value is truthy:
  displayValue = key.substring(0, 3) === "dt_" ? formatDataItem(value) : String(value)
```

## Edge cases (as implemented)
Falsy filter values (0, '', false, null, undefined) are silently skipped (map callback implicitly returns undefined for them, rendering nothing).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/Relatorios/GerarRelatorioInconsistenciaAssinatura/GerarRelatorioInconsistenciaAssinatura.tsx | 25-44 | f9656be2 | primary |
- Merged from: RULE-relatorio-FE-06-025
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-024, RULE-DOCUMENTACAO-FATURAMENTO-002

## Notes
formatDataItem/humanizeLabel implementations are out of this partition's scope (src/utils).

Phase-1 capture omitted a `status` field; reviewed content shows no divergence or unresolved ambiguity, so status is set to OK on reconciliation.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
