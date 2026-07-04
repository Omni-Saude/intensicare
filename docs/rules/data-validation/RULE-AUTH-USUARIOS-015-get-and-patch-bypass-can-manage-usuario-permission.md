# RULE-AUTH-USUARIOS-015 — GET and PATCH bypass can_manage_usuario permission

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
UsuarioViewSet declares permission_trilhas=('can_manage_usuario',) with exceto_metodo=('GET','PATCH') meaning read operations and partial updates are exempted from this trilha-permission check (enforced by TrilhasPermissaoMixin, out of partition scope); only POST/PUT/DELETE require the permission.

## Inputs

| name | type |
|---|---|
| request.method | string |

## Outputs

| name | type |
|---|---|
| permission_required | boolean |

## Logic

```text
escopo = "empresa"
permission_trilhas = ("can_manage_usuario",)
exceto_metodo = ("GET", "PATCH")
# enforcement logic lives in TrilhasPermissaoMixin (core/mixins, out of scope)
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/usuario.py` | 22-24 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-BE-05-008`

**Related rules:**

- [RULE-AUTH-USUARIOS-009](../billing-administrative/RULE-AUTH-USUARIOS-009-scope-based-rbac-permission-dispatch.md)
- [RULE-AUTH-USUARIOS-056](RULE-AUTH-USUARIOS-056-exceto-metodo-misspells-patch-as-path-across-write-viewsets.md)

## Notes

The actual permission-check enforcement mechanism (TrilhasPermissaoMixin) lives outside this partition (core/mixins); this rule records the declared configuration values observed in-scope.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
