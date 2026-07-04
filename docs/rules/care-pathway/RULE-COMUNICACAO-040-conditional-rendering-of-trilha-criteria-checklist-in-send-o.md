# RULE-COMUNICACAO-040 — Conditional rendering of trilha-criteria checklist in send-observation modal

| Field | Value |
|---|---|
| Cluster | comunicacao |
| Category | care-pathway |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
When sending an observation message from a bed's trilha (care pathway), the "Pontos de atenção" (points of attention) checkbox checklist section is rendered only if the trilha has at least one criterio; otherwise only the free-text observation field is shown.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| trilha.criterios | Models.Criterio[], optional |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| rendered checklist section | boolean (present/absent) |  |

## Logic

```text
show_criterios_section = trilha.criterios != null AND trilha.criterios.length > 0
// each checkbox option carries { nome, alerta, recomendacoes } from the criterio, displayed by its "alerta" label
```

## Edge cases (as implemented)

If trilha.criterios is an empty array or undefined, the section is omitted entirely (not shown disabled/empty).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/useModalSender.tsx` | 112-139 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-mensagem-FE-07-003`

**Related rules:**

- [RULE-COMUNICACAO-012](../data-validation/RULE-COMUNICACAO-012-patient-snapshot-in-observation-branches-by-leito-type.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
