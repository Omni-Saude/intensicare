# RULE-CADASTROS-UI-014 — Patient sex/gender code labels

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Maps patient sex codes to display labels.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| sexo | string |  | M \| F \| O \| N |

## Outputs

| name | type | unit |
|---|---|---|
| label | string |  |

## Logic

```text
M -> "Masculino"; F -> "Feminino"; O -> "Outro"; N -> "Não informado"
```

## Edge cases (as implemented)

Typed `as any`; unknown codes return undefined.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/labelSexo.ts` | 1-8 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-validation-FE-02-002`

**Related rules:** _none_

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
