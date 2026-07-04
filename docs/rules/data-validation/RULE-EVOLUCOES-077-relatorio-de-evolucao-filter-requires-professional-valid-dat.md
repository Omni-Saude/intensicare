# RULE-EVOLUCOES-077 — Relatório de Evolução filter requires professional + valid date range

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
The evolution-report search form requires a professional (profissional_id) and a start date (data_inicio) to be filled in (defaultFormRules), and validates that the end date (data_fim), if provided, is on or after the start date; the end-date calendar disables days before the start date.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| profissional_id | string (required) |  |  |
| data_inicio | date (required) |  |  |
| data_fim | date (optional but constrained) |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| getRelatorioEvolucao(id_empresa, profissional_id, data_inicio, data_fim) | API call |  |

## Logic
```text
Form.Item("profissional_id"): rules = defaultFormRules   // required
Form.Item("data_inicio"): rules = defaultFormRules       // required
Form.Item("data_fim"): rules = [
  validator(_, value): if (!value || data_inicio <= value) resolve(); else reject("A data final deve ser maior que a data inicial"),
  ...defaultFormRules
]
disabledDate(current) = current < data_inicio.endOf("day")
onFinish: _getRelatorioEvolucao(profissional_id, data_inicio.format("YYYY-MM-DD"), data_fim.format("YYYY-MM-DD"))
```

## Edge cases (as implemented)
Same inclusive "<=" boundary as RULE-filtro-FE-05-001 despite the "maior que" (greater than) wording in the error message. defaultFormRules is spread onto data_fim's rules array AFTER the custom validator, so both are enforced together (data_fim ends up required too, despite only being visually presented as an end of a range).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FilterFormRelatorioEvolucao/FilterFormRelatorioEvolucao.tsx` | 125-188 | `f9656be2` | primary |
- Merged from: RULE-filtro-FE-05-002
- Related rules: RULE-EVOLUCOES-048

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
