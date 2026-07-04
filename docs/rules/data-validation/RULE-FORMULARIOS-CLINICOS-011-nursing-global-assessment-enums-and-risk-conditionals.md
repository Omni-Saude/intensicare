# RULE-FORMULARIOS-CLINICOS-011 — Nursing global assessment enums and risk conditionals

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Nurse global assessment with edema severity scale, general-state enum, boolean signs, isolation-precaution set, and assistance-risk multicheck that conditionally opens allergy note and wound lists.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| avaliacao_global.edema | enum |  | sem_edema\|edema1\|edema2\|edema3\|anasarca |
| avaliacao_global.riscos_assistenciais | enum[] (multicheck) |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| global assessment | object |  |

## Logic

```text
edema {sem_edema, edema1 (MMII1), edema2 (MMII2), edema3 (MMII3), anasarca}  // ordinal edema grading
estado_geral {grave, regular}
booleans: hipocorado, ictericia, febre, cianose
precaucoes_isolamento multicheck {padrao, contato, goticulas, aerossois, vigilancia}
riscos_assistenciais multicheck {queda, alergia, sangramento, trombose_venosa, delirium, broncoaspiracao,
  flebite, alteracao_glicemica, lpp, outras_lesoes}
conditions: alergia -> observacao_alergia(string);
            lpp -> LPP list (RULE-FORMULARIOS-CLINICOS-002);
            outras_lesoes -> lesion list (RULE-FORMULARIOS-CLINICOS-019)
```

## Edge cases (as implemented)

Edema scale MMII1..3 is an ordinal lower-limb edema grade.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormEnfermagem.ts` | 25-306 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-nursing-FE-01-038`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-002](../clinical-scoring/RULE-FORMULARIOS-CLINICOS-002-pressure-injury-lpp-staging-wound-bed-composite-assessment-n.md)
- [RULE-FORMULARIOS-CLINICOS-008](../triage-eligibility/RULE-FORMULARIOS-CLINICOS-008-physiotherapy-early-mobilization-eligibility-flags.md)
- [RULE-FORMULARIOS-CLINICOS-019](RULE-FORMULARIOS-CLINICOS-019-other-lesion-non-pressure-assessment-list.md)

## Notes

riscos_assistenciais enum duplicated in Fisioterapeuta (dataFormFisioterapeuta.ts:48-63) and Farmaceutico (dataFormFarmaceutico.ts:48-63, conditions commented out).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
