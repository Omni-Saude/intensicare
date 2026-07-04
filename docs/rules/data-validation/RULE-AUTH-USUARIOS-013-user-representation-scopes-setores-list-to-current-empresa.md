# RULE-AUTH-USUARIOS-013 — User representation scopes setores list to current empresa

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
UsuarioSerializer.to_representation adds a 'setores' array to the payload containing only sectors whose estabelecimento belongs to the request's current empresa, hiding sector memberships from other companies (multi-tenant scoping), but only when a request is present in context.

## Inputs

| name | type |
|---|---|
| request.empresa | object |

## Outputs

| name | type |
|---|---|
| payload.setores | array of object |

## Logic

```text
payload = super().to_representation(instance)
if context and context.get("request"):
    payload["setores"] = SetorUsuarioSerializer(
        instance.setores.filter(estabelecimento__empresa=request.empresa), many=True
    ).data
return payload
```

## Edge cases (as implemented)

If no request in context, 'setores' key is absent entirely.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/usuario.py` | 193-203 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-BE-05-004`

**Related rules:**

- [RULE-AUTH-USUARIOS-039](../care-pathway/RULE-AUTH-USUARIOS-039-user-update-performs-diff-based-setor-sync-scoped-to-current.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
