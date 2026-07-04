# RULE-FORMULARIOS-CLINICOS-014 — Nursing-technician high-cost drug/antibiotic list and other info

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | drug-dosing |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
TecEnfermagem records high-cost drugs/antibiotics with administration route and body site (route 'outras' reveals free text), plus equipment-in-use (with 'outros' reveal), bathing type and 24 h incidents.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| medicamentos[].via_administracao | enum[] (multicheck) |  | ev\|im\|sc\|sl\|it\|outras |
| medicamentos[].local | enum[] (multicheck) |  | mid\|mie\|msd\|mse\|vjd\|vje |

## Outputs

| name | type | unit |
|---|---|---|
| medication + other-info record | object |  |

## Logic

```text
medicamentos formList: nome(string); via_administracao multicheck {ev, im, sc, sl, it, outras};
  outras -> outras_vias(string); local multicheck {mid, mie, msd, mse, vjd, vje}
equipamentos_em_uso multicheck {aspirador, concentrador, nebulizador, cilindro_de_o2, oximetro, outros};
  outros -> outros_equipamentos(string)
banho multicheck {leito, aspersao}
intercorrencias_24h(string)
```

## Edge cases (as implemented)

_None documented._

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published clinical reference exists. This rule captures an internal data-capture vocabulary (drug name + administration-route multicheck + body-site multicheck + equipment/bath/incident fields) for the TecEnfermagem form. The route codes (EV=endovenosa/IV, IM=intramuscular, SC=subcutanea, SL=sublingual, IT=intratecal, outras=other) and body-site codes (MID/MIE/MSD/MSE = membro inferior/superior direito/esquerdo; VJD/VJE = veia jugular direita/esquerda) are standard Brazilian-Portuguese clinical abbreviations, but the list is a proprietary form vocabulary, not a scored scale, formula, or dose calculator. There is no equation, coefficient, unit conversion, valid-range bound, rounding step, or score-band cutoff to audit against a guideline.

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| via_administracao=["outras"] | reveal free-text 'outras_vias' field (per rule logic: outras -> outras_vias) | conditions.outras fires -> outras_vias string field shown (lines 586-594) | yes |
| via_administracao=["ev"]; local=["vjd"] | route EV + site right-jugular recorded; no conditional reveal | ev/vjd stored as multicheck values; no condition triggered (lines 579,605) | yes |
| equipamentos_em_uso=["outros"] | reveal free-text 'outros_equipamentos' field (per rule logic: outros -> outros_equipamentos) | conditions.outros fires -> outros_equipamentos string field shown (lines 628-636) | yes |
| via_administracao=["ev", "im", "sc", "sl", "it", "outras"] | all 6 route options selectable together (multicheck); 'outras' still reveals free text | 6 options present exactly {ev,im,sc,sl,it,outras}; outras reveal fires (lines 578-594) | yes |

**Verifier notes**

Internal-review flag (not a defect). Legacy vocabulary and conditional-reveal logic reproduce the rule's logic field verbatim (dataFormTecEnfermagem.ts:555-655): route multicheck {ev,im,sc,sl,it,outras} with outras->outras_vias reveal; site multicheck {mid,mie,msd,mse,vjd,vje}; equipment multicheck with outros->outros_equipamentos reveal; banho {leito,aspersao}; intercorrencias_24h free text. Route and site abbreviations are clinically standard and mapped correctly (label<->value consistent, no unit or code errors observed). The rule carries verify=true only because its Phase-1 taxonomy category is 'drug-dosing', but it captures NO dose amount, concentration, rate, or weight - so none of the unit-mismatch failure modes this audit targets (mg/dl vs mmol/L, FiO2 fraction vs percent, mcg/kg/min vs mcg/kg/h) can occur here. Nothing to correct; no authoritative source to verify against.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormTecEnfermagem.ts` | 555-655 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-tecnursing-FE-01-077`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-023](../data-validation/RULE-FORMULARIOS-CLINICOS-023-physician-in-use-invasive-devices-vocabulary.md)
- [RULE-FORMULARIOS-CLINICOS-024](../data-validation/RULE-FORMULARIOS-CLINICOS-024-physician-in-use-equipment-vocabulary.md)

## Notes

Administration-route/site codes (EV/IM/SC/SL/IT; MID/MIE/MSD/MSE/VJD/VJE) are clinical abbreviations. verify=true because Phase-1 category is drug-dosing (per taxonomy rule), though the rule itself only captures route/site vocabulary, not dose calculations.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
