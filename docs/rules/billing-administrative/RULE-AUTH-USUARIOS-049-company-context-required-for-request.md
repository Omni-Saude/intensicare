# RULE-AUTH-USUARIOS-049 — Company-context required for request

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | billing-administrative |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Views using EmpresaRequiredMixin reject requests lacking a resolved company context with 404.

## Inputs

| name | type |
|---|---|
| request.empresa | Empresa\|None |

## Outputs

| name | type |
|---|---|
| allow \| 404 | HTTP response |

## Logic

```text
EmpresaRequiredMixin.dispatch: if not request.empresa -> 404 {"empresa":"Empresa não identificada"}; else super().dispatch()
ManageDataRequiredMixin.dispatch: on PUT/PATCH/POST, re-encode body utf-8 (fallback cp1252) then replace with json.dumps(manage_data(...)).
```

## Edge cases (as implemented)

cp1252 fallback handles legacy-encoded payloads; body is fully rewritten before downstream parsing.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/mixins/view.py` | 7-41 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-04-050`

**Related rules:** _none_

## Notes

request.empresa is injected by upstream middleware (out of partition).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
