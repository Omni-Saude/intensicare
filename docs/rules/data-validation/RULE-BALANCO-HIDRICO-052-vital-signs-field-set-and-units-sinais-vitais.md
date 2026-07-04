# RULE-BALANCO-HIDRICO-052 — Vital-signs field set and units (sinais vitais)

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Enumerates the vital-sign fields captured/displayed for a fluid-balance vital signs record, with their clinical units. Each field row is rendered only when its value is truthy (present/non-empty; 0 is falsy and thus hidden).

## Inputs

- frequencia_cardiaca (bpm)
- frequencia_respiratoria (FR/m (breaths per minute))
- pas / pad (mmHg)
- temperatura (°C)
- saturacao_o2 (%)
- hgt
- ventilacao_humanizado
- fluxo_o2_sup (% (Fluxo O2 Suplementar))
- fio2 (%)
- nv_consciencia_humanizado
- dor_humanizado
- escala_dor
- sinais_dor
- motivo_queixa

## Outputs

- rendered vital-sign rows

## Logic

```text
For each field option: render row only if option.value is truthy.
Field -> label(unit) mapping:
  frequencia_cardiaca      -> "Freq. Cardiaca (bpm)"
  frequencia_respiratoria  -> "Freq. Respiratoria (FR/m)"
  (pas,pad)                -> "Pressao Arterial (mmHg)" (see RULE-balanco-FE-03-001)
  temperatura              -> "Temperatura (°C)"
  saturacao_o2             -> "Saturacao O2 (%)"
  hgt                      -> "HGT"
  ventilacao_humanizado    -> "Ventilacao"
  fluxo_o2_sup             -> "Fluxo O2 Suplementar (%)"
  fio2                     -> "FiO2 (%)"
  nv_consciencia_humanizado-> "Nv. Consciencia"
  dor_humanizado           -> "Dor"
  escala_dor               -> "Escala de Dor"
  sinais_dor               -> "Sinais de Dor"
  motivo_queixa            -> "Queixa"
```

## Edge cases (as implemented)

Any field whose value is 0, null, undefined, or empty string is not rendered (truthiness filter at line 122). This means a genuine reading of 0 (e.g. escala_dor 0, saturacao 0) would be suppressed.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/BalancoHidricoItens/ItemSinaisVitais/ItemSinaisVitais.tsx` | 35-127 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-FE-03-002`

**Related rules:**

- [RULE-BALANCO-HIDRICO-018](../physiological-calculation/RULE-BALANCO-HIDRICO-018-blood-pressure-display-composition-systolic-diastolic.md)
- [RULE-BALANCO-HIDRICO-053](RULE-BALANCO-HIDRICO-053-fluid-intake-output-field-set-and-volume-unit-entrada-saida.md)

## Notes

Units are the clinical contract for a vitals capture form. No range validation is enforced client-side here; validation (if any) lives in the form/backend (out of partition). "HGT" = capillary blood glucose (hemoglucoteste); no unit label shown.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
