# RULE-SEPSE-053 — Sepsis C16 (minor) - poor oral intake with preserved consciousness

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Minor criterion - low oral diet acceptance AND Glasgow >= 13.

## Inputs

- baixa_aceitacao_dieta_vo (bool)
- glasgow (int)

## Outputs

- criterio_16 (bool)

## Logic

```text
all([ baixa_aceitacao_dieta_vo, (glasgow >= 13) if glasgow else False ])
```

## Edge cases (as implemented)

Both required. Inclusive glasgow>=13. Test baixa+glasgow13 -> True.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published sepsis criterion. 'Baixa aceitacao de dieta VO' (reduced oral intake) with preserved consciousness (Glasgow>=13) is an institutional early-warning/homecare screening observation, not part of SIRS, Sepsis-3, SOFA or qSOFA. ([source](n/a))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | Glasgow>=13 inclusive - institutional; no reference equation |
| units | GCS points (3-15) - internally consistent |
| ranges | n/a |
| rounding | n/a |
| cutoffs | AND of reduced-intake flag and GCS>=13 - no published cutoff to compare |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| baixa_aceitacao_dieta_vo=true; glasgow=13 | n/a (no reference) | all([True, True]) -> True | yes |
| baixa_aceitacao_dieta_vo=true; glasgow=12 | n/a | all([True, False]) -> False | yes |
| baixa_aceitacao_dieta_vo=false; glasgow=15 | n/a | all([False, True]) -> False | yes |
| baixa_aceitacao_dieta_vo=true; glasgow=0 | n/a | glasgow falsy -> all([True, False]) -> False | yes |

**Verifier notes**

Internal/institutional business rule with no authoritative published source - flagged for internal clinical review, NOT treated as wrong. Legacy logic (all([reduced_intake, GCS>=13])) is internally consistent and matches its own test (test_trilha_sepse.py:254-259). GCS>=13 inclusive; glasgow 0/None coerces the second condition to False.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 415-425 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-041`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:254-259.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
