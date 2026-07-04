# RULE-SEPSE-060 — Sepse pathway variant A - 11-criterion catalog + Meropenem/1500ml recommendation

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Sepsis pathway variant A: nested {"criterios": {...}} structure with 11 qualitative alert flags and a single global recommendation naming a specific empiric antibiotic and fixed fluid bolus. Structure differs from variants B/C (criterios nested under a key).

## Inputs

- criterio_1..criterio_11 flags (bool)

## Outputs

- alerta per criterion (string)
- recomendacao block (list[string])

## Logic

```text
Alerts: 1 Febre; 2 Taquipneia; 3 Falencia respiratoria; 4 Perfusao tecidual prejudicada;
5 Hipotensao; 6 Oliguria; 7 Alteracao do nivel de consciencia; 8 Hipotermia;
9 Taquicardia; 10 Cateter antigo; 11 Cateter femoral.
RECOMMENDATION: abrir protocolo SEPSE; solicitar hemocultura aerobica x2 perifericas;
cultura secrecao traqueal (se traqueostomia); urocultura (se diurese);
hemograma/bilirrubinas/ureia/creatinina/gasometria+lactato/TAP/TTPA; RX torax;
lactato arterial apos 3h. Considerar Meropenem 1 g EV. Se hipotensao OU oliguria OU
alt. consciencia -> ressuscitacao volemica 1500 ml Ringer Lactato em bolus. Se hipotensao
refrataria -> noradrenalina (mesmo em acesso periferico). Trocar/retirar cateter se > 7 dias
ou hiperemia/secrecao. Cuidados de fim de vida -> descontinuar.
```

## Edge cases (as implemented)

Recommendation strings are concatenated without separators (implicit joins).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Surviving Sepsis Campaign 2021 (Evans et al., Crit Care Med 2021) — weight-based 30 mL/kg IV crystalloid within 3h; remeasure lactate to guide resuscitation; empiric broad-spectrum antibiotics within 1h (agent not specified by guideline). Fixed-volume bolus is not a guideline construct. ([source](https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-guidelines-2021))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff — fixed 1500 mL Ringer Lactato bolus vs SSC weight-based 30 mL/kg (no per-kg scaling) |
| coefficients | n/a |
| units | ok (mL, g); lactate re-check 'apos 3h' consistent with SSC lactate-guided remeasurement |
| ranges | n/a |
| rounding | n/a |
| cutoffs | Meropenem 1 g EV is a specific institutional empiric choice; SSC recommends broad-spectrum but names no agent/dose. Trigger 'hipotensao OU oliguria OU alt. consciencia -> bolus' broadly aligns with sepsis-induced hypoperfusion concept. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| weight_kg=50 | 1500 mL (SSC 30 mL/kg x 50) | 1500 mL fixed bolus | yes |
| weight_kg=70 | 2100 mL (SSC 30 mL/kg x 70) | 1500 mL fixed bolus (under-resuscitates by 600 mL) | no |
| weight_kg=100 | 3000 mL (SSC 30 mL/kg x 100) | 1500 mL fixed bolus (under-resuscitates by 1500 mL) | no |

**Verifier notes**

Care-pathway text (core/facade/sepse.py:1-34, variant A). Fixed 1500 mL Ringer Lactato bolus diverges from SSC 2021 weight-based 30 mL/kg: coincides only at ~50 kg and progressively under-resuscitates heavier adults (600 mL short at 70 kg, 1500 mL short at 100 kg) — moderate impact because under-dosing initial fluid can delay perfusion restoration, though vasopressors and reassessment follow. Lactate remeasurement after 3h aligns with SSC lactate-guided approach; cultures/imaging/catheter change align. Meropenem 1 g is an institutional empiric choice (not guideline-specified). Rule status AMBIGUOUS from extraction: consumer not evident within scope (facade/sepse.py aliases the 27-criterion variant B instead), so this payload appears deprecated/unwired — the fluid discrepancy is characterized against SSC but may not reach patients if the payload is dead code. Not dismissing; flag for internal confirmation of wiring.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/sepse.py` | 1-34 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-01-003`

**Related rules:**

- [RULE-SEPSE-058](../alert-threshold/RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)
- [RULE-SEPSE-059](RULE-SEPSE-059-sepse-automatica-variant-b-27-criterion-alert-catalog-global.md)
- [RULE-SEPSE-061](../drug-dosing/RULE-SEPSE-061-sepse-volume-expansion-expansao-volemica-decision-and-dosing.md)

## Notes

AMBIGUOUS: this variant's consumer is not evident within scope (facade/sepse.py aliases the 27-criterion trilha_sepse instead). Appears to be an older/alternate sepsis payload. Distinct dosing: Meropenem 1g + fixed 1500ml bolus (vs 30ml/kg in variant B). Cross-ref -001, -002.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
