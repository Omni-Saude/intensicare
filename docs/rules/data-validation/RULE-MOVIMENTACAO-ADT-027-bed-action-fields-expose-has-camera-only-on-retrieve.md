# RULE-MOVIMENTACAO-ADT-027 — Bed action_fields expose has_camera only on retrieve

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
LeitoSerializer's base field set (used for list/create/update) does not include has_camera; the 'retrieve' action adds it.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| view.action | string |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| fields exposed | array of string |  |

## Logic
```text
Meta.fields = ("id","setor","setor_id","nome","ip_camera","codigo","ocupado")
action_fields = {"retrieve": {"fields": ("id","nome","codigo","setor","ip_camera","has_camera","ocupado")}}
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/leito.py | 37-53 | 8166c07e | primary |
- Merged from: RULE-leito-BE-05-001
- Related rules: RULE-MOVIMENTACAO-ADT-010, RULE-MOVIMENTACAO-ADT-028

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
