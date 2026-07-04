# RULE-TENANCY-ORGANIZACAO-031 — Establishment action_fields expose camera credentials only on retrieve/partial_update

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
EstabelecimentoSerializer exposes login_camera and senha_camera fields only for the 'retrieve' and 'partial_update' actions; they are absent from 'list' and from the default/create field set.

## Inputs

| Name | Type | Unit |
|---|---|---|
| view.action | string |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| fields exposed | array of string |  |

## Logic

```text
Meta.fields = ("id", "codigo", "nome", "empresa")
action_fields = {
  "list": {"fields": ("id","codigo","nome","empresa")},
  "retrieve": {"fields": ("id","codigo","nome","empresa","login_camera","senha_camera")},
  "partial_update": {"fields": ("id","nome","codigo","empresa","login_camera","senha_camera")},
}
```

## Edge cases (as implemented)
No explicit action_fields entry for 'create' or full 'update' - those fall back to the base Meta.fields (no camera credentials), meaning a client cannot set login_camera/senha_camera via full update/create through this serializer's declared field set, only via partial_update.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/estabelecimento.py` | 32-61 | `8166c07e` | primary |

- Merged from: `RULE-estabelecimento-BE-05-007`

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
