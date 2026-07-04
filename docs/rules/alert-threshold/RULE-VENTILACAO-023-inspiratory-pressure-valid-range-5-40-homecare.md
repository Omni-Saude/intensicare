# RULE-VENTILACAO-023 — Inspiratory pressure valid range 5-40 (homecare)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Inspiratory pressure is constrained to 5..40 (cmH2O).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| pressao_inspiratoria (int, cmH2O, 5-40) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| validated inspiratory pressure (int, cmH2O) | | |

## Logic

```text
PositiveIntegerField(validators=[MinValueValidator(5), MaxValueValidator(40)])
```

## Edge cases (as implemented)

Inclusive 5..40. Null allowed.

## Divergence

Backend homecare PINS bound 5-40 MATCHES the physiotherapist frontend form (RULE-VENTILACAO-020) but DIVERGES from the movimentacao/physician frontend forms (RULE-VENTILACAO-018/019) which allow PINS 0-30.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/formularios/avaliacoes/ventilacao.py` | 180-188 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-06-003
- Related rules: RULE-VENTILACAO-020, RULE-VENTILACAO-018, RULE-VENTILACAO-019, RULE-VENTILACAO-022

## Notes

Unit inferred (cmH2O). Input validator -> verify=false.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
