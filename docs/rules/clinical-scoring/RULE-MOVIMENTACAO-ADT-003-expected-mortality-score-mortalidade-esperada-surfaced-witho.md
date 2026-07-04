# RULE-MOVIMENTACAO-ADT-003 — Expected-mortality score (mortalidade_esperada) surfaced without formula

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | AMBIGUOUS |
| Verification | UNVERIFIABLE |
| Confidence | low |
| Cluster | movimentacao-adt |

## Rule
Each bed occupancy carries a numeric mortalidade_esperada (expected mortality) micro-indicator, presumably a backend-computed severity/mortality-prediction score (e.g. APACHE-like), but no computation formula, inputs, or units are present anywhere in the frontend partition.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
|  | unknown - computed server-side |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| mortalidade_esperada | number; unit unknown - presumed percentage 0-100 or probability 0-1 |  |

## Logic
```text
mortalidade_esperada: number   // opaque value, no frontend computation found
```

## Edge cases (as implemented)
Unknown; not computed, only displayed.

## Verification
- Verdict: UNVERIFIABLE
- Reference: Expected ICU mortality is conventionally derived from APACHE II (Knaus et al., Crit Care Med 1985;13:818-29) or SAPS 3 (Moreno et al., Intensive Care Med 2005); both output a predicted death probability 0-1 / 0-100%. The legacy field mortalidade_esperada is opaque: no formula, inputs, units, or coefficients exist in the captured partition (server-computed, out of scope).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/@types/models/Ocupacao.d.ts | 47-54 | f9656be2 | primary |
- Merged from: RULE-ocupacao-FE-07-005
- Related rules: RULE-MOVIMENTACAO-ADT-002

## Notes
Flagged AMBIGUOUS per ground rules rather than silently assumed. A verifier should check the backend partition for the actual scoring formula (likely APACHE II / SAPS-family) feeding this field.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
