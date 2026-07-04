# RULE-FORMULARIOS-CLINICOS-002 — Pressure-injury (LPP) staging + wound-bed composite assessment (nursing / dietitian FE form)

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | clinical-scoring |
| Type | scoring |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Frontend structured pressure-injury assessment list (dataFormEnfermagem, duplicated verbatim in dataFormNutricionista) capturing origin, anatomical location, tissue types, secretion, exudate amount, peri-wound skin color, peri-wound edema (4 cm distance thresholds) and NPUAP-style stage.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| tipo_lpp | enum |  | nova_lesao\|lesao_previa |
| estagio_lpp | enum |  | suspeita_de_lesao\|estagio_i\|estagio_ii\|estagio_iii\|estagio_iv\|nao_graduavel |
| edema_tecido | enum |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| wound record | object |  |

## Logic

```text
formList per LPP:
  tipo_lpp {nova_lesao, lesao_previa (prévia à admissão)}
  local_lpp: select from localLesoes (anatomical sites vocabulary, RULE-FORMULARIOS-CLINICOS-020)
  tipo_tecido multicheck {fibrina_esfacelos, granulacao, necrose, epitelizado}
  tipo_secrecao multicheck {ausente, fetida, purulenta, serosa, sanguinolenta}
  exsudato {nada, escasso, moderado, grande}          # FE nursing: 4 options
  cor_pele {rosa_ou_normal, vermelho_brilhante_palida, branca_cinza_hipopigmentada,
            vermelho_escuro_sem_empalidecimento, preta_hiperpigmentada}
  edema_tecido {minimo_edema, edema_sem_sulco_menor_4cm (<4cm), edema_sem_sulco_maior_4cm (>=4cm),
                edema_com_sulco_menor_4cm (<4cm), crepitacao_edema_com_sulco_maior_4cm (>=4cm)}  # 4cm boundary
  estagio_lpp {suspeita_de_lesao (deep tissue), estagio_i..iv, nao_graduavel}
  curativo(string)
```

## Edge cases (as implemented)

Peri-wound edema classified by a 4 cm radius boundary using >= vs < (crepitation escalates to top tier). Stage set matches NPUAP I-IV + suspected deep tissue + unstageable.

## Divergence

Peri-wound edema top-tier VALUE diverges from the backend canonical enum: this FE nursing/dietitian form stores "crepitacao_edema_com_sulco_maior_4cm" (dataFormEnfermagem.ts:220; dataFormNutricionista.ts:307), whereas the backend model (avaliacao_global.py:110) and the TecEnfermagem FE form (RULE-FORMULARIOS-CLINICOS-003) both store "crepitacao_maior_4cm" for the same clinical label. Same finding, two different stored codes -> cross-discipline data inconsistency; the backend agrees with TecEnfermagem, NOT with nursing/dietitian. Additionally, EXUDATE (exsudato) diverges: backend avaliacao_global.py:117-125 offers 5 options {nada, escasso, pequeno, moderado, grande}, but this FE form offers only 4 {nada, escasso, moderado, grande} - the "pequeno" option is dropped in the frontend.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Bates-Jensen Wound Assessment Tool (BWAT), item 'Peripheral Tissue Edema' (5-level, 4 cm boundary) and item 'Exudate Amount' (5-level: none/scant/small/moderate/large); plus NPUAP staging as in RULE-001. Bates-Jensen BM, formerly Pressure Sore Status Tool. ([source](https://aci.health.nsw.gov.au/__data/assets/pdf_file/0010/388243/22.-Bates-Jensen-wound-assessment-tool-BWAT.pdf))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| estagio_lpp=estagio_iii | NPUAP Stage III (full-thickness, fat visible) | estagio_iii accepted -> "III" | yes |
| exsudato=small/pequeno amount | BWAT Exudate Amount score 3 = 'small' is a valid recordable level | FE exsudato options = {nada, escasso, moderado, grande} -> NO 'pequeno' option; small exudate cannot be recorded (must round to escasso or moderado) | no |
| edema=crepitus + pitting extending 5 cm | BWAT Peripheral Edema score 5 = crepitus and/or pitting >4 cm | stored as "crepitacao_edema_com_sulco_maior_4cm" (clinically correct tier, but code string differs from backend canonical "crepitacao_maior_4cm") | yes |

**Verifier notes**

Clinical content matches the published references: NPUAP staging is faithful and the peri-wound edema 4 cm boundary reproduces the BWAT Peripheral Tissue Edema item. The extraction-flagged DISCREPANCY is IMPLEMENTATION-LEVEL, not a deviation from the clinical reference: (1) the edema top-tier stored CODE ("crepitacao_edema_com_sulco_maior_4cm") differs from the backend/TecEnfermagem canonical code ("crepitacao_maior_4cm") for the identical clinical label -> cross-discipline data-aggregation inconsistency; (2) the exsudato/exudate option list is reduced 5->4 (the "pequeno"/small level is dropped), which DOES deviate from the 5-level BWAT Exudate Amount scale and forces small exudate to be mis-binned. Impact low: affects data granularity/reporting consistency, no patient-facing calculation or auto-decision. Verdict DISCREPANCY preserved per extraction.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormEnfermagem.ts` | 107-247 | `f9656be266` | primary |
| trilhas-frontend | `src/utils/dataForms/dataFormNutricionista.ts` | 192-335 | `f9656be266` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-wound-FE-01-039`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-001](RULE-FORMULARIOS-CLINICOS-001-pressure-injury-lpp-npuap-staging-enum.md)
- [RULE-FORMULARIOS-CLINICOS-003](RULE-FORMULARIOS-CLINICOS-003-nursing-technician-tecenfermagem-tegumentary-lpp-list-varian.md)
- [RULE-FORMULARIOS-CLINICOS-004](../alert-threshold/RULE-FORMULARIOS-CLINICOS-004-peri-wound-edema-classification-4-cm-threshold-enum-backend.md)
- [RULE-FORMULARIOS-CLINICOS-018](../data-validation/RULE-FORMULARIOS-CLINICOS-018-pressure-injury-lpp-origin-classification-enum-tipo-lpp-back.md)
- [RULE-FORMULARIOS-CLINICOS-019](../data-validation/RULE-FORMULARIOS-CLINICOS-019-other-lesion-non-pressure-assessment-list.md)
- [RULE-FORMULARIOS-CLINICOS-020](../data-validation/RULE-FORMULARIOS-CLINICOS-020-anatomical-lesion-catheter-insertion-site-enumeration.md)

## Notes

LPP list is duplicated (disabledOnEdit) in dataFormNutricionista.ts:192-335 with identical values, and present commented-out in dataFormFarmaceutico.ts:72-212. Staging (estagio_lpp) and origin (tipo_lpp) values MATCH the backend; only edema top value and exsudato option-count diverge (see divergence). Status upgraded OK->DISCREPANCY during BE/FE reconciliation.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
