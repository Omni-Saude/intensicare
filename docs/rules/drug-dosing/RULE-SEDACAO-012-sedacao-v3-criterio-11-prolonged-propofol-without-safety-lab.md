# RULE-SEDACAO-012 — Sedacao v3 criterio_11 - prolonged propofol without safety labs (defined, unwired)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | drug-dosing |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Propofol present over the last 96h AND absence of CPK/TGO/TGP/triglycerides prescription in the last 48h (propofol-infusion syndrome surveillance).

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_pro (96h) | float | ml/h |
| cpoe.cpk/tgo/tgp/trigliceres (48h) | float |  |

## Outputs

| name | type |
|---|---|
| criterio_11 | boolean |

## Logic

```text
presenca_sedativos = any(balanco.qt_vol_pro) over balancos(dt >= now - 96h)
presenca_cpoe      = any(cpoe.cpk / tgo / tgp / trigliceres) over cpoe(dt >= now - 48h)
return all([ presenca_sedativos, not presenca_cpoe ]) if cpoe_48h and balanco_96h else False
```

## Edge cases (as implemented)

getattr(cpoe,"trigliceres",0) - the CPOE field is actually spelled "triglicerides"; the "trigliceres" typo means that clause always reads default 0 (triglycerides check inert). Unwired.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Mirrakhimov AE et al. Propofol Infusion Syndrome in Adults: A Clinical Update. Crit Care Res Pract 2015;2015:260385. PRIS surveillance for prolonged (>48h) or high-dose propofol infusion recommends serial monitoring of creatine kinase (CK), triglycerides, lactate/ABG and cardiac markers; alternative sedatives if propofol is prolonged/high-dose. ([source](https://onlinelibrary.wiley.com/doi/10.1155/2015/260385))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| propofol_in_96h=true; cpk_ordered_48h=true | false | false | yes |
| propofol_in_96h=true; no_labs_48h=true | true | true | yes |
| propofol_in_96h=true; only_triglycerides_ordered_48h=true | false | true | no |
| propofol_in_96h=false | false | false | yes |

**Verifier notes**

Concept aligns with published PRIS surveillance (CK + triglycerides are the primary markers; the 96h propofol threshold is more conservative than the >48h literature trigger, an acceptable institutional choice). One implementation defect confirmed at source (trilha_sedacao.py:743-785): getattr(cpoe,"trigliceres",0) misspells the field (actual "triglicerides"), so the triglyceride clause always reads 0 and never contributes to presenca_cpoe. Effect is in the SAFE direction (over-alert): a chart carrying only a triglyceride order still triggers the "order safety labs" recommendation. CK/TGO/TGP checks remain functional. Criterio_11 is unwired anyway (operational impact none). Verdict VERIFIED against the clinical reference; the typo is a low-severity, fail-safe code defect, documented not corrected.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 743-785 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-052`

**Related rules:**

- [RULE-SEDACAO-011](RULE-SEDACAO-011-sedacao-v3-criterio-10-prolonged-sedation-96h-defined-unwire.md)
- [RULE-SEDACAO-014](../alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)

## Notes

Minor field-name typo (trigliceres) makes the triglycerides check inert; kept OK per Phase 1. Unwired.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
