# RULE-SEPSE-057 — Sepsis C20 (minor) - recent abdominal surgery

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Minor criterion - history of recent abdominal surgery (boolean flag).

## Inputs

- historico_cirurgia_abdominal_recente (bool)

## Outputs

- criterio_20 (bool)

## Logic

```text
return dp.historico_cirurgia_abdominal_recente
```

## Edge cases (as implemented)

Direct boolean passthrough. Test False->False, True->True.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No validated published equation/cutoff. Directional support: recent abdominal/GI surgery is an established intra-abdominal infection source (Surviving Sepsis Campaign 2021, source-control section) but no published rule defines 'recent abdominal surgery' as a discrete numeric sepsis-screening criterion. The RULE-SEPSE-058 label pins it at '<20 dias' — an institutional definition. ([source](https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-guidelines-2021))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a (boolean flag; any day-count window applied upstream) |
| ranges | n/a |
| rounding | n/a |
| cutoffs | unverifiable — 'recent' (<20 days per v3 label) is institutional |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| historico_cirurgia_abdominal_recente=false | false (institutional passthrough) | false | yes |
| historico_cirurgia_abdominal_recente=true | true (institutional passthrough) | true | yes |
| historico_cirurgia_abdominal_recente= | n/a (no null handling) | null (returns flag unchanged) | yes |

**Verifier notes**

Legacy calcular_criterio_20 (trilha_sepse.py:484-489) is a pure boolean passthrough of historico_cirurgia_abdominal_recente. Passthrough faithful to source. The '<20 dias' recency window is institutional; no authoritative reference. Flag for internal review.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 484-489 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-045`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:284-287.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
