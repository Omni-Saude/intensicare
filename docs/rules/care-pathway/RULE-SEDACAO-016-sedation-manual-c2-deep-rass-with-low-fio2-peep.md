# RULE-SEDACAO-016 — Sedation manual C2 - deep RASS with low FiO2/PEEP

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | none |

## Rule
Flags deeply sedated (RASS -2..-5) patients on low ventilatory support (FiO2 <=40 and PEEP low).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| rass | str enum |  | -2..-5 |
| fio2 | float | percent/fraction |  |
| peep | float | cmH2O | 0-40 |

## Outputs

| name | type |
|---|---|
| criterio_2 | boolean |

## Logic

```text
criterio_2 = all([
  rass in ['-2','-3','-4','-5'],
  40 >= fio2 > 0,
  10 >= peep > 0,
])
```

## Edge cases (as implemented)

Requires fio2>0 and peep>0 strictly. fio2==40 allowed; peep==10 allowed.

## Divergence

Model _REGRAS text (line 22) states criterio_2 as "FIO2 <= 40 E PEEP < 10", but the code uses `10 >= peep` (line 119), which ALLOWS peep==10 (i.e. PEEP <= 10, not < 10). Threshold-boundary divergence between the code and its own descriptive rule text.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** none
- **Reference:** Sessler CN et al. The Richmond Agitation-Sedation Scale (RASS). Am J Respir Crit Care Med 2002;166:1338-1344 (10-point scale, -5 unresponsive to +4 combative; -2..-5 = moderate-to-deep sedation). Combined with PADIS 2018 light-sedation targeting: deeply sedated patients on low ventilatory support are candidates for sedation reduction. FiO2 in percent (0-100), PEEP in cmH2O. ([source](https://www.mdcalc.com/calc/1872/richmond-agitation-sedation-scale-rass))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| rass=-3; fio2=40; peep=10 | false | true | no |
| rass=-3; fio2=41; peep=8 | false | false | yes |
| rass=-1; fio2=30; peep=5 | false | false | yes |
| rass=-5; fio2=40; peep=11 | false | false | yes |

**Verifier notes**

Confirmed at source (trilha_manual/models/trilha_sedacao.py:113-120). The RASS deep-sedation band (-2..-5) and FiO2%/PEEP-cmH2O units are all valid against the published RASS scale, and FiO2 is correctly on the percent scale (no fraction/percent unit mismatch). The characterized discrepancy is code-vs-documentation only: code uses `10 >= peep` (PEEP<=10) while the model's own _REGRAS descriptor states "PEEP<10". This affects exactly the single boundary value PEEP==10 cmH2O; clinically negligible (1 cmH2O), so impact none. The composite "deep RASS + low support -> lighten sedation" criterion has no single published numeric cutoff (institutional), but its component scales verify against reference. Preserving extraction status DISCREPANCY, characterized not dismissed; not corrected.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sedacao.py` | 113-120 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-10-012`

**Related rules:**

- [RULE-SEDACAO-021](../alert-threshold/RULE-SEDACAO-021-sedation-manual-pathway-alert-level-count-of-criteria.md)

## Notes

DISCREPANCY vs _REGRAS text (PEEP<10 vs code PEEP<=10). Test test_trilha_sedacao.py:55-73 (fio2=41 or peep=11 -> False). Preserved verbatim.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
