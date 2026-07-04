# RULE-FORMULARIOS-CLINICOS-029 — Nursing abdominal assessment enums

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
Abdominal exam enums for shape, bowel sounds, pain, palpable masses, peristalsis.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| avaliacao_abdominal.* | enum/boolean |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| abdominal assessment | object |  |

## Logic

```text
geral multicheck {plano, globoso, escavado, cirurgia_recente}
ruidos_hidroaereos multicheck {presentes, diminuidos, ausentes}
presenca_dor multicheck {doloroso, indolor, ascitico}
massas_palpaveis(boolean); peristalse(boolean)
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormEnfermagem.ts` | 307-359 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-nursing-FE-01-041`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-030](RULE-FORMULARIOS-CLINICOS-030-nursing-genitourinary-assessment-enums.md)

## Notes

Nutricionista variant adds colostomia to geral and diurese/evacuacoes fields (other partition capture).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
