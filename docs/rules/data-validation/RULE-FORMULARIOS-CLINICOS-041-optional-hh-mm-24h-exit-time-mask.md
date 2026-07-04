# RULE-FORMULARIOS-CLINICOS-041 — Optional HH:MM 24h exit-time mask

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | formularios-clinicos |

## Rule
The horario_saida (exit time) field masked as 00:00 and validated as a 24-hour HH:MM time OR empty string.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horario_saida | string (masked) | HH:MM | 00:00-23:59 |

## Outputs

| Name | Type | Unit |
|---|---|---|
| valid | boolean | null |

## Logic

```text
mask = "00:00"
regex = /^(?:([01]\d|2[0-3]):([0-5]\d)|)$/   // hours 00-23, minutes 00-59, OR fully empty
```

## Edge cases (as implemented)

Empty value is explicitly valid (alternation with empty). "24:00" invalid; "23:59" valid.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormEnfermagem.ts | 16-22 | f9656be2 | primary |

- Merged from: RULE-time-FE-01-003

## Notes

Identical field duplicated verbatim in dataFormTecEnfermagem.ts:15-21, dataFormFisioterapeuta.ts:14-21, dataFormFarmaceutico.ts:13-19, dataFormFonoaudiologo.ts:13-19, dataFormNutricionista.ts:17-23, dataFormPsicologo.ts:13-19, dataFormMusicoterapia.ts:13-19, dataFormIntercorrencia.ts:13-19, dataFormFormularioMedico.ts:13-19.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
