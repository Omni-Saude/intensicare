# RULE-EVOLUCOES-071 — Required-if validation for text/date/extra fields

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
String (textarea), date, select, boolean, checkbox and the "extra" text field apply the standard required rule only when campo.required is true.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| campo.required |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| rules |  |  |

## Logic
```text
rules = campo.required ? [{ required:true, message:"Este campo e obrigatorio!" }] : undefined
# FieldSetStringExtra (nome_extra/label_extra) rendered only when both nome_extra and label_extra set.
# SubFormData format = campo.showTime ? "DD/MM/Y HH:mm" : "DD/MM/Y"
```

## Edge cases (as implemented)
The extra-field's required also keys off the PARENT campo.required (not a separate flag).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/SubFormsDadosProntuario/FieldSetStringExtra/FieldSetStringExtra.tsx` | 22-33 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-027
- Related rules: RULE-EVOLUCOES-072

## Notes
Same required-if pattern: SubFormString.tsx (39-55, and a disabled-condition discrepancy noted in RULE-prontuario-FE-04-029), SubFormData.tsx (37-52), SubFormSelect/Boolean/Checkbox.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
