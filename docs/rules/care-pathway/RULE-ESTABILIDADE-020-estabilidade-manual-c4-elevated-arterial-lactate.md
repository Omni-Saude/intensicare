# RULE-ESTABILIDADE-020 — Estabilidade manual C4 - elevated arterial lactate

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | care-pathway |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Flags arterial lactate >= 2.5.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| lactato_arterial | float | mmol/L (units ambiguous; _REGRAS text says mg/dl) | 0-20 |

## Outputs

| name | type |
|---|---|
| criterio_4 | bool |

## Logic

```text
lactato_arterial >= 2.5
```

## Edge cases (as implemented)

Inclusive >= 2.5. Default lactato 0 -> False.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Singer M, et al. The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). JAMA 2016;315(8):801-810 — septic shock identified by vasopressor need + serum lactate >2 mmol/L (>18 mg/dL); Surviving Sepsis Campaign 2021 uses lactate >2 mmol/L as the hypoperfusion anchor. ([source](https://pubmed.ncbi.nlm.nih.gov/26903338/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | diff |
| units | diff |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| lactato_arterial=2.0 | elevated/hypoperfusion TRUE (>2 mmol/L abnormal) | FALSE (2.0 >= 2.5 is false) | no |
| lactato_arterial=2.3 | TRUE (>2 mmol/L) | FALSE (2.3 >= 2.5 is false) | no |
| lactato_arterial=2.5 | TRUE | TRUE (2.5 >= 2.5) | yes |
| lactato_arterial=1.8 | FALSE (<2 mmol/L, normal) | FALSE | yes |
| lactato_arterial=0 | FALSE (default/normal) | FALSE | yes |

**Verifier notes**

Legacy manual C4 (trilha_estabilidade.py:130) flags lactato_arterial >= 2.5, whereas the Sepsis-3 / SSC hypoperfusion anchor is >2.0 mmol/L (>18 mg/dL). The higher, inclusive 2.5 cutoff misses mild hyperlactatemia in the 2.0-2.49 mmol/L band that references would flag — a screening-sensitivity gap, hence low (not none). Secondary flag: input unit label is ambiguous — _REGRAS text says mg/dl but the 2.5 value is only coherent as mmol/L (2.5 mg/dL is far below the normal lactate ceiling of ~18 mg/dL; if code were fed mg/dL, essentially no patient would trigger). Value is consistent with the mmol/L interpretation, so no evidence of an active unit bug in the comparison, but the mislabel should be corrected. Sibling v3/facade criteria use the 2.0 anchor (per catalog notes), so 2.5 is an intra-system inconsistency too.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_estabilidade.py` | 129-130 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estab-BE-10-022`

**Related rules:**

- [RULE-ESTABILIDADE-003](../alert-threshold/RULE-ESTABILIDADE-003-estabilidade-v3-criterio-1-hypoperfusion-on-vasopressor.md)
- [RULE-ESTABILIDADE-023](../alert-threshold/RULE-ESTABILIDADE-023-estabilidade-manual-pathway-alert-level.md)

## Notes

Manual uses lactate >= 2.5; v3/facade criteria use the Sepsis-3 anchor of 2.0. Unit label inconsistent across pathways (_REGRAS says mg/dl, clinically mmol/L). Same 2.5 value also appears in sepse C13 and ventilacao C9 per Phase-1 cross-cluster notes. Unit test test_trilha_estabilidade.py:90-93.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
