# RULE-AUTH-USUARIOS-050 — GrupoAcesso incoming permissoes payload rewrite

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
On input, if the client sends a non-empty 'permissoes' dict, it is renamed to 'assign_permissions' before internal validation.

## Inputs

| name | type |
|---|---|
| permissoes | object (codename->bool) |

## Outputs

| name | type |
|---|---|
| assign_permissions | object (codename->bool) |

## Logic

```text
def to_internal_value(data):
    if bool(data.get("permissoes", {})):
        data["assign_permissions"] = data.pop("permissoes")
    return super().to_internal_value(data)
```

## Edge cases (as implemented)

An empty dict/falsy 'permissoes' value is left untouched (not renamed), so it will not reach assign_permissions and update() permission logic will not run for it.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/grupo_acesso.py` | 105-108 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-05-002`

**Related rules:**

- [RULE-AUTH-USUARIOS-035](RULE-AUTH-USUARIOS-035-grupoacesso-update-replaces-entire-permission-set.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
