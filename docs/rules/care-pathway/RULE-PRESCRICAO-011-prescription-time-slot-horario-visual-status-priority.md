# RULE-PRESCRICAO-011 — Prescription time-slot (horario) visual status priority

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
A prescription horario (scheduled administration time) is rendered in a status color chosen by a strict priority ladder over its boolean/string state flags. This encodes the horario state machine: suspended > administered > not-administered (with reason) > add-button placeholder > pending.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horario.suspenso | boolean |  |  |
| horario.administrado | boolean |  |  |
| horario.motivo_nao_administrado | string |  |  |
| asbutton | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| colorCheck | object {icon:hexColor, tag:antdTagColor} |  |

## Logic

```text
if (horario.suspenso)                      -> { icon:"#CCCCCC", tag:"grey"   }   # suspended
else if (horario.administrado)             -> { icon:"#389e0c", tag:"green"  }   # administered
else if (horario.motivo_nao_administrado)  -> { icon:"#d4b105", tag:"yellow" }   # not administered (has reason)
else if (asbutton)                         -> { icon:"var(--primary-color)", tag:"" }  # add-new placeholder
else                                       -> { icon:"#25979c", tag:"cyan"   }   # pending/unchecked
# First matching branch wins; evaluation order is fixed (suspenso beats administrado, etc.)
```

## Edge cases (as implemented)
Order-sensitive: a suspended-and-administered horario renders as suspended (grey). Related display (CustomWrapper popover): if administrado -> icon mdiCheckCircleOutline color "#acff76" label "Administrado"; if motivo_nao_administrado -> icon mdiCloseCircleOutline color "#ff5252" label "Nao administrado corretamente". The reason label is resolved from the motivosNaoAdministrado enum, falling back to the raw stored value.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/HorarioCheck/HorarioCheck.tsx` | 126-138 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-001

**Related rules:**

- RULE-PRESCRICAO-009
- RULE-PRESCRICAO-029
- RULE-PRESCRICAO-023

## Notes
Popover status mapping at lines 55-124. Colors differ between the tag/icon set (389e0c/d4b105) and the popover set (acff76/ff5252) for the same logical states.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
