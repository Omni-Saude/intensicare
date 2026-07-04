# RULE-DOCUMENTACAO-FATURAMENTO-022 — Prescricao PDF export has no explicit validation for missing 'dia'

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | documentacao-faturamento |

## Rule
Unlike BalancoHidricoViewSet.list() (RULE-balanco-BE-08-007), the continuous-prescription PDF export reads 'dia' from query params with no presence check, then immediately parses it with datetime.strptime(dia, "%Y-%m-%d"). If 'dia' is missing, this raises a TypeError from strptime(None, ...) rather than a friendly ValidationError.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dia (query param) | string or None |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| dia (formatted) | string | dd/mm/yyyy |

## Logic
```text
dia = request.query_params.get("dia")   # no None check
...
"dia": datetime.strptime(dia, "%Y-%m-%d").date().strftime("%d/%m/%Y"),
```

## Edge cases (as implemented)
Missing 'dia' → unhandled TypeError (500), not a 400 ValidationError.

## Divergence
The continuous-prescription PDF export reads `dia = request.query_params.get("dia")` with NO presence check, then immediately calls `datetime.strptime(dia, "%Y-%m-%d")` — a missing 'dia' therefore raises an unhandled TypeError (500) instead of a friendly ValidationError (400). This is the opposite behavior of the sibling BalancoHidricoViewSet.list() endpoint (same PDF-export subsystem, not itself captured in this cluster's inputs), which explicitly validates that 'dia' is present before use — i.e. the two PDF-export endpoints handle the identical 'required date query param' concern with different rigor.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/views/pdf_prescricao.py | 24-34,59 | 8166c07e | primary |
- Merged from: RULE-pdf-BE-08-039
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-006, RULE-DOCUMENTACAO-FATURAMENTO-023, RULE-DOCUMENTACAO-FATURAMENTO-001

## Notes
Contrast with BalancoHidricoViewSet.list(), which explicitly validates a required 'dia' parameter.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
