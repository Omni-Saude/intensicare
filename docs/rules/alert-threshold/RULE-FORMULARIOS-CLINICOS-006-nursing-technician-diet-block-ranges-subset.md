# RULE-FORMULARIOS-CLINICOS-006 — Nursing-technician diet block ranges (subset)

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
TecEnfermagem diet block with route booleans, acceptance enum and vomit / gastric-residue numeric ranges (no HGT/prophylaxis, unlike nurse/dietitian forms).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| vomitos / residuo_gastrico | number | ml | 0-10000 |

## Outputs

| name | type | unit |
|---|---|---|
| diet assessment | object |  |

## Logic

```text
booleans: dieta_zero, dieta_via_oral, enteral_sne_gtt, nutricao_parenteral
aceitacao {total, parcial, recusado}
vomitos 0-10000; residuo_gastrico 0-10000
```

## Edge cases (as implemented)

Omits hgt_max/hgt_min and indicacao_profilaxia present in nurse/dietitian diet blocks (other partitions).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormTecEnfermagem.ts` | 289-339 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-tecnursing-FE-01-075`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-012](../data-validation/RULE-FORMULARIOS-CLINICOS-012-nursing-technician-respiratory-assessment-with-aspiration-co.md)

## Notes

Numeric bounds are input-validation ranges (0-10000 ml), not clinical decision thresholds -> verify=false.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
