# RULE-EVOLUCOES-023 — Dynamic clinical-form field-type vocabulary (declared union vs render dispatch)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
The set of input types the dynamic clinical-form engine supports is declared as the CampoType TypeScript union (11 members) but consumed by the SelectCampoType render dispatch, which maps only 10 of them to widgets. The 'time' member is declared as a valid field type but has no render branch, so a 'time' field silently renders no control.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| campo.type |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| widget (SubForm* React component) or nothing |  |  |

## Logic
```text
CampoType (src/@types/models/DadosFormDinamico.d.ts) =
  select | interval | number | boolean | data | list | string | masked | time | multicheck | checkbox   # 11 declared
SelectCampoType render dispatch (SubForm* widgets):
  "string"     -> SubFormString
  "select"     -> SubFormSelect
  "interval"   -> SubFormInterval
  "number"     -> SubFormNumber
  "boolean"    -> SubFormBoolean
  "checkbox"   -> SubFormCheckbox
  "data"       -> SubFormData
  "list"       -> SubFormList
  "masked"     -> SubFormMaskedInput
  "multicheck" -> SubFormMultiCheck
  # NO branch for "time"  -> unknown/unhandled type renders nothing
```

## Edge cases (as implemented)
A 'time'-typed field is valid per the CampoType union but matches no dispatch branch and renders no input at all. Any unhandled type renders nothing. campo.mainKey injects a hidden [mainKey,'id'] field.

## Divergence
CampoType union declares 11 types INCLUDING 'time' (DadosFormDinamico.d.ts:53-64); SelectCampoType dispatch implements only 10 and has NO case for 'time' (SelectCampoType.tsx:74-160), so a 'time' field renders nothing. The other 10 types match on both sides. Declaration side = formdinamico enum; consumer side = prontuario dispatch.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/DadosFormDinamico.d.ts` | 53-64 | `f9656be2` | primary |
| trilhas-frontend | `src/components/FormDadosProntuario/SubFormsDadosProntuario/SelectCampoType/SelectCampoType.tsx` | 61-171 | `f9656be2` | duplicate |
- Merged from: RULE-formdinamico-FE-07-003, RULE-prontuario-FE-04-019
- Related rules: RULE-EVOLUCOES-072, RULE-EVOLUCOES-073, RULE-EVOLUCOES-066, RULE-EVOLUCOES-067, RULE-EVOLUCOES-068, RULE-EVOLUCOES-069, RULE-EVOLUCOES-070

## Notes
Phase-1 captured these as two separate OK rules (RULE-formdinamico-FE-07-003 field-type enumeration + RULE-prontuario-FE-04-019 dispatch vocabulary). Reconciliation compared them against the legacy source at commit f9656be2660ec2048ce6240b4ac418b7fe7d5a5b and found the 'time' gap — a NEW divergence not flagged in Phase 1. Merged; status upgraded to DISCREPANCY.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
