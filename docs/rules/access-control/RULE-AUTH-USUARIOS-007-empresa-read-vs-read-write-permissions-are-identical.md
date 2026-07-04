# RULE-AUTH-USUARIOS-007 — Empresa read vs read-write permissions are identical

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | eligibility |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Both the empresa read-only permission and the empresa read-and-write permission are implemented identically, checking only that the user is authenticated (non-anonymous); neither actually distinguishes read from write.

## Inputs

| name | type | range |
|---|---|---|
| request.user | object | authenticated non-anonymous => allowed |

## Outputs

| name | type |
|---|---|
| has_permission | boolean |

## Logic

```text
class LeituraEmpresaPermission:      # "read"
    def has_permission(request, view): return bool(request.user and not request.user.is_anonymous)
class ReadAndWriteEmpresaPermission:  # "read+write"
    def has_permission(request, view): return bool(request.user and not request.user.is_anonymous)
# identical bodies
```

## Edge cases (as implemented)

Anonymous -> denied; any authenticated user -> allowed for BOTH read and write.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/permissions/empresa.py` | 4-13 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ACCESS-BE-12-018`

**Related rules:**

- [RULE-AUTH-USUARIOS-006](RULE-AUTH-USUARIOS-006-authenticated-user-predicate-isauthenticated.md)
- [RULE-AUTH-USUARIOS-047](../billing-administrative/RULE-AUTH-USUARIOS-047-access-level-enumeration-read-vs-read-write-dormant.md)

## Notes

DISCREPANCY - class names imply differentiated read vs write authorization, but both grant identical access to any authenticated user (no write-specific gating). Same predicate as core/permissions/authenticated.py IsAuthenticated (RULE-...-019? no, see below).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
