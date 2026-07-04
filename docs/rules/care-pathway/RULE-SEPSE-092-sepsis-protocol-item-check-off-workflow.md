# RULE-SEPSE-092 — Sepsis protocol item check-off workflow

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Each sepsis protocol step can be checked off. The checkbox is interactive only when an onCheck handler is supplied (otherwise read-only). Toggling calls onCheck(item.id, checked). Label reads "Checado" if already checked, else "Checar". A checked item records checado_por and horario_checagem.

## Inputs

- item.checado (boolean)
- onCheck (function|undefined)

## Outputs

- onCheck(item.id, checked) (side-effect)

## Logic

```text
checkbox.disabled = onCheck ? false : true
checkbox.defaultChecked = item.checado || false
onClick(e):
  stopPropagation()
  setChecado(e.target.checked)
  if (onCheck) onCheck(item.id, e.target.checked)
label = item.checado ? "Checado" : "Checar"
```

## Edge cases (as implemented)

With no onCheck the checkbox is disabled (view-only mode, e.g. history). e.stopPropagation prevents the click from toggling the Collapse panel.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ProtocoloSepseContent/ItemProtocoloSepse/ItemProtocoloSepse.tsx` | 55-66 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-03-004`

**Related rules:**

- [RULE-SEPSE-075](RULE-SEPSE-075-sepse-item-check-uncheck-and-protocol-completion-state-machi.md)
- [RULE-SEPSE-077](RULE-SEPSE-077-sepse-item-checker-auto-attribution.md)

## Notes

The onCheck callback wiring to the backend PATCH is provided by the parent page (out of partition); ProtocoloSepseContent passes it through unchanged (lines 101-106).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
