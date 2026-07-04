# RULE-FORMULARIOS-CLINICOS-019 — Other-lesion (non-pressure) assessment list

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Structured list for non-pressure lesions with type, location, aspect, dressing, and dressing-change frequency.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| tipo_lesao | enum |  | see logic |
| frequencia_troca | enum |  | dia\|mes\|ano |

## Outputs

| name | type | unit |
|---|---|---|
| lesion record | object |  |

## Logic

```text
formList: tipo_lesao {ferida_cirurgica, escoriacao, equimose, queimadura, ulcera_vascular,
  ulcera_neuropatica, ferida_arma_fogo}; local_lesao(localLesoes); aspecto(string);
  curativo(string); frequencia_troca {dia, mes, ano}
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormEnfermagem.ts` | 248-302 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-wound-FE-01-040`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-002](../clinical-scoring/RULE-FORMULARIOS-CLINICOS-002-pressure-injury-lpp-staging-wound-bed-composite-assessment-n.md)
- [RULE-FORMULARIOS-CLINICOS-003](../clinical-scoring/RULE-FORMULARIOS-CLINICOS-003-nursing-technician-tecenfermagem-tegumentary-lpp-list-varian.md)
- [RULE-FORMULARIOS-CLINICOS-020](RULE-FORMULARIOS-CLINICOS-020-anatomical-lesion-catheter-insertion-site-enumeration.md)

## Notes

Duplicated in dataFormTecEnfermagem.ts:495-549; commented-out in dataFormFarmaceutico.ts:213-267.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
