# RULE-FORMULARIOS-CLINICOS-013 — Nursing-technician genitourinary with diaper-change conditional

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
TecEnfermagem genitourinary exam; selecting 'fralda' (diaper) in the diuresis multicheck reveals a 24 h change-count field.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| diurese | enum[] (multicheck) |  | ausente\|presente\|svd\|sva\|fralda |
| nr_trocas_24h | string |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| genitourinary assessment | object |  |

## Logic

```text
booleans: edema_bolsa_escrotal, lesoes, secrecao_uretral, secrecao_vaginal
diurese multicheck {ausente, presente, svd, sva, fralda}; fralda -> nr_trocas_24h (string, "Nº trocas/24 horas")
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormTecEnfermagem.ts` | 216-288 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-tecnursing-FE-01-074`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-030](RULE-FORMULARIOS-CLINICOS-030-nursing-genitourinary-assessment-enums.md)

## Notes

Nursing genitourinary (RULE-FORMULARIOS-CLINICOS-030) has no fralda conditional.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
