# RULE-EVOLUCOES-069 — Masked field regex pattern validation

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
A masked field applies campo.mask and validates against campo.regex; required flag comes from campo.required.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| value [must match campo.regex] |  |  |  |
| campo.mask |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid |  |  |

## Logic
```text
rules = [
  { required: campo.required, message: `Informe ${label}` },
  { pattern: campo.regex, message: `Informe um valor valido para ${label}` }
]
MaskedInput mask={campo.mask || ""} inputMode="numeric"
```

## Edge cases (as implemented)
Empty regex/mask => no pattern/mask enforcement. required uses campo.required directly (may be undefined => not required).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/SubFormsDadosProntuario/SubFormMaskedInput/SubFormMaskedInput.tsx` | 28-51 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-023
- Related rules: RULE-EVOLUCOES-072, RULE-EVOLUCOES-023

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
