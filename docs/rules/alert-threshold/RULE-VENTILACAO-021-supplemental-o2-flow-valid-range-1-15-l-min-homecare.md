# RULE-VENTILACAO-021 — Supplemental O2 flow valid range 1-15 L/min (homecare)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Supplemental oxygen flow is constrained to 1..15 L/min.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| fluxo_o2 (int, L/min, 1-15) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| validated fluxo_o2 (int, L/min) | | |

## Logic

```text
PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(15)])
```

## Edge cases (as implemented)

Inclusive 1..15. Null allowed.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/formularios/avaliacoes/respiratoria.py` | 135-140 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-06-001
- Related rules: RULE-VENTILACAO-019, RULE-VENTILACAO-018

## Notes

Same 1-15 L/min bound as the physician form's fluxo_o2 field (RULE-VENTILACAO-019) - agrees. Input validator (plausibility bound), no published clinical target -> verify=false.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
