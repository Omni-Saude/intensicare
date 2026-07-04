# RULE-AUTH-USUARIOS-047 — Access-level enumeration (read vs read-write) — dormant

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | billing-administrative |
| Type | validation |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Legacy permission access levels ('r'=read, 'rw'=read/write) and coarse roles (admin/medico/enfermeiro); the owning Permissao model is commented out.

## Inputs

| name | type | range |
|---|---|---|
| nivel_acesso | string | r\|rw |
| acesso | string | admin\|medico\|enfermeiro |

## Outputs

| name | type |
|---|---|
| access_level | string |

## Logic

```text
PermissaoChoices.acesso() -> (admin, medico, enfermeiro).
PermissaoChoices.nivel_acesso() -> (r=Leitura, rw="Leitura e escrita").
PermissionsChoices.permissions() aggregates every model._meta.permissions across all apps.
```

## Edge cases (as implemented)

Permissao model in core/models/permissao.py is fully commented out; these choices may be unused.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/choices/permissao.py` | 6-31 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-04-008`

**Related rules:**

- [RULE-AUTH-USUARIOS-007](../access-control/RULE-AUTH-USUARIOS-007-empresa-read-vs-read-write-permissions-are-identical.md)

## Notes

AMBIGUOUS — enum defined but its model is disabled; real RBAC is enforced via Django group permissions (see RULE-acesso-BE-04-045).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
