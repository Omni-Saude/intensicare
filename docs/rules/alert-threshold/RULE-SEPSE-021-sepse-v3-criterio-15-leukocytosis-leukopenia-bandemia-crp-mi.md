# RULE-SEPSE-021 — SEPSE v3 criterio_15 - leukocytosis/leukopenia/bandemia/CRP (minor)

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
Intended - no noradrenaline (6h) AND (leukocytes>12000 OR <4000 OR bands>10% OR PCR>100) in 24h. Parses leukocytes (strip . and ,) and bands (strip %) to float.

## Inputs

- evolucao.diurna_leucocitos, diurna_bastoes, diurna_pcr (string parsed to float, /mm3 / % / mg/L)

## Outputs

- criterio_15 (boolean)

## Logic

```text
evolucao_24h = evolucoes(dt>=now-24h, leucocitos not null, bastoes not null)
                 .exclude(leucocitos in {"", " ", ","}).exclude(bastoes in {"", " ", ","})
                 .annotate(leucocitos=Cast(replace(replace(diurna_leucocitos,".",""),",",""), Float),
                           bastoes   =Cast(replace(replace(diurna_bastoes,"%",""),",","."), Float))
return all([
  not balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  evolucao_24h.filter(Q(leucocitos__gt=12000) | Q(leucocitos__lt=4000) | Q(bastoes__gt=10)).exists(),
  evolucao_24h.filter(diurna_pcr__gt=100).exists(),          # PCR ANDed, docstring says OR
]) if balanco_6h else False
```

## Edge cases (as implemented)

Requires BOTH a WBC/band abnormality AND PCR>100 (two separate all([]) entries), so PCR is a mandatory co-condition, not an alternative. leucocitos parse removes both "." and "," (thousands), bastoes removes "%" and converts decimal comma.

## Divergence

DISCREPANCY - PCR>100 is AND-combined with the leukocyte/band clause; docstring lists all four as OR alternatives.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** ACCP/SCCM Consensus Conference (Bone RC et al., 1992) SIRS/sepsis criteria: WBC >12,000/mm3 OR <4,000/mm3 OR >10% immature (band) forms — one of the four SIRS criteria (Sepsis-2). CRP >100 mg/L is NOT a SIRS component (institutional add-on). ([source](https://mdcalc.scholasticahq.com/article/154405-sirs-sepsis-and-septic-shock-criteria))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | diff — WBC cutoffs 12,000/4,000 and band >10% match SIRS exactly; PCR>100 threshold is institutional (not in any SIRS/Sepsis-3 reference) |
| units | ok — leukocytes /mm3, bands %, PCR mg/L; parser strips '.' and ',' as thousands separators, bands strips '%' and converts decimal comma |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff — the four markers are combined as (WBC/band clause) AND (PCR>100 clause) via two separate all([]) entries; reference SIRS logic AND the rule's own docstring treat all four as independent OR alternatives |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nora_6h=absent; leucocitos=15000; bastoes=5%; pcr=50 | criterion fires (leukocytosis >12,000 satisfies the OR) | False — WBC/band clause True but PCR clause (>100) False, so all([...]) is False | no |
| nora_6h=absent; leucocitos=8000; bastoes=5%; pcr=150 | criterion fires per docstring OR (PCR>100 alone) | False — WBC/band clause False (8000 not >12000/<4000, 5% not >10), so all([...]) False even though PCR>100 | no |
| nora_6h=absent; leucocitos=15000; bastoes=5%; pcr=150 | criterion fires (leukocytosis OR PCR) | True — both WBC clause and PCR clause satisfied | yes |
| nora_6h=absent; leucocitos=12000; bastoes=10%; pcr=150 | does NOT fire on WBC/bands (SIRS uses strict >12,000 and >10%); would fire only if PCR counts as OR | False — leucocitos not >12000, bastoes not >10 (strict), WBC/band clause False -> all False | yes |

**Verifier notes**

Confirms the extraction-flagged DISCREPANCY. PCR>100 is AND-combined (mandatory co-condition) rather than an OR alternative, so isolated leukocytosis, leukopenia, or bandemia (all valid SIRS markers) fail to trigger this minor criterion unless PCR>100 also present. Reduces sensitivity of the sepsis minor-criteria screen; moderate because it is one of nine minor criteria and the alert can still fire via other criteria. WBC/band cutoffs themselves are faithful to SIRS.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 844-913 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-115`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

DISCREPANCY - PCR>100 is AND-combined with the leukocyte/band clause; docstring lists all four as OR alternatives.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
