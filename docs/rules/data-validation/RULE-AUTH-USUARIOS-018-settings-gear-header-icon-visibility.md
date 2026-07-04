# RULE-AUTH-USUARIOS-018 — Settings-gear header icon visibility

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
The header "configurações" gear-icon button is shown only if the current user holds at least one of the administrative permissions: manage empresa, manage grupo de acesso, or manage usuário.

## Inputs

| name | type |
|---|---|
| can_manage_empresa | boolean (permission) |
| can_manage_grupo_acesso | boolean (permission) |
| can_manage_usuario | boolean (permission) |

## Outputs

| name | type |
|---|---|
| canAccessConfigs | boolean |

## Logic

```text
canAccessConfigs = can_manage_empresa || can_manage_grupo_acesso || can_manage_usuario
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/PageContainer/PageContainer.tsx` | 99-101 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-permissao-FE-06-023`

**Related rules:**

- [RULE-AUTH-USUARIOS-027](../access-control/RULE-AUTH-USUARIOS-027-admin-sidebar-menu-item-visibility-gating.md)
- [RULE-AUTH-USUARIOS-058](../access-control/RULE-AUTH-USUARIOS-058-rbac-permission-catalog.md)

## Notes

Same file also renders the footer environment label (baseURL.includes("homol") ? "Homologação" : "Produção") at lines 476-480, a minor operational (not clinical) display rule.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
