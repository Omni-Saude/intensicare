# RULE-BALANCO-HIDRICO-045 — Fluid-balance record signing/deletion lifecycle

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | care-pathway |
| Type | workflow |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Every fluid-balance record (Entrada/Saida/SinaisVitais) carries an "ativo" (active) flag, a per-item "can_delete" eligibility flag, an optional "data_assinatura" (signed-at timestamp) and "can_assinar" (can-sign) flag, and — when removed — a "deletado_por" (deleted-by) actor. This implies records move through the following states — created (ativo=true), then optionally signed (data_assinatura set), then optionally soft-deleted (ativo=false, deletado_por populated) — with deletion/signing eligibility computed server-side and merely exposed as booleans to the frontend.

## Inputs

- ativo
- can_delete
- can_assinar
- data_assinatura

## Outputs

- record lifecycle state

## Logic

```text
// shape-only inference, no explicit state-transition code in this partition:
state = ativo ? (data_assinatura ? "signed" : "active/unsigned") : "deleted"
can_delete and can_assinar are opaque server-computed eligibility flags (exact business
rule behind their computation is not present in this frontend partition).
```

## Edge cases (as implemented)

can_delete/can_assinar are per-record booleans, not derived client-side from any visible rule (e.g. time-since-creation) — the frontend only consumes them as already-resolved permissions.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/BalancoHidrico.d.ts` | 17-85 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-FE-07-002`

**Related rules:**

- [RULE-BALANCO-HIDRICO-026](RULE-BALANCO-HIDRICO-026-balanco-hidrico-sub-record-delete-authorization-can-delete-e.md)
- [RULE-BALANCO-HIDRICO-033](RULE-BALANCO-HIDRICO-033-balanco-hidrico-sub-record-digital-signature-eligibility-can.md)
- [RULE-BALANCO-HIDRICO-042](RULE-BALANCO-HIDRICO-042-fluid-balance-record-signature-eligibility.md)

## Notes

Best interpretation only; the actual eligibility computation (e.g. "can only delete within N minutes of creation and before signing") lives server-side and is out of scope for this frontend partition. Same can_delete/can_assinar pattern recurs on Prescricao.Horario (see RULE-prescricao-FE-07-001) and BalancoHidrico signing — a recurring medical-legal "sign to finalize" theme across the app.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
