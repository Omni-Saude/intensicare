# RULE-AUTH-USUARIOS-010 — GrupoAcesso hierarchical scope resolution

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
GrupoAcesso queryset filtering and creation scope resolve in priority order: setor (if setor__pk in URL) > estabelecimento (if estabelecimento__pk in URL) > empresa (default/fallback).

## Inputs

| name | type |
|---|---|
| setor__pk | uuid |
| estabelecimento__pk | uuid |

## Outputs

| name | type |
|---|---|
| queryset_scope | string enum |

## Logic

```text
qs = GrupoAcesso.objects_without_deleted.all()
if kwargs.get("setor__pk"):
    qs = qs.filter(setor=request.setor.pk)
elif kwargs.get("estabelecimento__pk"):
    qs = qs.filter(estabelecimento=request.estabelecimento.pk)
else:
    qs = qs.filter(empresa=request.empresa.pk)
# create() mirrors this: injects request.data["setor"|"estabelecimento"|"empresa"] using same if/elif/else order
```

## Edge cases (as implemented)

Soft-deleted groups excluded via objects_without_deleted manager. Only one of the three scopes is ever applied, never combined.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/grupo_acesso.py` | 21-39 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-05-001`

**Related rules:**

- [RULE-AUTH-USUARIOS-011](RULE-AUTH-USUARIOS-011-permission-lookup-hierarchical-scope-resolution.md)
- [RULE-AUTH-USUARIOS-008](../access-control/RULE-AUTH-USUARIOS-008-hierarchical-permission-cascade-get-permissoes-empresa-estab.md)

## Notes

Same setor>estabelecimento>empresa priority pattern is reused in PermissaoDeUsuarioViewSet (RULE-acesso-BE-05-007).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
