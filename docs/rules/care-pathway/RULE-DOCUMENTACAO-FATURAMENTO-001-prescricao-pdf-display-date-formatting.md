# RULE-DOCUMENTACAO-FATURAMENTO-001 — Prescricao PDF display date formatting

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | formula |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
The report's display date is converted from ISO 'YYYY-MM-DD' to Brazilian 'DD/MM/YYYY' format.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dia | string |  | 'YYYY-MM-DD' |

## Outputs
| Name | Type | Unit |
|---|---|---|
| dia (display) | string |  |

## Logic
```text
dia_display = datetime.strptime(dia, "%Y-%m-%d").date().strftime("%d/%m/%Y")
```

## Edge cases (as implemented)
Raises ValueError (uncaught) if dia does not match 'YYYY-MM-DD'.

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: ISO 8601:2004 calendar date format (YYYY-MM-DD); Brazilian date convention DD/MM/YYYY (ABNT NBR 5892 / pt-BR locale); Python 3 datetime.strftime/strptime format-code semantics (%Y=4-digit year, %m=zero-padded month, %d=zero-padded day).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/views/pdf_prescricao.py | 59-59 | 8166c07e | primary |
- Merged from: RULE-pdf-BE-08-042
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-006, RULE-DOCUMENTACAO-FATURAMENTO-022, RULE-DOCUMENTACAO-FATURAMENTO-023

## Notes
verify=true because type is 'formula' per audit rule 4 (mechanical rule, not a clinical calculation).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
