# RULE-SEPSE-025 — SEPSE v3 criterio_19 - femoral central line > 5 days (minor)

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
No noradrenaline (6h) AND CVC/CDL in femoral site (VFD/VFE) in evolution older than 5 days.

## Inputs

- evolucao.enf_cvc + enf_cvc_local, enf_cdl + enf_cdl_local (float + string)
- regiao_femural (tuple {VFD, VFE})

## Outputs

- criterio_19 (boolean)

## Logic

```text
regiao_femural = ("VFD", "VFE")
evolucao_5dias = evolucoes(dt < now-5d)
return all([
  not balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  evolucao_5dias.filter(Q(enf_cvc__gt=0, enf_cvc_local__in=regiao_femural)
                        | Q(enf_cdl__gt=0, enf_cdl_local__in=regiao_femural)).exists(),
]) if evolucao_5dias and balanco_6h else False
```

## Edge cases (as implemented)

Femoral site codes hardcoded VFD/VFE (veia femoral direita/esquerda).

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** CDC/HICPAC 2011 catheter guidelines and Marik PE et al. (Crit Care Med 2012 meta-analysis): femoral venous access carries higher infection/thrombosis risk and femoral placement should be avoided when possible. No authoritative source defines a specific >5-day femoral dwell cutoff as a sepsis-risk threshold. ([source](https://www.cdc.gov/infection-control/hcp/intravascular-catheter-related-infection/index.html))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a — >5-day femoral cutoff and site codes (VFD/VFE) are institutional |
| units | ok — days |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a — femoral-higher-risk premise is guideline-supported but the exact 5-day threshold has no published source |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nora_6h=absent; record_older_than_5d={"enf_cvc": 1, "enf_cvc_local": "VFD"} | per algorithm -> fires (femoral CVC >5d) | True — evolucao_5dias with enf_cvc>0 and local in (VFD,VFE) exists | yes |
| nora_6h=absent; femoral_cvc_record=only <5d old | per algorithm -> does not fire | False — evolucao_5dias (dt<now-5d) has no matching record | yes |
| nora_6h=absent; record_older_than_5d={"enf_cvc": 1, "enf_cvc_local": "VJID (jugular)"} | per algorithm -> does not fire (non-femoral site) | False — local not in (VFD,VFE), Q filter no match | yes |

**Verifier notes**

Femoral-site higher-infection-risk premise is guideline-supported (CDC/HICPAC, Marik meta-analysis), but the specific >5-day dwell cutoff and the hardcoded VFD/VFE site codes are internal institutional parameters with no published threshold. Logic traces consistently with the docstring. Flag for internal review; not a defect.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 1003-1028 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-119`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
