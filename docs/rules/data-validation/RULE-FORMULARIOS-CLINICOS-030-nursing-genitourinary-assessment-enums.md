# RULE-FORMULARIOS-CLINICOS-030 — Nursing genitourinary assessment enums

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
Genitourinary exam with boolean lesion/secretion flags and a diuresis-route multicheck.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| avaliacao_genital.diurese | enum[] (multicheck) |  | ausente\|presente\|svd\|sva\|fralda |

## Outputs

| name | type | unit |
|---|---|---|
| genitourinary assessment | object |  |

## Logic

```text
booleans: edema_bolsa_escrotal, lesoes, secrecao_uretral, secrecao_vaginal
strings: descricao_lesao, aspecto, descrever, aspecto_urina, observacao
diurese multicheck {ausente, presente, svd, sva, fralda}
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormEnfermagem.ts` | 360-423 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-nursing-FE-01-042`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-013](RULE-FORMULARIOS-CLINICOS-013-nursing-technician-genitourinary-with-diaper-change-conditio.md)
- [RULE-FORMULARIOS-CLINICOS-029](RULE-FORMULARIOS-CLINICOS-029-nursing-abdominal-assessment-enums.md)

## Notes

TecEnfermagem variant (RULE-FORMULARIOS-CLINICOS-013) adds a fralda->nr_trocas_24h conditional.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
