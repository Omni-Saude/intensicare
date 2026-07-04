# RULE-SINAIS-VITAIS-009 — PorcentagemValidator — generic percentage range

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Generic percentage field validator; value must be between 0 and 100 inclusive.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| valor | number | percent | 0-100 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| validity | raises ValidationError otherwise |  |

## Logic
```text
IF NOT (0 <= valor <= 100): RAISE ValidationError(f"{valor} deve estar entre 0 e 100")
(TypeError on non-numeric input -> ValidationError "deve ser um numero")
```

## Edge cases (as implemented)
No zero-value exemption; 0 and 100 are both valid boundary values.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 32-43 | `8166c07e` | primary |

- Merged from: RULE-vitais-BE-11-006

## Notes
Generic percentage validator; used wherever a percentage-typed field needs bounding (not tied to one specific vital sign). No dedicated model-field capture in this cluster.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
