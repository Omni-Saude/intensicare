# RULE-AUTH-USUARIOS-011 — Permission lookup hierarchical scope resolution

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
PermissaoDeUsuarioViewSet.list resolves which permission-computation function to call using the same priority order as GrupoAcesso: setor > estabelecimento > empresa.

## Inputs

| name | type |
|---|---|
| setor__pk | uuid |
| estabelecimento__pk | uuid |

## Outputs

| name | type |
|---|---|
| permissions | object |

## Logic

```text
if kwargs.get("setor__pk"):
    permissions = get_permissoes_setor(usuario, request.setor)
elif kwargs.get("estabelecimento__pk"):
    permissions = get_permissoes_estabelecimento(usuario, request.estabelecimento)
else:
    permissions = get_permissoes_empresa(usuario, request.empresa)
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/permissao.py` | 28-38 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-05-007`

**Related rules:**

- [RULE-AUTH-USUARIOS-010](RULE-AUTH-USUARIOS-010-grupoacesso-hierarchical-scope-resolution.md)
- [RULE-AUTH-USUARIOS-008](../access-control/RULE-AUTH-USUARIOS-008-hierarchical-permission-cascade-get-permissoes-empresa-estab.md)

## Notes

get_permissoes_setor/estabelecimento/empresa implementations live in core/utils, out of this partition's scope.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
