# RULE-SEPSE-059 — Sepse automatica variant B - 27-criterion alert catalog + global recommendation

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Sepsis pathway variant B (payload_sepse_automatica). 27 flagged-criterion alert labels plus one shared "recomendacao" block prescribing the sepsis work-up and resuscitation.

## Inputs

- criterio_1..criterio_27 (flags set by model layer) (bool)

## Outputs

- alerta per criterion (string)
- shared recomendacao block (list[string])

## Logic

```text
Flagged-criterion -> alert label mapping (qualitative unless noted):
1 taquipneico; 2 falencia respiratoria c/ necessidade de suporte ventilatorio;
3 hipotenso; 4 oligurico (disfuncao renal); 5 ictericia (disfuncao hepatica);
6 febre; 7 taquicardico; 8 hipocapnia/hiperventilacao; 9 P/F baixa (troca gasosa);
10 hiperlactatemia; 11 aumento TEC; 12 SOFA > 6; 13 piora do SOFA;
14 piora disfuncao respiratoria c/ aumento FiO2; 15 elevacao da pressao positiva;
16 conversao p/ modo ventilatorio controlado; 17 leucocitose OU leucopenia;
18 plaquetopenia; 19 prejuizo nivel consciencia; 20 piora nivel consciencia;
21 baixa aceitacao dieta VO; 22 dispositivo invasivo > 10 dias;
23 dispositivo vascular femoral > 7 dias; 24 inicio antibiotico nas ultimas 24h;
25 cirurgia abdominal recente; 26 instabilidade + uso de noradrenalina;
27 piora funcao renal nas ultimas 24h.
GLOBAL RECOMMENDATION when pathway opens: hemocultura x2 perifericas; cultura secrecao
traqueal; urocultura; hemograma/bilirrubinas/ureia/creatinina/gasometria+lactato/TAP/TTPA;
RX torax. Antibiotico amplo espectro; se necessidade de noradrenalina -> dupla cobertura
GRAM negativo. Se hipotensao + hipoperfusao (lactato > 2.5 mg/dl, oliguria, TEC aumentado,
alt. consciencia, livedo) -> ressuscitacao volemica 30 ml/kg Ringer Lactato. Trocar/retirar
cateter vascular se > 7 dias ou hiperemia/secrecao. USG p/ fluido-responsividade -> dobutamina.
Cuidados de fim de vida -> descontinuar protocolo.
```

## Edge cases (as implemented)

All per-criterion recomendacoes lists are empty; content only in shared block.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Surviving Sepsis Campaign: International Guidelines 2021 (Evans et al., Crit Care Med 2021;49:e1063-e1143) — 30 mL/kg IV crystalloid within 3h, balanced crystalloid preferred, >=2 blood culture sets before empiric broad-spectrum antibiotics, lactate-guided resuscitation, source control including removal of infected intravascular devices. SOFA per Sepsis-3 (JAMA 2016). ([source](https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-guidelines-2021))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | diff — hypoperfusion trigger written 'lactato > 2,5 mg/dl'; lactate is measured in mmol/L, not mg/dl. 2.5 mg/dL ~= 0.28 mmol/L (physiologically below normal, nonsensical as a hyperlactatemia cutoff). Value is consistent only if read as 2.5 mmol/L (approx SSC's >2 mmol/L). Unit label is wrong. |
| ranges | n/a |
| rounding | n/a |
| cutoffs | SOFA>6 (criterio_12) is an institutional severity marker, not the Sepsis-3 diagnostic cutoff (Sepsis-3 defines sepsis as acute SOFA rise >=2); device >10d / femoral >7d institutional. Resuscitation cutoffs otherwise align with SSC. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| weight_kg=70; fluid_order=30 ml/kg Ringer Lactato | 2100 mL crystalloid within 3h (SSC 2021 >=30 mL/kg, balanced fluid) | 30 ml/kg Ringer Lactato = 2100 mL | yes |
| workup=hemocultura x2 + broad-spectrum antibiotic | >=2 blood culture sets before empiric broad-spectrum antibiotics (SSC 2021) | hemocultura x2 perifericas + antibiotico amplo espectro | yes |
| lactate_actual_mmol_L=2.5; label=lactato > 2,5 mg/dl | hyperlactatemia trigger at >2 mmol/L (SSC/Sepsis-3) | label uses mg/dl unit (should be mmol/L); numerically ~correct only if reinterpreted as mmol/L | no |

**Verifier notes**

Care-pathway text (trilha_sepse.py facade, payload_sepse_automatica). Core resuscitation content matches SSC 2021 exactly: 30 mL/kg Ringer Lactato bolus, blood cultures x2, broad-spectrum antibiotics, gram-negative double coverage with noradrenaline, catheter change/removal >7d, USG fluid-responsiveness then dobutamine. Sole defect is the lactate hypoperfusion trigger labeled 'mg/dl' instead of 'mmol/L' — exactly the unit-mismatch class this audit targets. Impact rated low because it is a narrative trigger listed alongside redundant hypoperfusion signs (oliguria, TEC aumentado, alt. consciencia, livedo) and does not gate an automated dose; but the mislabel could confuse a clinician reading the value. SOFA>6 is an institutional severity flag, not misaligned with any specific SSC dosing.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_sepse.py` | 1-108 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-01-002`

**Related rules:**

- [RULE-SEPSE-058](../alert-threshold/RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)
- [RULE-SEPSE-060](RULE-SEPSE-060-sepse-pathway-variant-a-11-criterion-catalog-meropenem-1500m.md)

## Notes

= sepse_automatica (facade/sepse.py). SOFA>6 (criterio_12) is the only explicit score threshold. Lactate threshold here is 2.5 mg/dl (note unit mg/dl, unusual for lactate; v3 uses 3 mmol/L). Fluid bolus 30 ml/kg vs variant A 1500ml fixed. Cross-ref -001, -003.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
