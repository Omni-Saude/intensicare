# RULE-BALANCO-HIDRICO-025 — Fluid-balance overview cell visibility threshold (grid vs mobile mismatch)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
In the fluid-balance overview, a quantity cell is only shown when the value is nonzero. The desktop GridView shows a cell when value !== 0 (so negative values ARE shown), while the MobileView shows a value only when quantidades[i] > 0 (negative and zero suppressed). The two views apply different thresholds to the same data.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| value (GridView) / quantidades[i] (MobileView) | — | ml | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| cell rendered? | — | — |

## Logic
```text
GridView (desktop):
  if (value !== 0) render "<value> ml" else render empty cell
MobileView:
  rowHasData = valores.some(v => v.quantidades[i] > 0)
  if (rowHasData) for each valor: if (valor.quantidades[i] > 0) render
    "<quantidades[i]> ml"
  else render "Nenhum registro informado"
```

## Edge cases (as implemented)
A negative quantity (value < 0) renders in GridView but is hidden in MobileView. A zero quantity is hidden in both. MobileView additionally renders a "Nenhum registro informado" placeholder for a time-slot with no positive value.

## Divergence
Desktop GridView (GridView.tsx:86) renders a cell when `value !== 0` (so negative volumes ARE shown); MobileView (MobileView.tsx:41 & 44) renders only when `quantidades[i] > 0` (negative and zero suppressed) and otherwise shows 'Nenhum registro informado'. The two views apply different visibility predicates to the same overview payload; they coincide only if the domain never produces negative volumes.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/BalancoHidricoVisaoGeral/GridView/GridView.tsx | 81-96 | f9656be2 | primary |
- Merged from: RULE-balanco-FE-03-004
- Related rules: RULE-BALANCO-HIDRICO-013, RULE-BALANCO-HIDRICO-054

## Notes
DISCREPANCY: inconsistent visibility predicate between desktop (value !== 0, line 86) and mobile (quantidades[i] > 0, MobileView.tsx lines 41 & 44). If the domain never produces negative volumes the behaviors coincide; if it can (e.g. corrections), the two views disagree. Verifier should confirm whether negative quantities are possible in Models.BalancoHidricoGeral.Valores.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
