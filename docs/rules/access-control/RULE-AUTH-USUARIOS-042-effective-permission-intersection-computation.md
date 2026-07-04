# RULE-AUTH-USUARIOS-042 — Effective-permission intersection computation

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A user's effective permission map is computed by intersecting the system's known permission catalog (allPermissions, fetched from the backend) with the specific permissions granted to the user (permissions array on the auth context); any permission not present in the system catalog is silently excluded from the effective map even if it were somehow present in the user's own permissions array.

## Inputs

| name | type |
|---|---|
| allPermissions | Record<Permission, string> |
| userPermissions | Permission[] |

## Outputs

| name | type |
|---|---|
| effectivePermissions | Models.Permissions (Record<Permission, boolean>) |

## Logic

```text
for each permission in Object.keys(allPermissions):
  effectivePermissions[permission] = userPermissions.includes(permission)
// permissions in userPermissions but NOT in allPermissions are never surfaced
```

## Edge cases (as implemented)

On unmount / when allPermissions or userPermissions changes, effectivePermissions resets to {} before recomputing (via the effect cleanup), causing a brief moment where all permission checks evaluate to undefined/falsy.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/useEffectivePermissions.tsx` | 5-29 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-permissoes-FE-07-002`

**Related rules:**

- [RULE-AUTH-USUARIOS-058](RULE-AUTH-USUARIOS-058-rbac-permission-catalog.md)

## Notes

Extends the fixed category taxonomy with 'access-control' (see RULE-permissoes-FE-07-001).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
