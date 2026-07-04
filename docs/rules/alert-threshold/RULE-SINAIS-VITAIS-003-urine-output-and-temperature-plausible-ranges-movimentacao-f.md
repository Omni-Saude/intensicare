# RULE-SINAIS-VITAIS-003 — Urine-output and temperature plausible ranges (movimentacao form)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Frontend min/max bounds for 24h urine output and body temperature on the movimentacao form. Numeric bounds match the backend validators exactly.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| debito_urinario_24h | number | mL | 0-10000 |
| temperatura | number | Celsius | 20-43 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid values | boolean |  |

## Logic
```text
debito_urinario_24h: 0-10000
temperatura: min 20, max 43
```

## Edge cases (as implemented)
Temperature floor 20C admits severe hypothermia; ceiling 43C. FE temperature min of 20 has no zero-exemption, whereas backend TemperaturaValidator exempts 0 as a "not measured" sentinel (FE expresses "not measured" via blank).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 199-212 | `f9656be2` | frontend-copy |

- Merged from: RULE-vitals-FE-01-025
- Related rules: RULE-SINAIS-VITAIS-021, RULE-SINAIS-VITAIS-023

## Notes
Bounds reconcile exactly with backend RULE-SINAIS-VITAIS-021 (urine) and RULE-SINAIS-VITAIS-023 (temperature).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
