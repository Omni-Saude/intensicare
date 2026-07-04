# RULE-ESTABILIDADE-009 — Estabilidade v3 criterio_9 - dobutamine with high-dose noradrenaline

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Noradrenaline > 50ml/h AND dobutamine > 10ml/h in last 4h. Defined but UNWIRED.

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_nora | float | ml/h |
| balanco.qt_vol_dobuta | float | ml/h |

## Outputs

| name | type |
|---|---|
| criterio_9 | boolean |

## Logic

```text
return all([
  balanco_4h.filter(qt_vol_nora__gt=50, qt_vol_dobuta__gt=10).exists(),
]) if balanco_4h else False
```

## Edge cases (as implemented)

nora>50 AND dobuta>10 in the SAME record. Unwired.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Surviving Sepsis Campaign 2021 (Evans et al.): for septic shock with cardiac dysfunction and persistent hypoperfusion despite adequate volume and arterial pressure, add dobutamine (or switch to epinephrine). Rationale for facade FC>130 note: tachycardia shortens diastolic LV filling and can reduce cardiac output. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | diff |
| units | diff |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_nora_mlh=55; qt_vol_dobuta_mlh=12; FC=140 | SSC: high-dose vasopressor + dobutamine = refractory shock on inotrope; facade advises suspend dobutamine IF FC>130 — here FC=140 so advice fits, but predicate never verified FC | filter(nora>50, dobuta>10) T -> True (FC ignored) | no |
| qt_vol_nora_mlh=55; qt_vol_dobuta_mlh=12; FC=90 | at FC 90 (no tachycardia) the 'suspend dobutamine for FC>130' advice is inappropriate | filter(nora>50, dobuta>10) T -> True and displays the FC>130-conditional advice regardless of FC=90 | no |
| qt_vol_nora_mlh=50; qt_vol_dobuta_mlh=15; FC=140 | no published ml/h anchor; nora at exactly 50 is not high-dose per this rule | nora>50 strict -> 50 not >50 -> filter empty -> False | no |

**Verifier notes**

Two divergences from the paired facade recommendation (RULE-016 criterio_9): (1) the displayed advice is conditioned on FC >130 bpm (physiologically sound — suspend dobutamine when tachycardia impairs filling), but the predicate tests ONLY nora>50 ml/h AND dobuta>10 ml/h and never reads FC, so the FC-conditional recommendation is shown irrespective of actual heart rate (vector 2); (2) same ml/h-vs-mcg/kg/min unit issue as 007/008. The underlying concept (dobutamine used with high-dose vasopressor = cardiac dysfunction in shock) aligns with SSC-2021. Moderate impact: clinician may see 'suspend dobutamine' framed around a tachycardia threshold that was not checked. Predicate is UNWIRED. ml/h cutoffs institution-specific/unverifiable.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 523-542 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-069`

**Related rules:**

- [RULE-ESTABILIDADE-016](../drug-dosing/RULE-ESTABILIDADE-016-estabilidade-facade-alert-text-vasopressor-inotrope-escalati.md)
- [RULE-ESTABILIDADE-022](../care-pathway/RULE-ESTABILIDADE-022-estabilidade-manual-c6-dobutamine-with-exact-noradrenaline-5.md)

## Notes

Facade criterio_9 alert also describes a FC>130 bpm tachycardia trigger that this predicate does NOT implement (see divergence on RULE-016). Manual-pathway counterpart RULE-022 uses dobutamine>10 AND noradrenaline == 50 (equality bug).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
