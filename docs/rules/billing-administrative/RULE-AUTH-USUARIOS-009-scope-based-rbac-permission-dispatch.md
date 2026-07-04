# RULE-AUTH-USUARIOS-009 — Scope-based RBAC permission dispatch

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | billing-administrative |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Enforces per-view permission requirements resolved against a configurable scope (empresa/estabelecimento/setor), with optional per-HTTP-method permissions and method-based bypass.

## Inputs

| name | type | range |
|---|---|---|
| permission_trilhas | str \| tuple/list of (str \| (str, METHOD)) |  |
| escopo | string | empresa\|estabelecimento\|setor (default empresa) |
| exceto_metodo | str \| list/tuple |  |

## Outputs

| name | type |
|---|---|
| allow \| 403/404/400 error | HTTP response |

## Logic

```text
dispatch():
  if call_permission_mixin() and permission_trilhas is not None:
    if request.method in exceto_metodo (case-insensitive): allow (super().dispatch)
    if user.is_anonymous: 403 "Usuário não tem permissão..."
    resolve required `permission`:
      - str -> that permission
      - tuple/list -> for each entry: if str set permission; if (perm, METHOD) and METHOD matches request.method -> permission=perm & break, else permission=""
      - otherwise -> 400 "Permissão configurada incorretamente"
    permissoes = switcher[escopo](user, getattr(request, escopo))
      where switcher = {empresa:get_permissoes_empresa, estabelecimento:get_permissoes_estabelecimento, setor:get_permissoes_setor}
      if getattr(request, escopo) is None -> 404 "<Escopo> não encontrado!"
    if permission not in permissoes: 403
  super().dispatch()
```

## Edge cases (as implemented)

Tuple form with a matching (perm, METHOD) short-circuits; a bare string in the tuple sets permission for all methods. Empty permission "" (no method match) will fail the membership check -> 403. Scope object fetched via getattr(request, escopo).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/mixins/permissao.py` | 37-132 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-04-049`

**Related rules:**

- [RULE-AUTH-USUARIOS-008](../access-control/RULE-AUTH-USUARIOS-008-hierarchical-permission-cascade-get-permissoes-empresa-estab.md)
- [RULE-AUTH-USUARIOS-015](../data-validation/RULE-AUTH-USUARIOS-015-get-and-patch-bypass-can-manage-usuario-permission.md)
- [RULE-AUTH-USUARIOS-056](../data-validation/RULE-AUTH-USUARIOS-056-exceto-metodo-misspells-patch-as-path-across-write-viewsets.md)

## Notes

get_permissoes_* helpers in core.utils (out of partition). This is the live RBAC path (vs the dormant PermissaoChoices in RULE-008).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
