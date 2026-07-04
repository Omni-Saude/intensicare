# RULE-SEPSE-091 — Sepsis protocol item conditional visibility and expandability

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A sepsis protocol step is rendered only when item.exibir is true. A shown step is expandable (collapsible) only when it has a description (descricao_item) or a checker (checado_por); otherwise the panel is non-expandable.

## Inputs

- item.exibir (boolean)
- item.descricao_item (object {texto, link})
- item.checado_por (object {nome})

## Outputs

- item rendered / expandable (boolean)

## Logic

```text
if (!item.exibir) render nothing
else:
  collapsible = (item.descricao_item || item.checado_por) ? "header" : "disabled"
  showArrow   = (item.descricao_item || item.checado_por) ? true : false
  // Expanded body shows:
  //   if (checado_por && horario_checagem): "Checado por: <nome>" + date
  //   if (descricao_item.texto): description text
  //   if (descricao_item.link): image + open-in-new-tab button
```

## Edge cases (as implemented)

Steps with exibir=false are entirely hidden (conditional pathway branching). A step with neither description nor checker is displayed but not expandable.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ProtocoloSepseContent/ItemProtocoloSepse/ItemProtocoloSepse.tsx` | 17-118 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-03-003`

**Related rules:**

- [RULE-SEPSE-070](../scheduling-operational/RULE-SEPSE-070-bundle-item-visibility-exibir-reassessment-appears-after-2h.md)
- [RULE-SEPSE-092](RULE-SEPSE-092-sepsis-protocol-item-check-off-workflow.md)

## Notes

item.exibir encodes conditional care-pathway branching (which steps apply); the branching rule that sets exibir is server-side (out of partition).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
