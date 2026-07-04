# RULE-SEPSE-037 — Sepse criterio_11 - Placeholder (sempre False)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Minor criterion 11 is hard-coded to always return False (unimplemented placeholder).

## Inputs

_None._

## Outputs

- criterio_11 (boolean)

## Logic

```text
def calcular_criterio_11(self):
    return False
```

## Edge cases (as implemented)

Always False.

## Divergence

DISCREPANCY/consequence: because criterio_11 is always False, the "menores" group (c8,c9,c10,c11) can hold at most 3 True values, so the alert condition `menores == 4` in RULE-sepse-BE-06-013 is UNREACHABLE.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Impact rationale:** A permanently-False minor criterion caps the minor-criteria count at 3/4, making the downstream 'menores == 4' alert branch dead code and risking under-alerting for the four-minor-criteria pathway; severity is bounded because major-criteria and 3-minor pathways still fire.
- **Reference:** No clinical reference: criterio_11 is an unimplemented placeholder (calcular_criterio_11 -> return False, sepse.py:332-333). The intended minor criterion is unknown, so there is nothing to verify against a guideline. Pre-existing DISCREPANCY carried from extraction. ([source](n/a))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | n/a |
| units | n/a |
| ranges | n/a |
| rounding | n/a |
| cutoffs | hard-coded constant False; no cutoff implemented |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| any=any patient state | unknown (criterion never specified/implemented) | return False | no |
| menores_group=c8=True, c9=True, c10=True | menores could reach 4 if c11 implementable | c11 always False -> menores caps at 3 | no |
| alert_condition=menores == 4 (RULE-sepse-BE-06-013) | reachable | UNREACHABLE (max menores = 3) | no |

**Verifier notes**

Software-completeness defect, not a clinical-equation mismatch. Characterized per instruction: unimplemented placeholder with the documented consequence that the menores==4 alert branch is unreachable. Requires internal implementation decision on the intended 11th criterion.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 332-333 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-011`

**Related rules:**

- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)

## Notes

DISCREPANCY/consequence: because criterio_11 is always False, the "menores" group (c8,c9,c10,c11) can hold at most 3 True values, so the alert condition `menores == 4` in RULE-sepse-BE-06-013 is UNREACHABLE.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
