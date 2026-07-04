# RULE-AUTH-USUARIOS-008 — Hierarchical permission cascade (get_permissoes_empresa/estabelecimento/setor)

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | eligibility |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A user's effective permission codenames at a level are the union of permissions granted by access-groups at that level plus all permissions inherited from the parent level(s) - setor inherits estabelecimento, which inherits empresa.

## Inputs

| name | type | range |
|---|---|---|
| usuario | object | - |
| empresa\|estabelecimento\|setor | object | may be null (empresa) |

## Outputs

| name | type | unit |
|---|---|---|
| permissoes | list<string> | codenames |

## Logic

```text
get_permissoes_empresa(usuario, empresa):
    if not empresa: return []
    payload = []
    for grupo_acesso in empresa.grupos_acessos.filter(usuarios=usuario):
        payload += grupo_acesso.grupo.permissions.values_list("codename")
    return list(set(payload))
get_permissoes_estabelecimento(usuario, estab):
    payload = get_permissoes_empresa(usuario, estab.empresa)         # inherit up
    payload += (estab.grupos_acessos.filter(usuarios=usuario) permissions)
    return list(set(payload))
get_permissoes_setor(usuario, setor):
    payload = get_permissoes_estabelecimento(usuario, setor.estabelecimento)  # inherit up
    payload += (setor.grupos_acessos.filter(usuarios=usuario) permissions)
    return list(set(payload))
```

## Edge cases (as implemented)

Null empresa short-circuits to empty list. De-duplicated via set(). Only groups whose membership includes this usuario contribute. Permissions strictly cascade DOWN (parent perms flow to children); child perms do not flow up.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/utils.py` | 107-142 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ACCESS-BE-12-013`

**Related rules:**

- [RULE-AUTH-USUARIOS-009](../billing-administrative/RULE-AUTH-USUARIOS-009-scope-based-rbac-permission-dispatch.md)
- [RULE-AUTH-USUARIOS-010](../data-validation/RULE-AUTH-USUARIOS-010-grupoacesso-hierarchical-scope-resolution.md)
- [RULE-AUTH-USUARIOS-011](../data-validation/RULE-AUTH-USUARIOS-011-permission-lookup-hierarchical-scope-resolution.md)
- [RULE-AUTH-USUARIOS-002](../data-validation/RULE-AUTH-USUARIOS-002-user-cargos-roles-empresa-scoped-lookup.md)

## Notes

category 'access-control' added (none of the enumerated categories cover authorization; guidance lists permission/authorization predicates as rule-bearing). Org hierarchy - Empresa > Estabelecimento > Setor.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
