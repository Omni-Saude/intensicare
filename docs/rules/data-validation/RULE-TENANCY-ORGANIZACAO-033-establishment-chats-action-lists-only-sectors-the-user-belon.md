# RULE-TENANCY-ORGANIZACAO-033 — Establishment chats action lists only sectors the user belongs to

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
The chats custom action returns SetorChatsSerializer data for sectors of the establishment where the requesting user is a member, ordered alphabetically by sector name.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.user | object |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| setores | array of object |  |

## Logic
```text
setores = Setor.objects.filter(pk__in=Setor.objects.filter(estabelecimento=estabelecimento, usuarios=request.user).distinct("pk").values("pk")).order_by("nome")
return SetorChatsSerializer(setores, many=True).data
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/estabelecimento.py | 89-100 | 8166c07e | primary |

- Merged from: RULE-estabelecimento-BE-05-011
- Related rules: RULE-TENANCY-ORGANIZACAO-014

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
