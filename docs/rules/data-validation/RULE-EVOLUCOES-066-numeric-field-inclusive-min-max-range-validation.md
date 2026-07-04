# RULE-EVOLUCOES-066 — Numeric field inclusive min/max range validation

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
A number field is validated to lie within [campo.min, campo.max] inclusive, and is required when campo.required.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| value [[campo.min, campo.max]] |  |  |  |
| campo.required |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid |  |  |

## Logic
```text
rules = [
  { type:"number", max: campo.max, min: campo.min,
    message: `Valor invalido! O valor deve estar entre ${campo.min} e ${campo.max}` },
  ...(campo.required ? [{ required:true, message:"Este campo e obrigatorio!" }] : [])
]
```

## Edge cases (as implemented)
antd type:number max/min are inclusive bounds. If campo.min/max undefined, the corresponding bound is not enforced but the message still interpolates "undefined".

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/SubFormsDadosProntuario/SubFormNumber/SubFormNumber.tsx` | 32-51 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-020
- Related rules: RULE-EVOLUCOES-072, RULE-EVOLUCOES-023

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
