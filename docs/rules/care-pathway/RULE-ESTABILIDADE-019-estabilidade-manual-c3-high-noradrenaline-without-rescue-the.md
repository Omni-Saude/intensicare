# RULE-ESTABILIDADE-019 — Estabilidade manual C3 - high noradrenaline without rescue therapy

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Flags noradrenaline dose > 21 ml together with absence of vasopressin OR absence of hydrocortisone.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| noradrenalina.quantidade | float | ml | 0-200 |
| vasopressina | bool |  |  |
| hidrocortisona | bool |  |  |

## Outputs

| name | type |
|---|---|
| criterio_3 | bool |

## Logic

```text
all([
  buscar_quantidade_noradrenalina() > 21,
  any([not vasopressina, not hidrocortisona]),
])
```

## Edge cases (as implemented)

buscar_quantidade_noradrenalina returns False (->0) if no noradrenaline; False>21 -> False. Strict > 21. Test uses quantidade=22 -> True.

## Divergence

Code vs _REGRAS spec text: code uses strict `> 21` while the _REGRAS description states "noradrenalina >= 21ml mcg" (inclusive boundary). (Prior _ANTIGAS_REGRAS threshold was 25, lowered to 21.)

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Surviving Sepsis Campaign 2021 (Evans et al., Crit Care Med 2021): add vasopressin (usually at norepinephrine 0.25-0.5 mcg/kg/min) and IV hydrocortisone (norepinephrine/epinephrine >= 0.25 mcg/kg/min for >= 4h) as adjuncts in ongoing/high-dose vasopressor requirement. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

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
| quantidade=22; vasopressina=false; hidrocortisona=true | high vasopressor lacking vasopressin adjunct -> flag need for adjunct (concept SSC-concordant) | 22>21 True AND any([not False=True, not True=False]) = True -> criterio_3 = True | yes |
| quantidade=21; vasopressina=false; hidrocortisona=false | _REGRAS spec text says >= 21 -> should flag at exactly 21 | 21>21 False (strict >) -> criterio_3 = False (does NOT flag at boundary) | no |
| quantidade=30; vasopressina=true; hidrocortisona=true | both adjuncts already present -> no flag | 30>21 True AND any([not True=False, not True=False]) = False -> criterio_3 = False | yes |

**Verifier notes**

The clinical CONCEPT (high-dose noradrenaline without vasopressin OR hydrocortisone adjunct) is guideline-concordant with SSC-2021. Two divergences: (1) extraction-flagged code >21 vs internal _REGRAS spec ">=21" -- affects only the exact boundary dose 21, negligible; (2) the numeric anchor "21 ml" (noradrenalina.quantidade in ml, likely infusion volume) has NO published reference and its unit (ml) is not convertible to the SSC adjunct trigger dose in mcg/kg/min without concentration/ weight -- so the numeric threshold itself is unverifiable against the guideline (same ml-vs- mcg/kg/min theme as RULE-016). Verdict DISCREPANCY (honors carried status + boundary diff); impact low because the boundary affects a single value and the adjunct concept matches the reference.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_estabilidade.py` | 86-89,116-127 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estab-BE-10-021`

**Related rules:**

- [RULE-ESTABILIDADE-007](../alert-threshold/RULE-ESTABILIDADE-007-estabilidade-v3-criterio-7-high-dose-noradrenaline-without-a.md)
- [RULE-ESTABILIDADE-023](../alert-threshold/RULE-ESTABILIDADE-023-estabilidade-manual-pathway-alert-level.md)

## Notes

Variant of v3 criterio_7 (RULE-007, noradrenaline>20 ml/h) — same clinical rule (high vasopressor without vasopressin/hydrocortisone adjuncts), different unit/threshold. SSC adjunct anchor. Unit test test_trilha_estabilidade.py:76-88.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
