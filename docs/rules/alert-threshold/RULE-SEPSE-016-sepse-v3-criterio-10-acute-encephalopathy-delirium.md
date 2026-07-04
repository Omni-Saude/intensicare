# RULE-SEPSE-016 — SEPSE v3 criterio_10 - acute encephalopathy/delirium

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
No noradrenaline (12h) AND no invasive vent AND no dementia AND (GCS drop >=2 over 48h OR delirium in 24h OR GCS<14), with no prior delirium beyond 24h.

## Inputs

- evolucao.diurna_glasgow (last & penultimate), evolucao.diurna_delirium (float, GCS points)
- balanco.qt_vol_nora, cpoe.vent_mecanica_invasiva, diagnostico_1..4 (float / string)

## Outputs

- criterio_10 (boolean)

## Logic

```text
return all([
  not balanco_12h.filter(qt_vol_nora__gt=0).exists(),
  not get_number(ultima_cpoe.vent_mecanica_invasiva),
  not evolucao_mais_que_24h(dt>=now-26h).filter(diurna_delirium__lt=0).exists(),
  any([ get_number(ultima.diurna_glasgow) - get_number(penultima.diurna_glasgow) >= 2,   # INCREASE, docstring says reduction
        evolucao_24h.filter(diurna_delirium__gt=0).exists(),
        get_number(ultima.diurna_glasgow) < 14 ]),
  not list(filter(lambda x: x == "Demências", vars(ultima).fromkeys(("diagnostico_1".."diagnostico_4")))),  # always True
]) if balanco_12h and ultima_evolucao and penultima_evolucao and ultima_cpoe else False
```

## Edge cases (as implemented)

GCS-change condition computes (last - penultimate) >= 2 which detects an INCREASE of >=2, opposite of the intended "reduction of >=2 points". delirium-absence window uses dt>=now-26h with __lt=0.

## Divergence

DISCREPANCY - GCS delta sign inverted vs docstring; dementia exclusion vacuously true (fromkeys bug).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** SOFA CNS component (Vincent JL et al., Intensive Care Med 1996;22:707-710) - GCS <15 = neurologic dysfunction (13-14 = 1pt); Sepsis-3 / qSOFA (Singer M et al., JAMA 2016;315:801-810) altered mentation = GCS <15; sepsis-associated delirium (CAM-ICU) = acute brain dysfunction. ([source](https://jamanetwork.com/journals/jama/fullarticle/2492881))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | ok |
| units | ok |
| ranges | n/a |
| rounding | n/a |
| cutoffs | partial |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| glasgow_last=13; glasgow_penult=15; delirium_24h=false | fire (real 2-point drop; GCS 13<15 = CNS dysfunction) | fire (via GCS<14 branch; delta = 13-15 = -2, NOT >=2, so delta branch is False) | yes |
| glasgow_last=15; glasgow_penult=12; delirium_24h=false | no-fire (GCS 15 normal, patient IMPROVING, no dysfunction) | fire (delta = 15-12 = +3 >= 2 -> True) -- FALSE POSITIVE exposing inverted sign | no |
| glasgow_last=14; glasgow_penult=14; delirium_24h=true | fire (acute delirium = brain dysfunction) | fire (diurna_delirium__gt=0 branch True) | yes |

**Verifier notes**

Extraction-flagged DISCREPANCY confirmed. (1) GCS-delta computed as last-penult >=2 detects an INCREASE (recovery), inverse of the intended "reduction of >=2 points" - fires on improving patients (false positive) and never detects a decline via that branch (real declines that reach GCS<14 are still caught by the third OR-branch, mitigating missed detections). (2) The dementia exclusion `vars(...).fromkeys(...)` yields dict keys not values, so `not [...]` is vacuously True - dementia patients are never excluded (systemic fromkeys bug, reference-neutral). (3) The "delirium absent >24h" gate filters diurna_delirium__lt=0 (a value <0 never occurs) so the new-onset qualifier is non-functional. GCS<14 vs SOFA/qSOFA GCS<15 is a minor cutoff difference (legacy is 1 point less sensitive).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 673-739 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-110`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

DISCREPANCY - GCS delta sign inverted vs docstring; dementia exclusion vacuously true (fromkeys bug).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
