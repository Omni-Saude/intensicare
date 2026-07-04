# RULE-PRESCRICAO-030 — Not-administered reason enum with "outros" free-text requirement

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
When a medication is marked NOT administered, a reason must be selected from a fixed enum; choosing "outros" requires an additional free-text field.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| motivo_nao_administrado | enum |  | recusa_paciente \| medicacao_suspensa \| nao_tem_farmacia \| outros |
| outros_motivos | string |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| reasonPayload | string |  |

## Logic

```text
motivo select options (utils/motivosNaoAdministrado):
  recusa_paciente   -> "Paciente recusou a administracao"
  medicacao_suspensa-> "Medicacao suspensa pelo medico"
  nao_tem_farmacia  -> "Em falta na farmacia"
  outros            -> "Outros"
Both fields required (defaultFormRules). If motivo == "outros", render required
"outros_motivos" input; final reason = outros_motivos, else = motivo_nao_administrado.
```

## Edge cases (as implemented)
The reason select and (conditionally) the outros_motivos input are both required. Only shown when the administered radio is "Nao".

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/CheckModalContent/CheckModalContent.tsx` | 133-154 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-008

**Related rules:**

- RULE-PRESCRICAO-029
- RULE-PRESCRICAO-025

## Notes
Enum definition lives in src/utils/motivosNaoAdministrado.ts (cross-partition, utils). Same enum is used for label lookup in HorarioCheck popover.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
