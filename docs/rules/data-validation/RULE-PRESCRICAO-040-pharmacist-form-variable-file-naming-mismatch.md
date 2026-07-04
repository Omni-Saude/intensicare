# RULE-PRESCRICAO-040 — Pharmacist form variable/file naming mismatch

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
The pharmacist form file declares and exports a const named dataFormFisioterapeuta though its content and filename are pharmaceutical.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| N/A |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| N/A |  |  |

## Logic
```text
dataFormFarmaceutico.ts: `const dataFormFisioterapeuta = [...]; export default dataFormFisioterapeuta;`
Content = pharmacist groups (Antibioticos em uso, Profilaxias, Conciliacao Medicamentosa, Conduta farmaceutica).
Two files therefore both define a symbol named dataFormFisioterapeuta.
```

## Edge cases (as implemented)
Cosmetic to runtime (default export) but a maintenance/traceability hazard.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFarmaceutico.ts` | 1-3,690-693 | `f9656be2` | primary |

- Merged from: RULE-pharma-FE-01-056

## Notes
DISCREPANCY = filename says farmaceutico, symbol says fisioterapeuta.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
