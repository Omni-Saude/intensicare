# RULE-EVOLUCOES-061 — Ventilation/device date-field adapters for nursing forms

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
For the "enfermagem" (nursing) and "tec_enfermagem" (nursing-technician) evolution forms, the avaliacao_ventilacao field (and, for enfermagem only, dispositivos_invasivos) is converted between a moment/date object (for display in the form) and a plain string (for API submission), but only when the field itself is present/truthy.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_ventilacao |  |  |  |
| dispositivos_invasivos (enfermagem only) |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| avaliacao_ventilacao / dispositivos_invasivos |  |  |

## Logic
```text
// on submit (adaptSubmit):
avaliacao_ventilacao = values.avaliacao_ventilacao ? dateTreatmentString(values.avaliacao_ventilacao) : values.avaliacao_ventilacao
dispositivos_invasivos = values.dispositivos_invasivos ? dateTreatmentString(values.dispositivos_invasivos) : values.dispositivos_invasivos   // enfermagem only

// on load (adaptValues):
avaliacao_ventilacao = values.avaliacao_ventilacao ? dateTreatmentMoment(values.avaliacao_ventilacao) : values.avaliacao_ventilacao
dispositivos_invasivos = values.dispositivos_invasivos ? dateTreatmentMoment(values.dispositivos_invasivos) : values.dispositivos_invasivos   // enfermagem only
```

## Edge cases (as implemented)
tec_enfermagem only adapts avaliacao_ventilacao (no dispositivos_invasivos handling), while enfermagem adapts both — an intentional or accidental scope difference between the two near-identical role forms.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/useEvolucaoMenu.tsx` | 107-124,155-166 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-07-002
- Related rules: none

## Notes
dateTreatmentString/dateTreatmentMoment implementations are in utils/ (out of this partition's scope).

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
