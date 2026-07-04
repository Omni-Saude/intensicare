# RULE-OPERACIONAL-INFRA-015 — Exclude entities already in a given access group

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Sector and user list filters support a `grupo` parameter that EXCLUDES records already belonging to that access group (i.e. surfaces candidates available to add).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| grupo (id) | string | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| filtered queryset | queryset | - |

## Logic

```text
SetorFilter.filter_grupo:  queryset.exclude(grupos_acessos=value)
UsuarioFilter.filter_grupo: queryset.exclude(grupos_acessos=value)
```

## Edge cases (as implemented)

Excludes by group membership relation; value expected to be the group id.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/filters/setor.py` | 53-54 | `8166c07e` | primary |
| ahlabs-trilhas | `core/filters/usuario.py` | 18-19 | `8166c07e` | duplicate |

- Merged from: RULE-filter-BE-04-046

## Notes

Identical logic in core/filters/usuario.py lines 18-19.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
