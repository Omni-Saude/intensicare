# RULE-AUTH-USUARIOS-035 — GrupoAcesso update() replaces entire permission set

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
On update, if assign_permissions is a dict, the group's Django permission set is fully REPLACED (not merged) with only the permissions whose value is truthy AND whose codename is in the recognized system catalog.

## Inputs

| name | type |
|---|---|
| assign_permissions | object (codename->bool) |

## Outputs

| name | type |
|---|---|
| grupo.permissions | M2M set of Permission |

## Logic

```text
permissions_of_system = [p[0] for p in PermissionsChoices.permissions()]
if assign_permissions and isinstance(assign_permissions, dict):
    truthy = {k: v for k, v in assign_permissions.items() if v}
    valid_codenames = [k for k in truthy if k in permissions_of_system]
    permission_ids = Permission.objects.filter(codename__in=valid_codenames).values_list("id", flat=True)
    GrupoSerializer(instance.grupo, {"permissions": permission_ids}, partial=True).save()
    # this REPLACES instance.grupo.permissions entirely with permission_ids
```

## Edge cases (as implemented)

Codenames not in the system catalog are dropped even if truthy. Passing assign_permissions=None (unset) leaves existing permissions untouched (branch only runs when truthy dict). Passing an empty dict {} also skips the branch (falsy), leaving permissions unchanged - cannot be used to clear all permissions.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/grupo_acesso.py` | 118-136 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-05-004`

**Related rules:**

- [RULE-AUTH-USUARIOS-050](RULE-AUTH-USUARIOS-050-grupoacesso-incoming-permissoes-payload-rewrite.md)
- [RULE-AUTH-USUARIOS-053](RULE-AUTH-USUARIOS-053-user-payload-field-renames-with-empty-list-edge-case.md)

## Notes

Uses ModelSerializer M2M replace-all semantics via GrupoSerializer (fields=('id','permissions','name')).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
