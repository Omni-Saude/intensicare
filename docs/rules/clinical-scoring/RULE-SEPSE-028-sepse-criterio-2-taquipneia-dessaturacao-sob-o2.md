# RULE-SEPSE-028 — Sepse criterio_2 - Taquipneia / dessaturacao sob O2

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Major criterion 2 fires if the patient is NOT on mechanical ventilation and respiratory rate > 20, OR is on O2 support and SpO2 < 96%.

## Inputs

- sinais_vitais.ventilacao (enum, ambiente|suporte_o2|mecanica)
- sinais_vitais.frequencia_respiratoria (int, breaths/min)
- sinais_vitais.saturacao_o2 (float, percent)

## Outputs

- criterio_2 (boolean)

## Logic

```text
branch_A = (ventilacao != "mecanica" if ventilacao else True) AND (frequencia_respiratoria > 20 if frequencia_respiratoria else False)
branch_B = (ventilacao == "suporte_o2" if ventilacao else False) AND (saturacao_o2 < 96 if saturacao_o2 else False)
return any([branch_A if sinais_vitais else False, branch_B if sinais_vitais else False])
```

## Edge cases (as implemented)

If ventilacao is null, branch_A treats it as "not mechanical" (True). FR strict > 20. SpO2 strict < 96. Falsy FR/SpO2 (None or 0) fail their sub-conditions.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** ACCP/SCCM SIRS respiratory criterion (Bone RC et al., Chest 1992): respiratory rate > 20 breaths/min. SpO2 < 96% under O2 support is an institutional refinement (not a SIRS element; consistent with hypoxemia surveillance / NEWS2 supplemental-O2 flag). ([source](https://emedicine.medscape.com/article/168943-overview))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | ok |
| units | ok (breaths/min; percent SpO2) |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok for RR (>20 matches SIRS); SpO2<96% institutional |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| ventilacao=ambiente; fr=22; sat_o2= | tachypnea True (RR>20) | True (branch_A: not-mechanical AND 22>20) | yes |
| ventilacao=ambiente; fr=20; sat_o2= | False (SIRS strict >20) | False (20>20 False; branch_B needs suporte_o2) | yes |
| ventilacao=suporte_o2; fr=18; sat_o2=94 | SIRS RR not met; institutional hypoxemia-on-O2 flag True | True (branch_B: suporte_o2 AND 94<96) | yes |
| ventilacao=mecanica; fr=30; sat_o2=90 | excluded on invasive vent (RR/SpO2 not interpretable as spontaneous tachypnea) | False (branch_A not-mechanical False; branch_B suporte_o2 False) | yes |

**Verifier notes**

RR threshold >20 matches SIRS exactly. The SpO2<96%-on-O2-support branch is an institutional add-on with no single published cutoff but is clinically defensible. Null ventilacao defaults branch_A to 'not mechanical' (True) - conservative/sensitive, acceptable. Branch_B (suporte_o2 AND SpO2<96) is reused verbatim in criterio_6.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 114-142 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-002`

**Related rules:**

- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)

## Notes

Branch_B (suporte_o2 AND SpO2<96) is duplicated verbatim as one branch of criterio_6.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
