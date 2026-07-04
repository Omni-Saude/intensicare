# RULE-VENTILACAO-022 — PEEP (pressao expiratoria pulmonar) valid range 5-18 (homecare)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Positive end-expiratory pressure is constrained to 5..18 (cmH2O).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| pressao_expiratoria_pulmonar (int, cmH2O, 5-18) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| validated PEEP (int, cmH2O) | | |

## Logic

```text
PositiveIntegerField(validators=[MinValueValidator(5), MaxValueValidator(18)])
```

## Edge cases (as implemented)

Inclusive 5..18. Null allowed.

## Divergence

Backend homecare PEEP bound 5-18 MATCHES the physiotherapist frontend form (RULE-VENTILACAO-020) but DIVERGES from the movimentacao/physician frontend forms (RULE-VENTILACAO-018/019) which allow PEEP 0-40.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/formularios/avaliacoes/ventilacao.py` | 170-178 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-06-002
- Related rules: RULE-VENTILACAO-020, RULE-VENTILACAO-018, RULE-VENTILACAO-019, RULE-VENTILACAO-023

## Notes

Unit inferred (cmH2O) from ventilator context; not stated in code. Input validator -> verify=false.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
