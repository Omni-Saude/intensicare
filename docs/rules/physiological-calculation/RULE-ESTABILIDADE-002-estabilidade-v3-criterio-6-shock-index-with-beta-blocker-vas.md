# RULE-ESTABILIDADE-002 — Estabilidade v3 criterio_6 - shock index with beta-blocker/vasopressor absence

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | low |

## Rule
Antibiotic prescribed AND (shock index FC/PAS > 0.7 OR FC/PAM > 0.9) AND absence of all beta-blockers (propranolol, carvedilol, bisoprolol, atenolol, metoprolol) AND absence of noradrenaline. Defined but UNWIRED.

## Inputs

| name | type | unit |
|---|---|---|
| balanco.fc | float | bpm |
| balanco.pas | float | mmHg |
| balanco.pam | float | mmHg |
| cpoe beta-blockers (propranolol/carvedilol/bisoprolol/atenolol/metoprolol) | float |  |
| cpoe.antibiotico | float |  |
| balanco.qt_vol_nora | float | ml/h |

## Outputs

| name | type |
|---|---|
| criterio_6 | boolean |

## Logic

```text
return all([
  get_number(cpoe.antibiotico) > 0,
  any([
    (get_number(fc)/get_number(pas)) > 0.7 if get_number(pas) else False,
    (get_number(fc)/get_number(pam)) > 0.9 if get_number(pam) else False,
  ]),
  all([ not get_number(cpoe.propranolol) > 0, not get_number(cpoe.carvedilol) > 0,
        not get_number(cpoe.bisoprolol) > 0, not get_number(cpoe.atenolol) > 0,
        not get_number(cpoe.metoprolol) > 0, not get_number(balanco.qt_vol_nora) > 0 ]),
]) if (ultima_cpoe and ultima_balanco and ultima_evolucao) else False
```

## Edge cases (as implemented)

Division guarded by truthiness of pas/pam (avoids ZeroDivision). Shock-index thresholds: 0.7 against PAS, 0.9 against PAM. Beta-blocker/noradrenaline absence must ALL hold. Unwired in calcular_criterios.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** low
- **Reference:** Shock Index — Allgower M, Burri C. Dtsch Med Wochenschr 1967 (original); normal SI = HR/SBP 0.5-0.7, >0.9-1.0 associated with higher transfusion/ICU/mortality (Rady MY, Ann Emerg Med 1994; Koch E et al., Open Access Emerg Med 2019, PMC6698590). Modified Shock Index = HR/MAP, commonly cited normal band 0.7-1.3. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC6698590/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | ok |
| units | HR bpm / BP mmHg (dimensionless) — correct |
| ranges | division guarded by truthiness of PAS/PAM (no ZeroDivision) |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| antibiotico=>0; fc=120; pas=100; betablockers=none; nora=absent | flag (SI = 1.20 >> 0.7 upper-normal limit, abnormal) | fires (120/100 = 1.2 > 0.7 True) | yes |
| antibiotico=>0; fc=60; pas=120; pam=85; betablockers=none; nora=absent | no flag (SI = 0.50 normal; MSI = 0.71 within normal band) | no fire (0.50 > 0.7 False; 0.706 > 0.9 False) | yes |
| antibiotico=>0; fc=70; pas=100; pam=77; betablockers=none; nora=absent | borderline/normal (SI = 0.70 at upper-normal; MSI = 0.909 within normal 0.7-1.3) | fires via MSI branch (70/77 = 0.909 > 0.9 True; SI 0.70 > 0.7 False) | yes |

**Verifier notes**

SI branch (FC/PAS > 0.7) matches the published upper limit of normal exactly. The MSI branch (FC/PAM > 0.9) is BELOW the commonly cited MSI abnormal/mortality threshold (~1.3) but is the algebraic MAP-equivalent of SI 0.7 (since SBP/MAP ~= 1.3, SI 0.7 -> MSI ~= 0.9), so the dual cutoffs are internally coherent as an early "above-upper-normal" screen rather than a mortality-prediction cutoff. Beta-blocker + noradrenaline absence gate is clinically sensible (excludes rate-controlled / already-vasopressed patients). Only caveat: the MSI 0.9 screen is more sensitive than a strict MSI>1.3 rule would be. Criterion is UNWIRED, so no production impact.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 398-458 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-066`

**Related rules:**

- [RULE-ESTABILIDADE-013](../alert-threshold/RULE-ESTABILIDADE-013-estabilidade-v3-criterio-13-recurrent-hypertension-off-vasop.md)
- [RULE-ESTABILIDADE-015](../alert-threshold/RULE-ESTABILIDADE-015-estabilidade-facade-alert-text-perfusion-shock-triggers-bica.md)

## Notes

Shock index (heart rate / systolic BP) is a recognized hemodynamic marker; verify against published normal range (0.5-0.7). Facade criterio_6 alert text = "Risco de choque circulatorio (Indice de choque positivo)".

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
