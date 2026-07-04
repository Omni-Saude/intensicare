# RULE-VENTILACAO-003 — Ventilation C1 - high inspiratory pressure or tidal volume

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Flags inspiratory pressure > 16 OR tidal volume > 500 ml. Also a hard alert-forcing criterion.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| pressao_inspiratoria (cmH2O) | | | |
| volume_corrente (ml) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| criterio_1 (bool) | | |

## Logic

```text
any([ (pressao_inspiratoria > 16) if pressao_inspiratoria else False,
      (volume_corrente > 500) if volume_corrente else False ])
```

## Edge cases (as implemented)

Strict thresholds. pressao 16 -> False, 17 -> True; volume 500 -> False, 501 -> True.

## Divergence

Current code: PINS>16 OR VC>500 ml (absolute). _ANTIGAS_REGRAS used "Pressao Controlada >15 OU Volume Corrente >6 ml/kg" (weight-based). Current version replaced weight-based VC with absolute 500 ml and raised pressure cutoff 15->16.

## Verification

- Verdict: DISCREPANCY (clinical impact: moderate)
- Reference: Lung-protective ventilation: tidal volume <=6 mL/kg PREDICTED body weight (ARDSNet ARMA, NEJM 2000;342:1301); driving/plateau pressure limits (Amato et al, driving pressure <=15 cmH2O, NEJM 2015;372:747; plateau <=30 cmH2O). Tidal-volume safety is weight-indexed, not an absolute mL threshold.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 124-134 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-048
- Related rules: RULE-VENTILACAO-014, RULE-VENTILACAO-001, RULE-VENTILACAO-017

## Notes

Alert-forcing criterion (RULE-VENTILACAO-014). Test test_trilha_ventilacao.py:49-60. Verified verbatim against source.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
