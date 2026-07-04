# RULE-OPERACIONAL-INFRA-016 — Evolution (Formulario) full-day date-range filter

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Filters clinical evolution forms by professional and an inclusive full-day date range on dt_registro.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| data_inicio | date | - | - |
| data_fim | date | - | - |
| profissional_id | string | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| filtered queryset | queryset | - |

## Logic

```text
filter_data_inicio: dt_registro >= combine(value, time.min)          # 00:00:00.000000
filter_data_fim:    dt_registro <= combine(value, time.max)          # 23:59:59.999999
profissional_id -> preenchido_por_id exact.
```

## Edge cases (as implemented)

Boundaries are naive datetimes (no tzinfo); inclusive on both ends.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/filters/evolucoes_empresa.py` | 6-29 | `8166c07e` | primary |

- Merged from: RULE-filter-BE-04-048
- Related rules: RULE-OPERACIONAL-INFRA-052

## Notes

Model Formulario in trilha_homecare.models (out of partition).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
