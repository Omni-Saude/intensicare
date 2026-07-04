# RULE-EVOLUCOES-060 — Nutritional-assessment numeric coercion on load

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When loading a nutritionist evolution-form entry for editing, the weight (peso), height (altura), and BMI (imc) fields nested under avaliacao_global are coerced from string (as received from the API) to number via unary plus, but only if avaliacao_global itself is present.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_global.peso |  |  |  |
| avaliacao_global.altura |  |  |  |
| avaliacao_global.imc |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| avaliacao_global.peso / altura / imc |  |  |

## Logic
```text
if values.avaliacao_global:
  values.avaliacao_global.peso = +values.avaliacao_global.peso
  values.avaliacao_global.altura = +values.avaliacao_global.altura
  values.avaliacao_global.imc = +values.avaliacao_global.imc
else:
  avaliacao_global left undefined/falsy, no coercion attempted
```

## Edge cases (as implemented)
Unary-plus coercion of a non-numeric string yields NaN silently (no validation/guard against malformed API values in this partition). No corresponding reverse (number->string) coercion is applied on submit (adaptSubmit is not defined for this form, unlike enfermagem/tec_enfermagem).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/useEvolucaoMenu.tsx` | 255-263 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-07-001
- Related rules: none

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
