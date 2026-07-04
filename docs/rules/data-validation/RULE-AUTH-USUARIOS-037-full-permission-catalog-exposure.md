# RULE-AUTH-USUARIOS-037 — Full permission catalog exposure

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
TodasPermissoesViewSet.list returns the entire system permission catalog (codename->label) unconditionally to any authenticated user, with no scoping.

## Inputs

_None._

## Outputs

| name | type |
|---|---|
| permissions_catalog | object (codename->label) |

## Logic

```text
return Response(dict(PermissionsChoices.permissions()))
```

## Edge cases (as implemented)

No filtering by user's own permissions/role - any authenticated caller sees the full catalog of all possible permission codenames in the system.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/permissao.py` | 14-22 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-05-008`

**Related rules:**

- [RULE-AUTH-USUARIOS-001](RULE-AUTH-USUARIOS-001-grupoacesso-permission-catalog-payload-computation.md)
- [RULE-AUTH-USUARIOS-058](../access-control/RULE-AUTH-USUARIOS-058-rbac-permission-catalog.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
