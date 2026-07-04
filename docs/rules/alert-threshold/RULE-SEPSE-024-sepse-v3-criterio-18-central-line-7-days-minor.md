# RULE-SEPSE-024 — SEPSE v3 criterio_18 - central line > 7 days (minor)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
No noradrenaline (6h) AND CVC or CDL present in an evolution older than 7 days.

## Inputs

- evolucao.enf_cvc, evolucao.enf_cdl (float)
- balanco.qt_vol_nora (float, ml/h)

## Outputs

- criterio_18 (boolean)

## Logic

```text
evolucao_7dias = evolucoes(dt < now-7d)
return all([
  not balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  evolucao_7dias.filter(Q(enf_cvc__gt=0) | Q(enf_cdl__gt=0)).exists(),
]) if evolucao_7dias and balanco_6h else False
```

## Edge cases (as implemented)

More-than-7-days implemented as existence of any evolution record older than 7d with the device flagged.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** CDC/HICPAC Guidelines for the Prevention of Intravascular Catheter-Related Infections (O'Grady NP et al., 2011): central venous catheters are a recognized source of bloodstream infection, but routine replacement to prevent infection is explicitly NOT recommended — no authoritative dwell-time cutoff (e.g. 7 days) is defined as a sepsis-risk threshold. ([source](https://www.cdc.gov/infection-control/hcp/intravascular-catheter-related-infection/index.html))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a — 7-day dwell threshold is institutional; not from any published guideline |
| units | ok — days |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a — the >7 day cutoff has no authoritative source (implemented as any evolution record older than 7d with CVC/CDL flagged) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nora_6h=absent; cvc_record_older_than_7d={"enf_cvc": 1} | per algorithm -> fires | True — evolucao(dt<now-7d) with enf_cvc>0 exists | yes |
| nora_6h=absent; cvc_record=only <7d old | per algorithm -> does not fire | False — evolucao_7dias (dt<now-7d) has no matching record | yes |
| nora_6h=present; cvc_record_older_than_7d={"enf_cvc": 1} | nora gate -> does not fire | False — balanco_6h qt_vol_nora>0 exists, first clause False | yes |

**Verifier notes**

The premise (CVC/CDL as an infection source) is guideline-supported, but the specific >7-day dwell cutoff is an internal institutional threshold with no published anchor (CDC in fact discourages fixed replacement intervals). Logic traces consistently with the docstring. Flag for internal review; not a defect.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 980-1001 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-118`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
