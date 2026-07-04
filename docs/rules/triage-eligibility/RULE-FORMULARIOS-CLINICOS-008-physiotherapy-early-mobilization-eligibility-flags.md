# RULE-FORMULARIOS-CLINICOS-008 — Physiotherapy early-mobilization eligibility flags

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Physiotherapy global assessment captures edema grade, general state, delirium, and two boolean contraindications to early mobilization.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| instabilidade_hemodinamica_grave | boolean |  |  |
| contraindicacao_de_mobilizacao_precoce | boolean |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| mobilization eligibility flags | boolean set |  |

## Logic

```text
edema {sem_edema, edema1 (MMII1), edema2 (MMII2), edema3 (MMII3), anasarca}
estado_geral {grave, regular}
presenca_delirium(boolean)
instabilidade_hemodinamica_grave(boolean)
contraindicacao_de_mobilizacao_precoce(boolean)
```

## Edge cases (as implemented)

The two booleans gate whether early mobilization/physiotherapy is appropriate; the form does not auto-block conduct on them.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFisioterapeuta.ts` | 24-77 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-physio-FE-01-051`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-016](../care-pathway/RULE-FORMULARIOS-CLINICOS-016-physiotherapy-conduct-enums-respiratory-motor-techniques.md)
- [RULE-FORMULARIOS-CLINICOS-032](../data-validation/RULE-FORMULARIOS-CLINICOS-032-physiotherapy-neuro-cardio-respiratory-assessment-enums.md)
- [RULE-FORMULARIOS-CLINICOS-033](../data-validation/RULE-FORMULARIOS-CLINICOS-033-physiotherapy-motor-function-enums.md)

## Notes

'Dados do Paciente' subgroup delegates to FieldSetDadosPacienteFisioterapeuta (React component, out of partition). Boolean contraindication flags carry no numeric threshold to verify -> verify=false.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
