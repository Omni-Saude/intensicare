# RULE-AUTH-USUARIOS-006 — Authenticated-user predicate (IsAuthenticated)

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
Grants access to any user that exists and is not anonymous.

## Inputs

| name | type | range |
|---|---|---|
| request.user | object | must be truthy and not anonymous |

## Outputs

| name | type |
|---|---|
| has_permission | boolean |

## Logic

```text
def has_permission(request, view):
    return bool(request.user and not request.user.is_anonymous)
```

## Edge cases (as implemented)

Null user or AnonymousUser -> denied.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/permissions/authenticated.py` | 4-11 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ACCESS-BE-12-019`

**Related rules:**

- [RULE-AUTH-USUARIOS-007](RULE-AUTH-USUARIOS-007-empresa-read-vs-read-write-permissions-are-identical.md)

## Notes

Re-implements DRF IsAuthenticated. Same body reused by both empresa permissions (RULE-018).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
