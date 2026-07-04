# RULE-AUTH-USUARIOS-040 — User deletion is a soft-delete (is_active flag)

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Deleting a user does not remove the record; it sets is_active=False and returns 204.

## Inputs

_None._

## Outputs

| name | type |
|---|---|
| usuario.is_active | boolean |

## Logic

```text
def perform_destroy(instance):
    instance.is_active = False
    instance.save()
def destroy(request, *a, **kw):
    instance = get_object()
    perform_destroy(instance)
    return Response(status=204)
```

## Edge cases (as implemented)

The user record and its FK relations are preserved; combined with RULE-usuario-BE-05-006, a soft-deleted user simply disappears from subsequent listing/filtering.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/usuario.py` | 50-57 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-BE-05-007`

**Related rules:**

- [RULE-AUTH-USUARIOS-014](../data-validation/RULE-AUTH-USUARIOS-014-user-queryset-restricted-to-active-users-scoped-to-empresa.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
