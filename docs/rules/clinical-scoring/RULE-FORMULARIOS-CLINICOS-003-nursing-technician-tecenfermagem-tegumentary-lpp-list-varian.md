# RULE-FORMULARIOS-CLINICOS-003 — Nursing-technician (TecEnfermagem) tegumentary LPP list variant

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
TecEnfermagem pressure-injury list, reached via a lesions multicheck, reuses the LPP staging/wound-bed structure of RULE-FORMULARIOS-CLINICOS-002 but stores a DIVERGENT peri-wound-edema top-tier value.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| lesoes | enum[] (multicheck) |  | lpp\|outras_lesoes |

## Outputs

| name | type | unit |
|---|---|---|
| wound record | object |  |

## Logic

```text
lesoes multicheck {lpp, outras_lesoes}
  lpp -> LPP formList (same structure as RULE-FORMULARIOS-CLINICOS-002)
         BUT edema_tecido top option value = "crepitacao_maior_4cm"
         (dataFormTecEnfermagem.ts:467; matches backend, differs from nursing/dietitian FE)
  outras_lesoes -> other-lesion formList (same structure as RULE-FORMULARIOS-CLINICOS-019)
```

## Edge cases (as implemented)

Same clinical label, different stored value -> data inconsistency across disciplines for the same wound finding.

## Divergence

edema_tecido top value = "crepitacao_maior_4cm" (dataFormTecEnfermagem.ts:467). This MATCHES the backend canonical (avaliacao_global.py:110) but DIFFERS from the nursing/dietitian FE forms (RULE-FORMULARIOS-CLINICOS-002) which use "crepitacao_edema_com_sulco_maior_4cm".

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Bates-Jensen Wound Assessment Tool (BWAT), 'Peripheral Tissue Edema' item (5-level, 4 cm boundary); NPUAP staging as RULE-001. ([source](https://aci.health.nsw.gov.au/__data/assets/pdf_file/0010/388243/22.-Bates-Jensen-wound-assessment-tool-BWAT.pdf))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| edema=crepitus + pitting extending 5 cm | BWAT Peripheral Edema score 5 (crepitus and/or pitting >4 cm) | stored "crepitacao_maior_4cm" (matches backend canonical) | yes |
| estagio_lpp=estagio_iv | NPUAP Stage IV (full-thickness, exposed fascia/muscle/bone) | "IV" | yes |
| edema=non-pitting extending exactly 4 cm | BWAT scores 2 (<4 cm) vs 3 (>4 cm) leave =4 cm undefined | edema_sem_sulco_maior_4cm (>=4 cm) -> legacy closes the BWAT boundary gap at exactly 4 cm | yes |

**Verifier notes**

Against the published references the clinical content is correct: edema categories/4 cm boundary match BWAT and staging matches NPUAP. The extraction DISCREPANCY is an internal cross-implementation code-drift only: this TecEnfermagem form stores the edema top tier as "crepitacao_maior_4cm" (AGREES with backend canonical, avaliacao_global.py:110) but DIFFERS from the nursing/dietitian FE forms (RULE-002, "crepitacao_edema_com_sulco_maior_4cm"). Same clinical finding, inconsistent stored code across discipline forms -> data-consistency defect, no clinical-reference deviation. Impact low. Verdict DISCREPANCY preserved per extraction.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormTecEnfermagem.ts` | 340-553 | `f9656be266` | variant |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-tecnursing-FE-01-076`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-001](RULE-FORMULARIOS-CLINICOS-001-pressure-injury-lpp-npuap-staging-enum.md)
- [RULE-FORMULARIOS-CLINICOS-002](RULE-FORMULARIOS-CLINICOS-002-pressure-injury-lpp-staging-wound-bed-composite-assessment-n.md)
- [RULE-FORMULARIOS-CLINICOS-004](../alert-threshold/RULE-FORMULARIOS-CLINICOS-004-peri-wound-edema-classification-4-cm-threshold-enum-backend.md)
- [RULE-FORMULARIOS-CLINICOS-019](../data-validation/RULE-FORMULARIOS-CLINICOS-019-other-lesion-non-pressure-assessment-list.md)

## Notes

Kept SEPARATE from RULE-FORMULARIOS-CLINICOS-002 as a discipline-specific variant (TecEnfermagem form), not merged. The enum value drift is the load-bearing DISCREPANCY.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
