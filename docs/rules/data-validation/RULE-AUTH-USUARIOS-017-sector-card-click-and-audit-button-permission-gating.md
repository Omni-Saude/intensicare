# RULE-AUTH-USUARIOS-017 — Sector-card click and audit-button permission gating

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
On the dashboard list, clicking a sector's card only fires the navigation callback if the card is not sector-scoped, or if it is sector-scoped and the user has `can_view_ocupacoes`; an "Auditar" button is shown only when the card is sector-scoped and the user has `can_view_auditoria`.

## Inputs

| name | type |
|---|---|
| isSetor | boolean |
| can_view_ocupacoes | boolean (permission) |
| can_view_auditoria | boolean (permission) |

## Outputs

| name | type |
|---|---|
| canClick | boolean |
| showButtonAuditoria | boolean |

## Logic

```text
canClick = isSetor ? can_view_ocupacoes : true
onCardClick = () => { if (isSetor) { if (can_view_ocupacoes) onClick(item.id) } else { onClick(item.id) } }
showButtonAuditoria = isSetor && can_view_auditoria
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ListDashboard/ListDashboard.tsx` | 41-73 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-permissao-FE-06-022`

**Related rules:**

- [RULE-AUTH-USUARIOS-027](../access-control/RULE-AUTH-USUARIOS-027-admin-sidebar-menu-item-visibility-gating.md)
- [RULE-AUTH-USUARIOS-058](../access-control/RULE-AUTH-USUARIOS-058-rbac-permission-catalog.md)

## Notes

Consumed by DashboardCard.tsx (also this partition) via the canClick/showButtonAuditoria props.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
