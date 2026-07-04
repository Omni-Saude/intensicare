# RULE-SEPSE-017 — SEPSE v3 criterio_11 - hyperbilirubinemia/jaundice (incomplete)

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
Intended - no noradrenaline (12h) AND (bilirubin>2 OR jaundice present).

## Inputs

- evolucao.diurna_ictericia (float/string (truthiness))
- balanco.qt_vol_nora (float, ml/h)

## Outputs

- criterio_11 (boolean)

## Logic

```text
return all([
  not balanco_12h.filter(qt_vol_nora__gt=0).exists(),
  get_number(ultima_evolucao.diurna_ictericia),   # truthy jaundice value only
]) if balanco_12h and ultima_evolucao else False
```

## Edge cases (as implemented)

Missing values -> get_number 0 -> criterion False.

## Divergence

DISCREPANCY - the "bilirubina > 2mg/dl" branch from the docstring is not implemented; only the jaundice (diurna_ictericia) truthiness is checked. criterio_11 counts as a MAJOR in v3 alert.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** SOFA liver component (Vincent JL et al., Intensive Care Med 1996;22:707-710) - total bilirubin 2.0-5.9 mg/dL (34-102 umol/L) = 2 points hepatic dysfunction. Jaundice is the clinical correlate, typically visible only when bilirubin > ~2-3 mg/dL. ([source](https://link.springer.com/article/10.1007/BF01709751))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | n/a |
| units | n/a |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| bilirubin_mgdl=3.0; jaundice_flag=absent/blank | fire (bilirubin 3.0 mg/dL = SOFA hepatic dysfunction) | no-fire (bilirubin branch absent; get_number(blank jaundice)=0 -> False) | no |
| bilirubin_mgdl=5.0; jaundice_flag=present | fire | fire (get_number(diurna_ictericia) truthy) | yes |
| bilirubin_mgdl=1.5; jaundice_flag=present | no-fire (bilirubin <2 = no hepatic dysfunction) | fire (jaundice truthy) -- false positive when jaundice recorded but bilirubin normal | no |

**Verifier notes**

Extraction-flagged DISCREPANCY confirmed. Docstring/reference specify "bilirubina > 2 mg/dL OR jaundice", but code implements ONLY get_number(diurna_ictericia) truthiness. Objective hyperbilirubinemia without documented visible jaundice (scleral icterus is frequently not charted, and bilirubin can be 2-3 mg/dL before jaundice is clinically apparent) is missed. This is a MAJOR criterion in the v3 alert (criterio_11 -> maiores), so the omission reduces sensitivity of a high-weight signal - hence moderate impact.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 741-761 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-111`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

DISCREPANCY - the "bilirubina > 2mg/dl" branch from the docstring is not implemented; only the jaundice (diurna_ictericia) truthiness is checked. criterio_11 counts as a MAJOR in v3 alert.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
