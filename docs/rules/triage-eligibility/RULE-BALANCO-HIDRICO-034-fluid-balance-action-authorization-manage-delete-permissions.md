# RULE-BALANCO-HIDRICO-034 — Fluid-balance action authorization (manage / delete permissions)

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Fluid-balance actions are gated by role permissions. Adding a new record and the Salvar/Salvar-e-Assinar and sign flows require can_manage_balanco_hidrico. Removing a record requires can_delete_balanco_hidrico. Absent the permission the corresponding control is not rendered.

## Inputs

- can_manage_balanco_hidrico
- can_delete_balanco_hidrico
- record.can_delete

## Outputs

- control visibility/enabled

## Logic

```text
showAddButton         = can_manage_balanco_hidrico
showSignButton        = can_manage_balanco_hidrico AND (sign eligibility, RULE-...-005)
showDeleteButton      = can_delete_balanco_hidrico
deleteButton.disabled = NOT record.can_delete
// Popconfirm for sign is also disabled when NOT record.can_delete
//   (BalancoHidricoContent.tsx line 276), coupling sign-confirm to can_delete.
```

## Edge cases (as implemented)

In the desktop action column the sign Popconfirm's `disabled` prop is bound to `!can_delete` (line 276) even though it is a SIGN action, so a record the user cannot delete also cannot be signed from that column. record.can_delete is a per-record backend flag distinct from the can_delete_balanco_hidrico permission.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/BalancoHidricoContent/BalancoHidricoContent.tsx` | 259-342 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-FE-03-007`

**Related rules:**

- [RULE-BALANCO-HIDRICO-026](../care-pathway/RULE-BALANCO-HIDRICO-026-balanco-hidrico-sub-record-delete-authorization-can-delete-e.md)
- [RULE-BALANCO-HIDRICO-033](../care-pathway/RULE-BALANCO-HIDRICO-033-balanco-hidrico-sub-record-digital-signature-eligibility-can.md)
- [RULE-BALANCO-HIDRICO-042](../care-pathway/RULE-BALANCO-HIDRICO-042-fluid-balance-record-signature-eligibility.md)

## Notes

Permissions come from useEffectivePermissions(). The coupling of the sign Popconfirm's disabled state to !can_delete (line 276) is arguably unintended (a sign gated by a delete flag); flagged for verifier. Add button gate at lines 472-486; delete gate at lines 291-311.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
