# RULE-SEPSE-098 — Sepsis-checklist signer requires CPF, unlike other checklist types

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | low |
| Cluster | sepse |

## Rule
The "checado_por" (checked-by) actor on a sepsis-pathway checklist item includes a "cpf" (Brazilian tax ID) field, whereas the equivalent "checked-by"/"filled-by" actor shapes elsewhere in the codebase (Prescricao.ChecadoPor, BalancoHidrico.PreenchidoPor/DeletadoPor, Chat.ChecadoPor) only capture id and nome, without cpf.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| checado_por.cpf | string | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| checado_por | object | — |

## Logic
```text
TrilhaInterativa.Sepse.ChecadoPor = { id: string, nome: string, cpf: string }
// vs. Prescricao.ChecadoPor = { id: string, nome: string }
// vs. BalancoHidrico.PreenchidoPor / DeletadoPor = { id: string, nome: string }
// vs. Chat.ChecadoPor = { nome: string, id: string }
```

## Edge cases (as implemented)
None demonstrated in this partition beyond the shape difference itself.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/TrilhaInterativa.d.ts` | 45-49 | f9656be2 | primary |

- Merged from: RULE-sepse-FE-07-004
- Related rules: RULE-SEPSE-077

## Notes
Best interpretation is that sepsis-protocol checklist items carry a stronger medical-legal accountability requirement (CPF-verified signature) than other checklist types, given the severity/liability profile of sepsis-bundle compliance; not confirmed by any explicit validation code in this partition.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
