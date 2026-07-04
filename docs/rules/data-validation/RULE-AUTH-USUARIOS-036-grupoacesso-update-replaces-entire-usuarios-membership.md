# RULE-AUTH-USUARIOS-036 — GrupoAcesso update() replaces entire usuarios membership

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
On update, if 'usuarios' is a list (even empty), the group's user membership is fully replaced via .set(), meaning an empty list DOES clear membership (unlike the permissions branch).

## Inputs

| name | type |
|---|---|
| usuarios | array of uuid |

## Outputs

| name | type |
|---|---|
| grupo_acesso.usuarios | M2M set of Usuario |

## Logic

```text
if isinstance(usuarios, list):
    instance.usuarios.set(Usuario.objects.filter(pk__in=usuarios))
```

## Edge cases (as implemented)

usuarios=[] (empty list) passes isinstance check and DOES clear all group members - contrast with RULE-acesso-BE-05-004 where an empty permissions dict does NOT clear permissions.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/grupo_acesso.py` | 138-139 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-05-005`

**Related rules:**

- [RULE-AUTH-USUARIOS-050](RULE-AUTH-USUARIOS-050-grupoacesso-incoming-permissoes-payload-rewrite.md)
- [RULE-AUTH-USUARIOS-053](RULE-AUTH-USUARIOS-053-user-payload-field-renames-with-empty-list-edge-case.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
