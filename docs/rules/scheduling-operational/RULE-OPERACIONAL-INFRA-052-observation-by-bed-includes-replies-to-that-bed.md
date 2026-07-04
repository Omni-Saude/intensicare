# RULE-OPERACIONAL-INFRA-052 — Observation-by-bed includes replies to that bed

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | scheduling-operational |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Filtering observations by leito returns observations on that bed OR replies whose parent observation is on that bed.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| leito (id) | string |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| filtered queryset | queryset |  |

## Logic

```text
ObservacaoFilter.filter_leito: queryset.filter(Q(leito=value) | Q(resposta__leito=value))
```

## Edge cases (as implemented)

Reply observations may have leito=null but are still included via their parent (resposta__leito).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/filters/observacao.py` | 19-20 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-filter-BE-04-047`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-015](../billing-administrative/RULE-OPERACIONAL-INFRA-015-exclude-entities-already-in-a-given-access-group.md)
- [RULE-OPERACIONAL-INFRA-016](RULE-OPERACIONAL-INFRA-016-evolution-formulario-full-day-date-range-filter.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
