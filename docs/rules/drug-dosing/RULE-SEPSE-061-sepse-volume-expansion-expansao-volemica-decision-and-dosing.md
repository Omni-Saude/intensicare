# RULE-SEPSE-061 — SEPSE volume expansion (expansao volemica) decision and dosing

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | drug-dosing |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Clinical decision-support text presented for the hour-1 "realizacao_expansao_volemica" item. Trigger fluid resuscitation on persistent hypotension OR any hypoperfusion sign; dose by body weight with a reduced dose for cardiac dysfunction / oligo-anuric renal injury; start vasopressor early and secure central access within 6h.

## Inputs

- hipotensao_persistente (boolean)
- lactato_arterial (number, mg/dl)
- tempo_enchimento_capilar (number, segundos)
- diurese (number, ml/kg/h)
- disfuncao_cardiaca_ou_lesao_renal_oligoanurica (boolean)

## Outputs

- dose_ringer_lactato (number, ml/kg)

## Logic

```text
IF hipotensao_persistente
   OR lactato_arterial > 30 mg/dl
   OR tempo_enchimento_capilar > 3 s
   OR livedo_reticular presente
   OR indice_de_escamoteamento(frialdade) positivo
   OR (oliguria: diurese < 0.5 ml/kg/h nas ultimas 6h)
   OR alteracao_do_nivel_basal_de_consciencia:
       dose = 30 ml/kg de Ringer Lactato (preferencial), em bolus de 500 ml em 5 min (ideal)
       IF disfuncao_cardiaca_conhecida OR lesao_renal_oligo_anurica:
           dose = 20 ml/kg
Se necessario: iniciar norepinefrina em acesso venoso periferico calibroso;
garantir acesso venoso central em ate 6 h.
```

## Edge cases (as implemented)

Verbatim guidance text (no executable branching). Thresholds: lactate 30 mg/dl (~3.3 mmol/L), TEC 3 s, diuresis 0.5 ml/kg/h over 6h. Reduced-dose branch for cardiac dysfunction/oligo-anuric AKI.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Evans L, et al. Surviving Sepsis Campaign: International Guidelines for Management of Sepsis and Septic Shock 2021. Crit Care Med 2021;49(11):e1063-e1143 (>=30 mL/kg IV crystalloid, balanced/Ringer's preferred, within first 3h; hypoperfusion markers incl. lactate >2 mmol/L, prolonged capillary refill, mottling, oliguria, altered mentation; early norepinephrine; secure central access). ([source](https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-guidelines-2021))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | 30 mL/kg dose matches SSC-2021; 20 mL/kg reduced-dose caveat for cardiac dysfunction / oligo-anuric AKI is a reasonable institutional refinement (not an explicit SSC figure). |
| units | diff - lactate written in mg/dl; SSC uses mmol/L. 30 mg/dl = 3.33 mmol/L (mg/dl = mmol/L x 9.008), not the SSC hypoperfusion marker of 2 mmol/L = 18 mg/dl. |
| ranges | TEC >3 s, diuresis <0.5 mL/kg/h over 6h, livedo/mottling, altered consciousness all match standard hypoperfusion markers. |
| rounding | n/a |
| cutoffs | diff - lactate trigger 30 mg/dl vs 18 mg/dl equivalent of the 2 mmol/L reference marker. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| lactato_arterial = 20 mg/dl (2.2 mmol/L), no other signs | hypoperfusion marker POSITIVE (>2 mmol/L) -> consider fluid resuscitation | 20 > 30 FALSE -> lactate criterion does NOT fire | no |
| lactato_arterial = 36 mg/dl (4 mmol/L) | positive (well above 2 mmol/L) | 36 > 30 TRUE -> fires; 30 mL/kg Ringer Lactato | yes |
| hipotensao_persistente = true, cardiac dysfunction known | resuscitate; volume judgement in cardiac dysfunction | fires; dose reduced to 20 mL/kg | yes |
| diurese = 0.4 mL/kg/h x6h, lactate normal | oliguria = hypoperfusion -> resuscitate | oliguria <0.5 fires -> 30 mL/kg | yes |

**Verifier notes**

Core dose (30 mL/kg Ringer Lactate; 20 mL/kg reduced for cardiac/renal), early norepinephrine and 6h central-access target all match SSC-2021. Sole discrepancy: lactate hypoperfusion trigger written as 30 mg/dl (~3.3 mmol/L), higher than the SSC marker of 2 mmol/L (18 mg/dl). Impact low - lactate is one of many OR-linked perfusion triggers (hypotension, TEC>3s, mottling, oliguria, altered consciousness), so resuscitation still fires on other signs; the higher lactate bar only under-triggers on the isolated-lactate path. Verbatim clinician-facing guidance text, not executable code; may be an intentional institutional threshold. Legacy already recorded verbatim, not corrected.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/serializers/item_trilha_interativa_sepse.py` | 179-191 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-02-013`

**Related rules:**

- [RULE-SEPSE-060](../care-pathway/RULE-SEPSE-060-sepse-pathway-variant-a-11-criterion-catalog-meropenem-1500m.md)
- [RULE-SEPSE-063](../care-pathway/RULE-SEPSE-063-sepse-hemodynamic-status-decision-intubation-rass-2-fluid-ch.md)
- [RULE-SEPSE-081](../care-pathway/RULE-SEPSE-081-sepsis-1h-bundle-volume-expansion-auto-check-4h-window.md)

## Notes

Static descricao_item text surfaced to clinicians. Lactate threshold expressed in mg/dl (30) rather than the Surviving-Sepsis mmol/L convention (2 or 4 mmol/L = 18 or 36 mg/dl); recorded verbatim, not corrected.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
