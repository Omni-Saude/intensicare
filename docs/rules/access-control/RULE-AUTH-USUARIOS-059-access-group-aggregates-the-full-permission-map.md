# RULE-AUTH-USUARIOS-059 — Access group aggregates the full permission map

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | validation |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
An access group (Grupo) is modeled as a named bundle of the entire Permissions boolean map plus a list of member users, implying permission grants are managed at the group level and presumably inherited by its member users (inheritance mechanism itself not present in this partition).

## Inputs

| name | type |
|---|---|
| permissoes | Models.Permissions |

## Outputs

| name | type |
|---|---|
| Grupo | object |

## Logic

```text
Grupo = { id: string, nome: string, permissoes: Models.Permissions (all 28 keys), usuarios: any[] }
```

## Edge cases (as implemented)

usuarios is typed as `any[]`, so no shape constraint is enforced on group membership at the type level in this partition.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Grupo.d.ts` | 4-9 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-permissoes-FE-07-005`

**Related rules:**

- [RULE-AUTH-USUARIOS-058](RULE-AUTH-USUARIOS-058-rbac-permission-catalog.md)

## Notes

Extends the fixed category taxonomy with 'access-control' (see RULE-permissoes-FE-07-001).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
