# RULE-FORMULARIOS-CLINICOS-023 — Physician in-use invasive devices vocabulary

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
Multicheck of invasive devices currently in use.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| dispositivos_em_uso.tipos_dispositivo | enum[] (multicheck) |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| devices | enum set |  |

## Logic

```text
options { gastrostomia, traquestomia, jejunostopia, svd, avp, picc, avc, sne }
```

## Edge cases (as implemented)

Typos in labels (Traquestomia, Jejunostopia) preserved verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFormularioMedico.ts` | 95-115 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-medico-FE-01-032`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-024](RULE-FORMULARIOS-CLINICOS-024-physician-in-use-equipment-vocabulary.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
