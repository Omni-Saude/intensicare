# RULE-EVOLUCOES-067 — Interval field slider bounds

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
An interval field is entered via a Slider constrained to campo.min..campo.max; required when campo.required. In read-only mode it degrades to a disabled Input.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| value [[campo.min, campo.max]] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| value |  |  |

## Logic
```text
if (disableAll): render disabled Input
else: render Slider min={campo.min} max={campo.max}
required rule applied when campo.required.
```

## Edge cases (as implemented)
No explicit range validation message; Slider intrinsically clamps to min/max.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/SubFormsDadosProntuario/SubFormInterval/SubFormInterval.tsx` | 33-44 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-021
- Related rules: RULE-EVOLUCOES-023

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
