# RULE-SEPSE-008 — SEPSE v3 criterio_2 - tachypnea/hypoxemia without vasopressor or invasive vent

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | low |

## Rule
No noradrenaline (6h) AND no invasive mechanical ventilation AND (FR>20 OR SatO2<94).

## Inputs

- balanco.qt_vol_nora, balanco.fr, balanco.sat_o2 (float, ml/h / ipm / %)
- cpoe.vent_mecanica_invasiva, evolucao.diurna_ventilacao (float / string)

## Outputs

- criterio_2 (boolean)

## Logic

```text
return all([
  not balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  any([ not get_number(cpoe.vent_mecanica_invasiva),
        (not evolucao.diurna_ventilacao.strip().lower() in get_ventilacao("ventilacao_mecanica_invasiva")) if evolucao.diurna_ventilacao else False ]),
  any([ get_number(balanco.fr) > 20, get_number(balanco.sat_o2) < 94 ]),
]) if balanco_6h and ultimo_balanco and ultima_evolucao and ultima_cpoe else False
```

## Edge cases (as implemented)

get_number coerces null/blank to 0 (SatO2 0<94 would spuriously satisfy). fr here is the frequencia respiratoria column.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** low
- **Reference:** SIRS respiratory criterion (ACCP/SCCM Consensus 1992): respiratory rate > 20 breaths/min. SpO2 < 94% is a standard hypoxemia alert threshold (Surviving Sepsis Campaign 2021 supplemental O2 target SpO2 >= 94%). ([source](https://pubmed.ncbi.nlm.nih.gov/26903336/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| fr=22; sat_o2=98; noradrenaline_6h=absent; invasive_vent=false | Tachypnea (RR>20 SIRS), not on pressor/invasive vent -> fire | all([not nora=TRUE, not invasive=TRUE, (22>20=TRUE OR 98<94)=TRUE]) = TRUE | yes |
| fr=18; sat_o2=90; noradrenaline_6h=absent; ventilation=spontaneous | Hypoxemia SpO2<94 -> fire | all([TRUE, TRUE, (18>20=FALSE OR 90<94=TRUE)=TRUE]) = TRUE | yes |
| fr=20; sat_o2=98; noradrenaline_6h=absent; invasive_vent=false | RR=20 is NOT >20 (SIRS strict), SpO2 normal -> no fire | (20>20=FALSE OR 98<94=FALSE)=FALSE -> criterion FALSE | yes |
| fr=; sat_o2=; noradrenaline_6h=absent; invasive_vent=false | No data -> should not fire | get_number(null)=0; 0<94=TRUE -> criterion spuriously TRUE | no |

**Verifier notes**

Core physiologic thresholds match the reference: RR>20 is exactly the SIRS respiratory criterion (strict >, so 20 does not fire, correct), and SpO2<94% is a standard hypoxemia trigger consistent with SSC 2021 oxygenation targets. The no-vasopressor / no-invasive-vent composite gating is an institutional adaptation with no unit or coefficient error. VERIFIED on all reference-checkable dimensions. Caveat (data-quality, not a reference discrepancy): get_number coerces null/blank SatO2 to 0 and 0<94 spuriously satisfies the hypoxemia clause when SpO2 is simply unrecorded (low impact - requires missing data plus all other gates clear).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 384-425 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-102`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

get_ventilacao categories defined in trilha_automatica/utils.py (outside BE-03).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
