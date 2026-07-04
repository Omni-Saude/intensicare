# RULE-SEDACAO-004 — Sedacao v3 criterio_12 - weaning readiness (defined, unwired, bad thresholds)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | clinical-scoring |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | none |

## Rule
Intended: RASS>0 AND PSV mode AND PINS<15 AND PEEP<=10 AND P/F>250 AND FiO2<50% AND FR>22 AND absence of dexmedetomidine/morphine.

## Inputs

| name | type | unit |
|---|---|---|
| evolucao.rass, diurna_ventilacao, pins, peep, pf, fio2 | int / string / float |  |
| balanco.fr, qt_vol_dex, qt_vol_mor | float | ipm / ml/h |

## Outputs

| name | type |
|---|---|
| criterio_12 | boolean |

## Logic

```text
return all([
  int(evolucao.rass) >= 0 if evolucao.rass else False,
  evolucao.diurna_ventilacao == "PSV",
  get_number(evolucao.pins) < 15,
  get_number(evolucao.peep) <= 10,
  get_number(evolucao.pf)   > 250,
  get_number(evolucao.fio2) > 250,      # docstring intent: FiO2 < 50%
  get_number(ultimo_balanco.fr) > 250,  # docstring intent: FR > 22
  any([ ultimo_balanco.qt_vol_dex, ultimo_balanco.qt_vol_mor ]),  # docstring intent: ABSENCE
]) if ultima_evolucao else False
```

## Edge cases (as implemented)

fio2>250 and fr>250 are physiologically impossible; reads bare evolucao.pins/peep/pf/fio2 (real fields are diurna_*) so those default to 0.

## Divergence

Three code-vs-intent divergences (all inert since criterio_12 is unwired): (1) `fio2 > 250` instead of FiO2 < 50%; (2) `fr > 250` instead of FR > 22; (3) `any([qt_vol_dex, qt_vol_mor])` checks PRESENCE of dexmedetomidine/morphine though intent is ABSENCE. Also reads bare fields pins/peep/pf/fio2 (actual model fields are diurna_pins/diurna_peep/diurna_pf/diurna_fio2), so getattr defaults 0.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** none
- **Reference:** Spontaneous breathing / ventilator-weaning readiness screen concepts per SCCM/ATS liberation guidance: adequate oxygenation P/F>200-250, FiO2 <=0.4-0.5 (i.e. <50%), PEEP <=5-10 cmH2O, arousable patient (RASS >= -2/awake), plus tachypnea threshold RR>22 (qSOFA/clinical). FiO2 is a percent (0-100) or fraction (0-1); respiratory rate physiologic range ~8-40 ipm. ([source](https://www.atsjournals.org/doi/10.1164/rccm.201612-2427ST))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | 3 code-vs-intent divergences confirmed |
| units | UNIT ERROR - FiO2 compared with >250 though FiO2 is percent(0-100)/fraction(0-1); no FiO2 value can exceed 250 |
| ranges | fr>250 impossible (physiologic RR ~8-40 ipm); intended FR>22 |
| rounding | n/a |
| cutoffs | fio2>250 vs intended <50%; fr>250 vs intended >22; any([qt_vol_dex,qt_vol_mor]) checks PRESENCE vs intended ABSENCE |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| rass=1; diurna_ventilacao=PSV; pins=10; peep=8; pf=300; fio2=40; fr=24; dex=0; mor=0 | weaning-ready -> True | fio2>250 (40>250 False) -> all() False; also bare pins/peep/pf/fio2 read as 0 | no |
| rass=1; diurna_ventilacao=PSV; pins=10; peep=8; pf=300; fio2=30; fr=300; dex=0; mor=0 | FR 300 non-physiologic -> invalid input; true FR>22 would qualify | only a FR of 300 could pass fr>250, and fio2>250 still fails -> False | no |
| rass=1; diurna_ventilacao=PSV; pins=10; peep=8; pf=300; fio2=40; fr=24; dex=5; mor=0 | dexmedetomidine present -> NOT weaning-ready -> False | any([dex,mor]) True (rewards presence), but fio2>250 clause fails -> False | no |

**Verifier notes**

Multiple confirmed divergences, including the exact unit-mismatch class this audit targets: (1) `get_number(evolucao.fio2) > 250` - FiO2 is a percent/fraction, threshold physiologically impossible, intent is FiO2<50%; (2) `get_number(ultimo_balanco.fr) > 250` vs intended FR>22 ipm; (3) `any([qt_vol_dex, qt_vol_mor])` tests PRESENCE of dexmedetomidine/morphine though the docstring intent is ABSENCE. Additionally reads bare fields pins/peep/pf/fio2 while the real model fields are diurna_pins/diurna_peep/diurna_pf/diurna_fio2, so getattr defaults them to 0. Net effect: criterio_12 can essentially never be True. Clinical impact = none because criterio_12 is UNWIRED; were it wired, impact would be high (weaning-readiness alert would never fire, and the sedative-presence logic is inverted). Preserved verbatim; source lines 787-818.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 787-818 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-053`

**Related rules:**

- [RULE-SEDACAO-003](RULE-SEDACAO-003-sedacao-v3-criterio-9-deep-sedation-rass-3-5-defined-unwired.md)

## Notes

DISCREPANCY (multiple). Preserve verbatim. Unwired.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
