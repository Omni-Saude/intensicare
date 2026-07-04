# RULE-AUTH-USUARIOS-005 — Owner-organization object permission predicate

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | eligibility |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Object-level access granted only when the requesting user's id equals the object's owner id (or the object's own id if it has no owner attribute).

## Inputs

| name | type | range |
|---|---|---|
| request.user.id | id | - |
| obj.owner\|obj | object | - |

## Outputs

| name | type |
|---|---|
| has_object_permission | boolean |

## Logic

```text
def has_object_permission(request, view, obj):
    if hasattr(obj, 'owner'): obj = obj.owner
    return request.user.id == obj.id
```

## Edge cases (as implemented)

If obj lacks 'owner', compares user.id to obj.id directly (self-ownership).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/permissions.py` | 14-19 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ACCESS-BE-12-017`

**Related rules:** _none_

## Notes

-

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
