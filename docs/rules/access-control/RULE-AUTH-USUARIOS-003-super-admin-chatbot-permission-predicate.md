# RULE-AUTH-USUARIOS-003 — Super-admin (chatbot) permission predicate

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
Grants access only to users flagged as chatbot superusers.

## Inputs

| name | type | range |
|---|---|---|
| request.user.is_chatbot_superuser | boolean | true\|false |

## Outputs

| name | type |
|---|---|
| has_permission | boolean |

## Logic

```text
class IsSuperAdminPermission:
    def has_permission(request, view): return request.user.is_chatbot_superuser
```

## Edge cases (as implemented)

Anonymous/user without attribute would raise AttributeError (no guard).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/permissions.py` | 4-6 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ACCESS-BE-12-015`

**Related rules:**

- [RULE-AUTH-USUARIOS-006](RULE-AUTH-USUARIOS-006-authenticated-user-predicate-isauthenticated.md)

## Notes

Uses a bespoke is_chatbot_superuser flag (not Django is_superuser).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
