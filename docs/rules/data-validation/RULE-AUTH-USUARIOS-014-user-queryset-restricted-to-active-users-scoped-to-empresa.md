# RULE-AUTH-USUARIOS-014 — User queryset restricted to active users scoped to empresa

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
UsuarioViewSet.get_queryset only returns users with is_active=True, additionally filtered to users belonging to request.empresa when present on the request.

## Inputs

| name | type |
|---|---|
| request.empresa | object\|null |

## Outputs

| name | type |
|---|---|
| queryset | queryset of Usuario |

## Logic

```text
qs = Usuario.objects.filter(is_active=True)
if request.empresa:
    qs = qs.filter(empresas=request.empresa)
return qs
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/usuario.py` | 42-48 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-BE-05-006`

**Related rules:**

- [RULE-AUTH-USUARIOS-040](../care-pathway/RULE-AUTH-USUARIOS-040-user-deletion-is-a-soft-delete-is-active-flag.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
