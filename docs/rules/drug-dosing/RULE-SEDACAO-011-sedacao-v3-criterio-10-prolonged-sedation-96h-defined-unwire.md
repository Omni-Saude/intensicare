# RULE-SEDACAO-011 — Sedacao v3 criterio_10 - prolonged sedation >96h (defined, unwired)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | drug-dosing |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | none |

## Rule
Intended: absence of "Sedacao paliativa" justification AND propofol/midazolam/fentanil present for >4 days (96h). Code checks PRESENCE of "Sedacao paliativa".

## Inputs

| name | type | unit |
|---|---|---|
| evolucao.diurna_sedoanalgesia | string |  |
| balanco.qt_vol_mid/pro/fen (96h) | float | ml/h |

## Outputs

| name | type |
|---|---|
| criterio_10 | boolean |

## Logic

```text
presenca_sedativos = any(balanco.qt_vol_mid / qt_vol_pro / qt_vol_fen) over balancos(dt >= now - 96h)
return all([
  evolucao.diurna_sedoanalgesia in ["Sedacao paliativa"],   # intent per docstring: ABSENCE of palliative sedation
  presenca_sedativos,
]) if ultima_evolucao and balanco_96h else False
```

## Edge cases (as implemented)

The 96h condition = any balance within the 96h window (not continuous 96h presence). Unwired.

## Divergence

Docstring/intent requires ABSENCE of "Sedacao paliativa" (`... not in [...]`), but code checks `diurna_sedoanalgesia in ["Sedacao paliativa"]` i.e. PRESENCE. Condition inverted. Inert (unwired).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** none
- **Reference:** Devlin JW et al. Clinical Practice Guidelines for the Prevention and Management of Pain, Agitation/Sedation, Delirium, Immobility, and Sleep Disruption in Adult Patients in the ICU (PADIS). Crit Care Med 2018;46(9):e825-e873. Prolonged sedative/opioid exposure -> iatrogenic tolerance/withdrawal risk; minimize prolonged deep sedation unless a valid indication (e.g. palliative sedation) is present. ([source](https://www.sccm.org/clinical-resources/guidelines/guidelines/focused-update-padis-guideline))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| diurna_sedoanalgesia=Sedacao paliativa; propofol_in_96h=true | false | true | no |
| diurna_sedoanalgesia=Outros; midazolam_in_96h=true | true | false | no |
| diurna_sedoanalgesia=Sedacao paliativa; sedatives_in_96h=false | false | false | yes |

**Verifier notes**

Confirmed at source (trilha_sedacao.py:709-741): code uses `diurna_sedoanalgesia in ["Sedacao paliativa"]` (PRESENCE) whereas the docstring/clinical intent and PADIS-aligned logic require ABSENCE (`not in [...]`). The condition is fully inverted: as written it fires ONLY on patients whose prolonged sedation is appropriately justified (palliative) and never on the target population (prolonged non-palliative sedation). Operational impact is none because criterio_10 is unwired (not called by calcular_criterios); latent impact would be moderate if it were wired, as it would invert the clinical meaning of the alert. Preserved verbatim; not corrected.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 709-741 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-051`

**Related rules:**

- [RULE-SEDACAO-012](RULE-SEDACAO-012-sedacao-v3-criterio-11-prolonged-propofol-without-safety-lab.md)
- [RULE-SEDACAO-014](../alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)

## Notes

DISCREPANCY - condition inverted vs docstring. Preserved verbatim. Unwired.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
