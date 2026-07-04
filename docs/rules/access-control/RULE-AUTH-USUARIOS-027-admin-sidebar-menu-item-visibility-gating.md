# RULE-AUTH-USUARIOS-027 — Admin sidebar menu-item visibility gating

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The administrative sidebar menu shows/hides six navigation items strictly based on three permission flags — "Empresa", "Estabelecimentos", "Setores", and "Leitos" all require can_manage_empresa; "Grupos" requires can_manage_grupo_acesso; "Profissionais" requires can_manage_usuario.

## Inputs

| name | type |
|---|---|
| can_manage_empresa | boolean |
| can_manage_grupo_acesso | boolean |
| can_manage_usuario | boolean |

## Outputs

| name | type |
|---|---|
| menuItens | Utils.PropsMenuItem[] |

## Logic

```text
menuItens = []
if can_manage_empresa: menuItens += "empresa"
if can_manage_grupo_acesso: menuItens += "grupos"
if can_manage_empresa: menuItens += "estabelecimentos"
if can_manage_empresa: menuItens += "setores"
if can_manage_empresa: menuItens += "leitos"
if can_manage_usuario: menuItens += "profissionais"
// order above is exactly the order items are appended (Empresa, Grupos, Estabelecimentos, Setores, Leitos, Profissionais)
```

## Edge cases (as implemented)

A user with can_manage_grupo_acesso but not can_manage_empresa sees only "Grupos" and (if applicable) "Profissionais" — the four other admin sections are entirely hidden, not just disabled.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/useMenuByPermissions.tsx` | 9-111 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-permissoes-FE-07-003`

**Related rules:**

- [RULE-AUTH-USUARIOS-018](../data-validation/RULE-AUTH-USUARIOS-018-settings-gear-header-icon-visibility.md)
- [RULE-AUTH-USUARIOS-058](RULE-AUTH-USUARIOS-058-rbac-permission-catalog.md)

## Notes

Extends the fixed category taxonomy with 'access-control' (see RULE-permissoes-FE-07-001).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
