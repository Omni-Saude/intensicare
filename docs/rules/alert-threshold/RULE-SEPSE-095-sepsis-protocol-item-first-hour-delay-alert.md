# RULE-SEPSE-095 — Sepsis protocol item first-hour delay alert

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A sepsis protocol step that was completed/handled late relative to its first-hour target is visually flagged with a red clock-alert icon. The flag itself (atraso_primeira_hora) is computed server-side; the client renders the alert when it is true.

## Inputs

- item.atraso_primeira_hora (boolean)

## Outputs

- first-hour-delay icon shown? (boolean)

## Logic

```text
if (item.atraso_primeira_hora):
  render red clock-alert icon (mdiClockAlert, color "#e84748") next to
  item.nome_item_humanizado
```

## Edge cases (as implemented)

Purely presence-driven; no numeric threshold is evaluated client-side. Icon wrapped in an empty Popover (no explanatory content is passed).

## Divergence

Cross-implementation field-name mismatch: the backend item serializer exposes the first-hour delay flag as 'atraso_item_interativa' (computed by RULE-SEPSE-069), but the frontend type (TrilhaInterativa.d.ts) and component (ItemProtocoloSepse.tsx) read 'item.atraso_primeira_hora'. There is no 'atraso_primeira_hora' in the backend and no 'atraso_item_interativa' in the frontend, so the red first-hour-delay icon is bound to an always-undefined field and never renders.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ProtocoloSepseContent/ItemProtocoloSepse/ItemProtocoloSepse.tsx` | 42-50 | `f9656be266` | primary |
| trilhas-frontend | `src/@types/models/TrilhaInterativa.d.ts` | 26-38 | `f9656be266` | frontend-copy |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-03-002`
- `RULE-sepse-FE-07-002`

**Related rules:**

- [RULE-SEPSE-069](../scheduling-operational/RULE-SEPSE-069-bundle-item-overdue-atraso-item-interativa-time-windows.md)
- [RULE-SEPSE-070](../scheduling-operational/RULE-SEPSE-070-bundle-item-visibility-exibir-reassessment-appears-after-2h.md)

## Notes

Encodes the sepsis "first-hour bundle" concept (atraso primeira hora = delay in the first hour). The threshold logic that sets atraso_primeira_hora is in the backend (out of partition) and should be captured there; here only the alert rendering exists.
 || MERGED FE type-decl + render: RULE-sepse-FE-07-002: Aligns with the Surviving Sepsis Campaign "hour-1 bundle" concept; exact threshold-computation logic is out of scope (likely backend).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
