# RULE-AUTH-USUARIOS-019 — Company-switch dropdown visibility

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The header's company (empresa) name renders as a plain, non-clickable tag when the signed-in user has access to one or zero companies; only when the user has more than one company does it render as a clickable dropdown, whose menu lists every accessible company except the currently selected one.

## Inputs

| name | type |
|---|---|
| user.usuario.empresas | array |

## Outputs

| name | type |
|---|---|
| showDropdown | boolean |
| dropdownItems | array (excludes current empresa) |

## Logic

```text
showDropdown = (user.usuario.empresas || []).length > 1
dropdownItems = user.usuario.empresas.filter(e => e.id !== empresaAtual.id)
// if empresas.length === 0, menu shows a single disabled "Nenhuma permissão encontrada" item (though dropdown itself is unreachable, since showDropdown is false at length<=1)
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/SelectEmpresaAtual/SelectEmpresaAtual.tsx` | 16-55 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-permissao-FE-06-024`

**Related rules:**

- [RULE-AUTH-USUARIOS-027](../access-control/RULE-AUTH-USUARIOS-027-admin-sidebar-menu-item-visibility-gating.md)
- [RULE-AUTH-USUARIOS-058](../access-control/RULE-AUTH-USUARIOS-058-rbac-permission-catalog.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
