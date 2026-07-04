# RULE-AUTH-USUARIOS-012 — GrupoAcesso usuarios field suppressed on list/destroy actions

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
The serialized 'usuarios' array (full nested user objects) is added to the response payload for every view action EXCEPT 'list' and 'destroy', to avoid the cost of serializing all members on list endpoints.

## Inputs

| name | type |
|---|---|
| view.action | string |

## Outputs

| name | type |
|---|---|
| payload.usuarios | array of object |

## Logic

```text
payload = super().to_representation(instance)
if context["view"].action not in ["list", "destroy"]:
    payload["usuarios"] = UsuarioSerializer(instance.usuarios.all(), many=True, context=...).data
return payload
```

## Edge cases (as implemented)

'usuarios' key is entirely absent from the response body (not null/empty) for list and destroy actions.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/grupo_acesso.py` | 110-116 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-05-006`

**Related rules:** _none_

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
