# RULE-FORMULARIOS-CLINICOS-026 — Speech-therapy orofacial and language enums

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
Orofacial structure motility/tone and expressive/receptive language state enums.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| avaliacao_fonoaudiologica.* | enum |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| speech assessment | object |  |

## Logic

```text
motilidade {adequada, inadequada}; tonicidade {adequada, inadequada}
expressiva {presente, alterada, ausente}; receptiva {presente, alterada, ausente}
```

## Edge cases (as implemented)

Label "Ausênte" mis-accented; value "ausente" correct.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFonoaudiologo.ts` | 184-232 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-fono-FE-01-064`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-025](RULE-FORMULARIOS-CLINICOS-025-speech-therapy-global-assessment-enums.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
